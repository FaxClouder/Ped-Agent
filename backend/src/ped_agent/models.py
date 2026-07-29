from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class ResourceType(StrEnum):
    LITERATURE = "literature"
    REGULATION = "regulation"
    STANDARD = "standard"


class AdmissionStatus(StrEnum):
    CANDIDATE = "candidate"
    METADATA_VERIFIED = "metadata_verified"
    CONTENT_VERIFIED = "content_verified"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    WITHDRAWN = "withdrawn"


class RetrievalEligibility(StrEnum):
    EXCLUDED = "excluded"
    STAGING = "staging"
    OFFICIAL = "official"


class ResourceManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resource_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]+$")
    resource_type: ResourceType
    title: str = Field(min_length=3)
    language: str = Field(min_length=2)
    source_path: Path
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_url: HttpUrl | None = None
    doi: str | None = None
    document_number: str | None = None
    jurisdiction: str | None = None
    issuing_body: str | None = None
    effective_status: str | None = None
    published_date: str | None = None
    effective_date: str | None = None
    venue: str | None = None
    evidence_type: str | None = None
    methods: list[str] = Field(default_factory=list)
    scenarios: list[str] = Field(default_factory=list)
    applicable_scope: str | None = None
    legal_level: str | None = None
    accessed_date: str | None = None
    supersedes: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    datasets: list[str] = Field(default_factory=list)
    include: bool = False

    @model_validator(mode="after")
    def validate_domain_fields(self) -> ResourceManifest:
        if self.resource_type in {ResourceType.REGULATION, ResourceType.STANDARD}:
            if not all(
                (
                    self.document_number,
                    self.jurisdiction,
                    self.issuing_body,
                    self.effective_status,
                    self.published_date,
                    self.effective_date,
                    self.legal_level,
                )
            ):
                raise ValueError(
                    "regulations and standards require identity, jurisdiction, issuing body, "
                    "dates, legal level, and effective status"
                )
            if self.include and self.effective_status != "current":
                raise ValueError("official regulations require current effective_status")
        if self.resource_type is ResourceType.LITERATURE and not self.doi and not self.source_url:
            raise ValueError("literature requires a DOI or stable source URL")
        return self

    @property
    def admission_status(self) -> AdmissionStatus:
        return AdmissionStatus.APPROVED if self.include else AdmissionStatus.CANDIDATE

    @property
    def retrieval_eligibility(self) -> RetrievalEligibility:
        return RetrievalEligibility.OFFICIAL if self.include else RetrievalEligibility.EXCLUDED


class CanonicalChunk(BaseModel):
    chunk_id: str
    resource_id: str
    version_id: str
    ordinal: int
    text: str = Field(min_length=1)
    page_start: int
    page_end: int
    locator: str
    section: str | None = None
    parser_version: str


class EvidenceHit(BaseModel):
    resource_id: str
    version_id: str
    chunk_id: str
    title: str
    resource_type: ResourceType
    text: str
    locator: str
    source_url: str | None
    doi: str | None
    document_number: str | None
    jurisdiction: str | None
    effective_status: str | None
    score: float
