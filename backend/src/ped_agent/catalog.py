from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from ped_agent.models import CanonicalChunk, ResourceManifest

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS resources (
    resource_id TEXT PRIMARY KEY,
    resource_type TEXT NOT NULL,
    title TEXT NOT NULL,
    language TEXT NOT NULL,
    admission_status TEXT NOT NULL,
    retrieval_eligibility TEXT NOT NULL,
    canonical_metadata TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS resource_versions (
    version_id TEXT PRIMARY KEY,
    resource_id TEXT NOT NULL REFERENCES resources(resource_id),
    sha256 TEXT NOT NULL,
    vault_path TEXT NOT NULL,
    source_path TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
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
    parser_version TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_chunks_resource ON chunks(resource_id, version_id, ordinal);
CREATE TABLE IF NOT EXISTS resource_relations (
    source_resource_id TEXT NOT NULL REFERENCES resources(resource_id),
    relation_type TEXT NOT NULL,
    target_ref TEXT NOT NULL,
    PRIMARY KEY (source_resource_id, relation_type, target_ref)
);
"""


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

    def upsert_resource(
        self,
        record: ResourceManifest,
        *,
        version_id: str,
        vault_path: str,
    ) -> None:
        metadata = record.model_dump(mode="json")
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO resources VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(resource_id) DO UPDATE SET
                    resource_type=excluded.resource_type,
                    title=excluded.title,
                    language=excluded.language,
                    admission_status=excluded.admission_status,
                    retrieval_eligibility=excluded.retrieval_eligibility,
                    canonical_metadata=excluded.canonical_metadata
                """,
                (
                    record.resource_id,
                    record.resource_type.value,
                    record.title,
                    record.language,
                    record.admission_status.value,
                    record.retrieval_eligibility.value,
                    json.dumps(metadata, ensure_ascii=False),
                ),
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO resource_versions
                    (version_id, resource_id, sha256, vault_path, source_path)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    version_id,
                    record.resource_id,
                    record.sha256,
                    vault_path,
                    str(record.source_path),
                ),
            )
            connection.execute(
                "DELETE FROM resource_relations WHERE source_resource_id = ?",
                (record.resource_id,),
            )
            connection.executemany(
                """
                INSERT INTO resource_relations (source_resource_id, relation_type, target_ref)
                VALUES (?, ?, ?)
                """,
                [(record.resource_id, "supersedes", target) for target in record.supersedes]
                + [(record.resource_id, "uses_dataset", target) for target in record.datasets],
            )

    def replace_chunks(self, version_id: str, chunks: list[CanonicalChunk]) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM chunks WHERE version_id = ?", (version_id,))
            connection.executemany(
                """
                INSERT INTO chunks
                    (chunk_id, resource_id, version_id, ordinal, text, page_start,
                     page_end, locator, section, parser_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        item.chunk_id,
                        item.resource_id,
                        item.version_id,
                        item.ordinal,
                        item.text,
                        item.page_start,
                        item.page_end,
                        item.locator,
                        item.section,
                        item.parser_version,
                    )
                    for item in chunks
                ],
            )

    def get_resource(self, resource_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM resources WHERE resource_id = ?", (resource_id,)
            ).fetchone()
            if row is None:
                return None
            result = dict(row)
            result["canonical_metadata"] = json.loads(result["canonical_metadata"])
            return result

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
            rows = [dict(row) for row in connection.execute(query, params)]
        results: list[dict[str, Any]] = []
        for row in rows:
            metadata = json.loads(row["canonical_metadata"])
            row["canonical_metadata"] = metadata
            if topic and topic not in metadata.get("topics", []):
                continue
            if year and not str(metadata.get("published_date", "")).startswith(year):
                continue
            if effective_status and metadata.get("effective_status") != effective_status:
                continue
            results.append(row)
        return results

    def list_official_chunks(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            return [
                dict(row)
                for row in connection.execute(
                    """
                    SELECT c.*, r.title, r.resource_type, r.canonical_metadata
                    FROM chunks c
                    JOIN resources r ON r.resource_id = c.resource_id
                    WHERE r.retrieval_eligibility = 'official'
                    ORDER BY c.resource_id, c.ordinal
                    """
                )
            ]

    def hydrate_chunk(self, chunk_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT c.*, r.title, r.resource_type, r.retrieval_eligibility,
                       r.canonical_metadata
                FROM chunks c
                JOIN resources r ON r.resource_id = c.resource_id
                WHERE c.chunk_id = ?
                """,
                (chunk_id,),
            ).fetchone()
            if row is None:
                return None
            result = dict(row)
            result["canonical_metadata"] = json.loads(result["canonical_metadata"])
            return result

    def list_relations(self, resource_id: str) -> list[dict[str, str]]:
        with self.connect() as connection:
            return [
                {
                    "relation_type": row["relation_type"],
                    "target_ref": row["target_ref"],
                }
                for row in connection.execute(
                    """
                    SELECT relation_type, target_ref
                    FROM resource_relations
                    WHERE source_resource_id = ?
                    ORDER BY relation_type, target_ref
                    """,
                    (resource_id,),
                )
            ]

    def official_fingerprint(self) -> str:
        digest = hashlib.sha256()
        for chunk in self.list_official_chunks():
            digest.update(chunk["chunk_id"].encode("utf-8"))
            digest.update(chunk["text"].encode("utf-8"))
        return digest.hexdigest()
