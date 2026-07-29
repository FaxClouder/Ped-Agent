import hashlib
from pathlib import Path

from ped_agent.catalog import Catalog
from ped_agent.models import CanonicalChunk, ResourceManifest, ResourceType


def literature(source_path: Path) -> ResourceManifest:
    return ResourceManifest(
        resource_id="paper-catalog-2026",
        resource_type=ResourceType.LITERATURE,
        title="Catalog test paper",
        language="en",
        source_path=source_path,
        sha256="a" * 64,
        doi="10.1000/catalog",
        published_date="2026-03-01",
        topics=["fundamental-diagram"],
        datasets=["juelich-demo"],
        include=True,
    )


def test_catalog_persists_resource_version_and_chunks(tmp_path: Path) -> None:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    record = literature(tmp_path / "paper.pdf")
    catalog.upsert_resource(record, version_id=record.sha256, vault_path="objects/aa/file.pdf")
    catalog.replace_chunks(
        record.sha256,
        [
            CanonicalChunk(
                chunk_id="paper-catalog-2026:a:0000",
                resource_id=record.resource_id,
                version_id=record.sha256,
                ordinal=0,
                text="Pedestrian density and speed evidence.",
                page_start=3,
                page_end=3,
                locator="p.3",
                parser_version="pedestrian-pdf-v1",
            )
        ],
    )

    detail = catalog.get_resource(record.resource_id)
    assert detail["title"] == "Catalog test paper"
    assert catalog.list_official_chunks()[0]["locator"] == "p.3"
    assert catalog.list_relations(record.resource_id) == [
        {"relation_type": "uses_dataset", "target_ref": "juelich-demo"}
    ]


def test_catalog_filters_hydrates_and_fingerprints_official_evidence(tmp_path: Path) -> None:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    record = literature(tmp_path / "paper.pdf")
    catalog.upsert_resource(record, version_id=record.sha256, vault_path="objects/aa/file.pdf")
    chunk = CanonicalChunk(
        chunk_id="paper-catalog-2026:a:0000",
        resource_id=record.resource_id,
        version_id=record.sha256,
        ordinal=0,
        text="Pedestrian density and speed evidence.",
        page_start=3,
        page_end=3,
        locator="p.3",
        parser_version="pedestrian-pdf-v1",
    )
    catalog.replace_chunks(record.sha256, [chunk])

    resources = catalog.list_resources(
        ResourceType.LITERATURE.value,
        topic="fundamental-diagram",
        year="2026",
    )
    hydrated = catalog.hydrate_chunk(chunk.chunk_id)
    expected_fingerprint = hashlib.sha256(f"{chunk.chunk_id}{chunk.text}".encode()).hexdigest()

    assert [item["resource_id"] for item in resources] == [record.resource_id]
    assert catalog.list_resources(topic="missing-topic") == []
    assert hydrated is not None
    assert hydrated["canonical_metadata"]["doi"] == "10.1000/catalog"
    assert hydrated["retrieval_eligibility"] == "official"
    assert catalog.official_fingerprint() == expected_fingerprint
