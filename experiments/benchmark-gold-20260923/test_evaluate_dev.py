"""Fixed reference cases for the candidate Gold v2 development scorer."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from evaluate_dev import _chunk_ranking, _serialize_chunk_ranking, candidate_paths, paired_differences, score_question


def test_candidate_version_selects_matching_assets():
    for version in ("v2", "v3", "v4", "v5"):
        paths = candidate_paths(version)
        assert all(path.name.endswith(f"_{version}.jsonl") for path in paths[:2])
        assert paths[2].name == f"full_candidate_manifest_{version}.json"


def test_two_source_evidence_requires_both_groups_and_exact_pages():
    evidence = {
        "evidence_groups": [
            {"alternatives": [{"resource_id": "a", "source_pdf_sha256": "aa", "locator": {"page_index": 0, "element_id": None}}]},
            {"alternatives": [{"resource_id": "b", "source_pdf_sha256": "bb", "locator": {"page_index": 3, "element_id": None}}]},
        ]
    }
    rankings = [
        {"chunk_id": "a1", "resource_id": "a", "version_id": "aa", "page_start": 1, "page_end": 1, "element_ids": ()},
        {"chunk_id": "b1", "resource_id": "b", "version_id": "bb", "page_start": 2, "page_end": 2, "element_ids": ()},
    ]
    result = score_question(evidence, rankings, k=5)
    assert result["resource_hit_at_5"] == 1.0
    assert result["resource_recall_at_5"] == 1.0
    assert result["complete_evidence_at_5"] == 1.0
    assert result["exact_locator_group_recall_at_5"] == 0.5
    assert result["complete_locator_at_5"] == 0.0

    result = score_question(evidence, rankings[:1], k=5)
    assert result["resource_recall_at_5"] == 0.5
    assert result["complete_evidence_at_5"] == 0.0


def test_paired_difference_uses_intents_as_units():
    rows = [
        {"method": "bm25", "intent_id": "i1", "language": "en", "metrics": {"resource_hit_at_5": 1.0}},
        {"method": "bm25", "intent_id": "i1", "language": "zh", "metrics": {"resource_hit_at_5": 0.0}},
        {"method": "bm25", "intent_id": "i2", "language": "en", "metrics": {"resource_hit_at_5": 0.0}},
        {"method": "bm25", "intent_id": "i2", "language": "zh", "metrics": {"resource_hit_at_5": 0.0}},
    ]
    assert paired_differences(rows)["bm25"]["resource_hit_at_5"] == -0.5


def test_alternative_sources_count_as_one_required_group():
    evidence = {
        "evidence_groups": [
            {"alternatives": [
                {"resource_id": "a", "source_pdf_sha256": "aa", "locator": {"page_index": 0, "element_id": None}},
                {"resource_id": "a2", "source_pdf_sha256": "a2a2", "locator": {"page_index": 0, "element_id": None}},
            ]},
            {"alternatives": [
                {"resource_id": "b", "source_pdf_sha256": "bb", "locator": {"page_index": 1, "element_id": None}},
            ]},
        ]
    }
    ranking = [
        {"resource_id": "a2", "version_id": "a2a2", "page_start": 1, "page_end": 1, "element_ids": ()},
        {"resource_id": "b", "version_id": "bb", "page_start": 2, "page_end": 2, "element_ids": ()},
    ]
    result = score_question(evidence, ranking, k=5)
    assert result["resource_recall_at_5"] == 1.0
    assert result["ndcg_at_5"] == 1.0


def test_chunk_ranking_preserves_later_chunks_for_locator_scoring():
    from ped_knowledge.contracts import IndexHit

    chunks = {
        "first": {"chunk_id": "first", "resource_id": "a", "version_id": "aa", "page_start": 1, "page_end": 1, "element_ids": ()},
        "second": {"chunk_id": "second", "resource_id": "a", "version_id": "aa", "page_start": 2, "page_end": 2, "element_ids": ()},
    }
    hits = [IndexHit(chunk_id="first", score=2.0), IndexHit(chunk_id="second", score=1.0)]
    ranking = _chunk_ranking(hits, chunks)
    assert [row["chunk_id"] for row in ranking] == ["first", "second"]
    assert _serialize_chunk_ranking(ranking)[1] == {
        "rank": 2,
        "chunk_id": "second",
        "resource_id": "a",
        "version_id": "aa",
        "page_start": 2,
        "page_end": 2,
        "element_ids": [],
    }
