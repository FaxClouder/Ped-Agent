"""Build the versioned Stage 2 development answer-annotation scope.

This creates an auditable annotation work package only. It does not author
reference answers or promote candidate evidence to formal Gold labels.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
GOLD_DIR = ROOT / "memPed/knowledge/gold/2026-09-23-rebuild"
EVAL_DIR = ROOT / "paper/evaluation-reports/gold-v5-dev-20260924"
QUESTIONS_PATH = GOLD_DIR / "questions_full_candidate_v5.jsonl"
EVIDENCE_PATH = GOLD_DIR / "evidence_planned_candidate_v5.jsonl"
MANIFEST_PATH = GOLD_DIR / "full_candidate_manifest_v5.json"
SUMMARY_PATH = EVAL_DIR / "summary.json"
OUTPUT_PATH = GOLD_DIR / "answer_annotations_dev_v1.jsonl"
OUTPUT_MANIFEST_PATH = GOLD_DIR / "answer_annotation_manifest_dev_v1.json"
DECISIONS_PATH = GOLD_DIR / "annotation_decisions_dev_v1.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def build_rows() -> list[dict[str, Any]]:
    questions = [
        question
        for question in read_jsonl(QUESTIONS_PATH)
        if question.get("proposed_split") == "proposed_dev"
        and question.get("answerable") is True
    ]
    evidence = {
        record["intent_id"]: record for record in read_jsonl(EVIDENCE_PATH)
    }
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for question in questions:
        grouped[question["intent_id"]].append(question)

    rows: list[dict[str, Any]] = []
    for intent_id in sorted(grouped):
        variants = sorted(grouped[intent_id], key=lambda item: item["language"])
        languages = {item["language"] for item in variants}
        if languages != {"en", "zh"} or len(variants) != 2:
            raise ValueError(f"development intent is not exactly bilingual: {intent_id}")
        question_ids = [item["question_id"] for item in variants]
        if len(set(question_ids)) != 2:
            raise ValueError(f"duplicate development question IDs: {intent_id}")
        if any(item["pair_id"] != intent_id for item in variants):
            raise ValueError(f"unexpected pair ID for development intent: {intent_id}")
        if intent_id not in evidence:
            raise ValueError(f"missing evidence for development intent: {intent_id}")

        by_language = {item["language"]: item for item in variants}
        candidate_evidence = json.loads(json.dumps(evidence[intent_id], ensure_ascii=False))
        candidate_evidence["human_verified"] = False
        rows.append(
            {
                "schema_version": "answer-annotation-dev-v1",
                "intent_id": intent_id,
                "question_family_id": by_language["en"]["question_family_id"],
                "question_ids": question_ids,
                "queries": {
                    "en": by_language["en"]["query"],
                    "zh": by_language["zh"]["query"],
                },
                "primary_topic": by_language["en"].get("primary_topic"),
                "reference_answer_en": None,
                "reference_answer_zh": None,
                "required_facts": [],
                "acceptable_variants": [],
                "unsupported_claims": [],
                "answer_type": None,
                "requires_multi_hop": None,
                "numeric_constraints": [],
                "candidate_evidence": candidate_evidence,
                "annotation_status": "pending_human_review",
                "human_verified": False,
            }
        )
    if len(rows) != 20:
        raise ValueError(f"expected 20 development intents, found {len(rows)}")
    return rows


def resolve_output_paths(output_path: Path) -> tuple[Path, Path, Path]:
    """Keep all files of one annotation package in the same directory."""
    return (
        output_path,
        output_path.with_name(OUTPUT_MANIFEST_PATH.name),
        output_path.with_name(DECISIONS_PATH.name),
    )


def write_decisions(path: Path) -> None:
    with path.open("x", encoding="utf-8") as stream:
        stream.write("""# Development Answer Annotation Decisions v1

*Development-only annotation protocol · status: current*

**Status**: protocol and work-package scope; answers are not yet annotated

## Scope

This work package covers the 20 proposed development intents and their 40 paired Chinese/English queries. It does not include the 100 proposed test intents or 20 refusal intents. Candidate labels remain `human_verified=false`.

## Annotation unit

Annotate one intent at a time: one language-neutral fact specification, one English reference answer, and one Chinese reference answer. The paired answers must have the same factual boundary. Do not create independent facts for the two languages.

## Required fields

- `reference_answer_en` and `reference_answer_zh`: concise answers supported by the frozen source evidence.
- `required_facts`: atomic facts required for a fully correct answer; each fact should identify its evidence group.
- `acceptable_variants`: equivalent wording, unit conversions, or explicitly permitted rounding.
- `unsupported_claims`: plausible but unsupported conclusions that should count against faithfulness or correctness.
- `answer_type` and `requires_multi_hop`: describe reasoning demands, not writing style.
- `numeric_constraints`: exact value, unit, tolerance, or source-conflict rule for numerical answers.

## Evidence rules

Evidence groups are conjunctive (AND); alternatives inside one group are interchangeable (OR). Keep resource IDs, source PDF hashes, page indices, and element IDs from the candidate evidence. A page-level locator marked `needs_finer_locator_review` is a candidate locator, not a verified citation.

## Human review gates

Before `human_verified` can become true, a domain reviewer must verify bilingual equivalence, answer completeness, evidence sufficiency, numeric values, locator accuracy, and unsupported inference boundaries. Record disputes in a new versioned decision file; do not silently edit a released annotation file.

## Evaluation boundary

The annotation package enables development-only Answer Relevancy, Faithfulness, Answer Correctness, and citation checks after answers are reviewed. It is not a release gate and must not be used to score the sealed test set.
""")


def build(
    output_path: Path = OUTPUT_PATH,
    *,
    output_manifest_path: Path | None = None,
    decisions_path: Path | None = None,
) -> None:
    _, default_manifest_path, default_decisions_path = resolve_output_paths(output_path)
    output_manifest_path = output_manifest_path or default_manifest_path
    decisions_path = decisions_path or default_decisions_path
    for path in (output_path, output_manifest_path, decisions_path):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite research output: {path}")
    rows = build_rows()
    with output_path.open("x", encoding="utf-8") as stream:
        stream.write("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n")
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    candidate_manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest = {
        "schema_version": "answer-annotation-manifest-dev-v1",
        "status": "candidate_annotation_scope",
        "human_verified": False,
        "answer_annotation_status": "pending_human_review",
        "intent_count": len(rows),
        "query_variant_count": sum(len(row["question_ids"]) for row in rows),
        "intent_ids": [row["intent_id"] for row in rows],
        "source_sha256": {
            QUESTIONS_PATH.name: sha256(QUESTIONS_PATH),
            EVIDENCE_PATH.name: sha256(EVIDENCE_PATH),
            MANIFEST_PATH.name: sha256(MANIFEST_PATH),
            SUMMARY_PATH.name: sha256(SUMMARY_PATH),
        },
        "source_candidate_manifest_status": candidate_manifest["status"],
        "output_sha256": {output_path.name: sha256(output_path)},
        "catalog_fingerprint": summary["catalog_fingerprint"],
        "index_report_sha256": summary["index_report_sha256"],
        "questions_sha256": summary["questions_sha256"],
        "evidence_sha256": summary["evidence_sha256"],
        "excluded_scopes": {
            "proposed_test_intents": 100,
            "refusal_intents": 20,
        },
    }
    with output_manifest_path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    write_decisions(decisions_path)
    print(json.dumps({"intents": len(rows), "queries": manifest["query_variant_count"]}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    build(parser.parse_args().output.resolve())
