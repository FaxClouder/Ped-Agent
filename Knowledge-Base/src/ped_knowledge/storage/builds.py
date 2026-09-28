"""Immutable lifecycle records for parse, chunk, and index builds."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BuildStatus(StrEnum):
    STAGED = "staged"
    COMPLETE = "complete"
    FAILED = "failed"


class BuildManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    build_id: str = Field(min_length=1)
    kind: str = Field(pattern=r"^(parse|chunk|index)$")
    inputs: dict[str, str] = Field(min_length=1)
    artifacts: dict[str, str] = Field(min_length=1)
    status: BuildStatus = BuildStatus.STAGED
    failure_reason: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("inputs")
    @classmethod
    def validate_inputs(cls, values: dict[str, str]) -> dict[str, str]:
        if not values or any(not value.strip() for value in values.values()):
            raise ValueError("build inputs must be non-empty")
        return values

    @field_validator("artifacts")
    @classmethod
    def validate_artifacts(cls, values: dict[str, str]) -> dict[str, str]:
        if not values or any(
            len(value) != 64 or any(c not in "0123456789abcdef" for c in value)
            for value in values.values()
        ):
            raise ValueError("build artifact fingerprints must be lowercase SHA-256 values")
        return values

    def complete(self) -> BuildManifest:
        if self.status is BuildStatus.FAILED:
            raise ValueError("failed build cannot be completed")
        return self.model_copy(update={"status": BuildStatus.COMPLETE})

    def fail(self, reason: str) -> BuildManifest:
        if not reason.strip():
            raise ValueError("failure reason must not be empty")
        return self.model_copy(
            update={"status": BuildStatus.FAILED, "failure_reason": reason},
        )


__all__ = ["BuildManifest", "BuildStatus"]
