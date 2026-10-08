"""Provider-independent model requests; tool proposals come from native response fields."""

from __future__ import annotations

import json
from typing import Literal, Protocol, Self
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

from ped_agent_harness.contracts import ToolDefinition


class ModelValue(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ModelMessage(ModelValue):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_call_id: str | None = None
    tool_calls: tuple[ProposedToolCall, ...] = ()

    @model_validator(mode="after")
    def tool_identity(self) -> Self:
        if (self.role == "tool") != (self.tool_call_id is not None):
            raise ValueError("tool messages require a tool_call_id")
        if self.tool_calls and self.role != "assistant":
            raise ValueError("only assistant messages may propose tool calls")
        return self


class ProposedToolCall(ModelValue):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    arguments: dict[str, JsonValue]


class ModelUsage(ModelValue):
    input_tokens: int | None = Field(default=None, ge=0, strict=True)
    output_tokens: int | None = Field(default=None, ge=0, strict=True)


class ModelReply(ModelValue):
    content: str
    model: str = Field(min_length=1)
    structured: dict[str, JsonValue] | None = None
    tool_calls: tuple[ProposedToolCall, ...] = ()
    finish_reason: str | None = None
    usage: ModelUsage = Field(default_factory=ModelUsage)


class ModelCapabilities(ModelValue):
    structured: bool = False
    tools: bool = False


class ModelRequest(ModelValue):
    run_id: str = Field(min_length=1)
    call_id: str = Field(default_factory=lambda: str(uuid4()))
    parent_call_id: str | None = None
    role: str = Field(min_length=1)
    messages: tuple[ModelMessage, ...] = Field(min_length=1)
    response_schema: dict[str, JsonValue] | None = None
    tools: tuple[ToolDefinition, ...] = ()
    max_output_tokens: int = Field(default=4096, gt=0, strict=True)

    @model_validator(mode="after")
    def one_mode(self) -> Self:
        if self.response_schema is not None and self.tools:
            raise ValueError("structured response and tool chat are distinct request modes")
        names = [tool.name for tool in self.tools]
        if len(names) != len(set(names)):
            raise ValueError("duplicate model-facing tool names")
        pending: set[str] = set()
        for message in self.messages:
            if message.tool_calls:
                if pending:
                    raise ValueError("previous tool calls have no results")
                ids = [call.id for call in message.tool_calls]
                if len(ids) != len(set(ids)):
                    raise ValueError("duplicate assistant tool-call IDs")
                pending.update(ids)
            if message.role == "tool":
                if message.tool_call_id not in pending:
                    raise ValueError("tool result has no matching assistant call")
                pending.remove(message.tool_call_id)
        if pending:
            raise ValueError("model request contains unanswered tool calls")
        return self

    def input_estimate(self) -> int:
        # Byte bound plus explicit framing allowance; not provider-reported token usage.
        payload = {
            "messages": [m.model_dump() for m in self.messages],
            "tools": [t.model_dump() for t in self.tools],
            "schema": self.response_schema,
        }
        return len(json.dumps(payload, ensure_ascii=False).encode()) + 64 * len(self.messages)


class ModelPort(Protocol):
    def capabilities(self, role: str) -> ModelCapabilities: ...
    async def invoke(self, request: ModelRequest) -> ModelReply: ...


class UnsupportedModelCapability(RuntimeError):
    pass
