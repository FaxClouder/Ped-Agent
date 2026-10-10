"""Validate the AI-reviewed candidate against the frozen 104-PDF snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import pymupdf


ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "memPed/knowledge/gold/2026-09-23-rebuild"
SNAPSHOT = ROOT / "outputs/gold-v2-snapshot-20260924-01/snapshot.json"


def read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(version: str = "v3") -> dict:
    if version not in {"v3", "v4", "v5"}:
        raise ValueError(version)
    manifest_path = GOLD / f"full_candidate_manifest_{version}.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for name, digest in manifest["output_sha256"].items():
        if sha(GOLD / name) != digest:
            raise ValueError(f"Output hash mismatch: {name}")
    for name, digest in manifest["input_sha256"].items():
        if sha(GOLD / name) != digest:
            raise ValueError(f"Input hash mismatch: {name}")
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    sources = {row["resource_id"]: row for row in read(GOLD / "corpus_candidates.jsonl")}
    if set(sources) != set(snapshot["source_members"]):
        raise ValueError("Catalog source membership changed")
    questions = read(GOLD / f"questions_full_candidate_{version}.jsonl")
    refusals = read(GOLD / f"unanswerable_questions_candidate_{version}.jsonl")
    evidence = read(GOLD / f"evidence_planned_candidate_{version}.jsonl")
    reserve = read(GOLD / f"reclassified_answerable_candidate_{version}.jsonl")
    reserve_evidence = read(GOLD / f"reclassified_evidence_candidate_{version}.jsonl")
    if len(questions) != 280 or len(refusals) != 40 or len(evidence) != 120 or len(reserve) != 2 or len(reserve_evidence) != 1:
        raise ValueError("Candidate count mismatch")
    paired = defaultdict(list)
    exact_queries = set()
    for q in questions + reserve:
        paired[q["intent_id"]].append(q["language"])
        normalized = " ".join(q["query"].casefold().split())
        key = (q["language"], normalized)
        if key in exact_queries:
            raise ValueError(f"Duplicate query: {q['question_id']}")
        exact_queries.add(key)
        if q["human_verified"] is not False:
            raise ValueError(f"False human verification: {q['question_id']}")
    if len(paired) != 141 or any(sorted(langs) != ["en", "zh"] for langs in paired.values()):
        raise ValueError("Bilingual pairing mismatch")
    selected_ids = {q["intent_id"] for q in questions if q["answerable"] is True}
    refusal_ids = {q["intent_id"] for q in refusals}
    reserve_id = "rgq-066" if version == "v5" else "rgq-u012"
    if len(selected_ids) != 120 or len(refusal_ids) != 20 or selected_ids & refusal_ids or reserve_id in selected_ids | refusal_ids:
        raise ValueError("Answerability or reserve mismatch")
    if {q["question_id"] for q in refusals} != {q["question_id"] for q in questions if q["answerable"] is False}:
        raise ValueError("Refusal files disagree")
    if {e["intent_id"] for e in evidence} != selected_ids:
        raise ValueError("Evidence/answerable intent mismatch")
    splits = {q["intent_id"]: q["proposed_split"] for q in questions if q["answerable"] is True}
    split_counts = Counter(splits.values())
    if split_counts != {"proposed_dev": 20, "proposed_test": 100}:
        raise ValueError(f"Split count mismatch: {split_counts}")
    source_by_split = defaultdict(set)
    locators = 0
    for record in evidence + reserve_evidence:
        for group in record["evidence_groups"]:
            if not group["alternatives"]:
                raise ValueError(f"Empty evidence group: {record['intent_id']}")
            for alt in group["alternatives"]:
                resource_id = alt["resource_id"]
                source = sources[resource_id]
                digest = alt["source_pdf_sha256"]
                if digest != source["pdf_sha256"] or digest != snapshot["source_members"][resource_id]:
                    raise ValueError(f"Source hash mismatch: {record['intent_id']}")
                if record["intent_id"] in splits:
                    source_by_split[splits[record["intent_id"]]].add(resource_id)
                page = alt["locator"]["page_index"]
                if alt["locator"]["pdf_page_1based"] != page + 1 or not 0 <= page < source["page_count"]:
                    raise ValueError(f"Page out of bounds: {record['intent_id']}")
                locators += 1
    overlap = source_by_split["proposed_dev"] & source_by_split["proposed_test"]
    if overlap:
        raise ValueError(f"Dev/test source overlap: {sorted(overlap)}")
    used = {alt["resource_id"] for record in evidence + reserve_evidence for group in record["evidence_groups"] for alt in group["alternatives"]}
    checked_pages = set()
    for resource_id in used:
        source = sources[resource_id]
        path = ROOT / source["source_path"]
        if sha(path) != source["pdf_sha256"]:
            raise ValueError(f"PDF hash changed: {resource_id}")
        with pymupdf.open(path) as pdf:
            if len(pdf) != source["page_count"]:
                raise ValueError(f"PDF page count changed: {resource_id}")
            pages = {alt["locator"]["page_index"] for record in evidence + reserve_evidence for group in record["evidence_groups"] for alt in group["alternatives"] if alt["resource_id"] == resource_id}
            for page in pages:
                if not pdf[page].get_text().strip():
                    raise ValueError(f"Empty evidence page: {resource_id}/{page + 1}")
                checked_pages.add((resource_id, page))
    return {
        "status": "technical_validation_passed_candidate_only", "candidate_version": version, "question_variants": len(questions), "independent_intents": 140,
        "answerable_intents": len(selected_ids), "refusal_intents": len(refusal_ids), "reserve_answerable_intents": 1,
        "split_counts": dict(split_counts), "source_pdfs_checked": len(used), "page_locators_checked": locators,
        "distinct_pages_checked": len(checked_pages), "dev_test_source_overlap": len(overlap),
        "candidate_manifest_sha256": sha(manifest_path),
        "snapshot_sha256": sha(SNAPSHOT), "formal_gold_ready": False,
        "remaining_gates": manifest["pending_review"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--candidate-version", choices=("v3", "v4", "v5"), default="v3")
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    report = validate(args.candidate_version)
    args.output_dir.mkdir(parents=True)
    (args.output_dir / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
