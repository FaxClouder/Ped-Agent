"""The agent review package never masquerades as human-verified Gold."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_review import adjudicate, write_package


def _source() -> dict:
    return {
        "intent_id": "rgq-example", "queries": {"en": "Question?", "zh": "问题？"},
        "candidate_evidence": {"human_verified": False, "evidence_groups": [
            {"group_id": "g1", "alternatives": [{"resource_id": "paper-a",
              "source_pdf_sha256": "a" * 64, "locator": {"pdf_page_1based": 2}}]}
        ]},
        "human_verified": False, "reference_answer_en": None,
        "reference_answer_zh": None, "required_facts": [],
    }


def _review() -> dict:
    return {
        "intent_id": "rgq-example", "bilingual_equivalent": True,
        "evidence_supported": True, "answer_supported": True,
        "locator_status": "page_only", "numeric_status": "not_applicable",
        "decision": "accept", "confidence": "high", "rationale": "Checked PDF page 2.",
        "source_quotes_or_paraphrases": ["paper-a PDF p.2: supports the fact"],
        "unresolved_issues": [], "reference_answer_en": "One fact.",
        "reference_answer_zh": "一项事实。", "required_facts": [{
            "fact_id": "f1", "text_en": "One fact", "text_zh": "一项事实",
            "evidence_group_ids": ["g1"], "source_locator": {
                "resource_id": "paper-a", "pdf_page_1based": 2,
                "evidence_paraphrase": "Checked original PDF page 2"
            },
        }], "acceptable_variants": [], "unsupported_claims": [],
        "numeric_constraints": [],
    }


def test_accepted_agent_review_preserves_human_false_and_fact_mapping() -> None:
    row = adjudicate(_source(), _review())
    assert row["annotation_status"] == "agent_reviewed_candidate"
    assert row["human_verified"] is False
    assert row["reference_answer_en"] == "One fact."
    assert row["required_facts"][0]["evidence_group_ids"] == ["g1"]
    assert row["locator_precision"] == "page_only"
    assert row["development_usable"] is True
    assert row["answer_reference_status"] == "agent_candidate"


def test_disputed_review_cannot_be_promoted() -> None:
    review = _review()
    review["unresolved_issues"] = ["numeric conflict"]
    row = adjudicate(_source(), review)
    assert row["annotation_status"] == "agent_disputed"
    assert row["reference_answer_en"] is None
    assert row["required_facts"] == []
    assert row["development_usable"] is True
    assert row["answer_reference_status"] == "unavailable"


def test_unknown_fact_evidence_group_rejected() -> None:
    review = _review()
    review["required_facts"][0]["evidence_group_ids"] = ["g9"]
    with pytest.raises(ValueError, match="unknown evidence group"):
        adjudicate(_source(), review)


def test_fact_locator_pdf_hash_is_bound_to_candidate_source() -> None:
    row = adjudicate(_source(), _review())
    assert row["required_facts"][0]["source_locator"]["source_pdf_sha256"] == "a" * 64
    review = _review()
    review["required_facts"][0]["source_locator"]["source_pdf_sha256"] = "b" * 64
    with pytest.raises(ValueError, match="fact source hash mismatch"):
        adjudicate(_source(), review)


def test_review_top_level_source_hash_must_match_candidate() -> None:
    review = _review()
    review["source_pdf_sha256"] = "b" * 64
    with pytest.raises(ValueError, match="review source hash mismatch"):
        adjudicate(_source(), review)


def test_write_package_refuses_overwrite_and_records_hashes(tmp_path: Path) -> None:
    output = tmp_path / "review-package"
    source = [_source()]
    reviews = [_review()]
    write_package(source, reviews, output, input_hashes={"source": "a" * 64}, reviewer_id="/root/gold_agent_review")
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["reviewer_kind"] == "subagent"
    assert manifest["human_verified"] is False
    assert manifest["development_usable"] is True
    assert manifest["status_counts"] == {"agent_reviewed_candidate": 1}
    assert "annotations.jsonl" in manifest["output_sha256"]
    assert len(manifest["runner_sha256"]) == 64
    assert isinstance(manifest["working_tree_dirty"], bool)
    with pytest.raises(FileExistsError):
        write_package(source, reviews, output, input_hashes={}, reviewer_id="agent")
