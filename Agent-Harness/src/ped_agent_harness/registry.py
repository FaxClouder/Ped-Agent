"""Tool definitions and lookup; execution lives in ToolExecutor."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ped_agent_harness.contracts import ToolDefinition, ToolSpec


class DuplicateToolError(ValueError):
    pass


class ToolRegistry:
    def __init__(self, tools: Iterable[ToolSpec[Any, Any]] = ()) -> None:
        self._tools: dict[str, ToolSpec[Any, Any]] = {}
        for tool in tools:
            self.register(tool)

    def register(self, tool: ToolSpec[Any, Any]) -> None:
        if tool.name in self._tools:
            raise DuplicateToolError(f"tool {tool.name!r} is already registered")
        if tool.max_retries < 0:
            raise ValueError(f"tool {tool.name!r} has negative max_retries")
        if tool.timeout_seconds is not None and tool.timeout_seconds <= 0:
            raise ValueError(f"tool {tool.name!r} has non-positive timeout")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolSpec[Any, Any] | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return sorted(self._tools)

    def definitions(self, allowlist: Iterable[str] | None = None) -> list[ToolDefinition]:
        allowed = set(self._tools) if allowlist is None else set(allowlist)
        return [self._tools[name].definition() for name in self.names() if name in allowed]
