"""Check the current offline screening decision against its score boundary."""

import csv
from pathlib import Path


SCREENING = (
    Path(__file__).resolve().parents[2]
    / "memPed/knowledge/literature/records/screening.csv"
)
CANDIDATES = (
    Path(__file__).resolve().parents[2]
    / "memPed/knowledge/literature/records/candidates.csv"
)
PARTS = (
    "relevance_score",
    "method_score",
    "rag_evidence_score",
    "coverage_score",
    "traceability_score",
)


def test_content_score_threshold_reclassification() -> None:
    with SCREENING.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    # The two PyMuPDF sources were removed on 2026-10-08.
    assert len(rows) == 106
    assert len({row["doi"].casefold() for row in rows}) == 106
    assert all(row["doi"] for row in rows)
    assert sum(int(row["total_score"]) > 65 for row in rows) == 102
    for row in rows:
        score = int(row["total_score"])
        assert sum(int(row[name]) for name in PARTS) == score
        assert row["fulltext_screen"] == ("pass" if score > 65 else "fail")
        assert "below_80" not in row["decision"]
        if score <= 65:
            assert row["decision"] == "temporarily_not_used_content_at_most_65"
            assert not row["quality_tier"]


def test_below_threshold_candidates_are_temporarily_not_used() -> None:
    with SCREENING.open(newline="", encoding="utf-8-sig") as stream:
        screening = list(csv.DictReader(stream))
    with CANDIDATES.open(newline="", encoding="utf-8-sig") as stream:
        candidates = list(csv.DictReader(stream))
    by_doi = {row["doi"].casefold(): row for row in candidates}
    held = [row for row in screening if int(row["total_score"]) <= 65]
    assert len(held) == 4
    for row in held:
        candidate = by_doi[row["doi"].casefold()]
        assert candidate["screening_status"] == "temporarily_not_used"
        assert "content score" in candidate["notes"].lower()
