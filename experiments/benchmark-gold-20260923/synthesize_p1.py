"""Create a read-only intent-paired comparison of existing P1 development runs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = {
    "v1": ROOT / "outputs/gold-v5-dev-exploratory-20260924-01",
    "lexical_candidate": ROOT / "outputs/gold-v5-dev-p1-lexical-candidate-20260926-02",
    "v2_candidate": ROOT / "outputs/gold-v5-dev-p1-v2-candidate-20260926-02",
}
V1_VERIFICATION = ROOT / "paper/evaluation-reports/stage1-analysis-20260926-02/verification.json"
METHODS = {
    "v1": {"bm25": "bm25", "dense": "bge_m3", "rrf": "rrf"},
    "lexical_candidate": {"bm25": "candidate_bm25", "dense": "saved_v1_dense", "rrf": "candidate_rrf"},
    "v2_candidate": {"bm25": "bm25", "dense": "bge_m3", "rrf": "rrf"},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guard_output(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite research output: {path}")


def index_rows(rows: list[dict]) -> dict[tuple[str, str], dict]:
    indexed = {}
    for row in rows:
        key = (row["question_id"], row["method"])
        if key in indexed:
            raise ValueError(f"duplicate query/method result: {key}")
        indexed[key] = row
    return indexed


def verify_aggregate(rows: list[dict], metrics_by_method_language: dict) -> None:
    buckets: dict[str, list[dict]] = {}
    for row in rows:
        buckets.setdefault(f"{row['method']}/{row['language']}", []).append(row["metrics"])
    if set(buckets) != set(metrics_by_method_language):
        raise ValueError("summary method/language buckets differ from per-query rows")
    for key, metrics in metrics_by_method_language.items():
        items = buckets[key]
        if set(metrics) != set(items[0]):
            raise ValueError(f"summary metric names differ: {key}")
        for name, reported in metrics.items():
            actual = sum(item[name] for item in items) / len(items)
            if not math.isclose(actual, reported, abs_tol=1e-12, rel_tol=1e-12):
                raise ValueError(f"summary metric differs from per-query rows: {key}/{name}")


def run(output_dir: Path, *, runs: dict[str, Path] = RUNS) -> dict:
    guard_output(output_dir)
    indexed = {}
    summaries = {}
    hashes = {}
    verification = json.loads(V1_VERIFICATION.read_text(encoding="utf-8"))
    for config, directory in runs.items():
        per_query_path = directory / "per_query.jsonl"
        summary_path = directory / "summary.json"
        hashes[f"{config}/per_query.jsonl"] = sha256(per_query_path)
        hashes[f"{config}/summary.json"] = sha256(summary_path)
        rows = [json.loads(line) for line in per_query_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        indexed[config] = index_rows(rows)
        summaries[config] = json.loads(summary_path.read_text(encoding="utf-8"))
        if config == "v1":
            if (hashes[f"{config}/per_query.jsonl"] != verification["input_sha256"]["per_query.jsonl"]
                    or hashes[f"{config}/summary.json"] != verification["input_sha256"]["summary.json"]):
                raise ValueError("V1 run differs from independent Stage 1 verification")
        elif config == "lexical_candidate":
            if hashes[f"{config}/per_query.jsonl"] != summaries[config]["per_query_sha256"]:
                raise ValueError("lexical candidate per-query hash differs from summary")
        elif hashes[f"{config}/per_query.jsonl"] != summaries[config]["output_sha256"]["per_query.jsonl"]:
            raise ValueError("V2 candidate per-query hash differs from summary")
        verify_aggregate(rows, summaries[config]["metrics_by_method_language"])
        if len(indexed[config]) != 120:
            raise ValueError(f"unexpected development result count: {config}")
    if len({summaries[c]["source_sha256"]["questions_full_candidate_v5.jsonl"] for c in ("lexical_candidate", "v2_candidate")}) != 1:
        raise ValueError("candidate question hashes differ")
    v1 = summaries["v1"]
    if (v1["questions_sha256"] != summaries["v2_candidate"]["source_sha256"]["questions_full_candidate_v5.jsonl"]
            or v1["evidence_sha256"] != summaries["v2_candidate"]["source_sha256"]["evidence_planned_candidate_v5.jsonl"]):
        raise ValueError("Gold v5 inputs differ across comparisons")
    if any(summary["k"] != 5 or summary["recall_limit"] != 40 or summary["rrf_k"] != 60 for summary in summaries.values()):
        raise ValueError("top-k or candidate count differs across comparisons")
    question_ids = sorted({question_id for question_id, _ in indexed["v1"]})
    if len(question_ids) != 40 or any((question_id, method) not in indexed[config]
                                   for config in runs for question_id in question_ids
                                   for method in METHODS[config].values()):
        raise ValueError("missing development query/method result")
    intent_ids = sorted({indexed["v1"][(question_id, "bm25")]["intent_id"] for question_id in question_ids})
    if len(intent_ids) != 20:
        raise ValueError("development intent count differs")
    paired_rows = []
    for intent_id in intent_ids:
        by_language = {lang: f"{intent_id}-{lang}" for lang in ("en", "zh")}
        if any(question_id not in question_ids for question_id in by_language.values()):
            raise ValueError(f"unpaired development intent: {intent_id}")
        row = {"intent_id": intent_id,
               "topic": indexed["v1"][(by_language["en"], "bm25")]["topic"],
               "evidence_group_count": indexed["v2_candidate"][(by_language["en"], "bm25")]["evidence_group_count"]}
        for config in runs:
            for method, stored_name in METHODS[config].items():
                for lang, question_id in by_language.items():
                    metrics = indexed[config][(question_id, stored_name)]["metrics"]
                    prefix = f"{config}_{method}_{lang}"
                    row[f"{prefix}_complete_evidence_at_5"] = metrics["complete_evidence_at_5"]
                    row[f"{prefix}_complete_locator_at_5"] = metrics["complete_locator_at_5"]
                    row[f"{prefix}_mrr"] = metrics["mrr"]
                    row[f"{prefix}_ndcg_at_5"] = metrics["ndcg_at_5"]
        paired_rows.append(row)
    comparison = []
    for config, summary in summaries.items():
        for method, stored_name in METHODS[config].items():
            for lang in ("en", "zh"):
                key = f"{stored_name}/{lang}"
                metrics = summary["metrics_by_method_language"][key]
                comparison.append({
                    "configuration": config, "method": method, "language": lang,
                    "independent_intents": 20,
                    "complete_evidence_at_5": metrics["complete_evidence_at_5"],
                    "complete_locator_at_5": metrics["complete_locator_at_5"],
                    "mrr": metrics["mrr"], "ndcg_at_5": metrics["ndcg_at_5"],
                    "mean_retrieval_ms": summary.get("mean_retrieval_ms", {}).get(key),
                    "mean_parent_context_tokens": summary.get("mean_parent_context_tokens", {}).get(key),
                })
    output_dir.mkdir(parents=True)
    for filename, rows in (("paired_intents.csv", paired_rows), ("comparison.csv", comparison)):
        with (output_dir / filename).open("x", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    with (output_dir / "failure_cases.md").open("x", encoding="utf-8") as stream:
        stream.write("# P1 检索失败与回退案例\n\n*Gold v5 开发集候选标注对照 · status: current；未形成正式 Gold 或最佳配置*\n\n")
        stream.write("| 意图/语言 | V1 Dense | V2 Dense | V1 RRF | V2 RRF |\n| --- | ---: | ---: | ---: | ---: |\n")
        for row in paired_rows:
            for lang in ("en", "zh"):
                values = [row[f"{config}_{method}_{lang}_complete_evidence_at_5"]
                          for config, method in (("v1", "dense"), ("v2_candidate", "dense"),
                                                 ("v1", "rrf"), ("v2_candidate", "rrf"))]
                if any(value == 0 for value in values):
                    stream.write(f"| {row['intent_id']}/{lang} | " + " | ".join(f"{value:.0f}" for value in values) + " |\n")
        stream.write("\n中文 BM25 的 V1 与两项候选对照均未在 k=5 完整命中；逐题分词与 FTS 得分见 V1 诊断目录。\n")
    with (output_dir / "README.md").open("x", encoding="utf-8") as stream:
        stream.write("# P1 候选检索对照\n\n*104 篇语料、Gold v5 开发集的探索性合成 · status: current；未冻结 Best Static Retriever*\n\n")
        stream.write("`paired_intents.csv` 以 20 个 intent 为行保留中英指标；`comparison.csv` 为配置、方法、语言汇总；`failure_cases.md` 列出 V1/V2 的完整证据失败。输入哈希在 `summary.json`。\n\n")
        stream.write("V2 在中文 Dense/RRF 的完整证据@5 均由 V1 的 0.95 降至 0.85，新增 `rgq-005` 与 `rgq-022` 两题漏检；英文仍为 1.00。词法候选没有改变 BM25 或 RRF 的开发集汇总。V1 Dense 可作为下一轮人工核验后的静态检索候选，但现阶段不得宣布最佳或发布。\n\n")
        stream.write("V1 原始运行未记录延迟/上下文 token；词法候选复用保存的 Dense 排名；V2 的真实 BGE-M3 在 CUDA 上执行，延迟为模型预热后的检索时间。Cross-Encoder 没有固定的本地模型与权重清单，未运行。所有指标仍依赖未经人工验证的候选证据，100 个 sealed test intent 未参与。\n\n")
        stream.write("复现顺序：运行 `audit_dev_v5.py`、`diagnose_v1_dev.py`、`build_candidates.py` 的两个 mode、`compare_lexical_candidate.py`、`evaluate_v2_candidate.py`，每次指定新的 `--output-dir`；最后运行 `synthesize_p1.py --output-dir outputs/新的合成目录`。具体命令见实验 README。\n")
    summary = {
        "status": "p1_candidate_synthesis_not_frozen", "human_verified": False,
        "test_split_evaluated": False, "independent_intents": len(paired_rows),
        "source_sha256": hashes,
        "output_sha256": {name: sha256(output_dir / name) for name in ("paired_intents.csv", "comparison.csv", "failure_cases.md", "README.md")},
        "code_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "runner_sha256": sha256(Path(__file__)),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--lexical-run", type=Path, default=RUNS["lexical_candidate"])
    parser.add_argument("--v2-run", type=Path, default=RUNS["v2_candidate"])
    args = parser.parse_args()
    selected_runs = {"v1": RUNS["v1"], "lexical_candidate": args.lexical_run, "v2_candidate": args.v2_run}
    print(json.dumps(run(args.output_dir, runs=selected_runs), ensure_ascii=False, indent=2))
