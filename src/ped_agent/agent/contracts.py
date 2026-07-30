from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    INTERRUPTED = "interrupted"


class EvidenceOrigin(StrEnum):
    LOCAL_OFFICIAL = "local_official"
    EXTERNAL_ACADEMIC = "external_academic"
    EXTERNAL_WEB = "external_web"


class EvidenceItem(BaseModel):
    evidence_id: str
    origin: EvidenceOrigin
    title: str
    quote: str
    locator: str | None = None
    url: str | None = None
    doi: str | None = None
    document_number: str | None = None
    resource_id: str | None = None
    version_id: str | None = None
    chunk_id: str | None = None
    publisher: str | None = None
    authority: Literal["official", "primary", "secondary"] = "primary"
    retrieved_at: datetime
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    score: float = 0.0


class CitationRef(BaseModel):
    label: str
    evidence_id: str
    claim_ids: list[str] = Field(default_factory=list)


class InferenceItem(BaseModel):
    text: str
    basis_evidence_ids: list[str] = Field(default_factory=list)


class VerificationSummary(BaseModel):
    status: Literal["verified", "rules_only"]
    rules_passed: bool
    semantic_passed: bool | None = None
    repaired: bool = False


class AnswerDocument(BaseModel):
    answer_markdown: str
    citations: list[CitationRef] = Field(default_factory=list)
    inferences: list[InferenceItem] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    verification: VerificationSummary


class ModelOutput(BaseModel):
    content: str
    model: str
