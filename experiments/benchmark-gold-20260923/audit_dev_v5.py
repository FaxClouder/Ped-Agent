"""Read-only technical audit of Gold v5 development evidence and annotation scope.

This verifies identity and locators, not the truth of a scientific claim.
Only the materialized development annotation rows are parsed; the full
candidate files are hashed but their sealed test/refusal rows are not parsed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path

import pymupdf

from dev_scope import load_dev_scope

ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "memPed/knowledge/gold/2026-09-23-rebuild"
INDEX = ROOT / "outputs/knowledge-index-104-v1-20260924-01"
SNAPSHOT = ROOT / "outputs/gold-v2-snapshot-20260924-01/snapshot.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def audit_pairs(questions: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for question in questions:
        grouped[question["intent_id"]].append(question)
    pairs = []
    for intent_id, variants in sorted(grouped.items()):
        if len(variants) != 2 or {q["language"] for q in variants} != {"en", "zh"}:
            raise ValueError(f"incomplete language pair: {intent_id}")
        if any(q["pair_id"] != intent_id for q in variants):
            raise ValueError(f"invalid pair ID: {intent_id}")
        if len({q["question_id"] for q in variants}) != 2 or len({q["question_family_id"] for q in variants}) != 1:
            raise ValueError(f"inconsistent pair identity: {intent_id}")
        if any(not q["query"].strip() or q["human_verified"] is not False for q in variants):
            raise ValueError(f"invalid candidate pair status: {intent_id}")
        by_language = {q["language"]: q for q in variants}
        pairs.append({
            "intent_id": intent_id,
            "question_family_id": variants[0]["question_family_id"],
            "question_ids": {lang: by_language[lang]["question_id"] for lang in ("en", "zh")},
            "queries": {lang: by_language[lang]["query"] for lang in ("en", "zh")},
            "topic": by_language["en"].get("primary_topic"),
        })
    return pairs


def audit_evidence(evidence: dict, sources: dict[str, dict], members: dict[str, str]) -> dict:
    if evidence["human_verified"] is not False:
        raise ValueError(f"invalid human review status: {evidence['intent_id']}")
    groups = evidence["evidence_groups"]
    if not groups or len({g["group_id"] for g in groups}) != len(groups):
        raise ValueError(f"invalid evidence groups: {evidence['intent_id']}")
    locations = []
    for group in groups:
        if not group["alternatives"]:
            raise ValueError(f"empty evidence group: {evidence['intent_id']}/{group['group_id']}")
        for alt in group["alternatives"]:
            resource = alt["resource_id"]
            digest = alt["source_pdf_sha256"]
            if resource not in sources or digest != sources[resource]["pdf_sha256"] or digest != members.get(resource):
                raise ValueError(f"source hash mismatch: {evidence['intent_id']}/{resource}")
            locator = alt["locator"]
            page = locator["page_index"]
            if not isinstance(page, int) or not 0 <= page < sources[resource]["page_count"] or locator["pdf_page_1based"] != page + 1:
                raise ValueError(f"invalid page locator: {evidence['intent_id']}/{resource}")
            locations.append({
                "group_id": group["group_id"], "resource_id": resource,
                "source_pdf_sha256": digest, "page_index": page,
                "pdf_page_1based": page + 1, "element_id": locator.get("element_id"),
                "needs_finer_locator_review": bool(alt.get("needs_finer_locator_review") or not locator.get("element_id")),
            })
    return {
        "group_count": len(groups), "alternative_count": len(locations),
        "locations": locations,
        "needs_finer_locator_review": any(item["needs_finer_locator_review"] for item in locations),
        "human_verified": False,
    }


def write_report(output_dir: Path, rows: list[dict], summary: dict) -> None:
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite research output: {output_dir}")
    output_dir.mkdir(parents=True)
    with (output_dir / "per_intent.jsonl").open("x", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (output_dir / "review_queue.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=(
            "intent_id", "group_id", "resource_id", "source_pdf_sha256", "page_index", "pdf_page_1based",
            "element_id", "page_text_sha256", "page_text_chars", "needs_finer_locator_review",
            "bilingual_meaning_review", "claim_support_review", "numeric_conflict_review", "human_verified",
        ))
        writer.writeheader()
        for row in rows:
            for location in row["locations"]:
                writer.writerow({
                    "intent_id": row["intent_id"], **location,
                    "bilingual_meaning_review": "pending_human_review",
                    "claim_support_review": "pending_human_review",
                    "numeric_conflict_review": "pending_human_review",
                    "human_verified": False,
                })
    summary["output_sha256"] = {
        name: sha256(output_dir / name) for name in ("per_intent.jsonl", "review_queue.csv")
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(output_dir: Path) -> dict:
    if output_dir.exists():
        raise FileExistsError(output_dir)
    question_path = GOLD / "questions_full_candidate_v5.jsonl"
    evidence_path = GOLD / "evidence_planned_candidate_v5.jsonl"
    manifest_path = GOLD / "full_candidate_manifest_v5.json"
    annotation_path = GOLD / "answer_annotations_dev_v1.jsonl"
    annotation_manifest_path = GOLD / "answer_annotation_manifest_dev_v1.json"
    corpus_path = GOLD / "corpus_candidates.jsonl"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for path in (question_path, evidence_path):
        if sha256(path) != manifest["output_sha256"][path.name]:
            raise ValueError(f"candidate file hash mismatch: {path.name}")
    annotation_manifest = json.loads(annotation_manifest_path.read_text(encoding="utf-8"))
    if sha256(annotation_path) != annotation_manifest["output_sha256"][annotation_path.name]:
        raise ValueError("answer annotation package changed")
    for path in (question_path, evidence_path, manifest_path):
        if sha256(path) != annotation_manifest["source_sha256"][path.name]:
            raise ValueError(f"annotation source changed: {path.name}")

    questions, evidence = load_dev_scope()
    pairs = audit_pairs(questions)
    if len(pairs) != 20 or len(questions) != 40:
        raise ValueError("development scope must contain 20 paired intents")
    intent_ids = {pair["intent_id"] for pair in pairs}
    annotations = {a["intent_id"]: a for a in read_jsonl(annotation_path)}
    if set(evidence) != intent_ids or set(annotations) != intent_ids:
        raise ValueError("development evidence or answer annotation scope differs")
    sources = {s["resource_id"]: s for s in read_jsonl(corpus_path)}
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    index_report_path = INDEX / "build_report.json"
    index_report = json.loads(index_report_path.read_text(encoding="utf-8"))
    if snapshot["source_index_report_sha256"] != sha256(index_report_path) or snapshot["source_catalog_fingerprint"] != index_report["catalog_fingerprint"]:
        raise ValueError("frozen index and candidate snapshot disagree")
    checked_pages: dict[tuple[str, int], dict] = {}
    checked_sources: set[str] = set()
    rows = []
    for pair in pairs:
        intent_id = pair["intent_id"]
        audited = audit_evidence(evidence[intent_id], sources, snapshot["source_members"])
        annotation = annotations[intent_id]
        if annotation["queries"] != pair["queries"] or annotation["human_verified"] is not False or annotation["candidate_evidence"] != {**evidence[intent_id], "human_verified": False}:
            raise ValueError(f"annotation package differs from candidate: {intent_id}")
        if annotation["reference_answer_en"] is not None or annotation["reference_answer_zh"] is not None or annotation["required_facts"]:
            raise ValueError(f"unexpected pre-filled human answers: {intent_id}")
        for location in audited["locations"]:
            resource = location["resource_id"]
            path = ROOT / sources[resource]["source_path"]
            if resource not in checked_sources:
                if sha256(path) != location["source_pdf_sha256"]:
                    raise ValueError(f"PDF hash mismatch: {resource}")
                checked_sources.add(resource)
            key = (resource, location["page_index"])
            if key not in checked_pages:
                with pymupdf.open(path) as pdf:
                    if len(pdf) != sources[resource]["page_count"]:
                        raise ValueError(f"PDF page count mismatch: {resource}")
                    page_text = pdf[location["page_index"]].get_text().strip()
                if not page_text:
                    raise ValueError(f"empty PDF evidence page: {intent_id}/{resource}")
                checked_pages[key] = {
                    "page_text_sha256": hashlib.sha256(page_text.encode("utf-8")).hexdigest(),
                    "page_text_chars": len(page_text),
                }
            location.update(checked_pages[key])
        rows.append({
            **pair, **audited,
            "answer_annotation_status": annotation["annotation_status"],
            "reference_answers_present": False,
            "bilingual_meaning_review": "pending_human_review",
            "claim_support_review": "pending_human_review",
            "numeric_conflict_review": "pending_human_review",
        })
    summary = {
        "status": "technical_audit_passed_candidate_only",
        "formal_gold_ready": False, "human_verified": False,
        "test_split_evaluated": False, "refusal_evaluated": False,
        "independent_intents": len(rows), "query_variants": len(questions),
        "evidence_groups": sum(row["group_count"] for row in rows),
        "evidence_alternatives": sum(row["alternative_count"] for row in rows),
        "source_pdfs_checked": len(checked_sources), "distinct_pages_checked": len(checked_pages),
        "intents_needing_finer_locator": [row["intent_id"] for row in rows if row["needs_finer_locator_review"]],
        "intents_pending_bilingual_and_claim_review": [row["intent_id"] for row in rows],
        "source_sha256": {path.name: sha256(path) for path in (
            question_path, evidence_path, manifest_path, annotation_path,
            annotation_manifest_path, corpus_path, SNAPSHOT, index_report_path,
        )},
        "index_fingerprint": index_report["catalog_fingerprint"],
        "chunk_policy": index_report["policy_version"],
        "tokenizer_fingerprint": index_report["tokenizer_fingerprint"],
        "lexical_analyzer_fingerprint": index_report["lexical_analyzer_fingerprint"],
        "embedding_fingerprint": index_report["embedding_fingerprint"],
        "model_revision": index_report["model_revision"],
        "model_weights_sha256": index_report["model_weights_sha256"],
        "random_seed": None,
        "code_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "runner_sha256": sha256(Path(__file__)),
    }
    write_report(output_dir, rows, summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), ensure_ascii=False, indent=2))
