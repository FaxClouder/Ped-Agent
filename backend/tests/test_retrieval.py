from pathlib import Path

import pytest
from typer.testing import CliRunner

from ped_agent.catalog import Catalog
from ped_agent.cli import app
from ped_agent.index import FTSIndex
from ped_agent.models import CanonicalChunk, ResourceManifest, ResourceType
from ped_agent.retrieval import IndexStaleError, RetrievalService
from tests.manifest_samples import regulation_manifest


def add_regulation(catalog: Catalog, source_path: Path) -> CanonicalChunk:
    record = regulation_manifest(
        resource_id="reg-exit-2026",
        title="安全出口规范",
        source_path=source_path,
        sha256="c" * 64,
    )
    chunk = CanonicalChunk(
        chunk_id="reg-exit-2026:c:00000",
        resource_id=record.resource_id,
        version_id=record.sha256,
        ordinal=0,
        text="安全出口附近应避免形成高密度拥堵。",
        page_start=5,
        page_end=5,
        locator="第5.2条 / p.5",
        parser_version="pedestrian-pdf-v1",
    )
    catalog.upsert_resource(record, version_id=record.sha256, vault_path="objects/cc/reg.pdf")
    catalog.replace_chunks(record.sha256, [chunk])
    return chunk


def test_retrieval_returns_authoritative_locator_and_metadata(tmp_path: Path) -> None:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    add_regulation(catalog, tmp_path / "reg.pdf")
    index = FTSIndex(tmp_path / "fts.sqlite3")
    index.rebuild(
        catalog.list_official_chunks(),
        source_fingerprint=catalog.official_fingerprint(),
    )

    hit = RetrievalService(catalog, index).search("安全出口拥堵", limit=5)[0]

    assert hit.document_number == "GB-DEMO-2026"
    assert hit.locator == "第5.2条 / p.5"
    assert hit.effective_status == "current"


def test_retrieval_rejects_stale_index(tmp_path: Path) -> None:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    add_regulation(catalog, tmp_path / "reg.pdf")
    index = FTSIndex(tmp_path / "fts.sqlite3")
    index.rebuild(catalog.list_official_chunks(), source_fingerprint="stale")

    with pytest.raises(IndexStaleError, match="index is stale"):
        RetrievalService(catalog, index).search("安全出口", limit=5)


def test_retrieval_filters_non_official_candidates_after_index_lookup(tmp_path: Path) -> None:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    record = ResourceManifest(
        resource_id="paper-candidate-2026",
        resource_type=ResourceType.LITERATURE,
        title="Candidate density paper",
        language="en",
        source_path=tmp_path / "candidate.pdf",
        sha256="d" * 64,
        doi="10.1000/candidate",
        include=False,
    )
    chunk = CanonicalChunk(
        chunk_id="paper-candidate-2026:d:00000",
        resource_id=record.resource_id,
        version_id=record.sha256,
        ordinal=0,
        text="Candidate-only density evidence.",
        page_start=1,
        page_end=1,
        locator="p.1",
        parser_version="pedestrian-pdf-v1",
    )
    catalog.upsert_resource(record, version_id=record.sha256, vault_path="objects/dd/paper.pdf")
    catalog.replace_chunks(record.sha256, [chunk])
    index = FTSIndex(tmp_path / "fts.sqlite3")
    index.rebuild(
        [
            {
                "chunk_id": chunk.chunk_id,
                "resource_id": chunk.resource_id,
                "title": record.title,
                "text": chunk.text,
                "locator": chunk.locator,
            }
        ],
        source_fingerprint=catalog.official_fingerprint(),
    )

    assert RetrievalService(catalog, index).search("candidate density", limit=5) == []


def test_library_cli_lists_index_and_search_commands() -> None:
    result = CliRunner().invoke(app, ["library", "--help"])

    assert result.exit_code == 0
    assert "import-manifest" in result.stdout
    assert "build-index" in result.stdout
    assert "search" in result.stdout
