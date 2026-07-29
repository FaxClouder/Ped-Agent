from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

from ped_agent.tokenization import tokenize_for_search


@dataclass(frozen=True)
class IndexHit:
    chunk_id: str
    score: float


class FTSIndex:
    def __init__(self, path: Path) -> None:
        self.path = path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def rebuild(self, chunks: list[dict[str, object]], *, source_fingerprint: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.unlink(missing_ok=True)
        try:
            with closing(sqlite3.connect(temporary)) as connection, connection:
                self._create_index(connection, chunks, source_fingerprint)
            temporary.replace(self.path)
        finally:
            temporary.unlink(missing_ok=True)

    @staticmethod
    def _create_index(
        connection: sqlite3.Connection,
        chunks: list[dict[str, object]],
        source_fingerprint: str,
    ) -> None:
        connection.execute(
            """
            CREATE VIRTUAL TABLE documents USING fts5(
                chunk_id UNINDEXED,
                resource_id UNINDEXED,
                title,
                body,
                locator UNINDEXED,
                tokenize='unicode61'
            )
            """
        )
        connection.executemany(
            "INSERT INTO documents VALUES (?, ?, ?, ?, ?)",
            [
                (
                    item["chunk_id"],
                    item["resource_id"],
                    tokenize_for_search(str(item["title"])),
                    tokenize_for_search(str(item["text"])),
                    item["locator"],
                )
                for item in chunks
            ],
        )
        connection.execute(
            "CREATE TABLE index_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO index_metadata VALUES ('source_fingerprint', ?)",
            (source_fingerprint,),
        )

    def search(self, query: str, *, limit: int = 5) -> list[IndexHit]:
        tokenized = tokenize_for_search(query)
        if not tokenized:
            return []
        match_query = " AND ".join(
            f'"{token.replace(chr(34), chr(34) * 2)}"' for token in tokenized.split()
        )
        with closing(self.connect()) as connection:
            rows = connection.execute(
                """
                SELECT chunk_id, bm25(documents) AS rank
                FROM documents
                WHERE documents MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (match_query, limit),
            ).fetchall()
        return [IndexHit(chunk_id=row["chunk_id"], score=-float(row["rank"])) for row in rows]

    def source_fingerprint(self) -> str:
        if not self.path.exists():
            return ""
        try:
            with closing(self.connect()) as connection:
                row = connection.execute(
                    "SELECT value FROM index_metadata WHERE key = 'source_fingerprint'"
                ).fetchone()
        except sqlite3.OperationalError:
            return ""
        return "" if row is None else str(row["value"])
