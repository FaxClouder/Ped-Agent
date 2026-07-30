from __future__ import annotations

from typing import Protocol

from ped_agent.agent.contracts import EvidenceItem, ModelOutput, RetrievalBatch


class ModelGateway(Protocol):
    @property
    def verification_enabled(self) -> bool: ...

    async def generate(self, prompt: str) -> ModelOutput: ...

    async def verify(self, prompt: str) -> ModelOutput: ...

    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class LocalEvidenceRetriever(Protocol):
    async def retrieve(self, query: str) -> RetrievalBatch: ...


class ExternalEvidenceSearcher(Protocol):
    async def search(self, query: str) -> list[EvidenceItem]: ...
