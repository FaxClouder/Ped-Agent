"""Checks for the alternative-source and bilingual-review revision."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from integrate_review_v5 import build_bundle


ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "memPed/knowledge/gold/2026-09-23-rebuild"


def test_v5_replaces_leaking_test_intent_and_resolves_numeric_conflict():
    bundle = build_bundle(GOLD)
    questions = bundle["questions_full_candidate_v5.jsonl"]
    evidence = {e["intent_id"]: e for e in bundle["evidence_planned_candidate_v5.jsonl"]}
    selected = {q["intent_id"] for q in questions if q["answerable"]}
    assert len(questions) == 280 and len(selected) == 120
    assert "rgq-u012" in selected and "rgq-066" not in selected
    assert {q["intent_id"] for q in bundle["reclassified_answerable_candidate_v5.jsonl"]} == {"rgq-066"}
    assert len(evidence["rgq-034"]["evidence_groups"]) == 2
    assert len(evidence["rgq-122"]["evidence_groups"]) == 2
    assert "59%" in evidence["rgq-122"]["answer_summary_zh"]
    assert len(evidence["rgq-073"]["evidence_groups"][0]["alternatives"]) == 2
    en = {q["intent_id"]: q for q in questions if q["language"] == "en"}
    zh = {q["intent_id"]: q for q in questions if q["language"] == "zh"}
    assert "how many" in en["rgq-122"]["query"].lower()
    assert "更激进" in zh["rgq-080"]["query"]
