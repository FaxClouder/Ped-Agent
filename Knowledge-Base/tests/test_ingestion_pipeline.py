from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import fitz

from ped_knowledge.contracts import IngestionManifest
from ped_knowledge.ingestion import ImportService, preflight_manifest
from ped_knowledge.storage import Catalog


@dataclass(frozen=True)
class KnowledgeTestPaths:
    memped_root: Path
    catalog_path: Path
    derived_dir: Path
    reports_dir: Path
    literature_files_dir: Path
    regulations_files_dir: Path

    @classmethod
    def create(cls, root: Path) -> KnowledgeTestPaths:
        knowledge = root / "memPed" / "knowledge"
        return cls(
            memped_root=root / "memPed",
            catalog_path=knowledge / "knowledge.sqlite3",
            derived_dir=knowledge / "derived",
            reports_dir=knowledge / "reports",
            literature_files_dir=knowledge / "literature" / "files",
            regulations_files_dir=knowledge / "regulations" / "files",
        )

    def ensure_local_dirs(self) -> None:
        for path in (
            self.derived_dir,
            self.reports_dir,
            self.literature_files_dir,
            self.regulations_files_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)

    def resource_files_dir(self, resource_type: str) -> Path:
        if resource_type in {"regulation", "standard"}:
            return self.regulations_files_dir
        return self.literature_files_dir


def _create_pdf(path: Path, text: str) -> str:
    with fitz.open() as document:
        page = document.new_page()
        page.insert_text((72, 72), text)
        document.save(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest(path: Path, source: Path, sha256: str) -> None:
    path.write_text(
        json.dumps(
            {
                "resource_id": "paper-minimal-2026",
                "resource_type": "literature",
                "title": "Minimal selected pedestrian paper",
                "language": "en",
                "source_path": str(source),
                "sha256": sha256,
                "doi": "10.1000/minimal",
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_minimal_selected_document_imports_without_academic_quality_fields(
    tmp_path: Path,
) -> None:
    source = tmp_path / "paper.pdf"
    manifest = tmp_path / "manifest.jsonl"
    _manifest(
        manifest,
        source,
        _create_pdf(source, "1 Introduction\nPedestrian density and speed evidence."),
    )

    preflight = preflight_manifest(manifest)
    report = ImportService(KnowledgeTestPaths.create(tmp_path)).import_manifest(manifest)
    catalog = Catalog(tmp_path / "memPed" / "knowledge" / "knowledge.sqlite3")

    assert preflight.is_valid is True
    assert report.imported == 1
    assert report.failures == ()
    resource = catalog.get_resource("paper-minimal-2026")
    assert resource is not None
    assert resource["active_version_id"] == preflight.records[0].sha256
    assert catalog.list_official_chunks()
    derived = (
        tmp_path
        / "memPed"
        / "knowledge"
        / "derived"
        / "paper-minimal-2026"
        / preflight.records[0].sha256
    )
    for filename in ("document.json", "elements.jsonl", "chunks.jsonl", "parse_report.json"):
        assert (derived / filename).is_file()
    with sqlite3.connect(catalog.path) as connection:
        levels = dict(connection.execute("SELECT chunk_level, COUNT(*) FROM chunks GROUP BY 1"))
    assert levels["parent"] >= 1
    assert levels["child"] >= 1


def test_new_version_becomes_active_and_old_chunks_leave_official_index(tmp_path: Path) -> None:
    paths = KnowledgeTestPaths.create(tmp_path)
    first = tmp_path / "first.pdf"
    manifest = tmp_path / "manifest.jsonl"
    first_hash = _create_pdf(first, "First active pedestrian evidence.")
    _manifest(manifest, first, first_hash)
    service = ImportService(paths)
    assert service.import_manifest(manifest).imported == 1

    second = tmp_path / "second.pdf"
    second_hash = _create_pdf(second, "Second active pedestrian evidence.")
    _manifest(manifest, second, second_hash)
    assert service.import_manifest(manifest).imported == 1

    catalog = Catalog(paths.catalog_path)
    resource = catalog.get_resource("paper-minimal-2026")
    versions = {
        item["version_id"]: item["status"]
        for item in catalog.list_versions(resource["resource_id"])
    }
    assert resource["active_version_id"] == second_hash
    assert versions[first_hash] == "superseded"
    assert versions[second_hash] == "active"
    assert {item["version_id"] for item in catalog.list_official_chunks()} == {second_hash}

    failed = IngestionManifest(
        resource_id="paper-minimal-2026",
        resource_type="literature",
        title="Failed replacement metadata",
        language="en",
        source_path=tmp_path / "failed.pdf",
        sha256="d" * 64,
        doi="10.1000/minimal",
    )
    catalog.stage_resource(failed, version_id=failed.sha256, vault_path="objects/failed.pdf")
    catalog.mark_version_failed(failed.sha256)

    unchanged = catalog.get_resource("paper-minimal-2026")
    assert unchanged["active_version_id"] == second_hash
    assert unchanged["title"] == "Minimal selected pedestrian paper"
    assert unchanged["canonical_metadata"]["title"] == "Minimal selected pedestrian paper"


def test_catalog_migrates_existing_phase_one_schema_in_place(tmp_path: Path) -> None:
    path = tmp_path / "legacy.sqlite3"
    metadata = json.dumps(
        {
            "resource_id": "legacy-paper",
            "resource_type": "literature",
            "title": "Legacy paper",
            "language": "en",
            "source_path": "legacy.pdf",
            "sha256": "e" * 64,
            "include": True,
        }
    )
    with sqlite3.connect(path) as connection:
        connection.executescript(
            """
            CREATE TABLE resources (
                resource_id TEXT PRIMARY KEY, resource_type TEXT, title TEXT, language TEXT,
                admission_status TEXT, retrieval_eligibility TEXT, canonical_metadata TEXT
            );
            CREATE TABLE resource_versions (
                version_id TEXT PRIMARY KEY, resource_id TEXT, sha256 TEXT, vault_path TEXT,
                source_path TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE chunks (
                chunk_id TEXT PRIMARY KEY, resource_id TEXT, version_id TEXT, ordinal INTEGER,
                text TEXT, page_start INTEGER, page_end INTEGER, locator TEXT, section TEXT,
                parser_version TEXT
            );
            CREATE TABLE resource_relations (
                source_resource_id TEXT, relation_type TEXT, target_ref TEXT,
                PRIMARY KEY (source_resource_id, relation_type, target_ref)
            );
            CREATE TABLE resource_identifiers (
                identifier_type TEXT, identifier_value TEXT, resource_id TEXT,
                PRIMARY KEY (identifier_type, identifier_value)
            );
            """
        )
        connection.execute(
            "INSERT INTO resources VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("legacy-paper", "literature", "Legacy paper", "en", "approved", "official", metadata),
        )
        connection.execute(
            "INSERT INTO resource_versions VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
            ("e" * 64, "legacy-paper", "e" * 64, "objects/legacy.pdf", "legacy.pdf"),
        )
        connection.execute(
            "INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "legacy-child",
                "legacy-paper",
                "e" * 64,
                0,
                "Legacy evidence",
                1,
                1,
                "p.1",
                None,
                "legacy-parser",
            ),
        )

    catalog = Catalog(path)
    catalog.initialize()

    assert catalog.get_resource("legacy-paper")["active_version_id"] == "e" * 64
    assert [item["chunk_id"] for item in catalog.list_official_chunks()] == ["legacy-child"]
