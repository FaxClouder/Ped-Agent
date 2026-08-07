from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ChatProtocol = Literal["openai_compatible", "anthropic"]
StructuredOutputMethod = Literal["json_mode", "json_schema", "function_calling"]


class ChatModelSettings(BaseModel):
    protocol: ChatProtocol = "openai_compatible"
    model: str
    api_key: SecretStr | None = None
    base_url: str | None = None
    temperature: float = 0.1
    max_tokens: int = 4096
    timeout_seconds: float = 60.0
    max_retries: int = 2
    structured_output_method: StructuredOutputMethod = "json_schema"


class VerifySettings(BaseModel):
    enabled: bool = True
    protocol: Literal["inherit", "openai_compatible", "anthropic"] = "inherit"
    model: str | None = None
    api_key: SecretStr | None = None
    base_url: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    timeout_seconds: float | None = None
    max_retries: int | None = None
    structured_output_method: StructuredOutputMethod | None = None


class EmbeddingSettings(BaseModel):
    protocol: Literal["openai_compatible"] = "openai_compatible"
    model: str
    api_key: SecretStr | None = None
    base_url: str | None = None
    dimensions: int | None = None
    timeout_seconds: float = 60.0
    max_retries: int = 2


class SearchSettings(BaseModel):
    academic_enabled: bool = True
    parallel_enabled: bool = False
    parallel_api_key: SecretStr | None = None
    timeout_seconds: float = 20.0
    max_candidates_per_source: int = 5
    max_pages: int = 3


class RuntimeSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)
    max_concurrent_runs: int = Field(default=2, ge=1)
    agent_db_path: Path = Path("memPed/conversations/conversations.sqlite3")
    chroma_path: Path = Path("memPed/knowledge/vectors")
    recent_message_limit: int = Field(default=6, ge=1)


class LangSmithSettings(BaseModel):
    enabled: bool = False
    api_key: SecretStr | None = None
    project: str = "ped-agent-local"
    sampling_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    content_policy: Literal["redacted"] = "redacted"
    endpoint: str | None = None


class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PED_AGENT_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    answer: ChatModelSettings
    verify: VerifySettings = Field(default_factory=VerifySettings)
    embedding: EmbeddingSettings
    search: SearchSettings = Field(default_factory=SearchSettings)
    runtime: RuntimeSettings = Field(default_factory=RuntimeSettings)
    langsmith: LangSmithSettings = Field(default_factory=LangSmithSettings)

    @property
    def resolved_verify(self) -> ChatModelSettings:
        if self.verify.protocol == "inherit":
            overrides = {
                name: value
                for name, value in self.verify.model_dump(exclude={"enabled", "protocol"}).items()
                if value is not None
            }
            return self.answer.model_copy(update=overrides)

        return ChatModelSettings(
            protocol=self.verify.protocol,
            model=self.verify.model or self.answer.model,
            api_key=self.verify.api_key,
            base_url=self.verify.base_url,
            temperature=(
                self.verify.temperature
                if self.verify.temperature is not None
                else self.answer.temperature
            ),
            max_tokens=(
                self.verify.max_tokens
                if self.verify.max_tokens is not None
                else self.answer.max_tokens
            ),
            timeout_seconds=(
                self.verify.timeout_seconds
                if self.verify.timeout_seconds is not None
                else self.answer.timeout_seconds
            ),
            max_retries=(
                self.verify.max_retries
                if self.verify.max_retries is not None
                else self.answer.max_retries
            ),
            structured_output_method=(
                self.verify.structured_output_method or self.answer.structured_output_method
            ),
        )


def load_settings(env_file: str | Path | None = ".env") -> AgentSettings:
    settings = AgentSettings(_env_file=env_file)
    _validate_credentials(settings)
    return settings


def _validate_credentials(settings: AgentSettings) -> None:
    if settings.answer.api_key is None:
        raise ValueError("answer API key is required")
    if settings.embedding.api_key is None:
        raise ValueError("embedding API key is required")
    if settings.verify.enabled and settings.resolved_verify.api_key is None:
        raise ValueError("verify API key is required")
    if settings.search.parallel_enabled and settings.search.parallel_api_key is None:
        raise ValueError("Parallel Search API key is required when enabled")
    if settings.langsmith.enabled and settings.langsmith.api_key is None:
        raise ValueError("LangSmith API key is required when enabled")
