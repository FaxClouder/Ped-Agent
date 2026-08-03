from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ped_agent.agent.contracts import ModelOutput
from pydantic import BaseModel

from ped_agent_server.settings import AgentSettings, ChatModelSettings, EmbeddingSettings


class DirectModelGateway:
    def __init__(
        self,
        *,
        answer_client: Any,
        verify_client: Any | None,
        embedding_client: Any,
        answer_structured_method: str | None = None,
        verify_structured_method: str | None = None,
    ) -> None:
        self._answer_client = answer_client
        self._verify_client = verify_client
        self._embedding_client = embedding_client
        self._answer_structured_method = answer_structured_method
        self._verify_structured_method = verify_structured_method

    @classmethod
    def from_settings(cls, settings: AgentSettings) -> DirectModelGateway:
        verify_settings = settings.resolved_verify
        verify_client = (
            _build_chat_client(verify_settings) if settings.verify.enabled else None
        )
        return cls(
            answer_client=_build_chat_client(settings.answer),
            verify_client=verify_client,
            embedding_client=_build_embedding_client(settings.embedding),
            answer_structured_method=(
                settings.answer.structured_output_method
                if settings.answer.protocol == "openai_compatible"
                else None
            ),
            verify_structured_method=(
                verify_settings.structured_output_method
                if settings.verify.enabled
                and verify_settings.protocol == "openai_compatible"
                else None
            ),
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

    async def generate_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
    ) -> tuple[BaseModel | None, ModelOutput]:
        return await _invoke_structured(
            self._answer_client,
            prompt,
            schema,
            method=self._answer_structured_method,
        )

    async def verify_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
    ) -> tuple[BaseModel | None, ModelOutput]:
        if self._verify_client is None:
            raise RuntimeError("verification is disabled")
        return await _invoke_structured(
            self._verify_client,
            prompt,
            schema,
            method=self._verify_structured_method,
        )


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


async def _invoke_structured(
    client: Any,
    prompt: str,
    schema: type[BaseModel],
    *,
    method: str | None,
) -> tuple[BaseModel | None, ModelOutput]:
    kwargs: dict[str, Any] = {"include_raw": True}
    if method is not None:
        kwargs["method"] = method
    structured_client = client.with_structured_output(schema, **kwargs)
    result = await structured_client.ainvoke(prompt)
    if not isinstance(result, dict) or "raw" not in result:
        parsed = result if isinstance(result, schema) else schema.model_validate(result)
        model = getattr(client, "model_name", None) or getattr(client, "model", None) or "unknown"
        return parsed, ModelOutput(
            content=parsed.model_dump_json(),
            model=str(model),
        )

    raw = _to_model_output(result["raw"])
    parsed = result.get("parsed")
    if parsed is None:
        return None, raw
    try:
        return schema.model_validate(parsed), raw
    except (TypeError, ValueError):
        return None, raw
