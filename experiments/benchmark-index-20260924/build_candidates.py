"""Build separately named candidate indexes without changing the Catalog or V1 index.

Modes: V1 chunks with pinned domain lexical analyzer (FTS only), or V2 chunks
from frozen canonical documents with base lexical analyzer and BGE-M3 vectors.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sqlite3
import subprocess
from pathlib import Path

import yaml

from ped_knowledge.chunking import HierarchicalChunker
from ped_knowledge.contracts import CanonicalDocument, ChunkLevel, ChunkingPolicy
from ped_knowledge.indexing import ChromaVectorIndex, FTSIndex, embedding_fingerprint
from ped_knowledge.storage import Catalog
from ped_knowledge.tokenization import HuggingFaceTokenCounter, JiebaLexicalAnalyzer

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "memPed/knowledge/literature/records/core_manifest.jsonl"
CATALOG = ROOT / "memPed/knowledge/knowledge.sqlite3"
MODEL_DIR = ROOT / "memPed/knowledge/models/bge-m3"
V1_REPORT = ROOT / "outputs/knowledge-index-104-v1-20260924-01/build_report.json"
V2_POLICY = ROOT / "Knowledge-Base/config/retrieval/chunking-v2.yaml"
LEXICAL_POLICY = ROOT / "Knowledge-Base/config/retrieval/lexical-v1.yaml"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def guard_output(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite research output: {path}")


def verify_manifest_members(records: list[dict], active: dict[str, str], *, expected_count: int = 104) -> None:
    expected = {item["resource_id"]: item["sha256"] for item in records}
    if (len(records) != expected_count or len(expected) != expected_count
            or not all(item["include"] is True for item in records) or expected != active):
        raise ValueError("manifest and active Catalog members differ")


def chroma_content_sha256(collection: object) -> str:
    """Fingerprint stored IDs, vectors, documents and metadata independent of row order."""
    import numpy as np

    data = collection.get(include=["embeddings", "documents", "metadatas"])
    ids = data["ids"]
    embeddings = data["embeddings"]
    documents = data["documents"]
    metadatas = data["metadatas"]
    if embeddings is None or documents is None or metadatas is None or len(set(ids)) != len(ids):
        raise ValueError("incomplete Chroma collection content")
    digest = hashlib.sha256()
    for index in sorted(range(len(ids)), key=lambda item: ids[item]):
        payloads = (
            ids[index].encode("utf-8"),
            np.asarray(embeddings[index], dtype="<f4").tobytes(),
            documents[index].encode("utf-8"),
            json.dumps(metadatas[index], sort_keys=True, separators=(",", ":")).encode("utf-8"),
        )
        for payload in payloads:
            digest.update(len(payload).to_bytes(8, "big"))
            digest.update(payload)
    return digest.hexdigest()


class BGEM3Gateway:
    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path
        self.model = None

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if self.model is None:
            from FlagEmbedding import BGEM3FlagModel

            self.model = BGEM3FlagModel(str(self.model_path), devices="cuda:0", use_fp16=True)
        vectors = self.model.encode(
            texts, batch_size=8, max_length=1024, return_dense=True,
            return_sparse=False, return_colbert_vecs=False,
        )["dense_vecs"]
        return vectors.tolist()


def _v2_chunks(records: list[dict], catalog: Catalog) -> tuple[list[dict], dict[str, str], str]:
    config = yaml.safe_load(V2_POLICY.read_text(encoding="utf-8"))
    if config["policy_version"] != "parent-child-v2" or config["status"] != "candidate":
        raise ValueError("unexpected V2 candidate policy")
    tokenizer_path = ROOT / config["tokenizer"]["local_path"]
    token_counter = HuggingFaceTokenCounter.from_local_path(
        tokenizer_path, expected_sha256=config["tokenizer"]["sha256"]
    )
    policy = ChunkingPolicy(
        policy_version="parent-child-v2",
        parent_target_tokens=config["parent"]["target_tokens"],
        parent_max_tokens=config["parent"]["max_tokens"],
        child_target_tokens=config["child"]["target_tokens"],
        child_max_tokens=config["child"]["max_tokens"],
        child_overlap_tokens=config["child"]["overlap_tokens"],
    )
    chunker = HierarchicalChunker(policy, token_counter=token_counter)
    children: list[dict] = []
    canonical_hashes = {}
    for record in sorted(records, key=lambda item: item["resource_id"]):
        resource = record["resource_id"]
        digest = record["sha256"]
        doc_path = ROOT / "memPed/knowledge/derived" / resource / digest / "document.json"
        document = CanonicalDocument.model_validate_json(doc_path.read_text(encoding="utf-8"))
        if (document.resource_id, document.version_id, document.source_hash) != (resource, digest, digest):
            raise ValueError(f"canonical document source mismatch: {resource}")
        canonical_hashes[resource] = sha256(doc_path)
        title = catalog.get_resource(resource)["title"]
        for chunk in chunker.chunk(document):
            if chunk.chunk_level is ChunkLevel.CHILD:
                row = chunk.model_dump(mode="json")
                row["title"] = title
                if row["token_count"] > policy.child_max_tokens or row["tokenizer_fingerprint"] != token_counter.fingerprint:
                    raise ValueError(f"invalid V2 child budget or tokenizer: {chunk.chunk_id}")
                children.append(row)
    return children, canonical_hashes, token_counter.fingerprint


def _fingerprint(chunks: list[dict]) -> str:
    digest = hashlib.sha256()
    for row in sorted(chunks, key=lambda item: (item["resource_id"], item["ordinal"])):
        digest.update(row["chunk_id"].encode("utf-8"))
        digest.update(row["text"].encode("utf-8"))
    return digest.hexdigest()


async def build(output_dir: Path, *, mode: str) -> dict:
    guard_output(output_dir)
    if mode not in {"v2", "lexical-v1"}:
        raise ValueError(mode)
    records = [json.loads(line) for line in MANIFEST.read_text(encoding="utf-8").splitlines() if line.strip()]
    with sqlite3.connect(f"file:{CATALOG.as_posix()}?mode=ro", uri=True) as db:
        active = dict(db.execute("SELECT resource_id, active_version_id FROM resources WHERE retrieval_eligibility = 'official'"))
    verify_manifest_members(records, active)
    catalog = Catalog(CATALOG)
    v1_report = json.loads(V1_REPORT.read_text(encoding="utf-8"))
    if (sha256(MANIFEST) != v1_report["manifest_sha256"]
            or catalog.official_fingerprint(policy_version="parent-child-v1") != v1_report["catalog_fingerprint"]):
        raise ValueError("V1 corpus fingerprint changed")
    canonical_hashes = None
    if mode == "v2":
        chunks, canonical_hashes, tokenizer_fp = _v2_chunks(records, catalog)
        analyzer = JiebaLexicalAnalyzer()
        policy_version = "parent-child-v2"
        policy_path = V2_POLICY
    else:
        chunks = catalog.list_official_chunks(policy_version="parent-child-v1")
        tokenizer_fp = v1_report["tokenizer_fingerprint"]
        config = yaml.safe_load(LEXICAL_POLICY.read_text(encoding="utf-8"))
        if config["analyzer_version"] != "jieba-lexical-v1" or config["status"] != "candidate":
            raise ValueError("unexpected lexical candidate policy")
        analyzer = JiebaLexicalAnalyzer(
            domain_terms_path=ROOT / config["domain_terms_path"],
            stopwords_path=ROOT / config["stopwords_path"],
            version=config["analyzer_version"],
        )
        policy_version = "parent-child-v1"
        policy_path = LEXICAL_POLICY
    if {row["resource_id"] for row in chunks} != set(active) or len({row["chunk_id"] for row in chunks}) != len(chunks):
        raise ValueError("candidate chunks do not cover the exact corpus")
    chunk_fp = _fingerprint(chunks)
    if mode == "lexical-v1" and chunk_fp != v1_report["catalog_fingerprint"]:
        raise ValueError("lexical experiment changed V1 chunks")
    model_manifest = json.loads((MODEL_DIR / "model_manifest.json").read_text(encoding="utf-8"))
    weights_sha = None
    if mode == "v2":
        import torch

        if not torch.cuda.is_available():
            raise RuntimeError("CUDA required for V2 BGE-M3 index")
        weights_sha = sha256(MODEL_DIR / "pytorch_model.bin")
        if weights_sha != model_manifest["weights"]["pytorch_model.bin"]["sha256"]:
            raise ValueError("model weights differ from pinned manifest")
    code_revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    output_dir.mkdir(parents=True)
    if mode == "v2":
        with (output_dir / "child_chunks.jsonl").open("x", encoding="utf-8") as stream:
            for chunk in chunks:
                stream.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    fts = FTSIndex(output_dir / "fts.sqlite3", analyzer=analyzer)
    fts.rebuild(chunks, source_fingerprint=chunk_fp, policy_version=policy_version,
                tokenizer_fingerprint=tokenizer_fp, code_revision=code_revision)
    with sqlite3.connect(output_dir / "fts.sqlite3") as db:
        count = db.execute("SELECT count(*) FROM documents").fetchone()[0]
    if count != len(chunks) or fts.lexical_analyzer_fingerprint() != analyzer.fingerprint:
        raise RuntimeError("candidate FTS build verification failed")
    vector_count = None
    vector_content_sha = None
    embedding_fp = v1_report["embedding_fingerprint"]
    if mode == "v2":
        vector = ChromaVectorIndex(output_dir / "chroma", BGEM3Gateway(MODEL_DIR))
        embedding_fp = embedding_fingerprint(model="BAAI/bge-m3", base_url=None, dimensions=1024)
        if embedding_fp != v1_report["embedding_fingerprint"]:
            raise ValueError("embedding configuration differs from V1")
        await vector.rebuild(chunks, catalog_fingerprint=chunk_fp,
            embedding_fingerprint=embedding_fp, policy_version=policy_version,
            tokenizer_fingerprint=tokenizer_fp, embedding_max_length=1024,
            lexical_analyzer_fingerprint=analyzer.fingerprint, code_revision=code_revision)
        vector_count = vector._collection().count()
        if vector_count != len(chunks):
            raise RuntimeError("candidate Chroma count mismatch")
        vector_content_sha = chroma_content_sha256(vector._collection())
    report = {
        "status": "complete_candidate_index", "mode": mode,
        "not_active_default": True, "resource_count": len(active),
        "child_chunk_count": len(chunks), "fts_entry_count": count,
        "chroma_entry_count": vector_count,
        "chroma_content_sha256": vector_content_sha,
        "policy_version": policy_version, "policy_config_sha256": sha256(policy_path),
        "tokenizer_fingerprint": tokenizer_fp,
        "lexical_analyzer_fingerprint": analyzer.fingerprint,
        "catalog_or_chunk_fingerprint": chunk_fp,
        "v1_catalog_fingerprint": v1_report["catalog_fingerprint"],
        "manifest_sha256": sha256(MANIFEST),
        "canonical_document_sha256_by_resource": canonical_hashes,
        "model_id": "BAAI/bge-m3", "model_revision": model_manifest["revision"],
        "model_weights_sha256": weights_sha or v1_report["model_weights_sha256"],
        "embedding_fingerprint": embedding_fp,
        "dense_index_status": "built" if mode == "v2" else "reuses_frozen_v1_for_future_controlled_comparison",
        "random_seed": None, "code_revision": code_revision,
        "runner_sha256": sha256(Path(__file__)),
    }
    report["output_sha256"] = {"fts.sqlite3": sha256(output_dir / "fts.sqlite3")}
    if mode == "v2":
        report["output_sha256"]["child_chunks.jsonl"] = sha256(output_dir / "child_chunks.jsonl")
    (output_dir / "build_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("v2", "lexical-v1"), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(build(args.output_dir, mode=args.mode)), ensure_ascii=False, indent=2))
