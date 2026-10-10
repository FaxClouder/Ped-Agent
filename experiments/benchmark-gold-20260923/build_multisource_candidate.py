"""Build a versioned candidate bundle with two-source comparison questions.

This script does not admit sources or certify Gold annotations. It preserves the
earlier candidate snapshot and writes only new *_v2 files.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import pymupdf


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "memPed/knowledge/gold/2026-09-23-rebuild"
REMOVED = (
    "rgq-013", "rgq-002", "rgq-009", "rgq-016",
    "rgq-032", "rgq-043", "rgq-072", "rgq-083",
    "rgq-093", "rgq-094", "rgq-098", "rgq-099",
)
REVIEW_CORRECTIONS = {
    "rgq-m02": {
        "evidence_a_zh": "PDF 第 9 页讨论传统力项叠加造成反向速度和重叠；在展示的仿真设置中，改进模型生成走走停停波且未出现负速度，但作者说明某些参数仍可能造成碰撞或反向运动。",
    },
    "rgq-m06": {
        "evidence_a_zh": "PDF 第 10 页结果显示，在相同目标速度档位（步行、慢跑或跑步）下，对称汇合通道比非对称的直行流与偏转流汇合布局更快放行相同人数。",
    },
    "rgq-m09": {
        "query_en": "Which inputs enter the religious-gathering risk index, which movement responses does the bidirectional-ramp experiment measure, and what different questions can those results answer?",
        "query_zh": "宗教集会风险指数纳入哪些风险输入，双向斜坡实验测量哪些运动响应，这两类结果各自能回答什么问题？",
    },
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def jsonl(name: str) -> list[dict]:
    return [json.loads(line) for line in (DATA / name).read_text(encoding="utf-8").splitlines()]


def write_jsonl(name: str, records: list[dict]) -> None:
    (DATA / name).write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records),
        encoding="utf-8",
    )


def main() -> None:
    old_rows = tsv("candidate_intents_selected.tsv")
    old_by_id = {row["intent_id"]: row for row in old_rows}
    assert len(old_rows) == len(old_by_id) == 120
    assert all(old_by_id[qid]["proposed_split"] == "proposed_test" for qid in REMOVED)
    multi = [row for part in "abc" for row in tsv(f"multi_part_{part}.tsv")]
    for row in multi:
        row.update(REVIEW_CORRECTIONS.get(row["intent_id"], {}))
    assert len(multi) == len({row["intent_id"] for row in multi}) == len(REMOVED) == 12

    corpus = {row["resource_id"]: row for row in jsonl("corpus_candidates.jsonl")}
    assert len(corpus) == 104
    dev_sources = {row["resource_id"] for row in old_rows if row["proposed_split"] == "proposed_dev"}
    test_sources = {row["resource_id"] for row in old_rows if row["proposed_split"] == "proposed_test"}
    assert not (dev_sources & test_sources)

    old_q = jsonl("questions_planned_candidate.jsonl")
    old_e = jsonl("evidence_planned_candidate.jsonl")
    old_review = list(csv.DictReader((DATA / "review_queue_candidate.csv").open(encoding="utf-8-sig", newline="")))
    assert len(old_q) == 240 and len(old_e) == 120 and len(old_review) == 140
    positive = [row for row in old_q if row["intent_id"] not in REMOVED]
    evidence = [row for row in old_e if row["intent_id"] not in REMOVED]
    review = [row for row in old_review if row["intent_id"] not in REMOVED]
    selected = [row.copy() for row in old_rows if row["intent_id"] not in REMOVED]
    topic_for_multi = {f"rgq-m{i:02d}": old_by_id[REMOVED[i-1]]["primary_topic"] for i in range(1, 13)}

    for row in multi:
        qid = row["intent_id"]
        ra, rb = row["resource_id_a"], row["resource_id_b"]
        assert ra != rb and {ra, rb} <= test_sources and not ({ra, rb} & dev_sources)
        assert ra in corpus and rb in corpus
        groups = []
        for group_id, suffix in (("g1", "a"), ("g2", "b")):
            resource_id = row[f"resource_id_{suffix}"]
            source = corpus[resource_id]
            page = int(row[f"pdf_page_{suffix}"])
            path = ROOT / source["source_path"]
            assert 1 <= page <= source["page_count"] and sha(path) == source["pdf_sha256"]
            with pymupdf.open(path) as pdf:
                assert len(pdf) == source["page_count"]
                assert pdf[page - 1].get_text().strip()
            groups.append({
                "group_id": group_id,
                "alternatives": [{
                    "resource_id": resource_id,
                    "source_pdf_sha256": source["pdf_sha256"],
                    "version_id": None,
                    "locator": {"page_index": page - 1, "pdf_page_1based": page, "element_id": None},
                    "locator_granularity": "pdf_page",
                    "needs_finer_locator_review": True,
                }],
            })
        assert row["query_en"].strip() and row["query_zh"].strip()
        topic = topic_for_multi[qid]
        selected.append({
            "intent_id": qid, "resource_id": ra, "pdf_page_1based": row["pdf_page_a"],
            "query_en": row["query_en"], "query_zh": row["query_zh"],
            "evidence_summary_zh": row["evidence_a_zh"] + "；" + row["evidence_b_zh"],
            "source_draft_file": f"multi_part_{'abc'[(int(qid[-2:]) - 1) // 4]}.tsv",
            "revision_note": "Two source groups are both required; human review pending.",
            "primary_topic": topic, "proposed_split": "proposed_test",
            "resource_id_b": rb, "pdf_page_b": row["pdf_page_b"],
            "evidence_b_zh": row["evidence_b_zh"],
        })
        for language in ("en", "zh"):
            positive.append({
                "annotation_status": "candidate", "answerable": True,
                "evidence_record_id": qid, "human_verified": False,
                "intent_id": qid, "language": language, "pair_id": qid,
                "primary_topic": topic, "proposed_split": "proposed_test",
                "query": row[f"query_{language}"], "question_family_id": qid,
                "question_id": f"{qid}-{language}",
                "question_type": "cross_document_comparison",
            })
        evidence.append({
            "annotation_status": "candidate", "answer_summary_zh": row["evidence_a_zh"] + "；" + row["evidence_b_zh"],
            "evidence_groups": groups, "evidence_record_id": qid,
            "human_verified": False, "intent_id": qid,
            "question_type": "cross_document_comparison",
            "revision_note": "Both source groups required; relevance completeness and precise locators need human review.",
            "source_admission_status": "candidate_not_admitted",
            "source_draft_file": selected[-1]["source_draft_file"],
            "source_review_method": "agent_pdf_text_draft_not_human_verified",
        })
        review.append({
            "intent_id": qid, "proposed_split": "proposed_test",
            "proposed_answerability": "answerable", "resource_id": ra + " + " + rb,
            "pdf_page_1based": row["pdf_page_a"] + " + " + row["pdf_page_b"],
            "query_en": row["query_en"], "query_zh": row["query_zh"],
            "evidence_or_absence_note": row["evidence_a_zh"] + "；" + row["evidence_b_zh"],
            "source_admission": "candidate_not_admitted", "reviewer_1": "",
            "reviewer_2": "", "adjudication": "", "final_status": "candidate",
        })

    selected.sort(key=lambda r: (r["proposed_split"], r["intent_id"]))
    positive.sort(key=lambda r: (r["intent_id"], r["language"]))
    evidence.sort(key=lambda r: r["intent_id"])
    review.sort(key=lambda r: r["intent_id"])
    assert Counter(row["proposed_split"] for row in selected) == {"proposed_dev": 20, "proposed_test": 100}
    assert len(positive) == 240 and len(evidence) == 120 and len(review) == 140
    assert len({row["question_id"] for row in positive}) == 240
    assert len({row["query"].casefold() for row in positive}) == 240
    assert len({row["intent_id"] for row in evidence}) == 120
    assert sum(len(row["evidence_groups"]) == 2 for row in evidence) == 12
    assert all(len(row["evidence_groups"]) == (2 if row["intent_id"].startswith("rgq-m") else 1) for row in evidence)

    selected_name = "candidate_intents_selected_v2.tsv"
    with (DATA / selected_name).open("w", encoding="utf-8", newline="") as stream:
        fields = list(old_rows[0]) + ["resource_id_b", "pdf_page_b", "evidence_b_zh"]
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(selected)
    write_jsonl("questions_planned_candidate_v2.jsonl", positive)
    write_jsonl("evidence_planned_candidate_v2.jsonl", evidence)
    negatives = jsonl("unanswerable_questions_candidate.jsonl")
    assert len(negatives) == 40
    write_jsonl("questions_full_candidate_v2.jsonl", positive + negatives)
    with (DATA / "review_queue_candidate_v2.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(old_review[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(review)

    old_selection = json.loads((DATA / "selection_manifest_candidate.json").read_text(encoding="utf-8"))
    selection = old_selection.copy()
    selection["status"] = "candidate_proposed_split_v2_not_sealed"
    selection["source_grouping"] = "All question sources remain in one partition; comparison questions require two test sources."
    selection["test_intent_ids"] = sorted(set(selection["test_intent_ids"]) - set(REMOVED) | {row["intent_id"] for row in multi})
    selection["replacement_map"] = dict(zip(REMOVED, [row["intent_id"] for row in multi]))
    selection["cross_document_comparison_count"] = 12
    selection["topic_counts"] = {split: dict(Counter(row["primary_topic"] for row in selected if row["proposed_split"] == split)) for split in ("proposed_dev", "proposed_test")}
    selection["output_hashes"] = {name: sha(DATA / name) for name in (
        selected_name, "questions_planned_candidate_v2.jsonl", "evidence_planned_candidate_v2.jsonl",
        "questions_full_candidate_v2.jsonl", "review_queue_candidate_v2.csv",
    )}
    (DATA / "selection_manifest_candidate_v2.json").write_text(json.dumps(selection, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    old_manifest = json.loads((DATA / "full_candidate_manifest.json").read_text(encoding="utf-8"))
    manifest = old_manifest.copy()
    manifest["gold_schema_version"] = "candidate-gold-v2-multisource-draft"
    manifest["cross_document_comparison_intents"] = 12
    manifest["single_document_intents"] = 108
    manifest["selected_body_page_intents"] = sum(int(row["pdf_page_1based"]) > 1 or bool(row.get("pdf_page_b") and int(row["pdf_page_b"]) > 1) for row in selected)
    manifest["input_sha256"] = {name: sha(DATA / name) for name in (
        "corpus_candidates.jsonl", "candidate_intents_selected.tsv", "questions_planned_candidate.jsonl",
        "evidence_planned_candidate.jsonl", "review_queue_candidate.csv",
        "unanswerable_questions_candidate.jsonl", "multi_part_a.tsv", "multi_part_b.tsv", "multi_part_c.tsv",
    )}
    manifest["output_sha256"] = {name: sha(DATA / name) for name in (
        selected_name, "questions_planned_candidate_v2.jsonl", "evidence_planned_candidate_v2.jsonl",
        "questions_full_candidate_v2.jsonl", "review_queue_candidate_v2.csv", "selection_manifest_candidate_v2.json",
    )}
    manifest["release_gate_reason"] = "No source has formal admission; human double review, alternative relevance, refusal absence review, and v2 evaluator remain incomplete."
    (DATA / "full_candidate_manifest_v2.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Built 120 answerable intents (12 two-source), 20 proposed refusal intents, 280 bilingual variants; {manifest['selected_body_page_intents']} answerable intents use a body page.")


if __name__ == "__main__":
    main()
