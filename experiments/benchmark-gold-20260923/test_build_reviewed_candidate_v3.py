"""Fixed checks for the AI-reviewed Gold v2 candidate revision."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from build_reviewed_candidate_v3 import build_bundle, write_bundle


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "memPed/knowledge/gold/2026-09-23-rebuild"
REVIEW = ROOT / "outputs/gold-v2-agent-review-20260924-integrated"


def test_reviewed_bundle_keeps_selected_split_and_reclassifies_false_refusal() -> None:
    bundle = build_bundle(DATA, REVIEW)
    questions = bundle["questions_full_candidate_v3.jsonl"]
    evidence = bundle["evidence_planned_candidate_v3.jsonl"]
    refusals = bundle["unanswerable_questions_candidate_v3.jsonl"]
    reserve = bundle["reclassified_answerable_candidate_v3.jsonl"]

    assert len(questions) == 280
    assert len(evidence) == 120
    assert len(refusals) == 40
    assert len(reserve) == 2
    assert {q["intent_id"] for q in reserve} == {"rgq-u012"}
    assert all(q["answerable"] for q in reserve)
    assert not any(q["intent_id"] == "rgq-u012" for q in questions)
    assert {q["intent_id"] for q in refusals} == {
        f"rgq-u{i:03d}" for i in range(1, 22) if i != 12
    }
    assert all(q["answerable"] is False for q in refusals)
    assert all(q["human_verified"] is False for q in questions + reserve)


def test_reviewed_bundle_applies_source_scoped_corrections() -> None:
    bundle = build_bundle(DATA, REVIEW)
    questions = {(q["intent_id"], q["language"]): q for q in bundle["questions_full_candidate_v3.jsonl"]}
    evidence = {e["intent_id"]: e for e in bundle["evidence_planned_candidate_v3.jsonl"]}

    assert "experimental variables" in questions["rgq-031", "en"]["query"]
    assert "wide-track" in questions["rgq-055", "en"]["query"]
    assert "Yamori" in questions["rgq-080", "en"]["query"]
    assert "serpentine" in evidence["rgq-m09"]["answer_summary_zh"] or "蛇形" in evidence["rgq-m09"]["answer_summary_zh"]
    assert "movement aspects" in questions["rgq-m11", "en"]["query"]
    assert "2026" in questions["rgq-u004", "en"]["query"]
    assert "volunteer GPS" in questions["rgq-u008", "en"]["query"]


def test_writer_refuses_existing_target_files(tmp_path: Path) -> None:
    bundle = build_bundle(DATA, REVIEW)
    write_bundle(tmp_path, bundle)
    assert len(json.loads((tmp_path / "full_candidate_manifest_v3.json").read_text(encoding="utf-8"))["output_sha256"]) >= 5
    with pytest.raises(FileExistsError):
        write_bundle(tmp_path, bundle)
