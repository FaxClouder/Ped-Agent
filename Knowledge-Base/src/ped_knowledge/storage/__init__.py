"""Catalog, content vault, version activation, and derived-asset persistence."""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from ped_knowledge.contracts import VersionStatus, normalize_doi

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS resources (
    resource_id TEXT PRIMARY KEY,
    resource_type TEXT NOT NULL,
    title TEXT NOT NULL,
    language TEXT NOT NULL,
    admission_status TEXT NOT NULL,
    retrieval_eligibility TEXT NOT NULL,
    canonical_metadata TEXT NOT NULL,
    active_version_id TEXT
);
CREATE TABLE IF NOT EXISTS resource_versions (
    version_id TEXT PRIMARY KEY,
    resource_id TEXT NOT NULL REFERENCES resources(resource_id),
    sha256 TEXT NOT NULL,
    vault_path TEXT NOT NULL,
    source_path TEXT NOT NULL,
    canonical_metadata TEXT,
    status TEXT NOT NULL DEFAULT 'staged',
    derived_path TEXT,
    parser_version TEXT,
    chunk_policy_version TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_versions_resource ON resource_versions(resource_id, created_at);
CREATE TABLE IF NOT EXISTS chunks (
    chunk_id TEXT PRIMARY KEY,
    resource_id TEXT NOT NULL REFERENCES resources(resource_id),
    version_id TEXT NOT NULL REFERENCES resource_versions(version_id),
    ordinal INTEGER NOT NULL,
    text TEXT NOT NULL,
    page_start INTEGER NOT NULL,
    page_end INTEGER NOT NULL,
    locator TEXT NOT NULL,
    section TEXT,
    parser_version TEXT NOT NULL,
    chunk_level TEXT NOT NULL DEFAULT 'child',
    parent_chunk_id TEXT,
    heading_path TEXT NOT NULL DEFAULT '[]',
    policy_version TEXT NOT NULL DEFAULT 'legacy-v1',
    element_ids TEXT NOT NULL DEFAULT '[]'
);
CREATE INDEX IF NOT EXISTS idx_chunks_resource ON chunks(resource_id, version_id, ordinal);
CREATE TABLE IF NOT EXISTS resource_relations (
    source_resource_id TEXT NOT NULL REFERENCES resources(resource_id),
    relation_type TEXT NOT NULL,
    target_ref TEXT NOT NULL,
    PRIMARY KEY (source_resource_id, relation_type, target_ref)
);
CREATE TABLE IF NOT EXISTS resource_identifiers (
    identifier_type TEXT NOT NULL,
    identifier_value TEXT NOT NULL,
    resource_id TEXT NOT NULL REFERENCES resources(resource_id),
    PRIMARY KEY (identifier_type, identifier_value),
    UNIQUE (resource_id, identifier_type)
);
CREATE TABLE IF NOT EXISTS derived_assets (
    resource_id TEXT NOT NULL REFERENCES resources(resource_id),
    version_id TEXT NOT NULL REFERENCES resource_versions(version_id),
    asset_type TEXT NOT NULL,
    relative_path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    PRIMARY KEY (version_id, asset_type, relative_path)
);
CREATE TABLE IF NOT EXISTS retrieval_configs (
    config_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    payload TEXT NOT NULL,
    evaluation_report TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    activated_at TEXT
);
"""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class ContentVault:
    def __init__(self, root: Path) -> None:
        self.root = root

    def put(self, source: Path, expected_sha256: str) -> Path:
        actual = sha256_file(source)
        if actual != expected_sha256:
            raise ValueError(f"SHA-256 mismatch for {source}")
        suffix = source.suffix.lower() or ".bin"
        target = self.root / actual[:2] / f"{actual}{suffix}"
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)
        return target


class Catalog:
    def __init__(self, path: Path) -> None:
        self.path = path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(SCHEMA)
            self._migrate_existing_schema(connection)
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_chunks_parent ON chunks(parent_chunk_id)"
            )
            self._backfill_doi_identifiers(connection)
            self._backfill_version_metadata(connection)
            self._backfill_active_versions(connection)

    def upsert_resource(
        self,
        record: Any,
        *,
        version_id: str,
        vault_path: str,
    ) -> None:
        """Compatibility entrypoint that immediately activates a valid version."""
        self._save_resource(record, version_id=version_id, vault_path=vault_path, activate=True)

    def stage_resource(
        self,
        record: Any,
        *,
        version_id: str,
        vault_path: str,
    ) -> None:
        self._save_resource(record, version_id=version_id, vault_path=vault_path, activate=False)

    def _save_resource(
        self,
        record: Any,
        *,
        version_id: str,
        vault_path: str,
        activate: bool,
    ) -> None:
        metadata = _model_dump(record)
        resource_id = str(record.resource_id)
        resource_type = _enum_value(record.resource_type)
        sha256 = str(record.sha256)
        retrieval_status = (
            _enum_value(getattr(record, "retrieval_eligibility", "official"))
            if activate
            else "staging"
        )
        with self.connect() as connection:
            self._reject_identifier_conflict(connection, record)
            self._reject_hash_conflict(connection, resource_id, sha256)
            connection.execute(
                """
                INSERT OR IGNORE INTO resources
                    (resource_id, resource_type, title, language, admission_status,
                     retrieval_eligibility, canonical_metadata, active_version_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
                """,
                (
                    resource_id,
                    resource_type,
                    str(record.title),
                    str(record.language),
                    _enum_value(getattr(record, "admission_status", "approved")),
                    retrieval_status,
                    json.dumps(metadata, ensure_ascii=False),
                ),
            )
            self._replace_doi_identifier(connection, record)
            status = VersionStatus.ACTIVE.value if activate else VersionStatus.STAGED.value
            connection.execute(
                """
                INSERT INTO resource_versions
                    (version_id, resource_id, sha256, vault_path, source_path,
                     canonical_metadata, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(version_id) DO UPDATE SET
                    vault_path=excluded.vault_path,
                    source_path=excluded.source_path,
                    canonical_metadata=excluded.canonical_metadata,
                    status=excluded.status
                """,
                (
                    version_id,
                    resource_id,
                    sha256,
                    vault_path,
                    str(record.source_path),
                    json.dumps(metadata, ensure_ascii=False),
                    status,
                ),
            )
            self._replace_relations(connection, record)
            if activate:
                self._activate_version(connection, resource_id, version_id)

    def replace_chunks(self, version_id: str, chunks: Sequence[Any]) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM chunks WHERE version_id = ?", (version_id,))
            connection.executemany(
                """
                INSERT INTO chunks
                    (chunk_id, resource_id, version_id, ordinal, text, page_start,
                     page_end, locator, section, parser_version, chunk_level,
                     parent_chunk_id, heading_path, policy_version, element_ids)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        str(item.chunk_id),
                        str(item.resource_id),
                        str(item.version_id),
                        int(item.ordinal),
                        str(item.text),
                        int(item.page_start),
                        int(item.page_end),
                        str(item.locator),
                        getattr(item, "section", None),
                        str(item.parser_version),
                        _enum_value(getattr(item, "chunk_level", "child")),
                        getattr(item, "parent_chunk_id", None),
                        json.dumps(list(getattr(item, "heading_path", ())), ensure_ascii=False),
                        str(getattr(item, "policy_version", "legacy-v1")),
                        json.dumps(list(getattr(item, "element_ids", ())), ensure_ascii=False),
                    )
                    for item in chunks
                ],
            )

    def set_version_derivation(
        self,
        version_id: str,
        *,
        derived_path: str,
        parser_version: str,
        chunk_policy_version: str,
    ) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                UPDATE resource_versions
                SET derived_path = ?, parser_version = ?, chunk_policy_version = ?
                WHERE version_id = ?
                """,
                (derived_path, parser_version, chunk_policy_version, version_id),
            )

    def register_derived_assets(
        self,
        resource_id: str,
        version_id: str,
        assets: list[tuple[str, str, str]],
    ) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM derived_assets WHERE version_id = ?", (version_id,))
            connection.executemany(
                """
                INSERT INTO derived_assets
                    (resource_id, version_id, asset_type, relative_path, content_hash)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (resource_id, version_id, asset_type, relative_path, content_hash)
                    for asset_type, relative_path, content_hash in assets
                ],
            )

    def activate_version(self, resource_id: str, version_id: str) -> None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT status FROM resource_versions WHERE resource_id = ? AND version_id = ?",
                (resource_id, version_id),
            ).fetchone()
            if row is None:
                raise ValueError(f"unknown version {version_id} for {resource_id}")
            if row["status"] == VersionStatus.FAILED.value:
                raise ValueError(f"failed version cannot be activated: {version_id}")
            self._activate_version(connection, resource_id, version_id)

    def mark_version_failed(self, version_id: str) -> None:
        with self.connect() as connection:
            connection.execute(
                "UPDATE resource_versions SET status = ? WHERE version_id = ?",
                (VersionStatus.FAILED.value, version_id),
            )

    def get_resource(self, resource_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM resources WHERE resource_id = ?", (resource_id,)
            ).fetchone()
        if row is None:
            return None
        return _hydrate_resource_row(row)

    def list_resources(
        self,
        resource_type: str | None = None,
        *,
        topic: str | None = None,
        year: str | None = None,
        effective_status: str | None = None,
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM resources"
        params: tuple[str, ...] = ()
        if resource_type:
            query += " WHERE resource_type = ?"
            params = (resource_type,)
        query += " ORDER BY title"
        with self.connect() as connection:
            rows = [_hydrate_resource_row(row) for row in connection.execute(query, params)]
        results: list[dict[str, Any]] = []
        for row in rows:
            metadata = row["canonical_metadata"]
            if topic and topic not in metadata.get("topics", []):
                continue
            if year and not str(metadata.get("published_date", "")).startswith(year):
                continue
            if effective_status and metadata.get("effective_status") != effective_status:
                continue
            results.append(row)
        return results

    def list_versions(self, resource_id: str) -> list[dict[str, Any]]:
        with self.connect() as connection:
            return [
                dict(row)
                for row in connection.execute(
                    """
                    SELECT * FROM resource_versions
                    WHERE resource_id = ? ORDER BY created_at, version_id
                    """,
                    (resource_id,),
                )
            ]

    def list_official_chunks(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            return [
                _hydrate_chunk_row(row)
                for row in connection.execute(
                    """
                    SELECT c.*, r.title, r.resource_type, r.retrieval_eligibility,
                           r.canonical_metadata
                    FROM chunks c
                    JOIN resources r ON r.resource_id = c.resource_id
                    WHERE r.retrieval_eligibility = 'official'
                      AND c.version_id = r.active_version_id
                      AND c.chunk_level = 'child'
                    ORDER BY c.resource_id, c.ordinal
                    """
                )
            ]

    def hydrate_chunk(self, chunk_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT c.*, r.title, r.resource_type, r.retrieval_eligibility,
                       r.canonical_metadata, r.active_version_id
                FROM chunks c
                JOIN resources r ON r.resource_id = c.resource_id
                WHERE c.chunk_id = ?
                """,
                (chunk_id,),
            ).fetchone()
        return None if row is None else _hydrate_chunk_row(row)

    def context_for_chunk(self, chunk_id: str) -> str:
        row = self.hydrate_chunk(chunk_id)
        if row is None:
            return ""
        parent_id = row.get("parent_chunk_id")
        if not parent_id:
            return str(row["text"])
        parent = self.hydrate_chunk(str(parent_id))
        return str(parent["text"]) if parent is not None else str(row["text"])

    def list_relations(self, resource_id: str) -> list[dict[str, str]]:
        with self.connect() as connection:
            return [
                {"relation_type": row["relation_type"], "target_ref": row["target_ref"]}
                for row in connection.execute(
                    """
                    SELECT relation_type, target_ref FROM resource_relations
                    WHERE source_resource_id = ? ORDER BY relation_type, target_ref
                    """,
                    (resource_id,),
                )
            ]

    def official_fingerprint(self) -> str:
        digest = hashlib.sha256()
        for chunk in self.list_official_chunks():
            digest.update(str(chunk["chunk_id"]).encode("utf-8"))
            digest.update(str(chunk["text"]).encode("utf-8"))
        return digest.hexdigest()

    def register_retrieval_config(
        self,
        config_id: str,
        payload: dict[str, Any],
        evaluation_report: dict[str, Any] | None,
        *,
        activate: bool,
    ) -> None:
        with self.connect() as connection:
            status = "active" if activate else "candidate"
            if activate:
                connection.execute(
                    "UPDATE retrieval_configs SET status = 'superseded' WHERE status = 'active'"
                )
            connection.execute(
                """
                INSERT INTO retrieval_configs
                    (config_id, status, payload, evaluation_report, activated_at)
                VALUES (?, ?, ?, ?, CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE NULL END)
                ON CONFLICT(config_id) DO UPDATE SET
                    status=excluded.status,
                    payload=excluded.payload,
                    evaluation_report=excluded.evaluation_report,
                    activated_at=excluded.activated_at
                """,
                (
                    config_id,
                    status,
                    json.dumps(payload, ensure_ascii=False, sort_keys=True),
                    None
                    if evaluation_report is None
                    else json.dumps(evaluation_report, ensure_ascii=False, sort_keys=True),
                    int(activate),
                ),
            )

    def active_retrieval_config(self) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM retrieval_configs WHERE status = 'active' LIMIT 1"
            ).fetchone()
        if row is None:
            return None
        result = dict(row)
        result["payload"] = json.loads(result["payload"])
        if result["evaluation_report"]:
            result["evaluation_report"] = json.loads(result["evaluation_report"])
        return result

    def _migrate_existing_schema(self, connection: sqlite3.Connection) -> None:
        additions = {
            "resources": {"active_version_id": "TEXT"},
            "resource_versions": {
                "canonical_metadata": "TEXT",
                "status": "TEXT NOT NULL DEFAULT 'staged'",
                "derived_path": "TEXT",
                "parser_version": "TEXT",
                "chunk_policy_version": "TEXT",
            },
            "chunks": {
                "chunk_level": "TEXT NOT NULL DEFAULT 'child'",
                "parent_chunk_id": "TEXT",
                "heading_path": "TEXT NOT NULL DEFAULT '[]'",
                "policy_version": "TEXT NOT NULL DEFAULT 'legacy-v1'",
                "element_ids": "TEXT NOT NULL DEFAULT '[]'",
            },
        }
        for table, columns in additions.items():
            existing = {
                row["name"] for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
            }
            for name, declaration in columns.items():
                if name not in existing:
                    connection.execute(f"ALTER TABLE {table} ADD COLUMN {name} {declaration}")

    def _backfill_doi_identifiers(self, connection: sqlite3.Connection) -> None:
        for row in connection.execute(
            "SELECT resource_id, canonical_metadata FROM resources"
        ).fetchall():
            metadata = json.loads(row["canonical_metadata"])
            normalized = normalize_doi(metadata.get("doi"))
            if normalized:
                connection.execute(
                    """
                    INSERT OR IGNORE INTO resource_identifiers
                        (identifier_type, identifier_value, resource_id)
                    VALUES ('doi', ?, ?)
                    """,
                    (normalized, row["resource_id"]),
                )

    def _backfill_active_versions(self, connection: sqlite3.Connection) -> None:
        resources = connection.execute(
            "SELECT resource_id FROM resources WHERE active_version_id IS NULL"
        ).fetchall()
        for resource in resources:
            version = connection.execute(
                """
                SELECT version_id FROM resource_versions
                WHERE resource_id = ? ORDER BY created_at DESC, version_id DESC LIMIT 1
                """,
                (resource["resource_id"],),
            ).fetchone()
            if version is not None:
                self._activate_version(connection, resource["resource_id"], version["version_id"])

    @staticmethod
    def _backfill_version_metadata(connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            UPDATE resource_versions
            SET canonical_metadata = (
                SELECT resources.canonical_metadata FROM resources
                WHERE resources.resource_id = resource_versions.resource_id
            )
            WHERE canonical_metadata IS NULL
            """
        )

    def _replace_doi_identifier(self, connection: sqlite3.Connection, record: Any) -> None:
        resource_id = str(record.resource_id)
        connection.execute(
            "DELETE FROM resource_identifiers WHERE resource_id = ? AND identifier_type = 'doi'",
            (resource_id,),
        )
        normalized = normalize_doi(getattr(record, "doi", None))
        if normalized:
            connection.execute(
                """
                INSERT INTO resource_identifiers
                    (identifier_type, identifier_value, resource_id)
                VALUES ('doi', ?, ?)
                """,
                (normalized, resource_id),
            )

    def _replace_relations(self, connection: sqlite3.Connection, record: Any) -> None:
        resource_id = str(record.resource_id)
        connection.execute(
            "DELETE FROM resource_relations WHERE source_resource_id = ?", (resource_id,)
        )
        relations = [
            (resource_id, "supersedes", target) for target in getattr(record, "supersedes", [])
        ] + [(resource_id, "uses_dataset", target) for target in getattr(record, "datasets", [])]
        connection.executemany(
            """
            INSERT INTO resource_relations (source_resource_id, relation_type, target_ref)
            VALUES (?, ?, ?)
            """,
            relations,
        )

    def _reject_identifier_conflict(
        self,
        connection: sqlite3.Connection,
        record: Any,
    ) -> None:
        normalized = normalize_doi(getattr(record, "doi", None))
        if not normalized:
            return
        row = connection.execute(
            """
            SELECT resource_id FROM resource_identifiers
            WHERE identifier_type = 'doi' AND identifier_value = ?
            """,
            (normalized,),
        ).fetchone()
        resource_id = str(record.resource_id)
        if row is not None and row["resource_id"] != resource_id:
            raise ValueError(f"DOI already belongs to {row['resource_id']}")

    @staticmethod
    def _reject_hash_conflict(
        connection: sqlite3.Connection,
        resource_id: str,
        sha256: str,
    ) -> None:
        row = connection.execute(
            "SELECT resource_id FROM resource_versions WHERE sha256 = ?", (sha256,)
        ).fetchone()
        if row is not None and row["resource_id"] != resource_id:
            raise ValueError(f"SHA-256 already belongs to {row['resource_id']}")

    @staticmethod
    def _activate_version(
        connection: sqlite3.Connection,
        resource_id: str,
        version_id: str,
    ) -> None:
        version = connection.execute(
            """
            SELECT canonical_metadata FROM resource_versions
            WHERE resource_id = ? AND version_id = ?
            """,
            (resource_id, version_id),
        ).fetchone()
        if version is None:
            raise ValueError(f"unknown version {version_id} for {resource_id}")
        metadata = json.loads(version["canonical_metadata"] or "{}")
        include = bool(metadata.get("include", True))
        admission_status = metadata.get("admission_status") or (
            "approved" if include else "candidate"
        )
        retrieval_eligibility = metadata.get("retrieval_eligibility") or (
            "official" if include else "excluded"
        )
        connection.execute(
            """
            UPDATE resource_versions SET status = ?
            WHERE resource_id = ? AND version_id <> ? AND status = ?
            """,
            (
                VersionStatus.SUPERSEDED.value,
                resource_id,
                version_id,
                VersionStatus.ACTIVE.value,
            ),
        )
        connection.execute(
            "UPDATE resource_versions SET status = ? WHERE version_id = ?",
            (VersionStatus.ACTIVE.value, version_id),
        )
        connection.execute(
            """
            UPDATE resources
            SET resource_type = ?, title = ?, language = ?, admission_status = ?,
                retrieval_eligibility = ?, canonical_metadata = ?, active_version_id = ?
            WHERE resource_id = ?
            """,
            (
                metadata.get("resource_type", "literature"),
                metadata.get("title", resource_id),
                metadata.get("language", "unknown"),
                _enum_value(admission_status),
                _enum_value(retrieval_eligibility),
                json.dumps(metadata, ensure_ascii=False),
                version_id,
                resource_id,
            ),
        )


def _enum_value(value: object) -> str:
    return str(getattr(value, "value", value))


def _model_dump(record: Any) -> dict[str, Any]:
    return dict(record.model_dump(mode="json"))


def _hydrate_resource_row(row: sqlite3.Row) -> dict[str, Any]:
    result = dict(row)
    result["canonical_metadata"] = json.loads(result["canonical_metadata"])
    return result


def _hydrate_chunk_row(row: sqlite3.Row) -> dict[str, Any]:
    result = dict(row)
    result["canonical_metadata"] = json.loads(result["canonical_metadata"])
    result["heading_path"] = tuple(json.loads(result.get("heading_path") or "[]"))
    result["element_ids"] = tuple(json.loads(result.get("element_ids") or "[]"))
    return result


__all__ = ["Catalog", "ContentVault", "SCHEMA", "sha256_file"]
