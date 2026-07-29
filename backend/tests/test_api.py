from pathlib import Path

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from ped_agent.api import create_app
from ped_agent.catalog import Catalog
from ped_agent.cli import app
from ped_agent.index import FTSIndex
from ped_agent.models import ResourceManifest, ResourceType


def create_client(tmp_path: Path, *, fingerprint: str | None = None) -> TestClient:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    index = FTSIndex(tmp_path / "fts.sqlite3")
    index.rebuild(
        [],
        source_fingerprint=fingerprint or catalog.official_fingerprint(),
    )
    return TestClient(create_app(catalog_path=catalog.path, index_path=index.path))


def test_api_is_read_only_and_exposes_library_routes(tmp_path: Path) -> None:
    client = create_client(tmp_path)

    assert client.get("/api/library/resources").status_code == 200
    assert client.get("/api/library/search", params={"q": "density"}).status_code == 200
    assert client.post("/api/library/resources").status_code == 405


def test_api_returns_resource_detail_and_not_found(tmp_path: Path) -> None:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    record = ResourceManifest(
        resource_id="paper-api-2026",
        resource_type=ResourceType.LITERATURE,
        title="API paper",
        language="en",
        source_path=tmp_path / "paper.pdf",
        sha256="a" * 64,
        doi="10.1000/api",
        include=True,
    )
    catalog.upsert_resource(record, version_id=record.sha256, vault_path="objects/aa/api.pdf")
    FTSIndex(tmp_path / "fts.sqlite3").rebuild(
        [], source_fingerprint=catalog.official_fingerprint()
    )
    client = TestClient(create_app(catalog_path=catalog.path, index_path=tmp_path / "fts.sqlite3"))

    response = client.get(f"/api/library/resources/{record.resource_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "API paper"
    assert client.get("/api/library/resources/missing").status_code == 404


def test_api_reports_stale_index_as_service_unavailable(tmp_path: Path) -> None:
    client = create_client(tmp_path, fingerprint="stale")

    response = client.get("/api/library/search", params={"q": "density"})

    assert response.status_code == 503
    assert "index is stale" in response.json()["detail"]


def test_cli_lists_local_serve_command() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "serve" in result.stdout
