"""Ped-Agent Harness: typed tool execution support for Agentic research runs.

Implemented (2026-10-07): tool contracts, registry, executor, scheduler, run budget and
event recording. Planned: tool-chat model port, config loader, Agent controller wiring.
See ``docs/contract-and-controller-design.md``.
"""

from __future__ import annotations

from ped_agent_harness.budget import BudgetMeter, BudgetUsage, RunBudget
from ped_agent_harness.contracts import (
    TOOL_OUTCOME_ADAPTER,
    SideEffect,
    ToolCall,
    ToolDefinition,
    ToolErrorCode,
    ToolFailure,
    ToolOutcome,
    ToolProvenance,
    ToolRunContext,
    ToolSpec,
    ToolSuccess,
)
from ped_agent_harness.executor import ToolExecutor
from ped_agent_harness.recorder import JsonlRecorder, MemoryRecorder, Recorder, RunEvent
from ped_agent_harness.registry import DuplicateToolError, ToolRegistry
from ped_agent_harness.scheduler import ToolScheduler

__version__ = "0.2.0"

__all__ = [
    "TOOL_OUTCOME_ADAPTER",
    "BudgetMeter",
    "BudgetUsage",
    "DuplicateToolError",
    "JsonlRecorder",
    "MemoryRecorder",
    "Recorder",
    "RunBudget",
    "RunEvent",
    "SideEffect",
    "ToolCall",
    "ToolDefinition",
    "ToolErrorCode",
    "ToolExecutor",
    "ToolFailure",
    "ToolOutcome",
    "ToolProvenance",
    "ToolRegistry",
    "ToolRunContext",
    "ToolScheduler",
    "ToolSpec",
    "ToolSuccess",
]
