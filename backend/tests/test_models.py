from pathlib import Path

import pytest
from pydantic import ValidationError

from ped_agent.models import (
    AdmissionStatus,
    ResourceManifest,
    ResourceType,
    RetrievalEligibility,
)


def high_quality_literature_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "resource_id": "lit-2020-demo-quality",
        "resource_type": ResourceType.LITERATURE,
        "title": "High-quality pedestrian-flow evidence",
        "language": "en",
        "source_path": Path("paper.pdf"),
        "sha256": "1" * 64,
        "doi": "10.1000/high-quality",
        "authors": ["Demo Author"],
        "venue": "Transportation Research Part C",
        "published_date": "2020-01-01",
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
        "cas_category": "Transportation Science & Technology",
        "cas_year": 2025,
        "cas_source": "cas_journal_partition",
        "metrics_checked_at": "2026-07-01",
        "quality_tier": "A",
        "content_quality_score": 90,
        "primary_topic": "flow_fundamentals",
        "topics": ["flow_fundamentals"],
        "include": True,
    }
    payload.update(overrides)
    return payload


def test_regulation_requires_document_number_and_jurisdiction() -> None:
    with pytest.raises(ValidationError):
        ResourceManifest(
            resource_id="reg-cn-missing",
            resource_type=ResourceType.REGULATION,
            title="Missing fields",
            language="zh-CN",
            source_path=Path("missing.pdf"),
            sha256="0" * 64,
        )


def test_included_manifest_maps_to_approved_official() -> None:
    record = ResourceManifest.model_validate(high_quality_literature_payload())

    assert record.admission_status is AdmissionStatus.APPROVED
    assert record.retrieval_eligibility is RetrievalEligibility.OFFICIAL


def test_inactive_regulation_cannot_enter_official_retrieval() -> None:
    with pytest.raises(ValidationError, match="current effective_status"):
        ResourceManifest(
            resource_id="reg-expired-2026",
            resource_type=ResourceType.REGULATION,
            title="Expired regulation",
            language="zh-CN",
            source_path=Path("expired.pdf"),
            sha256="2" * 64,
            document_number="GB-DEMO-OLD",
            jurisdiction="CN",
            issuing_body="Demo authority",
            effective_status="superseded",
            published_date="2020-01-01",
            effective_date="2020-06-01",
            legal_level="national_standard",
            include=True,
        )


def test_approved_literature_requires_quality_evidence() -> None:
    with pytest.raises(ValidationError, match="approved literature requires quality evidence"):
        ResourceManifest(
            resource_id="lit-2026-missing-quality",
            resource_type=ResourceType.LITERATURE,
            title="Missing quality evidence",
            language="en",
            source_path=Path("paper.pdf"),
            sha256="3" * 64,
            doi="10.1000/missing-quality",
            include=True,
        )


def test_a_tier_formal_literature_enters_official_retrieval() -> None:
    record = ResourceManifest.model_validate(high_quality_literature_payload())

    assert record.admission_status is AdmissionStatus.APPROVED
    assert record.retrieval_eligibility is RetrievalEligibility.OFFICIAL


def test_preprint_cannot_enter_official_retrieval() -> None:
    with pytest.raises(ValidationError, match="formal publication_status"):
        ResourceManifest.model_validate(
            high_quality_literature_payload(publication_status="preprint")
        )


def test_exception_tier_requires_reason_and_approver() -> None:
    with pytest.raises(ValidationError, match="X-tier literature requires"):
        ResourceManifest.model_validate(
            high_quality_literature_payload(
                quality_tier="X",
                cas_zone=3,
                jci_value=0.8,
                exception_reason=None,
                approved_by=None,
            )
        )


def test_retracted_literature_is_withdrawn_and_excluded() -> None:
    record = ResourceManifest.model_validate(
        high_quality_literature_payload(
            integrity_status="retracted",
            include=False,
        )
    )

    assert record.admission_status is AdmissionStatus.WITHDRAWN
    assert record.retrieval_eligibility is RetrievalEligibility.EXCLUDED


def test_official_regulation_requires_source_and_controlled_topic() -> None:
    payload = {
        "resource_id": "reg-cn-quality-2026",
        "resource_type": ResourceType.REGULATION,
        "title": "Official regulation",
        "language": "zh-CN",
        "source_path": Path("regulation.pdf"),
        "sha256": "4" * 64,
        "document_number": "GB-DEMO-2026",
        "jurisdiction": "CN",
        "issuing_body": "Demo authority",
        "effective_status": "current",
        "published_date": "2026-01-01",
        "effective_date": "2026-07-01",
        "legal_level": "national_standard",
        "primary_topic": "building_fire_evacuation",
        "topics": ["building_fire_evacuation"],
        "include": True,
    }

    with pytest.raises(ValidationError, match="issuing-body source_url"):
        ResourceManifest.model_validate(payload)

    payload["source_url"] = "https://example.org/regulation"
    payload["accessed_date"] = "2026-07-29"
    payload["source_verified_by"] = "regulation-reviewer"
    payload["primary_topic"] = "unsupported_topic"
    payload["topics"] = ["unsupported_topic"]
    with pytest.raises(ValidationError, match="controlled regulation topics"):
        ResourceManifest.model_validate(payload)


def test_official_regulation_requires_source_verification_record() -> None:
    payload = {
        "resource_id": "reg-cn-source-check-2026",
        "resource_type": ResourceType.REGULATION,
        "title": "Source-checked regulation",
        "language": "zh-CN",
        "source_path": Path("regulation.pdf"),
        "sha256": "5" * 64,
        "source_url": "https://example.org/regulation",
        "document_number": "GB-DEMO-CHECK-2026",
        "jurisdiction": "CN",
        "issuing_body": "Demo authority",
        "effective_status": "current",
        "published_date": "2026-01-01",
        "effective_date": "2026-07-01",
        "legal_level": "national_standard",
        "primary_topic": "building_fire_evacuation",
        "topics": ["building_fire_evacuation"],
        "include": True,
    }

    with pytest.raises(ValidationError, match="source verification record"):
        ResourceManifest.model_validate(payload)
