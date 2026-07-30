from __future__ import annotations

from ped_agent_server.catalog import Catalog
from ped_agent_server.index import FTSIndex
from ped_agent_server.models import EvidenceHit


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
            if row is None or row["retrieval_eligibility"] != "official":
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
