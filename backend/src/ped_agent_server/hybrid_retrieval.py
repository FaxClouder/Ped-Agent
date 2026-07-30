from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from ped_agent.agent.contracts import EvidenceItem, EvidenceOrigin

from ped_agent_server.catalog import Catalog
from ped_agent_server.index import FTSIndex, IndexHit


class VectorSearch(Protocol):
    @property
    def catalog_fingerprint(self) -> str: ...

    @property
    def embedding_fingerprint(self) -> str: ...

    async def search(self, query: str, *, limit: int) -> list[IndexHit]: ...


@dataclass(frozen=True)
class HybridRetrievalResult:
    items: list[EvidenceItem]
    degraded: bool = False
    degradation_reason: str | None = None


class HybridRetriever:
    def __init__(
        self,
        catalog: Catalog,
        fts_index: FTSIndex,
        vector_index: VectorSearch | None,
        *,
        embedding_fingerprint: str,
        recall_limit: int = 20,
        rrf_k: int = 60,
        max_chunks_per_resource: int = 2,
    ) -> None:
        self.catalog = catalog
        self.fts_index = fts_index
        self.vector_index = vector_index
        self.embedding_fingerprint = embedding_fingerprint
        self.recall_limit = recall_limit
        self.rrf_k = rrf_k
        self.max_chunks_per_resource = max_chunks_per_resource

    async def retrieve(self, query: str, *, limit: int = 8) -> HybridRetrievalResult:
        ranked_lists = [self.fts_index.search(query, limit=self.recall_limit)]
        degraded, reason = self._vector_degradation()
        if not degraded and self.vector_index is not None:
            try:
                ranked_lists.append(
                    await self.vector_index.search(query, limit=self.recall_limit)
                )
            except Exception:  # noqa: BLE001 - a broken vector index must degrade to FTS.
                degraded = True
                reason = "vector_index_unavailable"

        fused = self._rrf(ranked_lists)
        evidence: list[EvidenceItem] = []
        resource_counts: dict[str, int] = {}
        for chunk_id, score in fused:
            row = self.catalog.hydrate_chunk(chunk_id)
            if row is None or row["retrieval_eligibility"] != "official":
                continue
            resource_id = str(row["resource_id"])
            if resource_counts.get(resource_id, 0) >= self.max_chunks_per_resource:
                continue
            resource_counts[resource_id] = resource_counts.get(resource_id, 0) + 1
            evidence.append(_to_evidence(row, score))
            if len(evidence) >= limit:
                break
        return HybridRetrievalResult(evidence, degraded, reason)

    def _vector_degradation(self) -> tuple[bool, str | None]:
        if self.vector_index is None:
            return True, "vector_index_unavailable"
        if self.vector_index.catalog_fingerprint != self.catalog.official_fingerprint():
            return True, "vector_index_stale"
        if self.vector_index.embedding_fingerprint != self.embedding_fingerprint:
            return True, "embedding_fingerprint_changed"
        return False, None

    def _rrf(self, ranked_lists: list[list[IndexHit]]) -> list[tuple[str, float]]:
        scores: dict[str, float] = {}
        for ranked in ranked_lists:
            seen: set[str] = set()
            for rank, hit in enumerate(ranked, start=1):
                if hit.chunk_id in seen:
                    continue
                seen.add(hit.chunk_id)
                scores[hit.chunk_id] = scores.get(hit.chunk_id, 0.0) + 1 / (
                    self.rrf_k + rank
                )
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
