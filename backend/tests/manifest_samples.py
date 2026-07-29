from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from ped_agent.models import ResourceManifest


def literature_data(
    *,
    resource_id: str,
    source_path: Path,
    sha256: str,
    doi: str,
    title: str = "High-quality pedestrian-flow paper",
    topic: str = "flow_fundamentals",
    include: bool = True,
    **overrides: object,
) -> dict[str, object]:
    checked_at = datetime.now(UTC).date()
    payload: dict[str, object] = {
        "resource_id": resource_id,
        "resource_type": "literature",
        "title": title,
        "language": "en",
        "source_path": source_path,
        "sha256": sha256,
        "doi": doi,
        "authors": ["Demo Author"],
        "venue": "Safety Science",
        "published_date": "2016-01-01",
        "publication_status": "version_of_record",
        "integrity_status": "clear",
        "citation_count": 600,
        "citation_source": "web_of_science",
        "citation_checked_at": checked_at.isoformat(),
        "jci_value": 1.8,
        "jci_quartile": "Q1",
        "jci_year": checked_at.year,
        "jci_source": "clarivate_jcr",
        "cas_zone": 1,
        "cas_category": "Engineering",
        "cas_year": checked_at.year,
        "cas_source": "cas_journal_partition",
        "metrics_checked_at": checked_at.isoformat(),
        "quality_tier": "A",
        "content_quality_score": 90,
        "primary_topic": topic,
        "topics": [topic],
        "include": include,
    }
    payload.update(overrides)
    return payload


def literature_manifest(**kwargs: object) -> ResourceManifest:
    return ResourceManifest.model_validate(literature_data(**kwargs))


def regulation_manifest(
    *,
    resource_id: str,
    source_path: Path,
    sha256: str,
    title: str = "Official evacuation regulation",
    topic: str = "building_fire_evacuation",
    **overrides: object,
) -> ResourceManifest:
    payload: dict[str, object] = {
        "resource_id": resource_id,
        "resource_type": "regulation",
        "title": title,
        "language": "zh-CN",
        "source_path": source_path,
        "sha256": sha256,
        "source_url": "https://example.org/official-regulation",
        "document_number": "GB-DEMO-2026",
        "jurisdiction": "CN",
        "issuing_body": "Demo authority",
        "effective_status": "current",
        "published_date": "2026-01-01",
        "effective_date": "2026-07-01",
        "legal_level": "national_standard",
        "accessed_date": "2026-07-29",
        "source_verified_by": "regulation-reviewer",
        "primary_topic": topic,
        "topics": [topic],
        "include": True,
    }
    payload.update(overrides)
    return ResourceManifest.model_validate(payload)
