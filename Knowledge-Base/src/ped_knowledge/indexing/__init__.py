"""Rebuildable FTS5 and Chroma indexes for active child chunks."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path

from ped_knowledge.contracts import EmbeddingGateway, IndexHit
from ped_knowledge.tokenization import JiebaLexicalAnalyzer


def tokenize_for_search(text: str) -> str:
    return " ".join(JiebaLexicalAnalyzer().analyze(text))


class FTSIndex:
    def __init__(
        self,
        path: Path,
        analyzer: JiebaLexicalAnalyzer | None = None,
    ) -> None:
        self.path = path
        self.analyzer = analyzer or JiebaLexicalAnalyzer()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def rebuild(
        self,
        chunks: list[dict[str, object]],
        *,
        source_fingerprint: str,
        policy_version: str = "parent-child-v1",
        tokenizer_fingerprint: str = "regex-token-v1",
        gold_sha256: str = "",
        code_revision: str = "",
    ) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.unlink(missing_ok=True)
        try:
            with closing(sqlite3.connect(temporary)) as connection, connection:
                self._create_index(
                    connection,
                    chunks,
                    source_fingerprint,
                    self.analyzer,
                    policy_version,
                    tokenizer_fingerprint,
                    gold_sha256,
                    code_revision,
                )
            temporary.replace(self.path)
        finally:
            temporary.unlink(missing_ok=True)

    @staticmethod
    def _create_index(
        connection: sqlite3.Connection,
        chunks: list[dict[str, object]],
        source_fingerprint: str,
        analyzer: JiebaLexicalAnalyzer,
        policy_version: str,
        tokenizer_fingerprint: str,
        gold_sha256: str,
        code_revision: str,
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
                    " ".join(analyzer.analyze(str(item["title"]))),
                    " ".join(analyzer.analyze(_heading_text(item.get("heading_path")))),
                    " ".join(analyzer.analyze(str(item["text"]))),
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
        connection.execute(
            "INSERT INTO index_metadata VALUES ('lexical_analyzer_fingerprint', ?)",
            (analyzer.fingerprint,),
        )
        connection.executemany(
            "INSERT INTO index_metadata VALUES (?, ?)",
            [
                ("policy_version", policy_version),
                ("tokenizer_fingerprint", tokenizer_fingerprint),
                ("gold_sha256", gold_sha256),
                ("code_revision", code_revision),
            ],
        )

    def search(self, query: str, *, limit: int = 5) -> list[IndexHit]:
        self._validate_analyzer_fingerprint()
        tokens = self.analyzer.analyze(query)
        if not tokens:
            return []
        match_query = " OR ".join(
            f'"{token.replace(chr(34), chr(34) * 2)}"' for token in tokens
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

    def lexical_analyzer_fingerprint(self) -> str:
        return self._metadata_value("lexical_analyzer_fingerprint")

    def policy_version(self) -> str:
        return self._metadata_value("policy_version")

    def tokenizer_fingerprint(self) -> str:
        return self._metadata_value("tokenizer_fingerprint")

    def _validate_analyzer_fingerprint(self) -> None:
        stored = self.lexical_analyzer_fingerprint()
        if stored != self.analyzer.fingerprint:
            raise ValueError(
                "lexical analyzer fingerprint mismatch: "
                f"index has {stored or '<missing>'}, active analyzer has "
                f"{self.analyzer.fingerprint}"
            )

    def _metadata_value(self, key: str) -> str:
        if not self.path.exists():
            return ""
        try:
            with closing(self.connect()) as connection:
                row = connection.execute(
                    "SELECT value FROM index_metadata WHERE key = ?", (key,)
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

    @property
    def policy_version(self) -> str:
        return str(self._metadata().get("policy_version", ""))

    @property
    def tokenizer_fingerprint(self) -> str:
        return str(self._metadata().get("tokenizer_fingerprint", ""))

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
        policy_version: str = "parent-child-v1",
        tokenizer_fingerprint: str = "regex-token-v1",
        embedding_max_length: int | None = None,
        normalize_embeddings: bool = True,
        lexical_analyzer_fingerprint: str = "",
        gold_sha256: str = "",
        code_revision: str = "",
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
                "policy_version": policy_version,
                "tokenizer_fingerprint": tokenizer_fingerprint,
                "embedding_max_length": embedding_max_length or 0,
                "normalize_embeddings": normalize_embeddings,
                "lexical_analyzer_fingerprint": lexical_analyzer_fingerprint,
                "gold_sha256": gold_sha256,
                "code_revision": code_revision,
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
