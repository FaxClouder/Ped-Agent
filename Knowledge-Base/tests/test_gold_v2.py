"""Reference cases for versioned Gold v2 evidence and refusal scoring."""

from __future__ import annotations

import pytest

from ped_knowledge.evaluation.gold_v2 import (
    score_answerable,
    score_refusal,
    summarize_paired,
)


def _alt(resource: str, version: str, page: int, element: str | None = None) -> dict:
    return {
        "resource_id": resource,
        "source_pdf_sha256": version,
        "locator": {"page_index": page, "element_id": element},
    }


def _hit(resource: str, version: str, page: int, elements: tuple[str, ...] = ()) -> dict:
    return {
        "resource_id": resource,
        "version_id": version,
        "page_start": page + 1,
        "page_end": page + 1,
        "element_ids": elements,
    }


def test_answerable_requires_each_group_but_accepts_an_alternative() -> None:
    evidence = {
        "evidence_groups": [
            {"alternatives": [_alt("a", "va", 0), _alt("a2", "va2", 1)]},
            {"alternatives": [_alt("b", "vb", 2, "table-1")]},
        ]
    }
    result = score_answerable(
        evidence,
        [_hit("a2", "va2", 1), _hit("b", "vb", 2, ("table-1",))],
        k=5,
    )
    assert result["resource_hit_at_5"] == 1.0
    assert result["resource_recall_at_5"] == 1.0
    assert result["complete_evidence_at_5"] == 1.0
    assert result["complete_locator_at_5"] == 1.0
    assert result["ndcg_at_5"] == pytest.approx(1.0)


def test_exact_locator_rejects_wrong_version_page_and_element() -> None:
    evidence = {"evidence_groups": [{"alternatives": [_alt("a", "va", 2, "fig-1")]}]}
    for hit in (
        _hit("a", "old", 2, ("fig-1",)),
        _hit("a", "va", 1, ("fig-1",)),
        _hit("a", "va", 2, ("fig-2",)),
    ):
        result = score_answerable(evidence, [hit], k=5)
        assert result["resource_hit_at_5"] == 1.0
        assert result["complete_locator_at_5"] == 0.0


def test_duplicate_chunks_cannot_inflate_resource_metrics() -> None:
    evidence = {"evidence_groups": [{"alternatives": [_alt("a", "va", 0)]}]}
    result = score_answerable(evidence, [_hit("a", "va", 0)] * 5, k=5)
    assert result["resource_recall_at_5"] == 1.0
    assert result["ndcg_at_5"] == pytest.approx(1.0)


def test_later_chunk_of_selected_resource_can_match_exact_locator() -> None:
    evidence = {"evidence_groups": [{"alternatives": [_alt("a", "va", 1)]}]}
    result = score_answerable(evidence, [_hit("a", "va", 0), _hit("a", "va", 1)], k=5)
    assert result["resource_hit_at_5"] == 1.0
    assert result["complete_locator_at_5"] == 1.0


def test_one_resource_can_cover_two_required_groups_without_ndcg_penalty() -> None:
    evidence = {"evidence_groups": [
        {"alternatives": [_alt("a", "va", 0)]},
        {"alternatives": [_alt("a", "va", 1)]},
    ]}
    result = score_answerable(evidence, [_hit("a", "va", 0)], k=5)
    assert result["complete_evidence_at_5"] == 1.0
    assert result["ndcg_at_5"] == pytest.approx(1.0)


def test_refusal_is_scored_only_with_verified_absence() -> None:
    with pytest.raises(ValueError, match="verified absence"):
        score_refusal(label_status="candidate", refused=True)
    assert score_refusal(label_status="verified_absent", refused=True) == {"correct_refusal": 1.0}
    assert score_refusal(label_status="verified_absent", refused=False) == {"correct_refusal": 0.0}
    assert score_refusal(label_status="verified_answerable", refused=True) == {"false_refusal": 1.0}
    assert score_refusal(label_status="verified_answerable", refused=False) == {"false_refusal": 0.0}


def test_paired_summary_requires_both_languages() -> None:
    rows = [
        {"intent_id": "i1", "language": "en", "metrics": {"resource_hit_at_5": 1.0}},
        {"intent_id": "i1", "language": "zh", "metrics": {"resource_hit_at_5": 0.0}},
    ]
    assert summarize_paired(rows)["zh_minus_en"]["resource_hit_at_5"] == -1.0
    with pytest.raises(ValueError, match="paired"):
        summarize_paired(rows[:1])
