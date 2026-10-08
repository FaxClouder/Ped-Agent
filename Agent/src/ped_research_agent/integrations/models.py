"""LangChain provider adaptation and the metered implementation of the old Agent port."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from pydantic import BaseModel, JsonValue, TypeAdapter, ValidationError

from ped_agent_harness.model_contracts import (
    ModelCapabilities,
    ModelMessage,
    ModelReply,
    ModelRequest,
    ModelUsage,
    ProposedToolCall,
    UnsupportedModelCapability,
)
from ped_agent_harness.models import ModelExecutor
from ped_contracts.evidence import ModelOutput
from ped_research_agent.config import AgentSettings
from ped_research_agent.model_gateway import _build_chat_client, _to_model_output

_OBJECT = TypeAdapter(dict[str, JsonValue])


class LangChainModelPort:
    def __init__(
        self,
        clients: Mapping[str, Any],
        *,
        capabilities: Mapping[str, ModelCapabilities],
        methods: Mapping[str, str | None] | None = None,
    ) -> None:
        if set(clients) != set(capabilities):
            raise ValueError("each model role requires explicit capabilities")
        for client in clients.values():
            if getattr(client, "max_retries", None) != 0:
                raise ValueError("provider SDK retries must be explicitly disabled")
        self.clients = dict(clients)
        self._capabilities = dict(capabilities)
        self.methods = dict(methods or {})

    @classmethod
    def from_settings(cls, settings: AgentSettings) -> LangChainModelPort:
        answer = settings.answer.model_copy(update={"max_retries": 0})
        clients = {"answer": _build_chat_client(answer)}
        methods = {
            "answer": answer.structured_output_method
            if answer.protocol == ("openai_compatible")
            else None
        }
        if settings.verify.enabled:
            verifier = settings.resolved_verify.model_copy(update={"max_retries": 0})
            verify_client = _build_chat_client(verifier)
            for role in ("verify", "planner", "judge", "replan"):
                clients[role] = verify_client
                methods[role] = (
                    verifier.structured_output_method
                    if verifier.protocol == ("openai_compatible")
                    else None
                )
        return cls(
            clients,
            capabilities={role: ModelCapabilities(structured=True, tools=True) for role in clients},
            methods=methods,
        )

    def capabilities(self, role: str) -> ModelCapabilities:
        if role not in self._capabilities:
            raise UnsupportedModelCapability(f"model role is not configured: {role}")
        return self._capabilities[role]

    async def invoke(self, request: ModelRequest) -> ModelReply:
        client = self.clients[request.role]
        # Check again to prevent a mutable injected SDK object from enabling hidden retries.
        if getattr(client, "max_retries", None) != 0:
            raise UnsupportedModelCapability("provider SDK retries changed")
        runnable = client
        try:
            if request.response_schema is not None:
                kwargs: dict[str, Any] = {"include_raw": True}
                method = self.methods.get(request.role)
                if method is not None:
                    kwargs["method"] = method
                runnable = client.with_structured_output(request.response_schema, **kwargs)
            elif request.tools:
                runnable = client.bind_tools([t.model_dump() for t in request.tools])
        except (AttributeError, NotImplementedError) as exc:
            raise UnsupportedModelCapability("provider cannot implement requested mode") from exc
        messages: list[BaseMessage] = []
        for item in request.messages:
            if item.role == "system":
                messages.append(SystemMessage(content=item.content))
            elif item.role == "user":
                messages.append(HumanMessage(content=item.content))
            elif item.role == "tool":
                messages.append(ToolMessage(content=item.content, tool_call_id=item.tool_call_id))
            else:
                messages.append(
                    AIMessage(
                        content=item.content,
                        tool_calls=[
                            {
                                "id": call.id,
                                "name": call.name,
                                "args": call.arguments,
                                "type": "tool_call",
                            }
                            for call in item.tool_calls
                        ],
                    )
                )
        result = await runnable.bind(max_tokens=request.max_output_tokens).ainvoke(messages)
        parsed = None
        if request.response_schema is not None:
            if not isinstance(result, dict) or "raw" not in result:
                raise ValueError("structured provider must retain its raw response")
            parsed = result.get("parsed")
            raw = result["raw"]
        else:
            raw = result
        if getattr(raw, "invalid_tool_calls", None):
            raise ValueError("provider returned malformed native tool calls")
        metadata = getattr(raw, "response_metadata", {}) or {}
        usage = getattr(raw, "usage_metadata", None) or metadata.get("token_usage") or {}
        calls = tuple(
            ProposedToolCall(
                id=call["id"],
                name=call["name"],
                arguments=call["args"],
            )
            for call in (getattr(raw, "tool_calls", None) or [])
        )
        if isinstance(parsed, BaseModel):
            parsed = parsed.model_dump(mode="json")
        output = _to_model_output(raw)
        return ModelReply(
            content=output.content,
            model=output.model,
            structured=_OBJECT.validate_python(parsed) if parsed is not None else None,
            tool_calls=calls,
            finish_reason=metadata.get("finish_reason") or metadata.get("stop_reason"),
            usage=ModelUsage(
                input_tokens=usage.get("input_tokens", usage.get("prompt_tokens")),
                output_tokens=usage.get("output_tokens", usage.get("completion_tokens")),
            ),
        )


class MeteredModelGateway:
    def __init__(
        self,
        executor: ModelExecutor,
        *,
        run_id: str,
        cancel_event: asyncio.Event,
        max_output_tokens: int,
    ) -> None:
        self.executor = executor
        self.run_id = run_id
        self.cancel_event = cancel_event
        self.max_output_tokens = max_output_tokens

    @property
    def verification_enabled(self) -> bool:
        try:
            self.executor.provider.capabilities("verify")
        except UnsupportedModelCapability:
            return False
        return True

    async def _invoke(
        self, role: str, prompt: str, schema: type[BaseModel] | None = None
    ) -> ModelReply:
        request = ModelRequest(
            run_id=self.run_id,
            role=role,
            messages=(ModelMessage(role="user", content=prompt),),
            response_schema=_OBJECT.validate_python(schema.model_json_schema()) if schema else None,
            max_output_tokens=self.max_output_tokens,
        )
        return await self.executor.execute(request, self.cancel_event)

    async def generate(self, prompt: str) -> ModelOutput:
        reply = await self._invoke("answer", prompt)
        return ModelOutput(content=reply.content, model=reply.model)

    async def verify(self, prompt: str) -> ModelOutput:
        reply = await self._invoke("verify", prompt)
        return ModelOutput(content=reply.content, model=reply.model)

    async def _structured(
        self,
        role: str,
        prompt: str,
        schema: type[BaseModel],
    ) -> tuple[BaseModel | None, ModelOutput]:
        reply = await self._invoke(role, prompt, schema)
        try:
            value = (
                schema.model_validate(reply.structured) if reply.structured is not None else None
            )
        except ValidationError:
            value = None  # The existing explicit, once-only JSON repair remains budgeted.
        return value, ModelOutput(content=reply.content, model=reply.model)

    async def generate_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
    ) -> tuple[BaseModel | None, ModelOutput]:
        return await self._structured("answer", prompt, schema)

    async def verify_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
    ) -> tuple[BaseModel | None, ModelOutput]:
        return await self._structured("verify", prompt, schema)
