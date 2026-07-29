from pathlib import Path

import pytest
from pydantic import ValidationError

from ped_agent.models import (
    AdmissionStatus,
    ResourceManifest,
    ResourceType,
    RetrievalEligibility,
)


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
    record = ResourceManifest(
        resource_id="paper-demo-2026",
        resource_type=ResourceType.LITERATURE,
        title="Pedestrian bottleneck experiment",
        language="en",
        source_path=Path("paper.pdf"),
        sha256="1" * 64,
        doi="10.1000/demo",
        include=True,
    )

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
