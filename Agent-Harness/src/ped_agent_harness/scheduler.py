"""Schedules one batch of tool calls.

Parallel-safe calls form bounded groups; any other call runs alone and acts as a barrier.
Outcomes are returned in request order regardless of completion order.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from ped_agent_harness.contracts import ToolCall, ToolFailure, ToolSuccess
from ped_agent_harness.executor import ToolExecutor


class ToolScheduler:
    def __init__(self, executor: ToolExecutor, *, max_parallel: int = 1) -> None:
        if max_parallel < 1:
            raise ValueError("max_parallel must be at least 1")
        self.executor = executor
        self.max_parallel = max_parallel

    def _parallel_safe(self, call: ToolCall) -> bool:
        tool = self.executor.registry.get(call.tool_name)
        args = self.executor.validated_arguments(call)
        if tool is None or args is None:
            return False
        try:
            return tool.parallel_safe(args) is True
        except Exception:
            return False

    async def run_batch(
        self,
        calls: Sequence[ToolCall],
        cancel_event: asyncio.Event | None = None,
    ) -> list[ToolSuccess | ToolFailure]:
        cancel = cancel_event or asyncio.Event()
        outcomes: list[ToolSuccess | ToolFailure] = []
        index = 0
        while index < len(calls):
            if self.max_parallel == 1 or not self._parallel_safe(calls[index]):
                outcomes.append(await self.executor.execute(calls[index], cancel))
                index += 1
                continue
            end = index
            while end < len(calls) and self._parallel_safe(calls[end]):
                end += 1
            outcomes.extend(await self._run_group(calls[index:end], cancel))
            index = end
        return outcomes

    async def _run_group(
        self,
        group: Sequence[ToolCall],
        cancel: asyncio.Event,
    ) -> list[ToolSuccess | ToolFailure]:
        semaphore = asyncio.Semaphore(self.max_parallel)

        async def run(call: ToolCall) -> ToolSuccess | ToolFailure:
            async with semaphore:
                return await self.executor.execute(call, cancel)

        return list(await asyncio.gather(*(run(call) for call in group)))
