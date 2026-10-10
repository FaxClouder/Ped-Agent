"""Run V2 candidate BM25, BGE-M3 and RRF on Gold v5 development intents.

This is a candidate-label experiment; it does not activate V2 or read sealed test.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

import yaml

from ped_knowledge.chunking import HierarchicalChunker
from ped_knowledge.contracts import CanonicalDocument, ChunkLevel, ChunkingPolicy
from ped_knowledge.evaluation.gold_v2 import score_answerable
from ped_knowledge.indexing import ChromaVectorIndex, FTSIndex
from ped_knowledge.storage import Catalog
from ped_knowledge.tokenization import HuggingFaceTokenCounter

from compare_lexical_candidate import fuse_rrf, read_jsonl, sha256, _distinct_top, _aggregate
from dev_scope import load_dev_scope

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments/benchmark-index-20260924"))
from build_candidates import chroma_content_sha256

GOLD = ROOT / "memPed/knowledge/gold/2026-09-23-rebuild"
INDEX = ROOT / "outputs/knowledge-index-104-v2-candidate-20260926-01"
MANIFEST = ROOT / "memPed/knowledge/literature/records/core_manifest.jsonl"
POLICY_CONFIG = ROOT / "Knowledge-Base/config/retrieval/chunking-v2.yaml"
V1_SUMMARY = ROOT / "outputs/gold-v5-dev-exploratory-20260924-01/summary.json"
MODEL_DIR = ROOT / "memPed/knowledge/models/bge-m3"


def verify_report(report: dict, *, manifest_sha: str) -> None:
    if report.get("status") != "complete_candidate_index" or report.get("mode") != "v2" or report.get("policy_version") != "parent-child-v2":
        raise ValueError("candidate index policy or build status mismatch")
    if report.get("manifest_sha256") != manifest_sha:
        raise ValueError("candidate index corpus manifest mismatch")
    for key in ("tokenizer_fingerprint", "lexical_analyzer_fingerprint", "catalog_or_chunk_fingerprint", "embedding_fingerprint", "chroma_content_sha256"):
        if not report.get(key):
            raise ValueError(f"missing candidate index fingerprint: {key}")
    if not report.get("output_sha256", {}).get("fts.sqlite3"):
        raise ValueError("missing candidate FTS content fingerprint")


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


def _parent_contexts(counter: HuggingFaceTokenCounter, chunks: dict[str, dict]) -> dict[str, str]:
    config = yaml.safe_load(POLICY_CONFIG.read_text(encoding="utf-8"))
    policy = ChunkingPolicy(
        policy_version="parent-child-v2",
        parent_target_tokens=config["parent"]["target_tokens"],
        parent_max_tokens=config["parent"]["max_tokens"],
        child_target_tokens=config["child"]["target_tokens"],
        child_max_tokens=config["child"]["max_tokens"],
        child_overlap_tokens=config["child"]["overlap_tokens"],
    )
    chunker = HierarchicalChunker(policy, token_counter=counter)
    parents: dict[str, str] = {}
    seen_children = set()
    for record in sorted(read_jsonl(MANIFEST), key=lambda item: item["resource_id"]):
        path = ROOT / "memPed/knowledge/derived" / record["resource_id"] / record["sha256"] / "document.json"
        document = CanonicalDocument.model_validate_json(path.read_text(encoding="utf-8"))
        if document.source_hash != record["sha256"]:
            raise ValueError(f"canonical source changed: {record['resource_id']}")
        for chunk in chunker.chunk(document):
            if chunk.chunk_level is ChunkLevel.PARENT:
                parents[chunk.chunk_id] = chunk.text
            else:
                saved = chunks.get(chunk.chunk_id)
                if saved is None or saved["text"] != chunk.text or saved["parent_chunk_id"] != chunk.parent_chunk_id:
                    raise ValueError(f"candidate child differs from index snapshot: {chunk.chunk_id}")
                seen_children.add(chunk.chunk_id)
    if seen_children != set(chunks):
        raise ValueError("candidate child coverage differs from canonical documents")
    return parents


def _strata(rows: list[dict]) -> list[dict]:
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        for axis, value in (("language", row["language"]), ("topic", row["topic"]),
                            ("evidence_groups", row["evidence_group_count"])):
            buckets[(row["method"], axis, value)].append(row)
    output = []
    for (method, axis, value), items in sorted(buckets.items(), key=lambda kv: str(kv[0])):
        output.append({
            "method": method, "axis": axis, "value": value, "intent_count": len(items),
            "complete_evidence_at_5": sum(item["metrics"]["complete_evidence_at_5"] for item in items) / len(items),
            "complete_locator_at_5": sum(item["metrics"]["complete_locator_at_5"] for item in items) / len(items),
            "mrr": sum(item["metrics"]["mrr"] for item in items) / len(items),
            "ndcg_at_5": sum(item["metrics"]["ndcg_at_5"] for item in items) / len(items),
            "mean_retrieval_ms": sum(item["retrieval_only_query_ms"] for item in items) / len(items),
            "mean_parent_context_tokens": sum(item["selected_parent_context_tokens"] for item in items) / len(items),
        })
    return output


async def run(output_dir: Path, *, index_dir: Path = INDEX) -> dict:
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite research output: {output_dir}")
    report_path = index_dir / "build_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    verify_report(report, manifest_sha=sha256(MANIFEST))
    if report["policy_config_sha256"] != sha256(POLICY_CONFIG):
        raise ValueError("V2 chunk policy changed")
    question_path = GOLD / "questions_full_candidate_v5.jsonl"
    evidence_path = GOLD / "evidence_planned_candidate_v5.jsonl"
    gold_manifest_path = GOLD / "full_candidate_manifest_v5.json"
    gold_manifest = json.loads(gold_manifest_path.read_text(encoding="utf-8"))
    prior = json.loads(V1_SUMMARY.read_text(encoding="utf-8"))
    for path in (question_path, evidence_path):
        if sha256(path) != gold_manifest["output_sha256"][path.name]:
            raise ValueError(f"candidate Gold input changed: {path.name}")
    if (prior["questions_sha256"] != sha256(question_path) or prior["evidence_sha256"] != sha256(evidence_path)
            or prior["k"] != 5 or prior["recall_limit"] != 40 or prior["rrf_k"] != 60):
        raise ValueError("V1 development comparison protocol changed")
    catalog = Catalog(ROOT / "memPed/knowledge/knowledge.sqlite3")
    if catalog.official_fingerprint(policy_version="parent-child-v1") != report["v1_catalog_fingerprint"]:
        raise ValueError("active corpus differs from V1 control")
    config = yaml.safe_load(POLICY_CONFIG.read_text(encoding="utf-8"))
    counter = HuggingFaceTokenCounter.from_local_path(
        ROOT / config["tokenizer"]["local_path"], expected_sha256=config["tokenizer"]["sha256"])
    if counter.fingerprint != report["tokenizer_fingerprint"]:
        raise ValueError("V2 tokenizer fingerprint mismatch")
    child_path = index_dir / "child_chunks.jsonl"
    if sha256(child_path) != report["output_sha256"][child_path.name]:
        raise ValueError("candidate child snapshot changed")
    chunks = {row["chunk_id"]: row for row in read_jsonl(child_path)}
    if len(chunks) != report["child_chunk_count"]:
        raise ValueError("candidate child count mismatch")
    parents = _parent_contexts(counter, chunks)
    fts_path = index_dir / "fts.sqlite3"
    if sha256(fts_path) != report["output_sha256"]["fts.sqlite3"]:
        raise ValueError("candidate FTS content hash mismatch")
    fts = FTSIndex(fts_path)
    vector = ChromaVectorIndex(index_dir / "chroma", BGEM3Gateway(MODEL_DIR))
    if (fts.source_fingerprint() != report["catalog_or_chunk_fingerprint"]
            or fts.policy_version() != "parent-child-v2"
            or fts.tokenizer_fingerprint() != counter.fingerprint
            or fts.lexical_analyzer_fingerprint() != report["lexical_analyzer_fingerprint"]
            or vector.catalog_fingerprint != report["catalog_or_chunk_fingerprint"]
            or vector.policy_version != "parent-child-v2"
            or vector.tokenizer_fingerprint != counter.fingerprint
            or vector.embedding_fingerprint != report["embedding_fingerprint"]):
        raise ValueError("candidate index fingerprints differ")
    if vector._collection().count() != report["chroma_entry_count"] or chroma_content_sha256(vector._collection()) != report["chroma_content_sha256"]:
        raise ValueError("candidate Chroma content hash mismatch")
    if sha256(MODEL_DIR / "pytorch_model.bin") != report["model_weights_sha256"]:
        raise ValueError("BGE-M3 model weights changed")
    questions, evidence = load_dev_scope()
    intent_ids = {q["intent_id"] for q in questions}
    if len(questions) != 40 or len(intent_ids) != 20 or set(evidence) != intent_ids:
        raise ValueError("development-only scope mismatch")
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA required for configured BGE-M3 evaluation")
    warmup_start = time.perf_counter()
    await vector.embedding_gateway.embed(["pedestrian flow"])
    warmup_ms = (time.perf_counter() - warmup_start) * 1000
    rows = []
    for question in questions:
        t0 = time.perf_counter()
        sparse = fts.search(question["query"], limit=40)
        sparse_ms = (time.perf_counter() - t0) * 1000
        t0 = time.perf_counter()
        dense = await vector.search(question["query"], limit=40)
        dense_ms = (time.perf_counter() - t0) * 1000
        sparse_ids = [hit.chunk_id for hit in sparse]
        dense_ids = [hit.chunk_id for hit in dense]
        t0 = time.perf_counter()
        fused_ids = fuse_rrf(sparse_ids, dense_ids, rrf_k=60)
        fusion_ms = (time.perf_counter() - t0) * 1000
        for method, ids, latency_ms in (
            ("bm25", sparse_ids, sparse_ms),
            ("bge_m3", dense_ids, dense_ms),
            ("rrf", fused_ids, sparse_ms + dense_ms + fusion_ms),
        ):
            if any(chunk_id not in chunks for chunk_id in ids):
                raise ValueError(f"retrieved child absent from candidate snapshot: {question['question_id']}")
            ranking = [chunks[chunk_id] for chunk_id in ids]
            selected = _distinct_top(ranking)
            metrics = score_answerable(evidence[question["intent_id"]], ranking, k=5)
            rows.append({
                "question_id": question["question_id"], "intent_id": question["intent_id"],
                "language": question["language"], "topic": question.get("primary_topic"),
                "evidence_group_count": len(evidence[question["intent_id"]]["evidence_groups"]),
                "method": method, "metrics": metrics,
                "selected_resources": [row["resource_id"] for row in selected],
                "chunk_ranking": [{"rank": rank, "chunk_id": row["chunk_id"],
                    "resource_id": row["resource_id"], "version_id": row["version_id"],
                    "page_start": row["page_start"], "page_end": row["page_end"],
                    "element_ids": row["element_ids"]} for rank, row in enumerate(ranking, 1)],
                "retrieval_only_query_ms": latency_ms,
                "selected_parent_context_tokens": sum(counter.count(parents[row["parent_chunk_id"]]) for row in selected),
                "context_tokenizer_fingerprint": counter.fingerprint,
            })
        print(f"evaluated {question['question_id']}", flush=True)
    output_dir.mkdir(parents=True)
    with (output_dir / "per_query.jsonl").open("x", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (output_dir / "strata.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("method", "axis", "value", "intent_count",
            "complete_evidence_at_5", "complete_locator_at_5", "mrr", "ndcg_at_5",
            "mean_retrieval_ms", "mean_parent_context_tokens"))
        writer.writeheader()
        writer.writerows(_strata(rows))
    with (output_dir / "failure_cases.md").open("x", encoding="utf-8") as stream:
        stream.write("# V2 候选检索失败案例\n\n*Gold v5 开发集逐题结果 · status: current；候选标注未获人工 Gold 核验*\n\n")
        stream.write("| 题目 | 方法 | 完整证据@5 | 精确定位@5 | 首五资源 |\n| --- | --- | ---: | ---: | --- |\n")
        for row in rows:
            if row["metrics"]["complete_evidence_at_5"] == 0 or row["metrics"]["complete_locator_at_5"] == 0:
                stream.write(f"| {row['question_id']} | {row['method']} | {row['metrics']['complete_evidence_at_5']:.0f} | {row['metrics']['complete_locator_at_5']:.0f} | {', '.join(row['selected_resources'])} |\n")
    summary = {
        "status": "v2_candidate_dev_evaluated_not_frozen", "human_verified": False,
        "test_split_evaluated": False, "refusal_evaluated": False,
        "independent_intents": 20, "query_variants": 40, "k": 5, "recall_limit": 40, "rrf_k": 60,
        "methods": ["bm25", "bge_m3", "rrf"], "cross_encoder": "not_run_no_pinned_local_model",
        "model_warmup_ms": warmup_ms,
        "latency_scope": "warm model; each retrieval_only_query_ms excludes model load, parent hydration and token counting; RRF includes both recalls plus fusion",
        "context_scope": "sum BGE-M3 tokenizer counts of selected parent contexts for first five distinct resources",
        "metrics_by_method_language": _aggregate(rows),
        "mean_retrieval_ms": {key: sum(row["retrieval_only_query_ms"] for row in rows if f"{row['method']}/{row['language']}" == key) / 20
                              for key in sorted({f"{row['method']}/{row['language']}" for row in rows})},
        "mean_parent_context_tokens": {key: sum(row["selected_parent_context_tokens"] for row in rows if f"{row['method']}/{row['language']}" == key) / 20
                                       for key in sorted({f"{row['method']}/{row['language']}" for row in rows})},
        "v1_control_metrics": prior["metrics_by_method_language"],
        "source_sha256": {p.name: sha256(p) for p in (question_path, evidence_path, gold_manifest_path,
            MANIFEST, POLICY_CONFIG, report_path, child_path, V1_SUMMARY)},
        "index_fingerprint": report["catalog_or_chunk_fingerprint"],
        "tokenizer_fingerprint": counter.fingerprint,
        "lexical_analyzer_fingerprint": report["lexical_analyzer_fingerprint"],
        "embedding_fingerprint": report["embedding_fingerprint"],
        "model_revision": report["model_revision"],
        "model_weights_sha256": report["model_weights_sha256"],
        "random_seed": None,
        "code_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "runner_sha256": sha256(Path(__file__)),
        "output_sha256": {name: sha256(output_dir / name) for name in ("per_query.jsonl", "strata.csv", "failure_cases.md")},
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--index-dir", type=Path, default=INDEX)
    args = parser.parse_args()
    result = asyncio.run(run(args.output_dir, index_dir=args.index_dir))
    print(json.dumps({key: result[key] for key in ("status", "metrics_by_method_language", "mean_retrieval_ms", "mean_parent_context_tokens")}, ensure_ascii=False, indent=2))
