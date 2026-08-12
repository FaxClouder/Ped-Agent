"""Stable contracts for selection freezes and Manifest releases."""

from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class GovernanceValidationError(ValueError):
    """Raised when a governed review or release fails closed."""


class PrismaCounts(BaseModel):
    """Machine-checkable PRISMA flow counts."""

    model_config = ConfigDict(extra="forbid")

    records_identified: int = Field(ge=0)
    duplicates_removed: int = Field(ge=0)
    records_screened: int = Field(ge=0)
    records_excluded: int = Field(ge=0)
    reports_sought: int = Field(ge=0)
    reports_not_retrieved: int = Field(ge=0)
    reports_assessed: int = Field(ge=0)
    reports_excluded: int = Field(ge=0)
    reports_included: int = Field(ge=0)
    studies_included: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_conservation(self) -> PrismaCounts:
        equations = (
            (
                self.records_identified,
                self.duplicates_removed + self.records_screened,
                "records_identified = duplicates_removed + records_screened",
            ),
            (
                self.records_screened,
                self.records_excluded + self.reports_sought,
                "records_screened = records_excluded + reports_sought",
            ),
            (
                self.reports_sought,
                self.reports_not_retrieved + self.reports_assessed,
                "reports_sought = reports_not_retrieved + reports_assessed",
            ),
            (
                self.reports_assessed,
                self.reports_excluded + self.reports_included,
                "reports_assessed = reports_excluded + reports_included",
            ),
        )
        failures = [label for actual, expected, label in equations if actual != expected]
        if self.reports_included < self.studies_included:
            failures.append("reports_included >= studies_included")
        if failures:
            raise ValueError("PRISMA count conservation failed: " + "; ".join(failures))
        return self


class ArtifactDigest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class IncludedStudyRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    study_id: str = Field(min_length=1)
    report_id: str = Field(min_length=1)
    resource_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]+$")


class SelectionFreeze(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: int = 1
    review_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]+$")
    status: str = Field(pattern="^approved$")
    approved_by: str = Field(min_length=1)
    created_at: datetime
    prisma_counts: PrismaCounts
    included_studies: tuple[IncludedStudyRecord, ...] = Field(min_length=1)
    artifacts: tuple[ArtifactDigest, ...] = Field(min_length=1)


class ManifestRelease(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: int = 1
    review_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]+$")
    status: str = Field(pattern="^approved$")
    approved_by: str = Field(min_length=1)
    created_at: datetime
    selection_freeze_path: str = Field(min_length=1)
    selection_freeze_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    manifest_path: str = Field(min_length=1)
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    resource_ids: tuple[str, ...] = Field(min_length=1)

    @field_validator("resource_ids")
    @classmethod
    def validate_resource_ids(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if len(values) != len(set(values)):
            raise ValueError("resource_ids must be unique")
        invalid = [value for value in values if not re.fullmatch(r"[a-z0-9][a-z0-9._-]+", value)]
        if invalid:
            raise ValueError("resource_ids contain invalid values")
        return values
