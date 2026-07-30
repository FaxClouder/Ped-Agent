from __future__ import annotations

from typing import Protocol

from ped_agent.agent.contracts import ModelOutput


class ModelGateway(Protocol):
    @property
    def verification_enabled(self) -> bool: ...

    async def generate(self, prompt: str) -> ModelOutput: ...

    async def verify(self, prompt: str) -> ModelOutput: ...

    async def embed(self, texts: list[str]) -> list[list[float]]: ...

