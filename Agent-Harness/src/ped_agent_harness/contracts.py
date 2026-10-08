"""Typed tool contracts for the research harness.

Each tool declares an input model and a canonical output model. The executor validates
arguments before dispatch and the returned value after it; the value is kept as structured
JSON and rendered separately for the model. Design: ``docs/contract-and-controller-design.md``.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any, ClassVar, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, JsonValue, TypeAdapter


class SideEffect(StrEnum):
    READONLY = "readonly"
    CREATES_ARTIFACT = "creates_artifact"


class ToolErrorCode(StrEnum):
    UNKNOWN_TOOL = "unknown_tool"
    INVALID_ARGUMENTS = "invalid_arguments"
    DENIED = "denied"
    BUDGET_EXHAUSTED = "budget_exhausted"
    ABORTED_BEFORE_DISPATCH = "aborted_before_dispatch"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    TOOL_ERROR = "tool_error"
    INVALID_OUTPUT = "invalid_output"
    OUTCOME_UNKNOWN = "outcome_unknown"


def canonical_json(value: JsonValue) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value: JsonValue) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


class ToolCall(BaseModel):
    """One requested invocation; identity is fixed before any policy runs."""

    model_config = ConfigDict(frozen=True)

    run_id: str
    call_id: str
    parent_call_id: str | None = None
    round: int = Field(default=0, ge=0)
    tool_name: str
    arguments: dict[str, JsonValue] = Field(default_factory=dict)
    arguments_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @classmethod
    def create(
        cls,
        *,
        run_id: str,
        tool_name: str,
        arguments: dict[str, JsonValue] | None = None,
        round: int = 0,
        parent_call_id: str | None = None,
        call_id: str | None = None,
    ) -> ToolCall:
        snapshot: dict[str, JsonValue] = json.loads(canonical_json(arguments or {}))
        return cls(
            run_id=run_id,
            call_id=call_id or str(uuid4()),
            parent_call_id=parent_call_id,
            round=round,
            tool_name=tool_name,
            arguments=snapshot,
            arguments_sha256=sha256_json(snapshot),
        )


class ToolProvenance(BaseModel):
    tool_version: str | None = None
    side_effect: SideEffect | None = None
    attempts: int = 0
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_ms: float | None = None
    details: dict[str, JsonValue] = Field(default_factory=dict)


class ToolSuccess(BaseModel):
    status: Literal["ok"] = "ok"
    call: ToolCall
    value: JsonValue
    value_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    content: str
    provenance: ToolProvenance


class ToolFailure(BaseModel):
    status: Literal["error"] = "error"
    call: ToolCall
    code: ToolErrorCode
    message: str
    dispatched: bool
    provenance: ToolProvenance

    @property
    def content(self) -> str:
        return f"Error ({self.code.value}): {self.message}"


ToolOutcome = Annotated[ToolSuccess | ToolFailure, Field(discriminator="status")]
TOOL_OUTCOME_ADAPTER: TypeAdapter[ToolSuccess | ToolFailure] = TypeAdapter(ToolOutcome)


class ToolDefinition(BaseModel):
    """The model-facing projection of a tool; execution metadata is never included."""

    name: str
    description: str
    parameters: dict[str, Any]


@dataclass(frozen=True)
class ToolRunContext:
    call: ToolCall
    cancel_event: asyncio.Event
    attempt: int

    @property
    def cancelled(self) -> bool:
        return self.cancel_event.is_set()


class ToolSpec[I: BaseModel, O: BaseModel](ABC):
    """Base class for a registered tool.

    ``execute`` returns the canonical output model; failures that are part of the domain
    (for example zero hits) belong in that value, while infrastructure failures raise.
    """

    name: ClassVar[str]
    version: ClassVar[str]
    description: ClassVar[str]
    input_model: ClassVar[type[BaseModel]]
    output_model: ClassVar[type[BaseModel]]
    side_effect: ClassVar[SideEffect] = SideEffect.READONLY
    # Execution policy can be resolved per run; schemas and tool identity remain class metadata.
    timeout_seconds: float | None = None
    max_retries: int = 0

    def parallel_safe(self, args: I) -> bool:
        return False

    @abstractmethod
    async def execute(self, args: I, ctx: ToolRunContext) -> O: ...

    def render(self, args: I, value: O) -> str:
        return value.model_dump_json()

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters=self.input_model.model_json_schema(),
        )
