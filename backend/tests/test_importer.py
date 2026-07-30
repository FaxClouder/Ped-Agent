import hashlib
import json
from pathlib import Path

import fitz
import pytest
from typer.testing import CliRunner

from ped_agent_server.catalog import Catalog
from ped_agent_server.cli import app
from ped_agent_server.importer import ImportService
from ped_agent_server.manifest import ManifestPreflightError
from ped_agent_server.paths import WorkspacePaths
from tests.manifest_samples import literature_data


def create_pdf(path: Path) -> str:
    with fitz.open() as document:
        page = document.new_page()
        page.insert_text((72, 72), "Pedestrian bottleneck density evidence.")
        document.save(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_import_is_idempotent_and_stores_official_chunks(tmp_path: Path) -> None:
    paths = WorkspacePaths.from_repo_root(tmp_path)
    source = tmp_path / "paper.pdf"
    digest = create_pdf(source)
    manifest = tmp_path / "manifest.jsonl"
    manifest.write_text(
        json.dumps(
            literature_data(
                resource_id="paper-import-2026",
                title="Import paper",
                source_path=source,
                sha256=digest,
                doi="10.1000/import",
            ),
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )
    service = ImportService(paths)

    first = service.import_manifest(manifest)
    second = service.import_manifest(manifest)

    assert first.imported == 1
    assert second.unchanged == 1
    assert len(Catalog(paths.catalog_path).list_official_chunks()) == 1


def test_import_isolates_one_processing_failure(tmp_path: Path) -> None:
    paths = WorkspacePaths.from_repo_root(tmp_path)
    good = tmp_path / "good.pdf"
    good_hash = create_pdf(good)
    bad = tmp_path / "bad.pdf"
    bad.write_bytes(b"not-a-pdf")
    bad_hash = hashlib.sha256(bad.read_bytes()).hexdigest()
    manifest = tmp_path / "mixed.jsonl"
    records = [
        literature_data(
            resource_id="paper-good-2026",
            title="Good paper",
            source_path=good,
            sha256=good_hash,
            doi="10.1000/good",
        ),
        literature_data(
            resource_id="paper-bad-2026",
            title="Bad paper",
            source_path=bad,
            sha256=bad_hash,
            doi="10.1000/bad",
        ),
    ]
    manifest.write_text(
        "\n".join(json.dumps(item, default=str) for item in records) + "\n",
        encoding="utf-8",
    )

    report = ImportService(paths).import_manifest(manifest)

    assert report.imported == 1
    assert report.failures[0].resource_id == "paper-bad-2026"
    assert Catalog(paths.catalog_path).get_resource("paper-good-2026") is not None


def test_import_preflight_failure_does_not_create_library_storage(tmp_path: Path) -> None:
    paths = WorkspacePaths.from_repo_root(tmp_path)
    source = tmp_path / "paper.pdf"
    create_pdf(source)
    manifest = tmp_path / "invalid.jsonl"
    manifest.write_text(
        json.dumps(
            literature_data(
                resource_id="paper-invalid-2026",
                title="Invalid paper",
                source_path=source,
                sha256="0" * 64,
                doi="10.1000/invalid",
            ),
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ManifestPreflightError):
        ImportService(paths).import_manifest(manifest)

    assert not paths.library_root.exists()


def test_cli_exposes_library_command_group() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "library" in result.stdout
