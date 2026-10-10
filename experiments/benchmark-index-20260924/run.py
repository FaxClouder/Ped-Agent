"""Build isolated V1 retrieval indexes for the frozen 104-paper corpus."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sqlite3
import subprocess
from pathlib import Path

from ped_knowledge.indexing import ChromaVectorIndex, FTSIndex, embedding_fingerprint
from ped_knowledge.storage import Catalog


ROOT = Path(__file__).resolve().parents[2]
POLICY = "parent-child-v1"
TOKENIZER = "regex-token-v1"
MODEL_ID = "BAAI/bge-m3"


class BGEM3Gateway:
    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path
        self.model = None

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if self.model is None:
            from FlagEmbedding import BGEM3FlagModel

            self.model = BGEM3FlagModel(
                str(self.model_path), devices="cuda:0", use_fp16=True
            )
        result = self.model.encode(
            texts,
            batch_size=8,
            max_length=1024,
            return_dense=True,
            return_sparse=False,
            return_colbert_vecs=False,
        )
        return result["dense_vecs"].tolist()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_corpus(catalog: Catalog, manifest_path: Path) -> tuple[list[dict], str]:
    records = [
        json.loads(line)
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    expected = {record["resource_id"]: record["sha256"] for record in records}
    if len(records) != 104 or len(expected) != 104 or not all(
        record["include"] is True for record in records
    ):
        raise ValueError("expected 104 unique, included manifest records")
    with sqlite3.connect(f"file:{catalog.path.as_posix()}?mode=ro", uri=True) as db:
        actual = dict(
            db.execute(
                "SELECT resource_id, active_version_id FROM resources "
                "WHERE retrieval_eligibility = 'official'"
            )
        )
    if actual != expected:
        raise ValueError("active official Catalog members do not match the manifest")
    chunks = catalog.list_official_chunks(policy_version=POLICY)
    if {chunk["resource_id"] for chunk in chunks} != set(expected):
        raise ValueError("one or more manifest resources have no active child chunks")
    if {chunk["tokenizer_fingerprint"] for chunk in chunks} != {TOKENIZER}:
        raise ValueError("unexpected tokenizer fingerprint")
    return chunks, catalog.official_fingerprint(policy_version=POLICY)


async def build(output_dir: Path) -> None:
    if output_dir.exists():
        raise FileExistsError(f"output directory already exists: {output_dir}")
    manifest = ROOT / "memPed/knowledge/literature/records/core_manifest.jsonl"
    catalog = Catalog(ROOT / "memPed/knowledge/knowledge.sqlite3")
    model_dir = ROOT / "memPed/knowledge/models/bge-m3"
    weights = model_dir / "pytorch_model.bin"
    model_manifest = json.loads((model_dir / "model_manifest.json").read_text(encoding="utf-8"))
    actual_weight_hash = sha256_file(weights)
    if actual_weight_hash != model_manifest["weights"]["pytorch_model.bin"]["sha256"]:
        raise ValueError("BGE-M3 weight hash differs from model manifest")
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for this configured BGE-M3 experiment")
    chunks, catalog_fingerprint = verify_corpus(catalog, manifest)
    code_revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    output_dir.mkdir(parents=True)
    fts = FTSIndex(output_dir / "fts.sqlite3")
    fts.rebuild(
        chunks,
        source_fingerprint=catalog_fingerprint,
        policy_version=POLICY,
        tokenizer_fingerprint=TOKENIZER,
        code_revision=code_revision,
    )
    with sqlite3.connect(output_dir / "fts.sqlite3") as db:
        fts_count = db.execute("SELECT count(*) FROM documents").fetchone()[0]
    if fts_count != len(chunks):
        raise RuntimeError("FTS5 entry count differs from active child chunk count")
    print(f"FTS5 ready: {fts_count} child chunks", flush=True)

    vector = ChromaVectorIndex(output_dir / "chroma", BGEM3Gateway(model_dir))
    embedding_fp = embedding_fingerprint(model=MODEL_ID, base_url=None, dimensions=1024)
    await vector.rebuild(
        chunks,
        catalog_fingerprint=catalog_fingerprint,
        embedding_fingerprint=embedding_fp,
        policy_version=POLICY,
        tokenizer_fingerprint=TOKENIZER,
        embedding_max_length=1024,
        lexical_analyzer_fingerprint=fts.lexical_analyzer_fingerprint(),
        code_revision=code_revision,
    )
    vector_count = vector._collection().count()
    if vector_count != len(chunks):
        raise RuntimeError("Chroma entry count differs from active child chunk count")
    report = {
        "status": "complete",
        "resource_count": 104,
        "child_chunk_count": len(chunks),
        "fts_entry_count": fts_count,
        "chroma_entry_count": vector_count,
        "policy_version": POLICY,
        "tokenizer_fingerprint": TOKENIZER,
        "lexical_analyzer_fingerprint": fts.lexical_analyzer_fingerprint(),
        "catalog_fingerprint": catalog_fingerprint,
        "manifest_sha256": sha256_file(manifest),
        "model_id": MODEL_ID,
        "model_revision": model_manifest["revision"],
        "model_weights_sha256": actual_weight_hash,
        "embedding_fingerprint": embedding_fp,
        "embedding_max_length": 1024,
        "normalize_embeddings": True,
        "device": "cuda:0",
        "fp16": True,
        "code_revision": code_revision,
        "runner_sha256": sha256_file(Path(__file__)),
        "gold_sha256": "",
        "random_seed": None,
    }
    (output_dir / "build_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(build(args.output_dir.resolve()))
