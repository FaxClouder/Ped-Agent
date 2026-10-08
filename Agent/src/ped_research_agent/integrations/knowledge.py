"""Run-scoped KB adapters and readonly tools; no knowledge algorithm is duplicated here.

HybridRetriever and Catalog satisfy the structural ports below. Snapshot fingerprints are
checked before and after access; only evidence retrieved in this run can be read by ID.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Mapping
from typing import Any, Literal, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ped_agent_harness.contracts import ToolRunContext, ToolSpec
from ped_contracts.evidence import EvidenceItem, EvidenceOrigin, RetrievalBatch


class ToolModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SnapshotIdentity(ToolModel):
    policy_version: str = Field(min_length=1)
    catalog_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    index_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")


class RetrievalResult(Protocol):
    @property
    def items(self) -> list[EvidenceItem]: ...
    @property
    def degraded(self) -> bool: ...
    @property
    def degradation_reason(self) -> str | None: ...
    @property
    def parent_contexts(self) -> dict[str, str]: ...


class RetrievalBackend(Protocol):
    async def retrieve(self, query: str, *, limit: int = 8) -> RetrievalResult: ...


class CatalogBackend(Protocol):
    def hydrate_chunk(self, chunk_id: str) -> Mapping[str, Any] | None: ...
    def official_fingerprint(self, *, policy_version: str) -> str: ...


class KnowledgeSnapshotError(RuntimeError):
    """Asset identity changed or does not match the frozen configuration."""


class EvidenceReadError(LookupError):
    """Requested evidence/context is unavailable; never converted to empty evidence."""


class _CatalogChunk(BaseModel):
    # Catalog rows contain additional parser metadata; validate only the adapter's boundary.
    model_config = ConfigDict(extra="ignore")
    chunk_id: str
    resource_id: str
    version_id: str
    active_version_id: str
    retrieval_eligibility: Literal["official"]
    chunk_level: Literal["child", "parent"]
    policy_version: str
    text: str
    parent_chunk_id: str | None = None
    character_start: int | None = None
    character_end: int | None = None
    token_count: int = Field(ge=0)


class SearchInput(ToolModel):
    query: str = Field(min_length=1, pattern=r"\S")
    limit: int = Field(default=8, gt=0, le=100, strict=True)


class SearchOutput(ToolModel):
    items: list[EvidenceItem]
    degraded: bool
    degradation_reason: str | None
    parent_contexts: dict[str, str]
    snapshot: SnapshotIdentity


class ReadEvidenceInput(ToolModel):
    evidence_id: str | None = Field(default=None, min_length=1)
    chunk_id: str | None = Field(default=None, min_length=1)
    expand: Literal["child", "parent"] = "child"

    @model_validator(mode="after")
    def one_identity(self) -> Self:
        if (self.evidence_id is None) == (self.chunk_id is None):
            raise ValueError("provide exactly one evidence_id or chunk_id")
        return self


class ReadEvidenceOutput(ToolModel):
    evidence: EvidenceItem
    parent_text: str | None = None
    parent_chunk_id: str | None = None
    parent_content_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    character_start: int | None
    character_end: int | None
    token_count: int
    snapshot: SnapshotIdentity


class KnowledgeAdapter:
    def __init__(
        self,
        retriever: RetrievalBackend,
        catalog: CatalogBackend,
        *,
        snapshot: SnapshotIdentity,
        current_index_fingerprint: Callable[[], str],
        baseline_sufficiency: Callable[[str, list[EvidenceItem]], bool],
        limit: int = 8,
    ) -> None:
        self.retriever = retriever
        self.catalog = catalog
        self.snapshot = snapshot
        self.current_index_fingerprint = current_index_fingerprint
        self.baseline_sufficiency = baseline_sufficiency
        self.limit = SearchInput(query="validate limit", limit=limit).limit
        self._evidence: dict[str, EvidenceItem] = {}
        self._parent_contexts: dict[str, str] = {}
        self._run_id: str | None = None

    def bind_run(self, run_id: str) -> None:
        if self._run_id is not None or self._evidence:
            raise ValueError("use a fresh knowledge adapter for each run")
        self._run_id = run_id

    def validate_run(self, run_id: str) -> None:
        if self._run_id is None:
            self.bind_run(run_id)
        elif self._run_id != run_id:
            raise KnowledgeSnapshotError("tool call belongs to another run")

    def validate_snapshot(self) -> None:
        catalog = self.catalog.official_fingerprint(policy_version=self.snapshot.policy_version)
        if catalog != self.snapshot.catalog_fingerprint:
            raise KnowledgeSnapshotError("catalog fingerprint changed")
        if self.current_index_fingerprint() != self.snapshot.index_fingerprint:
            raise KnowledgeSnapshotError("index fingerprint changed")

    async def search(self, args: SearchInput) -> SearchOutput:
        self.validate_snapshot()
        result = await self.retriever.retrieve(args.query, limit=args.limit)
        self.validate_snapshot()
        for item in result.items:
            if (
                item.origin is not EvidenceOrigin.LOCAL_OFFICIAL
                or not item.resource_id
                or not item.version_id
                or hashlib.sha256(item.quote.encode()).hexdigest() != item.content_hash
            ):
                raise KnowledgeSnapshotError("retrieved evidence has invalid provenance")
            prior = self._evidence.get(item.evidence_id)
            if prior is not None and (
                prior.content_hash,
                prior.resource_id,
                prior.version_id,
                prior.chunk_id,
            ) != (item.content_hash, item.resource_id, item.version_id, item.chunk_id):
                raise KnowledgeSnapshotError("evidence identity changed within a run")
            if not item.chunk_id or item.evidence_id != f"local:{item.chunk_id}":
                raise KnowledgeSnapshotError("retrieval returned an unsupported evidence identity")
            context = result.parent_contexts.get(item.evidence_id)
            prior_context = self._parent_contexts.get(item.evidence_id)
            if prior_context is not None and context != prior_context:
                raise KnowledgeSnapshotError("parent context changed within a run")
        self._evidence.update({i.evidence_id: i.model_copy(deep=True) for i in result.items})
        self._parent_contexts.update(result.parent_contexts)
        return SearchOutput(
            items=result.items,
            degraded=result.degraded,
            degradation_reason=result.degradation_reason,
            parent_contexts=result.parent_contexts,
            snapshot=self.snapshot,
        )

    async def retrieve(self, query: str) -> RetrievalBatch:
        result = await self.search(SearchInput(query=query, limit=self.limit))
        return RetrievalBatch(
            items=result.items,
            sufficient=self.baseline_sufficiency(query, result.items),
            degraded=result.degraded,
            degradation_reason=result.degradation_reason,
        )

    def _chunk(self, chunk_id: str) -> _CatalogChunk:
        raw = self.catalog.hydrate_chunk(chunk_id)
        if raw is None:
            raise EvidenceReadError("requested chunk is missing")
        row = _CatalogChunk.model_validate(raw)
        if row.chunk_id != chunk_id or row.version_id != row.active_version_id:
            raise KnowledgeSnapshotError("chunk identity/version is no longer active")
        if row.policy_version != self.snapshot.policy_version:
            raise KnowledgeSnapshotError("chunk policy differs from frozen snapshot")
        return row

    def read(self, args: ReadEvidenceInput) -> ReadEvidenceOutput:
        self.validate_snapshot()
        key = args.evidence_id or f"local:{args.chunk_id}"
        evidence = self._evidence.get(key)
        if evidence is None or evidence.chunk_id is None:
            raise EvidenceReadError("evidence must first be retrieved in this run")
        child = self._chunk(evidence.chunk_id)
        if (
            child.chunk_level != "child"
            or (child.resource_id, child.version_id) != (evidence.resource_id, evidence.version_id)
            or hashlib.sha256(child.text.encode()).hexdigest() != evidence.content_hash
        ):
            raise KnowledgeSnapshotError("child differs from retrieved evidence")
        parent = None
        if args.expand == "parent":
            if child.parent_chunk_id is None:
                raise EvidenceReadError("requested parent is unavailable")
            parent = self._chunk(child.parent_chunk_id)
            if parent.chunk_level != "parent" or (parent.resource_id, parent.version_id) != (
                child.resource_id,
                child.version_id,
            ):
                raise KnowledgeSnapshotError("parent identity/version does not match child")
            if self._parent_contexts.get(evidence.evidence_id) != parent.text:
                raise KnowledgeSnapshotError("parent differs from frozen retrieval context")
        self.validate_snapshot()
        return ReadEvidenceOutput(
            evidence=evidence.model_copy(deep=True),
            parent_text=parent.text if parent else None,
            parent_chunk_id=parent.chunk_id if parent else None,
            parent_content_hash=hashlib.sha256(parent.text.encode()).hexdigest()
            if parent
            else None,
            character_start=child.character_start,
            character_end=child.character_end,
            token_count=child.token_count,
            snapshot=self.snapshot,
        )


class KnowledgeSearchTool(ToolSpec[SearchInput, SearchOutput]):
    name = "knowledge.search"
    version = "1"
    description = "Search the frozen knowledge snapshot for child evidence."
    input_model = SearchInput
    output_model = SearchOutput

    def __init__(self, adapter: KnowledgeAdapter) -> None:
        self.adapter = adapter

    def parallel_safe(self, args: SearchInput) -> bool:
        return True

    async def execute(self, args: SearchInput, ctx: ToolRunContext) -> SearchOutput:
        self.adapter.validate_run(ctx.call.run_id)
        return await self.adapter.search(args)


class KnowledgeReadTool(ToolSpec[ReadEvidenceInput, ReadEvidenceOutput]):
    name = "knowledge.read_evidence"
    version = "1"
    description = "Read previously retrieved child evidence and explicit parent context."
    input_model = ReadEvidenceInput
    output_model = ReadEvidenceOutput

    def __init__(self, adapter: KnowledgeAdapter) -> None:
        self.adapter = adapter

    def parallel_safe(self, args: ReadEvidenceInput) -> bool:
        return True

    async def execute(self, args: ReadEvidenceInput, ctx: ToolRunContext) -> ReadEvidenceOutput:
        self.adapter.validate_run(ctx.call.run_id)
        return self.adapter.read(args)
