"""Diagnose saved V1 development rankings; only BM25 is re-queried read-only.

No embedding model, sealed test split, or candidate index is used here.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

from ped_knowledge.indexing import FTSIndex
from ped_knowledge.storage import Catalog

from dev_scope import load_dev_scope

ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "memPed/knowledge/gold/2026-09-23-rebuild"
INDEX = ROOT / "outputs/knowledge-index-104-v1-20260924-01"
RUN = ROOT / "outputs/gold-v5-dev-exploratory-20260924-01"
VERIFICATION = ROOT / "paper/evaluation-reports/stage1-analysis-20260926-02/verification.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def distinct(ranking: list[dict]) -> list[dict]:
    seen = set()
    rows = []
    for hit in ranking:
        if hit["resource_id"] not in seen:
            rows.append(hit)
            seen.add(hit["resource_id"])
    return rows


def first_complete_rank(ranking: list[dict], groups: list[dict[str, set[str]]]) -> int | None:
    remaining = [set(next(iter(group.values()))) for group in groups]
    for rank, hit in enumerate(distinct(ranking), 1):
        remaining = [group for group in remaining if hit["resource_id"] not in group]
        if not remaining:
            return rank
    return None


def classify_sparse_miss(ranking: list[dict], groups: list[dict[str, set[str]]], *, k: int) -> str:
    if not ranking:
        return "no_fts_candidates"
    complete = first_complete_rank(ranking, groups)
    if complete is not None and complete <= k:
        return "complete_at_k"
    if complete is not None and complete > k:
        return "relevant_below_k"
    relevant = set().union(*(next(iter(group.values())) for group in groups))
    if any(hit["resource_id"] in relevant for hit in ranking[:k]):
        return "partial_groups"
    return "candidate_wrong_resource"


def summarize(rows: list[dict]) -> list[dict]:
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        for axis, value in (("language", row["language"]), ("topic", row["topic"]),
                            ("evidence_groups", row["evidence_group_count"])):
            buckets[(row["method"], axis, value)].append(row)
    result = []
    for (method, axis, value), items in sorted(buckets.items(), key=lambda kv: str(kv[0])):
        result.append({
            "method": method, "axis": axis, "value": value, "intent_count": len(items),
            "complete_evidence_at_5": sum(x["complete_evidence_at_5"] for x in items) / len(items),
            "complete_locator_at_5": sum(x["complete_locator_at_5"] for x in items) / len(items),
            "mrr": sum(x["mrr"] for x in items) / len(items),
            "ndcg_at_5": sum(x["ndcg_at_5"] for x in items) / len(items),
        })
    return result


def write_outputs(output_dir: Path, rows: list[dict], summary: dict) -> None:
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite research output: {output_dir}")
    output_dir.mkdir(parents=True)
    with (output_dir / "per_query.jsonl").open("x", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (output_dir / "strata.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("method", "axis", "value", "intent_count",
            "complete_evidence_at_5", "complete_locator_at_5", "mrr", "ndcg_at_5"))
        writer.writeheader()
        writer.writerows(summarize(rows))
    failures = [row for row in rows if row["complete_evidence_at_5"] == 0 or (row.get("rank_shift_vs_dense") or 0) > 0]
    with (output_dir / "failure_cases.md").open("x", encoding="utf-8") as stream:
        stream.write("# V1 开发集失败案例\n\n*保存排名与只读 FTS 的逐题诊断 · status: current；候选标签未人工核验*\n\n")
        stream.write("| 问题 | 方法 | 完整证据@5 | 首次完整资源排名 | 分类 |\n| --- | --- | ---: | ---: | --- |\n")
        for row in failures:
            stream.write(f"| {row['question_id']} | {row['method']} | {row['complete_evidence_at_5']:.0f} | {row['first_complete_resource_rank'] or '—'} | {row.get('failure_mode', 'RRF rank below Dense')} |\n")
    summary["output_sha256"] = {name: sha256(output_dir / name) for name in (
        "per_query.jsonl", "strata.csv", "failure_cases.md")}
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(output_dir: Path) -> dict:
    if output_dir.exists():
        raise FileExistsError(output_dir)
    question_path = GOLD / "questions_full_candidate_v5.jsonl"
    evidence_path = GOLD / "evidence_planned_candidate_v5.jsonl"
    manifest_path = GOLD / "full_candidate_manifest_v5.json"
    per_query_path = RUN / "per_query.jsonl"
    prior_summary_path = RUN / "summary.json"
    verified = json.loads(VERIFICATION.read_text(encoding="utf-8"))
    if (sha256(prior_summary_path) != verified["input_sha256"]["summary.json"]
            or sha256(per_query_path) != verified["input_sha256"]["per_query.jsonl"]):
        raise ValueError("saved V1 run differs from independent Stage 1 verification")
    index_report_path = INDEX / "build_report.json"
    prior = json.loads(prior_summary_path.read_text(encoding="utf-8"))
    index_report = json.loads(index_report_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (sha256(question_path) != prior["questions_sha256"] or sha256(evidence_path) != prior["evidence_sha256"]
            or sha256(index_report_path) != prior["index_report_sha256"]):
        raise ValueError("saved development run inputs changed")
    if any(sha256(path) != manifest["output_sha256"][path.name] for path in (question_path, evidence_path)):
        raise ValueError("candidate manifest inputs changed")
    if prior["catalog_fingerprint"] != index_report["catalog_fingerprint"] or prior["k"] != 5 or prior["recall_limit"] != 40:
        raise ValueError("unexpected V1 evaluation protocol")
    fts = FTSIndex(INDEX / "fts.sqlite3")
    catalog = Catalog(ROOT / "memPed/knowledge/knowledge.sqlite3")
    fingerprint = catalog.official_fingerprint(policy_version="parent-child-v1")
    if fingerprint != index_report["catalog_fingerprint"] or fts.source_fingerprint() != fingerprint:
        raise ValueError("catalog or FTS differs from saved V1 index")
    if fts.lexical_analyzer_fingerprint() != index_report["lexical_analyzer_fingerprint"]:
        raise ValueError("lexical analyzer fingerprint mismatch")
    chunks = {row["chunk_id"]: row for row in catalog.list_official_chunks(policy_version="parent-child-v1")}
    dev_questions, evidence = load_dev_scope()
    questions = {q["question_id"]: q for q in dev_questions}
    intent_ids = {q["intent_id"] for q in questions.values()}
    stored = read_jsonl(per_query_path)
    if len(questions) != 40 or len(intent_ids) != 20 or len(stored) != 120:
        raise ValueError("unexpected development run size")
    saved = {(r["question_id"], r["method"]): r for r in stored}
    if len(saved) != 120:
        raise ValueError("duplicate saved query/method result")
    source_languages = Counter(s["language"] for s in read_jsonl(GOLD / "corpus_candidates.jsonl"))
    rows = []
    sparse_modes = Counter()
    for question_id, question in sorted(questions.items()):
        groups = [{g["group_id"]: {a["resource_id"] for a in g["alternatives"]}}
                  for g in evidence[question["intent_id"]]["evidence_groups"]]
        query = question["query"]
        hits = fts.search(query, limit=40)
        actual_ids = [hit.chunk_id for hit in hits]
        saved_ids = [hit["chunk_id"] for hit in saved[(question_id, "bm25")]["chunk_ranking"]]
        if actual_ids != saved_ids:
            raise ValueError(f"live FTS ranking differs from saved result: {question_id}")
        sparse_chunks = [chunks[hit.chunk_id] for hit in hits]
        mode = classify_sparse_miss(distinct(sparse_chunks), groups, k=5)
        sparse_modes[(question["language"], mode)] += 1
        dense_complete = first_complete_rank(saved[(question_id, "bge_m3")]["ranking"], groups)
        for method in ("bm25", "bge_m3", "rrf"):
            item = saved[(question_id, method)]
            ranking = item["ranking"]
            metrics = item["metrics"]
            result = {
                "question_id": question_id, "intent_id": question["intent_id"],
                "language": question["language"], "topic": question.get("primary_topic"),
                "evidence_group_count": len(groups), "method": method,
                "resource_ranking_top_5": [x["resource_id"] for x in ranking],
                "first_complete_resource_rank": first_complete_rank(ranking, groups),
                "complete_evidence_at_5": metrics["complete_evidence_at_5"],
                "complete_locator_at_5": metrics["complete_locator_at_5"],
                "mrr": metrics["mrr"], "ndcg_at_5": metrics["ndcg_at_5"],
            }
            if method == "bm25":
                result.update({
                    "query_tokens": fts.analyzer.analyze(query), "fts_chunk_count_top_40": len(hits),
                    "fts_top_5_scores": [hit.score for hit in hits[:5]],
                    "fts_top_5_resources": [chunks[hit.chunk_id]["resource_id"] for hit in hits[:5]],
                    "failure_mode": mode,
                })
            if method == "rrf":
                result["rank_shift_vs_dense"] = None if dense_complete is None or result["first_complete_resource_rank"] is None else result["first_complete_resource_rank"] - dense_complete
            rows.append(result)
    summary = {
        "status": "v1_dev_diagnosis_candidate_only", "human_verified": False,
        "test_split_evaluated": False, "refusal_evaluated": False,
        "independent_intents": 20, "query_variants": 40, "methods": ["bm25", "bge_m3", "rrf"],
        "method_execution": {"bm25": "read_only_requery_identical_to_saved_chunks", "bge_m3": "saved_ranking_only", "rrf": "saved_ranking_only"},
        "k": 5, "recall_limit": 40, "rrf_k": prior["rrf_k"],
        "corpus_language_counts": dict(source_languages),
        "bm25_failure_modes": {f"{lang}/{mode}": count for (lang, mode), count in sorted(sparse_modes.items())},
        "rrf_vs_dense": {lang: {
            "worse_rank_count": sum(r["rank_shift_vs_dense"] > 0 for r in rows if r["method"] == "rrf" and r["language"] == lang and r["rank_shift_vs_dense"] is not None),
            "better_rank_count": sum(r["rank_shift_vs_dense"] < 0 for r in rows if r["method"] == "rrf" and r["language"] == lang and r["rank_shift_vs_dense"] is not None),
        } for lang in ("en", "zh")},
        "latency_ms": None, "context_tokens": None,
        "latency_context_note": "original run did not record per-query timing or context text/token counts; no retrospective estimate",
        "source_sha256": {p.name: sha256(p) for p in (question_path, evidence_path, manifest_path, per_query_path, prior_summary_path, index_report_path)},
        "index_fingerprint": fingerprint, "chunk_policy": index_report["policy_version"],
        "tokenizer_fingerprint": index_report["tokenizer_fingerprint"],
        "lexical_analyzer_fingerprint": index_report["lexical_analyzer_fingerprint"],
        "embedding_fingerprint": index_report["embedding_fingerprint"],
        "model_revision": index_report["model_revision"], "model_weights_sha256": index_report["model_weights_sha256"],
        "random_seed": None,
        "code_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "runner_sha256": sha256(Path(__file__)),
    }
    write_outputs(output_dir, rows, summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), ensure_ascii=False, indent=2))
