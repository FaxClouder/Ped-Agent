from __future__ import annotations

from datetime import date
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


class PublicationStatus(StrEnum):
    VERSION_OF_RECORD = "version_of_record"
    EARLY_ACCESS = "early_access"
    PREPRINT = "preprint"
    THESIS = "thesis"
    CONFERENCE_ABSTRACT = "conference_abstract"
    OTHER = "other"


class IntegrityStatus(StrEnum):
    CLEAR = "clear"
    EXPRESSION_OF_CONCERN = "expression_of_concern"
    RETRACTED = "retracted"
    UNKNOWN = "unknown"


class CitationSource(StrEnum):
    WEB_OF_SCIENCE = "web_of_science"
    SCOPUS = "scopus"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    OPENALEX = "openalex"


class JournalQuartile(StrEnum):
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"


class QualityTier(StrEnum):
    A = "A"
    B = "B"
    EXCEPTION = "X"


FORMAL_PUBLICATION_STATUSES = {
    PublicationStatus.VERSION_OF_RECORD,
    PublicationStatus.EARLY_ACCESS,
}

LITERATURE_TOPICS = {
    "flow_fundamentals",
    "experiment_measurement",
    "facility_scenario_flow",
    "evacuation_behavior_modeling",
    "safety_risk_intervention",
}

REGULATION_TOPICS = {
    "building_fire_evacuation",
    "transport_public_space",
    "emergency_large_events",
    "accessibility_pedestrian_facilities",
    "international_comparison",
}


def normalize_doi(doi: str | None) -> str | None:
    if doi is None:
        return None
    normalized = doi.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        normalized = normalized.removeprefix(prefix)
    return normalized or None


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
    authors: list[str] = Field(default_factory=list)
    document_number: str | None = None
    jurisdiction: str | None = None
    issuing_body: str | None = None
    effective_status: str | None = None
    published_date: date | None = None
    effective_date: date | None = None
    venue: str | None = None
    evidence_type: str | None = None
    methods: list[str] = Field(default_factory=list)
    scenarios: list[str] = Field(default_factory=list)
    applicable_scope: str | None = None
    legal_level: str | None = None
    accessed_date: date | None = None
    source_verified_by: str | None = None
    supersedes: list[str] = Field(default_factory=list)
    primary_topic: str | None = None
    topics: list[str] = Field(default_factory=list)
    datasets: list[str] = Field(default_factory=list)
    publication_status: PublicationStatus | None = None
    integrity_status: IntegrityStatus | None = None
    citation_count: int | None = Field(default=None, ge=0)
    citation_source: CitationSource | None = None
    citation_checked_at: date | None = None
    jci_value: float | None = Field(default=None, ge=0)
    jci_quartile: JournalQuartile | None = None
    jci_year: int | None = Field(default=None, ge=2000)
    jci_source: str | None = None
    cas_zone: int | None = Field(default=None, ge=1, le=4)
    cas_category: str | None = None
    cas_year: int | None = Field(default=None, ge=2000)
    cas_source: str | None = None
    metrics_checked_at: date | None = None
    quality_tier: QualityTier | None = None
    content_quality_score: int | None = Field(default=None, ge=0, le=100)
    exception_reason: str | None = None
    approved_by: str | None = None
    admission_status: AdmissionStatus | None = None
    include: bool = False

    @model_validator(mode="after")
    def validate_domain_fields(self) -> ResourceManifest:
        self._normalize_admission_status()
        if self.resource_type in {ResourceType.REGULATION, ResourceType.STANDARD}:
            self._validate_regulation_or_standard()
        if self.resource_type is ResourceType.LITERATURE:
            self._validate_literature()
        if self.source_path.suffix.lower() != ".pdf":
            raise ValueError("knowledge resources require a PDF source_path")
        return self

    def _normalize_admission_status(self) -> None:
        if self.integrity_status in {
            IntegrityStatus.EXPRESSION_OF_CONCERN,
            IntegrityStatus.RETRACTED,
        }:
            if self.include:
                raise ValueError("integrity-flagged literature cannot enter official retrieval")
            self.admission_status = AdmissionStatus.WITHDRAWN
            return
        expected = AdmissionStatus.APPROVED if self.include else AdmissionStatus.CANDIDATE
        if self.admission_status is None:
            self.admission_status = expected
        elif self.include and self.admission_status is not AdmissionStatus.APPROVED:
            raise ValueError("included resources require approved admission_status")
        elif not self.include and self.admission_status is AdmissionStatus.APPROVED:
            raise ValueError("approved admission_status requires include=true")

    def _validate_regulation_or_standard(self) -> None:
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
        if not self.include:
            return
        if self.effective_status != "current":
            raise ValueError("official regulations require current effective_status")
        if self.source_url is None:
            raise ValueError("official regulations require an issuing-body source_url")
        if self.accessed_date is None or not self.source_verified_by:
            raise ValueError("official regulations require a source verification record")
        if not self.topics or not set(self.topics).issubset(REGULATION_TOPICS):
            raise ValueError("official regulations require controlled regulation topics")
        if self.primary_topic not in self.topics:
            raise ValueError("official regulation primary_topic must be included in topics")

    def _validate_literature(self) -> None:
        if not self.doi and not self.source_url:
            raise ValueError("literature requires a DOI or stable source URL")
        if not self.include:
            return
        required = (
            self.doi,
            self.authors,
            self.venue,
            self.published_date,
            self.publication_status,
            self.integrity_status,
            self.citation_count is not None,
            self.citation_source,
            self.citation_checked_at,
            self.jci_value is not None,
            self.jci_quartile,
            self.jci_year,
            self.jci_source,
            self.cas_zone,
            self.cas_category,
            self.cas_year,
            self.cas_source,
            self.metrics_checked_at,
            self.quality_tier,
            self.content_quality_score is not None,
            self.primary_topic,
            self.topics,
        )
        if not all(required):
            raise ValueError("approved literature requires quality evidence and formal metadata")
        if self.publication_status not in FORMAL_PUBLICATION_STATUSES:
            raise ValueError("approved literature requires a formal publication_status")
        if self.integrity_status is not IntegrityStatus.CLEAR:
            raise ValueError("approved literature requires clear integrity_status")
        if self.content_quality_score is None or self.content_quality_score < 80:
            raise ValueError("approved literature requires content_quality_score >= 80")
        if not set(self.topics).issubset(LITERATURE_TOPICS):
            raise ValueError("approved literature requires controlled pedestrian-flow topics")
        if self.primary_topic not in self.topics:
            raise ValueError("approved literature primary_topic must be included in topics")
        if self.jci_source != "clarivate_jcr" or self.cas_source != "cas_journal_partition":
            raise ValueError("approved literature requires official JCI and CAS metric sources")
        self._validate_quality_tier()

    def _validate_quality_tier(self) -> None:
        if self.quality_tier is QualityTier.A:
            if self.cas_zone != 1 or self.jci_value is None or self.jci_value < 1.5:
                raise ValueError("A-tier literature requires CAS zone 1 and JCI >= 1.5")
            return
        if self.quality_tier is QualityTier.B:
            if self.cas_zone is None or self.cas_zone > 2:
                raise ValueError("B-tier literature requires CAS zone 1 or 2")
            if self.jci_value is None or self.jci_value < 1.0:
                raise ValueError("B-tier literature requires JCI >= 1.0")
            return
        if self.quality_tier is QualityTier.EXCEPTION:
            if not self.exception_reason or not self.approved_by:
                raise ValueError("X-tier literature requires exception_reason and approved_by")
            return
        raise ValueError("approved literature requires quality tier A, B, or X")

    @property
    def retrieval_eligibility(self) -> RetrievalEligibility:
        if self.include and self.admission_status is AdmissionStatus.APPROVED:
            return RetrievalEligibility.OFFICIAL
        return RetrievalEligibility.EXCLUDED


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
