from pathlib import Path

import pytest

from ped_agent_server.catalog import Catalog
from ped_agent_server.hybrid_retrieval import HybridRetriever, retrieval_is_sufficient
from ped_agent_server.index import IndexHit
from ped_agent_server.models import CanonicalChunk
from tests.manifest_samples import regulation_manifest


class FakeFTS:
    def __init__(self, hits: list[IndexHit]) -> None:
        self.hits = hits

    def search(self, query: str, *, limit: int) -> list[IndexHit]:
        return self.hits[:limit]


class FakeVector:
    def __init__(
        self,
        hits: list[IndexHit],
        *,
        catalog_fingerprint: str,
        embedding_fingerprint: str,
    ) -> None:
        self.hits = hits
        self.catalog_fingerprint = catalog_fingerprint
        self.embedding_fingerprint = embedding_fingerprint

    async def search(self, query: str, *, limit: int) -> list[IndexHit]:
        return self.hits[:limit]


def add_resource(catalog: Catalog, tmp_path: Path, resource_id: str, chunk_count: int) -> list[str]:
    record = regulation_manifest(
        resource_id=resource_id,
        title=f"{resource_id} official rule",
        source_path=tmp_path / f"{resource_id}.pdf",
        sha256=(resource_id[-1] * 64),
    )
    chunks = [
        CanonicalChunk(
            chunk_id=f"{resource_id}:{index}",
            resource_id=resource_id,
            version_id=record.sha256,
            ordinal=index,
            text=f"Evidence {index} for {resource_id}",
            page_start=index + 1,
            page_end=index + 1,
            locator=f"p.{index + 1}",
            parser_version="test",
        )
        for index in range(chunk_count)
    ]
    catalog.upsert_resource(record, version_id=record.sha256, vault_path=f"objects/{resource_id}")
    catalog.replace_chunks(record.sha256, chunks)
    return [chunk.chunk_id for chunk in chunks]


@pytest.mark.asyncio
async def test_hybrid_retriever_rrf_deduplicates_and_caps_chunks_per_resource(
    tmp_path: Path,
) -> None:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    first = add_resource(catalog, tmp_path, "reg-a", 3)
    second = add_resource(catalog, tmp_path, "reg-b", 1)
    fingerprint = catalog.official_fingerprint()
    fts = FakeFTS([IndexHit(item, 1.0) for item in [first[0], first[1], first[2], second[0]]])
    vector = FakeVector(
        [IndexHit(item, 1.0) for item in [second[0], first[1]]],
        catalog_fingerprint=fingerprint,
        embedding_fingerprint="embed-v1",
    )

    result = await HybridRetriever(
        catalog,
        fts,
        vector,
        embedding_fingerprint="embed-v1",
    ).retrieve("density", limit=8)

    assert result.degraded is False
    assert result.items[0].chunk_id == first[1]
    assert result.items[1].resource_id == "reg-b"
    assert sum(item.resource_id == "reg-a" for item in result.items) == 2
    assert len({item.evidence_id for item in result.items}) == len(result.items)


@pytest.mark.asyncio
async def test_hybrid_retriever_falls_back_to_fts_for_stale_vector_index(tmp_path: Path) -> None:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    chunks = add_resource(catalog, tmp_path, "reg-c", 1)
    vector = FakeVector(
        [IndexHit(chunks[0], 1.0)],
        catalog_fingerprint="stale",
        embedding_fingerprint="embed-v1",
    )

    result = await HybridRetriever(
        catalog,
        FakeFTS([IndexHit(chunks[0], 1.0)]),
        vector,
        embedding_fingerprint="embed-v1",
    ).retrieve("density")

    assert result.degraded is True
    assert result.degradation_reason == "vector_index_stale"
    assert [item.chunk_id for item in result.items] == chunks


def test_retrieval_sufficiency_requires_two_resources_or_exact_identifier() -> None:
    class Evidence:
        def __init__(self, resource_id: str, title: str, doi: str | None = None) -> None:
            self.resource_id = resource_id
            self.title = title
            self.doi = doi
            self.document_number = None

    one = Evidence("r1", "Bottleneck dynamics", "10.1000/exact")
    two = Evidence("r2", "Another source")

    assert retrieval_is_sufficient("general question", [one]) is False
    assert retrieval_is_sufficient("general question", [one, two]) is True
    assert retrieval_is_sufficient("10.1000/exact", [one]) is True
    assert retrieval_is_sufficient("Bottleneck dynamics", [one]) is True
