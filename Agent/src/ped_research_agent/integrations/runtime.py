"""Explicit production composition of the frozen graph and knowledge execution support.

Tool and model calls share the run budget. The frozen graph remains unchanged; the new
composition requires an explicit ModelPort, not an unmetered legacy gateway.
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
from ped_agent_harness.execution import ExecutionCancelled, ExecutionTimeout, run_cancellable
from ped_agent_harness.model_contracts import ModelPort
from ped_agent_harness.models import ModelErrorCode, ModelExecutionError, ModelExecutor
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
from ped_research_agent.integrations.models import MeteredModelGateway


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
    models: ModelExecutor

    async def execute(self, context: ResearchQuery) -> EvidenceGraphResult:
        if context.run_id != self.events.run_id:
            raise ValueError("query and recorder run identities differ")
        try:
            return await run_cancellable(
                lambda: self.graph.execute(context, self.events.emit, self.cancel_event.is_set),
                self.cancel_event,
                self.meter.remaining_seconds(),
            )
        except ExecutionTimeout as exc:
            await self.events.emit("run.stopped", {"code": "budget_exhausted"})
            raise ModelExecutionError(
                ModelErrorCode.BUDGET_EXHAUSTED, "run deadline reached"
            ) from exc
        except ExecutionCancelled as exc:
            await self.events.emit("run.stopped", {"code": "cancelled"})
            raise ModelExecutionError(ModelErrorCode.CANCELLED, str(exc)) from exc


@dataclass(frozen=True)
class ExecutionSupport:
    tools: ToolExecutor
    models: ModelExecutor
    meter: BudgetMeter
    cancel: asyncio.Event
    events: AgentEventBridge
    scheduler: ToolScheduler


def build_execution(
    profile: RunProfile,
    knowledge: KnowledgeAdapter,
    gateway: ModelPort,
    recorder: Recorder,
    *,
    run_id: str,
) -> ExecutionSupport:
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
    models = ModelExecutor(
        gateway,
        meter,
        recorder,
        timeout_seconds=profile.harness.model_timeout_seconds,
        max_retries=profile.harness.retry_model,
    )
    knowledge.bind_run(run_id)
    return ExecutionSupport(
        executor,
        models,
        meter,
        cancel,
        AgentEventBridge(recorder, run_id=run_id),
        ToolScheduler(executor, max_parallel=profile.harness.max_parallel),
    )


def build_baseline(
    profile: RunProfile,
    knowledge: KnowledgeAdapter,
    gateway: ModelPort,
    recorder: Recorder,
    *,
    run_id: str,
) -> BaselineRuntime:
    support = build_execution(profile, knowledge, gateway, recorder, run_id=run_id)
    return BaselineRuntime(
        graph=EvidenceGraph(
            MeteredModelGateway(
                support.models,
                run_id=run_id,
                cancel_event=support.cancel,
                max_output_tokens=profile.harness.model_max_output_tokens,
            ),
            ExecutedLocalRetriever(
                knowledge, support.tools, run_id=run_id, cancel_event=support.cancel
            ),
            DisabledExternalSearch(),
        ),
        scheduler=support.scheduler,
        meter=support.meter,
        events=support.events,
        cancel_event=support.cancel,
        models=support.models,
    )
