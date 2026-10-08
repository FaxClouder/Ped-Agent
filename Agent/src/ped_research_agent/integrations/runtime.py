"""Explicit production composition of the frozen graph and knowledge execution support.

Only tools are budgeted here. Model metering and the dynamic controller are subsequent stages;
this entry does not claim to enforce the configured model/token limits on the legacy gateway.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from ped_agent_harness import (
    BudgetMeter,
    Recorder,
    RunBudget,
    ToolCall,
    ToolExecutor,
    ToolFailure,
    ToolRegistry,
    ToolScheduler,
    ToolSpec,
)
from ped_contracts.evidence import RetrievalBatch
from ped_research_agent.agentic.config import RunProfile
from ped_research_agent.context import ResearchQuery
from ped_research_agent.evidence_graph import EvidenceGraph, EvidenceGraphResult
from ped_research_agent.integrations.events import AgentEventBridge, DisabledExternalSearch
from ped_research_agent.integrations.knowledge import (
    KnowledgeAdapter,
    KnowledgeReadTool,
    KnowledgeSearchTool,
    SearchOutput,
    SnapshotIdentity,
)
from ped_research_agent.ports import ModelGateway


class KnowledgeToolError(RuntimeError):
    def __init__(self, failure: ToolFailure) -> None:
        super().__init__(f"{failure.code}: {failure.message}")
        self.failure = failure


class ExecutedLocalRetriever:
    def __init__(
        self,
        knowledge: KnowledgeAdapter,
        executor: ToolExecutor,
        *,
        run_id: str,
        cancel_event: asyncio.Event,
    ) -> None:
        self.knowledge = knowledge
        self.executor = executor
        self.run_id = run_id
        self.cancel_event = cancel_event

    async def retrieve(self, query: str) -> RetrievalBatch:
        outcome = await self.executor.execute(
            ToolCall.create(
                run_id=self.run_id,
                tool_name="knowledge.search",
                arguments={"query": query, "limit": self.knowledge.limit},
            ),
            self.cancel_event,
        )
        if isinstance(outcome, ToolFailure):
            raise KnowledgeToolError(outcome)
        result = SearchOutput.model_validate(outcome.value)
        return RetrievalBatch(
            items=result.items,
            sufficient=self.knowledge.baseline_sufficiency(query, result.items),
            degraded=result.degraded,
            degradation_reason=result.degradation_reason,
        )


@dataclass(frozen=True)
class BaselineRuntime:
    graph: EvidenceGraph
    scheduler: ToolScheduler
    meter: BudgetMeter
    events: AgentEventBridge
    cancel_event: asyncio.Event

    async def execute(self, context: ResearchQuery) -> EvidenceGraphResult:
        if context.run_id != self.events.run_id:
            raise ValueError("query and recorder run identities differ")
        return await self.graph.execute(context, self.events.emit, self.cancel_event.is_set)


def build_baseline(
    profile: RunProfile,
    knowledge: KnowledgeAdapter,
    gateway: ModelGateway,
    recorder: Recorder,
    *,
    run_id: str,
) -> BaselineRuntime:
    UUID(run_id)  # Validate before any tool/model dispatch.
    profile.validate_assets()
    manifest = SnapshotIdentity.model_validate_json(profile.knowledge.manifest.read_text())
    if manifest != knowledge.snapshot:
        raise ValueError("configured snapshot and knowledge adapter differ")
    if "knowledge.search" not in profile.harness.tool_allowlist:
        raise ValueError("fixed baseline requires knowledge.search")
    knowledge.validate_snapshot()
    budget = RunBudget(
        **profile.harness.model_dump(
            include={
                "max_tool_calls",
                "max_model_calls",
                "max_total_input_tokens",
                "max_total_output_tokens",
                "deadline_seconds",
            }
        )
    )
    meter = BudgetMeter(budget)
    tools: list[ToolSpec[Any, Any]] = [KnowledgeSearchTool(knowledge), KnowledgeReadTool(knowledge)]
    for tool in tools:
        tool.timeout_seconds = profile.harness.tool_timeout_seconds
        tool.max_retries = profile.harness.retry_readonly
    executor = ToolExecutor(
        ToolRegistry(tools), meter, recorder, allowlist=profile.harness.tool_allowlist
    )
    cancel = asyncio.Event()
    knowledge.bind_run(run_id)
    return BaselineRuntime(
        graph=EvidenceGraph(
            gateway,
            ExecutedLocalRetriever(knowledge, executor, run_id=run_id, cancel_event=cancel),
            DisabledExternalSearch(),
        ),
        scheduler=ToolScheduler(executor, max_parallel=profile.harness.max_parallel),
        meter=meter,
        events=AgentEventBridge(recorder, run_id=run_id),
        cancel_event=cancel,
    )
