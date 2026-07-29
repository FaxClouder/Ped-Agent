import hashlib
from pathlib import Path

import pytest

from ped_agent.catalog import Catalog
from ped_agent.models import CanonicalChunk, ResourceManifest, ResourceType
from tests.manifest_samples import literature_manifest


def literature(source_path: Path) -> ResourceManifest:
    return literature_manifest(
        resource_id="paper-catalog-2026",
        title="Catalog test paper",
        source_path=source_path,
        sha256="a" * 64,
        doi="10.1000/catalog",
        published_date="2026-03-01",
        topic="flow_fundamentals",
        datasets=["juelich-demo"],
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
        topic="flow_fundamentals",
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


def test_catalog_rejects_duplicate_doi_across_import_batches(tmp_path: Path) -> None:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    first = literature_manifest(
        resource_id="lit-2016-first-doi",
        source_path=tmp_path / "first.pdf",
        sha256="1" * 64,
        doi="10.1000/shared-doi",
    )
    second = literature_manifest(
        resource_id="lit-2016-second-doi",
        source_path=tmp_path / "second.pdf",
        sha256="2" * 64,
        doi="https://doi.org/10.1000/SHARED-DOI",
    )
    catalog.upsert_resource(first, version_id=first.sha256, vault_path="objects/11/first.pdf")

    with pytest.raises(ValueError, match="DOI already belongs to lit-2016-first-doi"):
        catalog.upsert_resource(
            second,
            version_id=second.sha256,
            vault_path="objects/22/second.pdf",
        )


def test_catalog_rejects_duplicate_hash_for_different_resource(tmp_path: Path) -> None:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    first = literature_manifest(
        resource_id="lit-2016-first-hash",
        source_path=tmp_path / "first.pdf",
        sha256="3" * 64,
        doi="10.1000/first-hash",
    )
    second = literature_manifest(
        resource_id="lit-2016-second-hash",
        source_path=tmp_path / "second.pdf",
        sha256=first.sha256,
        doi="10.1000/second-hash",
    )
    catalog.upsert_resource(first, version_id=first.sha256, vault_path="objects/33/first.pdf")

    with pytest.raises(ValueError, match="SHA-256 already belongs to lit-2016-first-hash"):
        catalog.upsert_resource(
            second,
            version_id=second.sha256,
            vault_path="objects/33/second.pdf",
        )
