"""Rebuildable FTS5 and Chroma indexes for active child chunks."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path

from ped_knowledge.contracts import EmbeddingGateway, IndexHit


def tokenize_for_search(text: str) -> str:
    try:
        import jieba
    except ImportError as exc:
        raise RuntimeError("jieba is required for multilingual FTS tokenization") from exc
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    tokens: list[str] = []
    for token in jieba.cut(normalized):
        cleaned = token.strip()
        if cleaned and re.search(r"[0-9a-z\u4e00-\u9fff]", cleaned):
            tokens.append(cleaned)
    return " ".join(tokens)


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
                version_id UNINDEXED,
                title,
                heading,
                body,
                locator UNINDEXED,
                tokenize='unicode61'
            )
            """
        )
        connection.executemany(
            "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    item["chunk_id"],
                    item["resource_id"],
                    item.get("version_id", ""),
                    tokenize_for_search(str(item["title"])),
                    tokenize_for_search(_heading_text(item.get("heading_path"))),
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
                SELECT chunk_id, bm25(documents, 0, 0, 0, 3.0, 1.5, 1.0, 0) AS rank
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


class ChromaVectorIndex:
    collection_name = "ped_agent_official_evidence"

    def __init__(
        self,
        path: Path,
        embedding_gateway: EmbeddingGateway,
        *,
        batch_size: int = 64,
    ) -> None:
        self.path = path
        self.embedding_gateway = embedding_gateway
        self.batch_size = batch_size

    @property
    def catalog_fingerprint(self) -> str:
        return str(self._metadata().get("catalog_fingerprint", ""))

    @property
    def embedding_fingerprint(self) -> str:
        return str(self._metadata().get("embedding_fingerprint", ""))

    async def search(self, query: str, *, limit: int = 20) -> list[IndexHit]:
        vector = (await self.embedding_gateway.embed([query]))[0]
        result = self._collection().query(query_embeddings=[vector], n_results=limit)
        ids = result.get("ids", [[]])[0]
        distances = result.get("distances", [[]])[0]
        return [
            IndexHit(chunk_id=chunk_id, score=-float(distance))
            for chunk_id, distance in zip(ids, distances, strict=False)
        ]

    async def rebuild(
        self,
        chunks: list[dict[str, object]],
        *,
        catalog_fingerprint: str,
        embedding_fingerprint: str,
    ) -> None:
        client = self._client()
        existing = {collection.name for collection in client.list_collections()}
        if self.collection_name in existing:
            client.delete_collection(self.collection_name)
        collection = client.create_collection(
            self.collection_name,
            metadata={
                "catalog_fingerprint": catalog_fingerprint,
                "embedding_fingerprint": embedding_fingerprint,
            },
        )
        for start in range(0, len(chunks), self.batch_size):
            batch = chunks[start : start + self.batch_size]
            texts = [str(item["text"]) for item in batch]
            vectors = await self.embedding_gateway.embed(texts)
            collection.add(
                ids=[str(item["chunk_id"]) for item in batch],
                embeddings=vectors,
                documents=texts,
                metadatas=[
                    {
                        "resource_id": str(item["resource_id"]),
                        "version_id": str(item["version_id"]),
                        "policy_version": str(item.get("policy_version", "legacy-v1")),
                    }
                    for item in batch
                ],
            )

    def _metadata(self) -> dict[str, object]:
        try:
            return dict(self._collection().metadata or {})
        except Exception:  # noqa: BLE001 - unavailable indexes expose empty metadata.
            return {}

    def _client(self):
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError("chromadb is required for dense retrieval") from exc
        self.path.mkdir(parents=True, exist_ok=True)
        return chromadb.PersistentClient(path=str(self.path))

    def _collection(self):
        return self._client().get_or_create_collection(self.collection_name)


def embedding_fingerprint(*, model: str, base_url: str | None, dimensions: int | None) -> str:
    payload = json.dumps(
        {"model": model, "base_url": base_url, "dimensions": dimensions},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _heading_text(value: object) -> str:
    if not isinstance(value, (tuple, list)):
        return ""
    return " > ".join(str(item) for item in value)


__all__ = [
    "ChromaVectorIndex",
    "FTSIndex",
    "IndexHit",
    "embedding_fingerprint",
    "tokenize_for_search",
]
