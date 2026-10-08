"""Reusable domain backend: explicit dependencies, shared execution support, no provider setup."""

from __future__ import annotations

from dataclasses import dataclass

from ped_agent_harness.model_contracts import ModelPort
from ped_agent_harness.recorder import Recorder
from ped_research_agent.agentic.answer import DynamicAnswerChain
from ped_research_agent.agentic.config import RunProfile
from ped_research_agent.agentic.controller import EvidenceController
from ped_research_agent.agentic.decisions import DecisionPolicy
from ped_research_agent.agentic.state import AgenticResult
from ped_research_agent.integrations.decisions import HarnessEvidenceActions, MeteredDecisionPolicy
from ped_research_agent.integrations.knowledge import KnowledgeAdapter
from ped_research_agent.integrations.runtime import ExecutionSupport, build_execution


@dataclass(frozen=True)
class AgenticRuntime:
    controller: EvidenceController
    answer: DynamicAnswerChain
    execution: ExecutionSupport

    async def execute(self, question: str) -> AgenticResult:
        return await self.answer.execute(await self.controller.execute(question))


def build_agentic(
    profile: RunProfile,
    knowledge: KnowledgeAdapter,
    provider: ModelPort,
    recorder: Recorder,
    *,
    run_id: str,
    decisions: DecisionPolicy | None = None,
) -> AgenticRuntime:
    support = build_execution(profile, knowledge, provider, recorder, run_id=run_id)
    policy = decisions or MeteredDecisionPolicy(
        support.models,
        run_id=run_id,
        cancel_event=support.cancel,
        limits=profile.agent,
        max_output_tokens=profile.harness.model_max_output_tokens,
    )
    actions = HarnessEvidenceActions(support.tools, run_id=run_id, cancel_event=support.cancel)
    return AgenticRuntime(
        EvidenceController(
            policy,
            actions,
            profile.agent,
            recorder,
            run_id=run_id,
            cancel_event=support.cancel,
            remaining_seconds=support.meter.remaining_seconds,
        ),
        DynamicAnswerChain(
            support.models,
            policy,
            profile.agent,
            recorder,
            run_id=run_id,
            cancel_event=support.cancel,
            max_output_tokens=profile.harness.model_max_output_tokens,
        ),
        support,
    )
