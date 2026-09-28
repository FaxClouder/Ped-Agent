"""Offline approval records that bind governance decisions to source bytes."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ApprovalRecord(BaseModel):
    """A review decision for one exact source asset."""

    model_config = ConfigDict(extra="forbid")

    approval_id: str = Field(min_length=1)
    resource_id: str = Field(min_length=1)
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    decision: str = Field(pattern=r"^(approved|rejected|withdrawn|unknown)$")
    rules_version: str = Field(min_length=1)
    reviewer: str = Field(min_length=1)
    reviewed_at: date
    reason: str = Field(min_length=1)


def validate_approval(
    record: ApprovalRecord,
    *,
    resource_id: str,
    source_sha256: str,
) -> bool:
    """Return whether a record authorizes this exact source for formal use."""

    return (
        record.decision == "approved"
        and record.resource_id == resource_id
        and record.source_sha256 == source_sha256
    )


__all__ = ["ApprovalRecord", "validate_approval"]
