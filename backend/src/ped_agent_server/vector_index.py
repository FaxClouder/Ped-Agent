from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Protocol

from ped_agent_server.index import IndexHit


class EmbeddingGateway(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class ChromaVectorIndex:
    collection_name = "ped_agent_official_evidence"

    def __init__(self, path: Path, embedding_gateway: EmbeddingGateway) -> None:
        self.path = path
        self.embedding_gateway = embedding_gateway

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
        if not chunks:
            return
        texts = [str(item["text"]) for item in chunks]
        vectors = await self.embedding_gateway.embed(texts)
        collection.add(
            ids=[str(item["chunk_id"]) for item in chunks],
            embeddings=vectors,
            documents=texts,
            metadatas=[{"resource_id": str(item["resource_id"])} for item in chunks],
        )

    def _metadata(self) -> dict[str, object]:
        try:
            return dict(self._collection().metadata or {})
        except Exception:  # noqa: BLE001 - an unavailable index is reported as empty metadata.
            return {}

    def _client(self):
        import chromadb

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
