import hashlib
import json
from datetime import date
from pathlib import Path

import pytest

from ped_agent_server.manifest import ManifestPreflightError, load_and_preflight
from ped_agent_server.vault import ContentVault, sha256_file


def write_manifest(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text("\n".join(json.dumps(item) for item in records) + "\n", encoding="utf-8")


def approved_literature_record(
    source: Path,
    digest: str,
    **overrides: object,
) -> dict[str, object]:
    record: dict[str, object] = {
        "resource_id": "lit-2016-preflight-quality",
        "resource_type": "literature",
        "title": "Preflight quality paper",
        "language": "en",
        "source_path": str(source),
        "sha256": digest,
        "doi": "10.1000/preflight-quality",
        "authors": ["Demo Author"],
        "venue": "Safety Science",
        "published_date": "2016-01-01",
        "publication_status": "version_of_record",
        "integrity_status": "clear",
        "citation_count": 600,
        "citation_source": "web_of_science",
        "citation_checked_at": "2026-07-01",
        "jci_value": 1.8,
        "jci_quartile": "Q1",
        "jci_year": 2025,
        "jci_source": "clarivate_jcr",
        "cas_zone": 1,
        "cas_category": "Engineering",
        "cas_year": 2025,
        "cas_source": "cas_journal_partition",
        "metrics_checked_at": "2026-07-01",
        "quality_tier": "A",
        "content_quality_score": 90,
        "primary_topic": "safety_risk_intervention",
        "topics": ["safety_risk_intervention"],
        "include": True,
    }
    record.update(overrides)
    return record


def test_preflight_rejects_hash_mismatch_without_creating_storage(tmp_path: Path) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-demo")
    manifest = tmp_path / "manifest.jsonl"
    write_manifest(
        manifest,
        [
            approved_literature_record(
                source,
                "0" * 64,
                resource_id="paper-preflight-2026",
                title="Preflight paper",
                doi="10.1000/preflight",
            )
        ],
    )

    with pytest.raises(ManifestPreflightError, match="SHA-256 mismatch"):
        load_and_preflight(manifest)

    assert not (tmp_path / "storage").exists()


def test_preflight_accepts_matching_hash(tmp_path: Path) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-demo")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest = tmp_path / "manifest.jsonl"
    write_manifest(
        manifest,
        [
            approved_literature_record(
                source,
                digest,
                resource_id="paper-preflight-2026",
                title="Preflight paper",
                doi="10.1000/preflight",
            )
        ],
    )

    assert load_and_preflight(manifest)[0].resource_id == "paper-preflight-2026"


def test_preflight_reports_duplicate_ids_and_missing_files(tmp_path: Path) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-demo")
    digest = sha256_file(source)
    base = approved_literature_record(
        source,
        digest,
        resource_id="paper-duplicate-2026",
        title="Duplicate paper",
        doi="10.1000/duplicate",
    )
    manifest = tmp_path / "manifest.jsonl"
    write_manifest(
        manifest,
        [
            base,
            base,
            {
                **base,
                "resource_id": "paper-missing-2026",
                "source_path": str(tmp_path / "missing.pdf"),
            },
        ],
    )

    with pytest.raises(ManifestPreflightError) as error:
        load_and_preflight(manifest)

    assert "duplicate resource_id paper-duplicate-2026" in str(error.value)
    assert "missing file" in str(error.value)


def test_content_vault_is_content_addressed_and_idempotent(tmp_path: Path) -> None:
    source = tmp_path / "paper.PDF"
    source.write_bytes(b"%PDF-vault")
    digest = sha256_file(source)
    vault = ContentVault(tmp_path / "objects")

    first = vault.put(source, digest)
    second = vault.put(source, digest)

    assert first == tmp_path / "objects" / digest[:2] / f"{digest}.pdf"
    assert second == first
    assert first.read_bytes() == source.read_bytes()


def test_preflight_rejects_duplicate_doi_and_file_hash(tmp_path: Path) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-quality")
    digest = sha256_file(source)
    first = approved_literature_record(source, digest)
    second = approved_literature_record(
        source,
        digest,
        resource_id="lit-2016-preflight-duplicate",
    )
    manifest = tmp_path / "duplicates.jsonl"
    write_manifest(manifest, [first, second])

    with pytest.raises(ManifestPreflightError) as error:
        load_and_preflight(manifest, as_of=date(2026, 7, 29))

    assert "duplicate DOI 10.1000/preflight-quality" in str(error.value)
    assert f"duplicate SHA-256 {digest}" in str(error.value)


def test_preflight_rejects_stale_quality_snapshots(tmp_path: Path) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-quality")
    digest = sha256_file(source)
    manifest = tmp_path / "stale.jsonl"
    write_manifest(
        manifest,
        [
            approved_literature_record(
                source,
                digest,
                citation_checked_at="2025-01-01",
                jci_year=2024,
                cas_year=2024,
            )
        ],
    )

    with pytest.raises(ManifestPreflightError) as error:
        load_and_preflight(manifest, as_of=date(2026, 7, 29))

    message = str(error.value)
    assert "citation snapshot is older than 90 days" in message
    assert "JCI snapshot is older than 12 months" in message
    assert "CAS snapshot is older than 12 months" in message


def test_preflight_rejects_stale_journal_metric_verification(tmp_path: Path) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-quality")
    digest = sha256_file(source)
    manifest = tmp_path / "stale-metric-verification.jsonl"
    write_manifest(
        manifest,
        [
            approved_literature_record(
                source,
                digest,
                metrics_checked_at="2025-07-28",
            )
        ],
    )

    with pytest.raises(
        ManifestPreflightError,
        match="journal metric snapshot is older than 12 months",
    ):
        load_and_preflight(manifest, as_of=date(2026, 7, 29))


def test_preflight_rejects_old_a_tier_without_high_citations(tmp_path: Path) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-quality")
    digest = sha256_file(source)
    manifest = tmp_path / "low-citation.jsonl"
    write_manifest(
        manifest,
        [approved_literature_record(source, digest, citation_count=499)],
    )

    with pytest.raises(ManifestPreflightError, match="age-adjusted citation threshold"):
        load_and_preflight(manifest, as_of=date(2026, 7, 29))


def test_preflight_rejects_non_a_literature_published_within_18_months(
    tmp_path: Path,
) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-quality")
    digest = sha256_file(source)
    manifest = tmp_path / "too-recent-b-tier.jsonl"
    write_manifest(
        manifest,
        [
            approved_literature_record(
                source,
                digest,
                published_date="2025-06-01",
                quality_tier="B",
                cas_zone=2,
                jci_value=1.2,
                jci_quartile="Q2",
            )
        ],
    )

    with pytest.raises(ManifestPreflightError, match="must be A-tier"):
        load_and_preflight(manifest, as_of=date(2026, 7, 29))
