"""Materialized development scope excludes sealed intent records."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dev_scope import load_dev_scope


def test_dev_scope_contains_only_twenty_paired_answerable_intents() -> None:
    questions, evidence = load_dev_scope()
    assert len(questions) == 40
    assert len(evidence) == 20
    assert {q["language"] for q in questions} == {"en", "zh"}
    assert {q["intent_id"] for q in questions} == set(evidence)
    assert all(q["proposed_split"] == "proposed_dev" for q in questions)
    assert all(q["human_verified"] is False for q in questions)
