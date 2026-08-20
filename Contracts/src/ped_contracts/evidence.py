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


class EvidenceRunMetrics(BaseModel):
    local_evidence_count: int = 0
    academic_evidence_count: int = 0
    web_evidence_count: int = 0
    external_search_used: bool = False
    retrieval_degraded: bool = False
    citation_rules_passed: bool | None = None
    semantic_verification_passed: bool | None = None
    revision_count: int = 0
    insufficient_evidence: bool = False


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


class AnswerClaim(BaseModel):
    claim_id: str
    text: str
    citation_labels: list[str] = Field(default_factory=list)


class InferenceItem(BaseModel):
    text: str
    basis_evidence_ids: list[str] = Field(default_factory=list)


class VerificationSummary(BaseModel):
    status: Literal["verified", "rules_only", "insufficient_evidence"]
    rules_passed: bool
    semantic_passed: bool | None = None
    repaired: bool = False


class AnswerDocument(BaseModel):
    answer_markdown: str
    citations: list[CitationRef] = Field(default_factory=list)
    inferences: list[InferenceItem] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    verification: VerificationSummary


class AnswerDraft(BaseModel):
    answer_markdown: str
    claims: list[AnswerClaim] = Field(default_factory=list)
    citations: list[CitationRef] = Field(default_factory=list)
    inferences: list[InferenceItem] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class RuleValidation(BaseModel):
    passed: bool
    errors: list[str] = Field(default_factory=list)


class ClaimReview(BaseModel):
    claim_id: str
    status: Literal["supported", "partial", "unsupported"]
    revised_text: str | None = None


class SemanticReview(BaseModel):
    claims: list[ClaimReview] = Field(default_factory=list)


class RetrievalBatch(BaseModel):
    items: list[EvidenceItem] = Field(default_factory=list)
    sufficient: bool = False
    degraded: bool = False
    degradation_reason: str | None = None


class ModelOutput(BaseModel):
    content: str
    model: str
