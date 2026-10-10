"""Load only the materialized Gold v5 development annotation work package.

The full candidate question/evidence files are hashed, not parsed here.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "memPed/knowledge/gold/2026-09-23-rebuild"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_dev_scope() -> tuple[list[dict], dict[str, dict]]:
    manifest_path = GOLD / "answer_annotation_manifest_dev_v1.json"
    annotation_path = GOLD / "answer_annotations_dev_v1.jsonl"
    question_path = GOLD / "questions_full_candidate_v5.jsonl"
    evidence_path = GOLD / "evidence_planned_candidate_v5.jsonl"
    gold_manifest_path = GOLD / "full_candidate_manifest_v5.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    gold_manifest = json.loads(gold_manifest_path.read_text(encoding="utf-8"))
    if (manifest["intent_count"] != 20 or manifest["query_variant_count"] != 40
            or manifest["human_verified"] is not False
            or sha256(annotation_path) != manifest["output_sha256"][annotation_path.name]):
        raise ValueError("development annotation scope or hash changed")
    for path in (question_path, evidence_path, gold_manifest_path):
        if sha256(path) != manifest["source_sha256"][path.name]:
            raise ValueError(f"development source hash changed: {path.name}")
    for path in (question_path, evidence_path):
        if sha256(path) != gold_manifest["output_sha256"][path.name]:
            raise ValueError(f"candidate Gold manifest hash changed: {path.name}")
    rows = [json.loads(line) for line in annotation_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != 20 or len({row["intent_id"] for row in rows}) != 20:
        raise ValueError("development annotation count changed")
    questions: list[dict] = []
    evidence: dict[str, dict] = {}
    for row in rows:
        intent = row["intent_id"]
        if (row["human_verified"] is not False or row["annotation_status"] != "pending_human_review"
                or row["candidate_evidence"]["intent_id"] != intent
                or row["candidate_evidence"]["human_verified"] is not False):
            raise ValueError(f"unexpected annotation review status: {intent}")
        evidence[intent] = row["candidate_evidence"]
        for language in ("en", "zh"):
            question_id = f"{intent}-{language}"
            if question_id not in row["question_ids"] or not row["queries"][language].strip():
                raise ValueError(f"incomplete development pair: {intent}")
            questions.append({
                "intent_id": intent, "pair_id": intent,
                "question_family_id": row["question_family_id"],
                "question_id": question_id, "language": language,
                "query": row["queries"][language],
                "primary_topic": row["primary_topic"],
                "answerable": True, "proposed_split": "proposed_dev",
                "human_verified": False,
            })
    return questions, evidence
