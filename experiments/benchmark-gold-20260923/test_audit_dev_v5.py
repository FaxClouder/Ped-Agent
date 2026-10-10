"""Development-only technical audit of candidate evidence."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_dev_v5 import audit_pairs, audit_evidence, write_report


def test_pairs_require_one_equivalent_scope_per_language() -> None:
    pair = [
        {"intent_id": "i1", "pair_id": "i1", "question_family_id": "f1", "question_id": "i1-en", "language": "en", "query": "What?", "human_verified": False},
        {"intent_id": "i1", "pair_id": "i1", "question_family_id": "f1", "question_id": "i1-zh", "language": "zh", "query": "什么？", "human_verified": False},
    ]
    assert audit_pairs(pair)[0]["intent_id"] == "i1"
    with pytest.raises(ValueError, match="pair"):
        audit_pairs([pair[0], {**pair[1], "pair_id": "other"}])


def test_evidence_checks_hash_and_page_without_claiming_human_review() -> None:
    source = {"r1": {"pdf_sha256": "abc", "page_count": 2}}
    evidence = {"intent_id": "i1", "human_verified": False, "evidence_groups": [
        {"group_id": "g1", "alternatives": [{"resource_id": "r1", "source_pdf_sha256": "abc", "locator": {"page_index": 0, "pdf_page_1based": 1, "element_id": None}, "needs_finer_locator_review": True}]}
    ]}
    result = audit_evidence(evidence, source, {"r1": "abc"})
    assert result["group_count"] == 1
    assert result["needs_finer_locator_review"] is True
    assert result["human_verified"] is False
    with pytest.raises(ValueError, match="source hash"):
        audit_evidence(evidence, {"r1": {"pdf_sha256": "changed", "page_count": 2}}, {"r1": "abc"})
    with pytest.raises(ValueError, match="page"):
        bad = json.loads(json.dumps(evidence))
        bad["evidence_groups"][0]["alternatives"][0]["locator"]["page_index"] = 2
        audit_evidence(bad, source, {"r1": "abc"})


def test_report_never_overwrites_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "audit"
    output.mkdir()
    (output / "keep.txt").write_text("preserve", encoding="utf-8")
    with pytest.raises(FileExistsError):
        write_report(output, [], {})
    assert (output / "keep.txt").read_text(encoding="utf-8") == "preserve"


def test_report_writes_page_level_review_queue(tmp_path: Path) -> None:
    output = tmp_path / "audit"
    row = {"intent_id": "i1", "locations": [{
        "group_id": "g1", "resource_id": "r1", "source_pdf_sha256": "abc",
        "page_index": 0, "pdf_page_1based": 1, "element_id": None,
        "page_text_sha256": "def", "page_text_chars": 42,
        "needs_finer_locator_review": True,
    }]}
    write_report(output, [row], {"status": "candidate_only"})
    assert "pending_human_review" in (output / "review_queue.csv").read_text(encoding="utf-8")
