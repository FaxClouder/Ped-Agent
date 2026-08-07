"""Stable contracts owned by the Ped-Agent knowledge module."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class ResourceType(StrEnum):
    LITERATURE = "literature"
    REGULATION = "regulation"
    STANDARD = "standard"


class RetrievalEligibility(StrEnum):
    EXCLUDED = "excluded"
    STAGING = "staging"
    OFFICIAL = "official"


class VersionStatus(StrEnum):
    STAGED = "staged"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    FAILED = "failed"


class ElementType(StrEnum):
    TITLE = "title"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    TABLE = "table"
    IMAGE = "image"
    CAPTION = "caption"
    FORMULA = "formula"
    CLAUSE = "clause"
    OCR_TEXT = "ocr_text"


class ChunkLevel(StrEnum):
    PARENT = "parent"
    CHILD = "child"


def normalize_doi(doi: str | None) -> str | None:
    if doi is None:
        return None
    normalized = doi.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        normalized = normalized.removeprefix(prefix)
    return normalized or None


class IngestionManifest(BaseModel):
    """Technical import description for a document selected before upload."""

    model_config = ConfigDict(extra="allow")

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
    effective_status: str | None = None
    topics: list[str] = Field(default_factory=list)
    datasets: list[str] = Field(default_factory=list)
    supersedes: list[str] = Field(default_factory=list)
    include: bool = True

    @field_validator("source_path")
    @classmethod
    def require_pdf_source(cls, value: Path) -> Path:
        if value.suffix.lower() != ".pdf":
            raise ValueError("knowledge resources require a PDF source_path")
        return value

    @property
    def admission_status(self) -> str:
        return "approved" if self.include else "candidate"

    @property
    def retrieval_eligibility(self) -> RetrievalEligibility:
        return RetrievalEligibility.OFFICIAL if self.include else RetrievalEligibility.EXCLUDED


class AssetRef(BaseModel):
    asset_type: str
    path: str
    page_number: int
    element_id: str | None = None


class Provenance(BaseModel):
    source_element_ids: list[str] = Field(default_factory=list)
    source_hash: str
    character_start: int | None = None
    character_end: int | None = None


class DocumentElement(BaseModel):
    element_id: str
    element_type: ElementType
    text: str = ""
    page_number: int
    bbox: tuple[float, float, float, float] | None = None
    order: int
    heading_path: tuple[str, ...] = ()
    locator: str
    table_data: list[list[str]] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CanonicalPage(BaseModel):
    page_number: int
    width: float
    height: float
    ocr_applied: bool = False
    element_ids: tuple[str, ...] = ()


class CanonicalDocument(BaseModel):
    resource_id: str
    version_id: str
    source_hash: str
    parser_version: str
    pages: list[CanonicalPage]
    elements: list[DocumentElement]
    assets: list[AssetRef] = Field(default_factory=list)


class ParseReport(BaseModel):
    resource_id: str
    version_id: str
    parser_version: str
    page_count: int
    text_page_count: int
    ocr_page_count: int
    empty_pages: tuple[int, ...] = ()
    element_count: int
    table_count: int
    image_count: int
    degraded: bool = False
    degradation_reasons: tuple[str, ...] = ()
    manual_review_pages: tuple[int, ...] = ()


class ChunkingPolicy(BaseModel):
    policy_version: str = "parent-child-v1"
    parent_target_tokens: int = Field(default=1200, ge=100)
    parent_max_tokens: int = Field(default=1800, ge=200)
    child_target_tokens: int = Field(default=320, ge=50)
    child_max_tokens: int = Field(default=450, ge=80)
    child_overlap_tokens: int = Field(default=48, ge=0)


class KnowledgeChunk(BaseModel):
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
    chunk_level: ChunkLevel = ChunkLevel.CHILD
    parent_chunk_id: str | None = None
    heading_path: tuple[str, ...] = ()
    policy_version: str = "parent-child-v1"
    element_ids: tuple[str, ...] = ()


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


@dataclass(frozen=True)
class IndexHit:
    chunk_id: str
    score: float


class RerankCandidate(BaseModel):
    chunk_id: str
    text: str
    initial_score: float


class RerankScore(BaseModel):
    chunk_id: str
    score: float


class EmbeddingGateway(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class VectorSearch(Protocol):
    @property
    def catalog_fingerprint(self) -> str: ...

    @property
    def embedding_fingerprint(self) -> str: ...

    async def search(self, query: str, *, limit: int) -> list[IndexHit]: ...


class RerankGateway(Protocol):
    async def rerank(
        self,
        query: str,
        candidates: list[RerankCandidate],
    ) -> list[RerankScore]: ...


class OCRGateway(Protocol):
    def extract_page_text(self, path: Path, page_number: int) -> str: ...


__all__ = [
    "AssetRef",
    "CanonicalDocument",
    "CanonicalPage",
    "ChunkLevel",
    "ChunkingPolicy",
    "DocumentElement",
    "ElementType",
    "EmbeddingGateway",
    "EvidenceHit",
    "IndexHit",
    "IngestionManifest",
    "KnowledgeChunk",
    "OCRGateway",
    "ParseReport",
    "Provenance",
    "RerankCandidate",
    "RerankGateway",
    "RerankScore",
    "ResourceType",
    "RetrievalEligibility",
    "VectorSearch",
    "VersionStatus",
    "normalize_doi",
]
