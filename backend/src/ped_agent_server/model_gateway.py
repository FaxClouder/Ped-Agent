from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ped_agent.agent.contracts import ModelOutput

from ped_agent_server.settings import AgentSettings, ChatModelSettings, EmbeddingSettings


class DirectModelGateway:
    def __init__(
        self,
        *,
        answer_client: Any,
        verify_client: Any | None,
        embedding_client: Any,
    ) -> None:
        self._answer_client = answer_client
        self._verify_client = verify_client
        self._embedding_client = embedding_client

    @classmethod
    def from_settings(cls, settings: AgentSettings) -> DirectModelGateway:
        verify_client = (
            _build_chat_client(settings.resolved_verify) if settings.verify.enabled else None
        )
        return cls(
            answer_client=_build_chat_client(settings.answer),
            verify_client=verify_client,
            embedding_client=_build_embedding_client(settings.embedding),
        )

    @property
    def verification_enabled(self) -> bool:
        return self._verify_client is not None

    async def generate(self, prompt: str) -> ModelOutput:
        return _to_model_output(await self._answer_client.ainvoke(prompt))

    async def verify(self, prompt: str) -> ModelOutput:
        if self._verify_client is None:
            raise RuntimeError("verification is disabled")
        return _to_model_output(await self._verify_client.ainvoke(prompt))

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return await self._embedding_client.aembed_documents(texts)


def _build_chat_client(settings: ChatModelSettings) -> Any:
    api_key = settings.api_key.get_secret_value() if settings.api_key else None
    common = {
        "model": settings.model,
        "api_key": api_key,
        "temperature": settings.temperature,
        "max_tokens": settings.max_tokens,
        "timeout": settings.timeout_seconds,
        "max_retries": settings.max_retries,
    }
    if settings.protocol == "anthropic":
        if settings.base_url:
            common["base_url"] = settings.base_url
        return ChatAnthropic(**common)

    if settings.base_url:
        common["base_url"] = settings.base_url
    return ChatOpenAI(**common)


def _build_embedding_client(settings: EmbeddingSettings) -> OpenAIEmbeddings:
    kwargs: dict[str, Any] = {
        "model": settings.model,
        "api_key": settings.api_key.get_secret_value() if settings.api_key else None,
        "request_timeout": settings.timeout_seconds,
        "max_retries": settings.max_retries,
    }
    if settings.base_url:
        kwargs["base_url"] = settings.base_url
    if settings.dimensions:
        kwargs["dimensions"] = settings.dimensions
    return OpenAIEmbeddings(**kwargs)


def _to_model_output(message: Any) -> ModelOutput:
    content = message.content
    if isinstance(content, Sequence) and not isinstance(content, str):
        content = "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    metadata = getattr(message, "response_metadata", {}) or {}
    model = metadata.get("model_name") or metadata.get("model") or "unknown"
    return ModelOutput(content=str(content), model=str(model))
