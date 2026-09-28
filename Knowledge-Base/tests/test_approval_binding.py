from __future__ import annotations

from datetime import date

import pytest

from ped_knowledge.governance.approvals import ApprovalRecord, validate_approval


def approval(**overrides: object) -> ApprovalRecord:
    payload: dict[str, object] = {
        "approval_id": "approval-001",
        "resource_id": "paper-001",
        "source_sha256": "a" * 64,
        "decision": "approved",
        "rules_version": "literature-quality-v2",
        "reviewer": "researcher",
        "reviewed_at": date(2026, 9, 22),
        "reason": "Meets the current offline selection policy.",
    }
    payload.update(overrides)
    return ApprovalRecord.model_validate(payload)


def test_validate_approval_requires_resource_and_source_hash_match() -> None:
    record = approval()

    assert validate_approval(record, resource_id="paper-001", source_sha256="a" * 64)
    assert not validate_approval(record, resource_id="other", source_sha256="a" * 64)
    assert not validate_approval(record, resource_id="paper-001", source_sha256="b" * 64)


def test_non_approved_decisions_are_not_eligible() -> None:
    record = approval(decision="withdrawn")

    assert not validate_approval(record, resource_id="paper-001", source_sha256="a" * 64)


def test_approval_record_rejects_invalid_hash() -> None:
    with pytest.raises(ValueError):
        approval(source_sha256="not-a-sha")
