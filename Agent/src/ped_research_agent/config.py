from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, SecretStr

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


class AgentSettings(BaseModel):
    """Minimal model configuration for reproducible answer experiments."""

    answer: ChatModelSettings
    verify: VerifySettings = Field(default_factory=VerifySettings)

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
            temperature=_fallback(self.verify.temperature, self.answer.temperature),
            max_tokens=_fallback(self.verify.max_tokens, self.answer.max_tokens),
            timeout_seconds=_fallback(
                self.verify.timeout_seconds,
                self.answer.timeout_seconds,
            ),
            max_retries=_fallback(self.verify.max_retries, self.answer.max_retries),
            structured_output_method=(
                self.verify.structured_output_method or self.answer.structured_output_method
            ),
        )


def load_settings(env_file: str | Path | None = ".env") -> AgentSettings:
    values = _read_env_file(Path(env_file)) if env_file else {}
    values.update(os.environ)
    answer = ChatModelSettings(
        protocol=values.get("PED_AGENT_ANSWER__PROTOCOL", "openai_compatible"),
        model=values.get("PED_AGENT_ANSWER__MODEL", "deepseek-v4-flash"),
        api_key=_secret(values.get("PED_AGENT_ANSWER__API_KEY")),
        base_url=values.get("PED_AGENT_ANSWER__BASE_URL"),
        structured_output_method=values.get(
            "PED_AGENT_ANSWER__STRUCTURED_OUTPUT_METHOD",
            "json_mode",
        ),
    )
    verify = VerifySettings(
        enabled=_boolean(values.get("PED_AGENT_VERIFY__ENABLED", "true")),
        protocol=values.get("PED_AGENT_VERIFY__PROTOCOL", "inherit"),
        model=values.get("PED_AGENT_VERIFY__MODEL"),
        api_key=_secret(values.get("PED_AGENT_VERIFY__API_KEY")),
        base_url=values.get("PED_AGENT_VERIFY__BASE_URL"),
    )
    settings = AgentSettings(answer=answer, verify=verify)
    if settings.answer.api_key is None:
        raise ValueError("answer API key is required")
    if settings.verify.enabled and settings.resolved_verify.api_key is None:
        raise ValueError("verify API key is required")
    return settings


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        normalized = line.strip()
        if not normalized or normalized.startswith("#") or "=" not in normalized:
            continue
        key, value = normalized.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def _secret(value: str | None) -> SecretStr | None:
    return SecretStr(value) if value else None


def _boolean(value: str) -> bool:
    return value.casefold() in {"1", "true", "yes", "on"}


def _fallback[T](value: T | None, default: T) -> T:
    return default if value is None else value
