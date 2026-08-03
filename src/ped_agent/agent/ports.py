from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel

from ped_agent.agent.contracts import EvidenceItem, ModelOutput, RetrievalBatch


class StructuredOutputUnsupported(RuntimeError):
    pass


class ModelGateway(Protocol):
    @property
    def verification_enabled(self) -> bool: ...

    async def generate(self, prompt: str) -> ModelOutput: ...

    async def verify(self, prompt: str) -> ModelOutput: ...

    async def generate_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
    ) -> tuple[BaseModel | None, ModelOutput]: ...

    async def verify_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
    ) -> tuple[BaseModel | None, ModelOutput]: ...

    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class LocalEvidenceRetriever(Protocol):
    async def retrieve(self, query: str) -> RetrievalBatch: ...


class ExternalEvidenceSearcher(Protocol):
    async def search(self, query: str) -> list[EvidenceItem]: ...
