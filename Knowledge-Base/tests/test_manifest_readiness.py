"""The readiness artifact must not be mistaken for an import manifest."""

import csv
import hashlib
from pathlib import Path

import pymupdf
import pytest

from ped_knowledge.governance.readiness import (
    ReadinessConflictError,
    _journal_evidence,
    build_readiness,
)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _fixture(root: Path) -> Path:
    knowledge = root / "memPed" / "knowledge"
    records = knowledge / "literature" / "records"
    pdf = knowledge / "batch-1-incoming" / "approved.pdf"
    pdf.parent.mkdir(parents=True)
    with pymupdf.open() as document:
        document.new_page().insert_text((72, 72), "Approved fixture")
        document.save(pdf)
    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    inventory_fields = ["filename", "doi", "sha256", "title", "venue"]
    _write_csv(
        knowledge / "batch-1-incoming" / "batch1_inventory.csv",
        inventory_fields,
        [
            {"filename": "approved.pdf", "doi": "10.1000/approved", "sha256": digest,
             "title": "Approved example", "venue": "Safety Science"},
            {"filename": "held.pdf", "doi": "10.1000/held", "sha256": "0" * 64,
             "title": "Held example", "venue": "Safety Science"},
        ],
    )
    for batch in range(2, 6):
        _write_csv(
            knowledge / f"batch-{batch}-incoming" / f"batch{batch}_inventory.csv",
            inventory_fields, [],
        )
    _write_csv(
        records / "candidates.csv",
        ["resource_id", "doi", "title", "language", "source_url", "venue",
         "publication_status", "primary_topic", "topics"],
        [
            {"resource_id": "lit-approved", "doi": "10.1000/approved",
             "title": "Approved example", "language": "en",
             "source_url": "https://doi.org/10.1000/approved", "venue": "Safety Science",
             "publication_status": "unverified", "primary_topic": "flow_fundamentals",
             "topics": "flow_fundamentals"},
            {"resource_id": "lit-held", "doi": "10.1000/held", "title": "Held example",
             "language": "en", "source_url": "https://doi.org/10.1000/held",
             "venue": "Safety Science", "publication_status": "unverified",
             "primary_topic": "flow_fundamentals", "topics": "flow_fundamentals"},
        ],
    )
    _write_csv(
        records / "screening.csv",
        ["resource_id", "doi", "total_score", "fulltext_screen", "decision",
         "quality_tier"],
        [
            {"resource_id": "lit-approved", "doi": "10.1000/approved",
             "total_score": "66", "fulltext_screen": "pass",
             "decision": "pending_manual_content_review", "quality_tier": ""},
            {"resource_id": "lit-held", "doi": "10.1000/held",
             "total_score": "65", "fulltext_screen": "fail",
             "decision": "temporarily_not_used_content_at_most_65", "quality_tier": ""},
        ],
    )
    _write_csv(
        records / "citation_snapshots.csv",
        ["resource_id", "doi", "citation_count", "citation_source",
         "citation_checked_at"],
        [{"resource_id": "lit-approved", "doi": "10.1000/approved",
          "citation_count": "12", "citation_source": "Web of Science Core Collection",
          "citation_checked_at": "2026-09-23"}],
    )
    _write_csv(
        records / "journal_metrics.csv",
        ["venue", "cas_major_zone", "cas_minor_zone", "jci_quartile",
         "jif_quartile", "jcr_year", "cas_year", "verified_at"],
        [{"venue": "Safety Science", "cas_major_zone": "2", "cas_minor_zone": "",
          "jci_quartile": "Q2", "jif_quartile": "", "jcr_year": "2025",
          "cas_year": "2025", "verified_at": "2026-09-21"}],
    )
    return pdf


def test_build_readiness_excludes_held_papers_and_is_not_importable(tmp_path: Path) -> None:
    _fixture(tmp_path)

    result = build_readiness(tmp_path)

    assert [row["doi"] for row in result.rows] == ["10.1000/approved"]
    assert result.excluded_count == 1
    assert len(result.input_hashes) == 9
    assert "include" not in result.rows[0]
    assert "10.1000/held" not in result.render_csv()
    assert "10.1000/held" not in result.render_report()


def test_build_readiness_preserves_pending_gates_and_pdf_evidence(tmp_path: Path) -> None:
    pdf = _fixture(tmp_path)

    row = build_readiness(tmp_path).rows[0]

    assert row["source_path"] == pdf.relative_to(tmp_path).as_posix()
    assert row["hash_status"] == "match"
    assert row["pdf_status"] == "readable"
    assert row["page_count"] == "1"
    assert row["citation_count"] == "12"
    assert row["citation_source"] == "Web of Science Core Collection"
    assert row["journal_match_status"] == "matched"
    assert row["journal_best_rank"] == "2"
    assert row["integrity_status"] == "pending"
    assert row["rights_status"] == "pending"
    assert row["quality_tier"] == ""
    assert "manual_content_review" in row["blocker_codes"]
    assert "publication_unverified" in row["blocker_codes"]


def test_readiness_report_does_not_treat_governance_flags_as_experiment_gate(tmp_path: Path) -> None:
    _fixture(tmp_path)

    report = build_readiness(tmp_path).render_report()

    assert "不阻断技术预检或明确标记的探索实验" in report


def test_build_readiness_marks_hash_mismatch(tmp_path: Path) -> None:
    _fixture(tmp_path)
    inventory = tmp_path / "memPed/knowledge/batch-1-incoming/batch1_inventory.csv"
    rows = list(csv.DictReader(inventory.open(newline="", encoding="utf-8")))
    rows[0]["sha256"] = "f" * 64
    _write_csv(inventory, list(rows[0]), rows)

    row = build_readiness(tmp_path).rows[0]

    assert row["hash_status"] == "mismatch"
    assert "hash_mismatch" in row["blocker_codes"]


def test_build_readiness_rejects_duplicate_inventory_doi(tmp_path: Path) -> None:
    _fixture(tmp_path)
    inventory = tmp_path / "memPed/knowledge/batch-1-incoming/batch1_inventory.csv"
    rows = list(csv.DictReader(inventory.open(newline="", encoding="utf-8")))
    rows[1]["doi"] = rows[0]["doi"]
    _write_csv(inventory, list(rows[0]), rows)

    with pytest.raises(ReadinessConflictError, match="duplicate inventory DOI") as error:
        build_readiness(tmp_path)

    assert "duplicate inventory DOI" in error.value.render_report()


def test_build_readiness_rejects_missing_candidate(tmp_path: Path) -> None:
    _fixture(tmp_path)
    candidates = tmp_path / "memPed/knowledge/literature/records/candidates.csv"
    rows = list(csv.DictReader(candidates.open(newline="", encoding="utf-8")))
    _write_csv(candidates, list(rows[0]), rows[1:])

    with pytest.raises(ValueError, match="missing candidate DOI 10.1000/approved"):
        build_readiness(tmp_path)


def test_build_readiness_validates_held_candidate_link(tmp_path: Path) -> None:
    _fixture(tmp_path)
    candidates = tmp_path / "memPed/knowledge/literature/records/candidates.csv"
    rows = list(csv.DictReader(candidates.open(newline="", encoding="utf-8")))
    _write_csv(candidates, list(rows[0]), rows[:1])

    with pytest.raises(ValueError, match="missing candidate DOI 10.1000/held"):
        build_readiness(tmp_path)


def test_build_readiness_ignores_candidate_outside_five_inventories(tmp_path: Path) -> None:
    _fixture(tmp_path)
    candidates = tmp_path / "memPed/knowledge/literature/records/candidates.csv"
    rows = list(csv.DictReader(candidates.open(newline="", encoding="utf-8")))
    rows.append({**rows[0], "doi": "10.1000/orphan", "resource_id": "lit-orphan"})
    _write_csv(candidates, list(rows[0]), rows)

    result = build_readiness(tmp_path)

    assert [row["doi"] for row in result.rows] == ["10.1000/approved"]


def test_build_readiness_does_not_credit_wrong_citation_resource(tmp_path: Path) -> None:
    _fixture(tmp_path)
    citations = tmp_path / "memPed/knowledge/literature/records/citation_snapshots.csv"
    rows = list(csv.DictReader(citations.open(newline="", encoding="utf-8")))
    rows[0]["resource_id"] = "lit-other"
    _write_csv(citations, list(rows[0]), rows)

    row = build_readiness(tmp_path).rows[0]

    assert row["citation_count"] == ""
    assert "citation_missing" in row["blocker_codes"]


def test_build_readiness_exposes_missing_citation(tmp_path: Path) -> None:
    _fixture(tmp_path)
    citations = tmp_path / "memPed/knowledge/literature/records/citation_snapshots.csv"
    _write_csv(
        citations,
        ["resource_id", "doi", "citation_count", "citation_source",
         "citation_checked_at"],
        [],
    )

    row = build_readiness(tmp_path).rows[0]

    assert row["citation_count"] == ""
    assert "citation_missing" in row["blocker_codes"]


def test_build_readiness_keeps_pdf_doi_identity_hold(tmp_path: Path) -> None:
    _fixture(tmp_path)
    screening = tmp_path / "memPed/knowledge/literature/records/screening.csv"
    rows = list(csv.DictReader(screening.open(newline="", encoding="utf-8")))
    rows[0]["decision"] = "pending_pdf_doi_identity_review"
    _write_csv(screening, list(rows[0]), rows)

    row = build_readiness(tmp_path).rows[0]

    assert row["manual_review_status"] == "pending"
    assert "pdf_doi_identity_review" in row["blocker_codes"]


@pytest.mark.parametrize(
    ("candidate_venue", "metrics_venue"),
    [
        (
            "Transportation Letters",
            "Transportation Letters-The International Journal of Transportation Research",
        ),
        (
            "Transportation Research Part C: Emerging Technologies",
            "Transportation Research Part C Emerging Technologies",
        ),
        (
            "Physica A Statistical Mechanics and its Applications",
            "Physica A: Statistical Mechanics and its Applications",
        ),
        ("Physica A", "Physica A: Statistical Mechanics and its Applications"),
    ],
)
def test_verified_venue_aliases_match_existing_journal_rows(
    candidate_venue: str, metrics_venue: str
) -> None:
    status, rank = _journal_evidence(
        candidate_venue,
        [{"venue": metrics_venue, "cas_major_zone": "2", "jcr_year": "2025",
          "cas_year": "2025", "verified_at": "2026-09-21"}],
    )

    assert (status, rank) == ("matched", "2")


def test_journal_match_requires_consistent_source_year() -> None:
    status, rank = _journal_evidence(
        "Safety Science",
        [{"venue": "Safety Science", "cas_major_zone": "2", "jcr_year": "2024",
          "cas_year": "2025", "verified_at": "2026-09-21"}],
    )

    assert (status, rank) == ("pending", "")
