"""Regression checks for the independently reviewed refusal correction."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from finalize_candidate_v4 import build_bundle


ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "memPed/knowledge/gold/2026-09-23-rebuild"


def test_replacement_refusal_is_unambiguous_and_not_human_verified():
    bundle = build_bundle(GOLD)
    questions = bundle["questions_full_candidate_v4.jsonl"]
    en = next(q for q in questions if q["question_id"] == "rgq-u021-en")
    zh = next(q for q in questions if q["question_id"] == "rgq-u021-zh")
    assert "eastern and western" in en["query"]
    assert "东、西两条" in zh["query"]
    assert en["annotation_status"] == "agent_reviewed_candidate"
    assert en["human_verified"] is False
    assert len(questions) == 280
    assert len(bundle["evidence_planned_candidate_v4.jsonl"]) == 120
