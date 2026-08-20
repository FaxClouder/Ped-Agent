"""Sparse, dense, RRF, optional rerank, and parent-context retrieval."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime

from ped_contracts.evidence import EvidenceItem, EvidenceOrigin
from ped_knowledge.contracts import (
    EvidenceHit,
    IndexHit,
    RerankCandidate,
    RerankGateway,
    VectorSearch,
)
from ped_knowledge.indexing import FTSIndex
from ped_knowledge.storage import Catalog


class IndexStaleError(RuntimeError):
    pass


class RetrievalService:
    def __init__(self, catalog: Catalog, index: FTSIndex) -> None:
        self.catalog = catalog
        self.index = index

    def search(self, query: str, *, limit: int = 5) -> list[EvidenceHit]:
        if self.index.source_fingerprint() != self.catalog.official_fingerprint():
            raise IndexStaleError(
                "search index is stale; rebuild it from the authoritative catalog"
            )
        evidence: list[EvidenceHit] = []
        for candidate in self.index.search(query, limit=limit):
            row = self.catalog.hydrate_chunk(candidate.chunk_id)
            if row is None or not _is_active_official(row):
                continue
            metadata = row["canonical_metadata"]
            evidence.append(
                EvidenceHit(
                    resource_id=row["resource_id"],
                    version_id=row["version_id"],
                    chunk_id=row["chunk_id"],
                    title=row["title"],
                    resource_type=row["resource_type"],
                    text=row["text"],
                    locator=row["locator"],
                    source_url=str(metadata["source_url"]) if metadata.get("source_url") else None,
                    doi=metadata.get("doi"),
                    document_number=metadata.get("document_number"),
                    jurisdiction=metadata.get("jurisdiction"),
                    effective_status=metadata.get("effective_status"),
                    score=candidate.score,
                )
            )
        return evidence


@dataclass(frozen=True)
class HybridRetrievalResult:
    items: list[EvidenceItem]
    degraded: bool = False
    degradation_reason: str | None = None
    parent_contexts: dict[str, str] = field(default_factory=dict)


class HybridRetriever:
    def __init__(
        self,
        catalog: Catalog,
        fts_index: FTSIndex,
        vector_index: VectorSearch | None,
        *,
        embedding_fingerprint: str,
        reranker: RerankGateway | None = None,
        recall_limit: int = 40,
        fusion_limit: int = 40,
        rrf_k: int = 60,
        max_chunks_per_resource: int = 2,
    ) -> None:
        self.catalog = catalog
        self.fts_index = fts_index
        self.vector_index = vector_index
        self.embedding_fingerprint = embedding_fingerprint
        self.reranker = reranker
        self.recall_limit = recall_limit
        self.fusion_limit = fusion_limit
        self.rrf_k = rrf_k
        self.max_chunks_per_resource = max_chunks_per_resource

    async def retrieve(self, query: str, *, limit: int = 8) -> HybridRetrievalResult:
        ranked_lists: list[list[IndexHit]] = []
        reasons: list[str] = []
        try:
            ranked_lists.append(self._fts_hits(query))
        except (IndexStaleError, OSError, RuntimeError):
            reasons.append("fts_index_unavailable")
        vector_reason = self._vector_degradation()
        if vector_reason is None and self.vector_index is not None:
            try:
                ranked_lists.append(await self.vector_index.search(query, limit=self.recall_limit))
            except Exception:  # noqa: BLE001 - vector failures must degrade to FTS.
                reasons.append("vector_index_unavailable")
        elif vector_reason:
            reasons.append(vector_reason)
        if not ranked_lists:
            raise IndexStaleError("no current sparse or dense knowledge index is available")

        fused = self._rrf(ranked_lists)[: self.fusion_limit]
        reranked = await self._rerank(query, fused, reasons)
        evidence: list[EvidenceItem] = []
        parent_contexts: dict[str, str] = {}
        resource_counts: dict[str, int] = {}
        for chunk_id, score in reranked:
            row = self.catalog.hydrate_chunk(chunk_id)
            if row is None or not _is_active_official(row):
                continue
            resource_id = str(row["resource_id"])
            if resource_counts.get(resource_id, 0) >= self.max_chunks_per_resource:
                continue
            resource_counts[resource_id] = resource_counts.get(resource_id, 0) + 1
            item = _to_evidence(row, score)
            evidence.append(item)
            parent_contexts[item.evidence_id] = self.catalog.context_for_chunk(chunk_id)
            if len(evidence) >= limit:
                break
        return HybridRetrievalResult(
            evidence,
            bool(reasons),
            ";".join(dict.fromkeys(reasons)) or None,
            parent_contexts,
        )

    def _fts_hits(self, query: str) -> list[IndexHit]:
        fingerprint_method = getattr(self.fts_index, "source_fingerprint", None)
        if callable(fingerprint_method):
            fingerprint = fingerprint_method()
            if fingerprint != self.catalog.official_fingerprint():
                raise IndexStaleError("FTS index fingerprint is stale")
        return self.fts_index.search(query, limit=self.recall_limit)

    def _vector_degradation(self) -> str | None:
        if self.vector_index is None:
            return "vector_index_unavailable"
        if self.vector_index.catalog_fingerprint != self.catalog.official_fingerprint():
            return "vector_index_stale"
        if self.vector_index.embedding_fingerprint != self.embedding_fingerprint:
            return "embedding_fingerprint_changed"
        return None

    async def _rerank(
        self,
        query: str,
        fused: list[tuple[str, float]],
        reasons: list[str],
    ) -> list[tuple[str, float]]:
        if self.reranker is None or not fused:
            return fused
        candidates: list[RerankCandidate] = []
        for chunk_id, score in fused:
            row = self.catalog.hydrate_chunk(chunk_id)
            if row is not None:
                candidates.append(
                    RerankCandidate(
                        chunk_id=chunk_id,
                        text=str(row["text"]),
                        initial_score=score,
                    )
                )
        try:
            scores = await self.reranker.rerank(query, candidates)
        except Exception:  # noqa: BLE001 - configured rerank failure degrades to RRF.
            reasons.append("reranker_unavailable")
            return fused
        rerank_scores = {item.chunk_id: item.score for item in scores}
        return sorted(
            fused,
            key=lambda item: (-rerank_scores.get(item[0], item[1]), item[0]),
        )

    def _rrf(self, ranked_lists: list[list[IndexHit]]) -> list[tuple[str, float]]:
        scores: dict[str, float] = {}
        for ranked in ranked_lists:
            seen: set[str] = set()
            for rank, hit in enumerate(ranked, start=1):
                if hit.chunk_id in seen:
                    continue
                seen.add(hit.chunk_id)
                scores[hit.chunk_id] = scores.get(hit.chunk_id, 0.0) + 1 / (self.rrf_k + rank)
        return sorted(scores.items(), key=lambda item: (-item[1], item[0]))


def retrieval_is_sufficient(query: str, items: list[object]) -> bool:
    resource_ids = {getattr(item, "resource_id", None) for item in items}
    resource_ids.discard(None)
    if len(resource_ids) >= 2:
        return True
    normalized_query = " ".join(query.casefold().split())
    for item in items:
        exact_values = (
            getattr(item, "title", None),
            getattr(item, "doi", None),
            getattr(item, "document_number", None),
        )
        if any(
            normalized_query == " ".join(str(value).casefold().split())
            for value in exact_values
            if value
        ):
            return True
    return False


def _is_active_official(row: dict[str, object]) -> bool:
    return bool(
        row["retrieval_eligibility"] == "official"
        and row["version_id"] == row.get("active_version_id", row["version_id"])
    )


def _to_evidence(row: dict[str, object], score: float) -> EvidenceItem:
    metadata = row["canonical_metadata"]
    if not isinstance(metadata, dict):
        raise TypeError("catalog metadata must be a dictionary")
    quote = str(row["text"])
    return EvidenceItem(
        evidence_id=f"local:{row['chunk_id']}",
        origin=EvidenceOrigin.LOCAL_OFFICIAL,
        title=str(row["title"]),
        quote=quote,
        locator=str(row["locator"]),
        url=str(metadata["source_url"]) if metadata.get("source_url") else None,
        doi=metadata.get("doi"),
        document_number=metadata.get("document_number"),
        resource_id=str(row["resource_id"]),
        version_id=str(row["version_id"]),
        chunk_id=str(row["chunk_id"]),
        authority="official",
        retrieved_at=datetime.now(UTC),
        content_hash=hashlib.sha256(quote.encode("utf-8")).hexdigest(),
        score=score,
    )


__all__ = [
    "HybridRetrievalResult",
    "HybridRetriever",
    "IndexStaleError",
    "RetrievalService",
    "retrieval_is_sufficient",
]
