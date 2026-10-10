"""P2 step 5: combine the saved parse review and retrieval run into paired tables.

Reads only saved outputs, the agent checklist, and the anchors; recomputes nothing
that needs a parser, model, or Adobe call.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from ped_knowledge.contracts import CanonicalDocument

from p2_common import ROOT, code_provenance, guard_output, load_anchors, read_jsonl, sha256

CHECKLIST = Path(__file__).with_name("parse_review_agent_dev.json")
FIELDS = ("reading_order", "missing_or_duplicated_text", "table_rows_columns", "page_numbers",
          "key_values_units", "gold_evidence_locatable")
HEADLINE = ("complete_evidence_at_5", "complete_locator_at_5", "mrr", "ndcg_at_5",
            "complete_text_locator_at_5", "complete_split_text_locator_at_5", "complete_parent_text_locator_at_5")


def structure_stats(path: Path) -> dict:
    document = CanonicalDocument.model_validate_json(path.read_text(encoding="utf-8"))
    types = Counter(item.element_type.value for item in document.elements if item.text)
    return {"heading_or_title_elements": types["heading"] + types["title"],
            "table_elements": types["table"], "text_elements": sum(types.values())}


def per_pdf(parse_dir: Path, checklist: dict) -> list[dict]:
    stats = {(row["resource_id"], row["parser"]): row for row in csv.DictReader(
        (parse_dir / "resource_stats.csv").open(encoding="utf-8"))}
    groups = defaultdict(list)
    for row in csv.DictReader((parse_dir / "group_locatability.csv").open(encoding="utf-8")):
        groups[(row["intent_id"], row["parser"])].append(row["all_required_in_one_gold_child"] == "True")
    anchors = load_anchors()
    rows = []
    for review in checklist["resources"]:
        resource = review["resource_id"]
        row = {"resource_id": resource, "layout": review["layout"]}
        for parser in ("pymupdf", "adobe"):
            item = stats.get((resource, parser))
            if item is None:
                row[f"{parser}_status"] = "not_run"
                continue
            document = parse_dir / "compare" / resource / f"{parser}-document.json"
            row.update({f"{parser}_{key}": value for key, value in structure_stats(document).items()})
            for key in ("child_chunks", "parent_chunks", "mean_child_page_span", "text_layer_shingle_recall",
                        "shingle_excess_over_text_layer"):
                row[f"{parser}_{key}"] = item[key]
            intents = [intent["intent_id"] for intent in anchors["intents"] if intent["resource_id"] == resource]
            located = [all(groups[(intent, parser)]) for intent in intents]
            row[f"{parser}_intents_all_groups_in_one_child"] = f"{sum(located)}/{len(located)}"
        for field in FIELDS:
            row[f"review_{field}"] = review[field]["verdict"]
        rows.append(row)
    return rows


def per_intent(retrieval_dir: Path) -> list[dict]:
    rows = read_jsonl(retrieval_dir / "per_query.jsonl")
    index = {(row["arm"], row["method"], row["question_id"]): row for row in rows}
    output = []
    for (arm, method, question), row in sorted(index.items()):
        if arm != "catalog_mixed":
            continue
        record = {"question_id": question, "intent_id": row["intent_id"], "language": row["language"], "method": method}
        for other in ("catalog_mixed", "pymupdf_all", "pymupdf_dev_targets"):
            item = index[(other, method, question)]
            short = {"catalog_mixed": "cat", "pymupdf_all": "pyall", "pymupdf_dev_targets": "pytgt"}[other]
            for metric in HEADLINE:
                value = item["metrics"].get(metric, item["text_metrics"].get(metric))
                record[f"{short}_{metric}"] = value
            record[f"{short}_gold_resource_rank"] = item["gold_resource_rank"]
            record[f"{short}_text_evidence_chunk_rank"] = item["text_metrics"]["first_text_evidence_chunk_rank"]
            record[f"{short}_top5"] = " ".join(item["selected_resources"])
        record["changed"] = any(record[f"cat_{metric}"] != record[f"{arm}_{metric}"]
                                for arm in ("pyall", "pytgt") for metric in HEADLINE) or any(
            record["cat_gold_resource_rank"] != record[f"{arm}_gold_resource_rank"] for arm in ("pyall", "pytgt"))
        output.append(record)
    return output


def failure_markdown(intents: list[dict]) -> str:
    lines = ["# P2 解析器敏感性：逐题变化与失败案例", "",
             "*Gold v5 开发集候选标注 · status: current；agent 复核标签，非人工 Gold；sealed test 未评测*", "",
             "列出任一指标或 Gold 资源排名在两个 PyMuPDF 臂与 `catalog_mixed` 之间不同的题目。"
             "证据@5 = complete_evidence_at_5；页定位 = complete_locator_at_5；文本定位 = 页码+全部锚点同在一个 child；分块文本定位 = 每个锚点各在某个 Gold 页 child。", "",
             "| 题目 | 方法 | Gold 资源名次 cat/pyall/pytgt | 证据@5 | 页定位@5 | 文本定位@5 | 分块文本定位@5 | 父块文本定位@5 |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for row in intents:
        if not row["changed"]:
            continue
        ranks = "/".join(str(row[f"{arm}_gold_resource_rank"] or "—") for arm in ("cat", "pyall", "pytgt"))
        cells = ["/".join(f"{row[f'{arm}_{metric}']:.0f}" for arm in ("cat", "pyall", "pytgt"))
                 for metric in ("complete_evidence_at_5", "complete_locator_at_5", "complete_text_locator_at_5",
                                "complete_split_text_locator_at_5", "complete_parent_text_locator_at_5")]
        lines.append(f"| {row['question_id']} | {row['method']} | {ranks} | " + " | ".join(cells) + " |")
    lines += ["", "三值依次为 catalog_mixed / pymupdf_all / pymupdf_dev_targets。“—”表示 Gold 资源不在前 40 个 child 所含资源中。", ""]
    return "\n".join(lines)


def run(parse_dir: Path, retrieval_dir: Path, output_dir: Path) -> dict:
    guard_output(output_dir)
    checklist = json.loads(CHECKLIST.read_text(encoding="utf-8"))
    if checklist["human_verified"] is not False:
        raise ValueError("checklist status changed")
    pdf_rows = per_pdf(parse_dir, checklist)
    intent_rows = per_intent(retrieval_dir)
    retrieval = json.loads((retrieval_dir / "summary.json").read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True)
    for name, rows in (("per_pdf_parse_diff.csv", pdf_rows), ("per_query_retrieval_diff.csv", intent_rows)):
        fields = list(dict.fromkeys(key for row in rows for key in row))
        with (output_dir / name).open("x", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    (output_dir / "failure_cases.md").write_text(failure_markdown(intent_rows), encoding="utf-8")
    headline = {key: {metric: value for metric, value in metrics.items() if metric in HEADLINE + ("text_evidence_mrr_top40", "mean_page_span_of_page_hit_chunks")}
                for key, metrics in retrieval["metrics_by_arm_method_language"].items()}
    summary = {
        "status": "p2_synthesis_dev_candidate_only", "human_verified": False, "test_split_evaluated": False,
        "changed_query_method_rows": sum(row["changed"] for row in intent_rows),
        "total_query_method_rows": len(intent_rows),
        "headline_metrics": headline,
        "reproduction_vs_saved_v1_dev_run": retrieval["reproduction_vs_saved_v1_dev_run"],
        "review_verdict_counts": {field: dict(Counter(row[f"review_{field}"] for row in pdf_rows)) for field in FIELDS},
        "source_sha256": {
            "parse/summary.json": sha256(parse_dir / "summary.json"),
            "retrieval/summary.json": sha256(retrieval_dir / "summary.json"),
            "retrieval/per_query.jsonl": sha256(retrieval_dir / "per_query.jsonl"),
            "parse_review_agent_dev.json": sha256(CHECKLIST),
        },
        "inputs": {"parse_dir": parse_dir.resolve().relative_to(ROOT).as_posix(),
                   "retrieval_dir": retrieval_dir.resolve().relative_to(ROOT).as_posix()},
        "code_provenance": code_provenance(),
    }
    summary["output_sha256"] = {name: sha256(output_dir / name) for name in
                                ("per_pdf_parse_diff.csv", "per_query_retrieval_diff.csv", "failure_cases.md")}
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parse-dir", type=Path, required=True)
    parser.add_argument("--retrieval-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.parse_dir, args.retrieval_dir, args.output_dir)
    print(json.dumps({key: result[key] for key in ("status", "changed_query_method_rows", "total_query_method_rows")}, indent=2))
