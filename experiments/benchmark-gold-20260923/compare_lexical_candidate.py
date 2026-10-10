"""Controlled development comparison of V1 baseline vs candidate lexical FTS.

The pinned V1 Dense ranking is reused; no embedding model is rerun here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from collections import defaultdict
from pathlib import Path

from ped_knowledge.evaluation.gold_v2 import score_answerable
from ped_knowledge.indexing import FTSIndex
from ped_knowledge.storage import Catalog
from ped_knowledge.tokenization import HuggingFaceTokenCounter, JiebaLexicalAnalyzer

from dev_scope import load_dev_scope

ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "memPed/knowledge/gold/2026-09-23-rebuild"
V1 = ROOT / "outputs/gold-v5-dev-exploratory-20260924-01"
V1_VERIFICATION = ROOT / "paper/evaluation-reports/stage1-analysis-20260926-02/verification.json"
INDEX = ROOT / "outputs/knowledge-index-104-v1-lexical-candidate-20260926-01"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def guard_output(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite research output: {path}")


def fuse_rrf(sparse_ids: list[str], dense_ids: list[str], *, rrf_k: int) -> list[str]:
    scores: dict[str, float] = defaultdict(float)
    for hits in (sparse_ids, dense_ids):
        for rank, chunk_id in enumerate(hits, 1):
            scores[chunk_id] += 1 / (rrf_k + rank)
    return [chunk_id for chunk_id, _ in sorted(scores.items(), key=lambda item: (-item[1], item[0]))]


def _ranking(ids: list[str], chunks: dict[str, dict]) -> list[dict]:
    if any(chunk_id not in chunks for chunk_id in ids):
        raise ValueError("retrieved chunk absent from frozen V1 Catalog")
    return [chunks[chunk_id] for chunk_id in ids]


def _distinct_top(rows: list[dict], *, k: int = 5) -> list[dict]:
    seen = set()
    selected = []
    for row in rows:
        if row["resource_id"] not in seen:
            seen.add(row["resource_id"])
            selected.append(row)
            if len(selected) == k:
                break
    return selected


def _aggregate(rows: list[dict]) -> dict:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        buckets[f"{row['method']}/{row['language']}"].append(row)
    return {
        key: {metric: sum(row["metrics"][metric] for row in items) / len(items)
              for metric in items[0]["metrics"]}
        for key, items in sorted(buckets.items())
    }


def run(output_dir: Path) -> dict:
    guard_output(output_dir)
    question_path = GOLD / "questions_full_candidate_v5.jsonl"
    evidence_path = GOLD / "evidence_planned_candidate_v5.jsonl"
    annotation_path = GOLD / "answer_annotations_dev_v1.jsonl"
    prior_summary_path = V1 / "summary.json"
    prior_ranking_path = V1 / "per_query.jsonl"
    verified = json.loads(V1_VERIFICATION.read_text(encoding="utf-8"))
    if (sha256(prior_summary_path) != verified["input_sha256"]["summary.json"]
            or sha256(prior_ranking_path) != verified["input_sha256"]["per_query.jsonl"]):
        raise ValueError("saved V1 Dense ranking or summary differs from independent Stage 1 verification")
    candidate_report_path = INDEX / "build_report.json"
    candidate_report = json.loads(candidate_report_path.read_text(encoding="utf-8"))
    prior = json.loads(prior_summary_path.read_text(encoding="utf-8"))
    if candidate_report["mode"] != "lexical-v1" or candidate_report["policy_version"] != "parent-child-v1":
        raise ValueError("candidate index has wrong policy")
    if (sha256(question_path) != prior["questions_sha256"] or sha256(evidence_path) != prior["evidence_sha256"]
            or candidate_report["v1_catalog_fingerprint"] != prior["catalog_fingerprint"]):
        raise ValueError("candidate comparison input changed")
    catalog = Catalog(ROOT / "memPed/knowledge/knowledge.sqlite3")
    if catalog.official_fingerprint(policy_version="parent-child-v1") != candidate_report["catalog_or_chunk_fingerprint"]:
        raise ValueError("V1 chunk corpus changed")
    analyzer = JiebaLexicalAnalyzer(
        domain_terms_path=ROOT / "Knowledge-Base/config/retrieval/pedestrian_terms.txt",
        stopwords_path=ROOT / "Knowledge-Base/config/retrieval/stopwords_zh_en.txt",
    )
    fts = FTSIndex(INDEX / "fts.sqlite3", analyzer=analyzer)
    if sha256(INDEX / "fts.sqlite3") != candidate_report["output_sha256"]["fts.sqlite3"]:
        raise ValueError("candidate FTS content hash mismatch")
    if (fts.source_fingerprint() != candidate_report["catalog_or_chunk_fingerprint"]
            or fts.lexical_analyzer_fingerprint() != candidate_report["lexical_analyzer_fingerprint"]
            or fts.policy_version() != "parent-child-v1"
            or fts.tokenizer_fingerprint() != candidate_report["tokenizer_fingerprint"]):
        raise ValueError("candidate FTS fingerprint mismatch")
    counter = HuggingFaceTokenCounter.from_local_path(
        ROOT / "memPed/knowledge/models/bge-m3/tokenizer.json",
        expected_sha256="21106b6d7dab2952c1d496fb21d5dc9db75c28ed361a05f5020bbba27810dd08",
    )
    chunks = {c["chunk_id"]: c for c in catalog.list_official_chunks(policy_version="parent-child-v1")}
    questions, evidence = load_dev_scope()
    intent_ids = {q["intent_id"] for q in questions}
    saved_dense = {(r["question_id"]): r for r in read_jsonl(prior_ranking_path) if r["method"] == "bge_m3"}
    if len(questions) != 40 or len(intent_ids) != 20 or len(saved_dense) != 40 or set(evidence) != intent_ids:
        raise ValueError("development scope mismatch")
    rows = []
    for question in questions:
        question_id = question["question_id"]
        t0 = time.perf_counter()
        sparse_hits = fts.search(question["query"], limit=40)
        sparse_ms = (time.perf_counter() - t0) * 1000
        sparse_ids = [hit.chunk_id for hit in sparse_hits]
        dense_ids = [hit["chunk_id"] for hit in saved_dense[question_id]["chunk_ranking"]]
        t0 = time.perf_counter()
        fused_ids = fuse_rrf(sparse_ids, dense_ids, rrf_k=60)
        fusion_ms = (time.perf_counter() - t0) * 1000
        for method, ids, latency_ms in (
            ("candidate_bm25", sparse_ids, sparse_ms),
            ("saved_v1_dense", dense_ids, None),
            ("candidate_rrf", fused_ids, sparse_ms + fusion_ms),
        ):
            ranking = _ranking(ids, chunks)
            selected = _distinct_top(ranking)
            metrics = score_answerable(evidence[question["intent_id"]], ranking, k=5)
            rows.append({
                "question_id": question_id, "intent_id": question["intent_id"],
                "language": question["language"], "topic": question.get("primary_topic"),
                "evidence_group_count": len(evidence[question["intent_id"]]["evidence_groups"]),
                "method": method, "metrics": metrics,
                "selected_resources": [row["resource_id"] for row in selected],
                "chunk_ranking": [{"chunk_id": row["chunk_id"], "resource_id": row["resource_id"],
                                   "page_start": row["page_start"], "page_end": row["page_end"]} for row in ranking],
                "retrieval_only_query_ms": latency_ms,
                "selected_parent_context_tokens": sum(counter.count(catalog.context_for_chunk(row["chunk_id"])) for row in selected),
                "context_tokenizer_fingerprint": counter.fingerprint,
            })
    output_dir.mkdir(parents=True)
    per_query_path = output_dir / "per_query.jsonl"
    with per_query_path.open("x", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    summary = {
        "status": "candidate_dev_comparison_not_human_gold", "test_split_evaluated": False,
        "human_verified": False, "independent_intents": 20, "query_variants": 40,
        "k": 5, "recall_limit": 40, "rrf_k": 60,
        "dense_execution": "saved_V1_ranking_reused_no_model_rerun",
        "latency_scope": "candidate_FTS_search_and_RRF_combination_only; saved dense latency unavailable; model load and context hydration excluded",
        "context_scope": "sum of parent text token counts for first five distinct resources, one selected child per resource",
        "metrics_by_method_language": _aggregate(rows),
        "mean_retrieval_ms": {key: sum(row["retrieval_only_query_ms"] for row in rows if f"{row['method']}/{row['language']}" == key) / 20
                              for key in sorted({f"{row['method']}/{row['language']}" for row in rows})
                              if not key.startswith("saved_v1_dense/")},
        "mean_parent_context_tokens": {key: sum(row["selected_parent_context_tokens"] for row in rows if f"{row['method']}/{row['language']}" == key) / 20
                                       for key in sorted({f"{row['method']}/{row['language']}" for row in rows})},
        "source_sha256": {p.name: sha256(p) for p in (question_path, evidence_path, annotation_path,
            prior_summary_path, prior_ranking_path, candidate_report_path, V1_VERIFICATION)},
        "candidate_index_fingerprint": candidate_report["catalog_or_chunk_fingerprint"],
        "candidate_lexical_analyzer_fingerprint": candidate_report["lexical_analyzer_fingerprint"],
        "model_revision": candidate_report["model_revision"],
        "model_weights_sha256": candidate_report["model_weights_sha256"],
        "random_seed": None,
        "code_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "runner_sha256": sha256(Path(__file__)), "per_query_sha256": sha256(per_query_path),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), ensure_ascii=False, indent=2))
