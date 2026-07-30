from __future__ import annotations

from ped_agent.agent.contracts import RetrievalBatch
from ped_agent.agent.evidence_graph import EvidenceGraph

from ped_agent_server.hybrid_retrieval import HybridRetriever, retrieval_is_sufficient
from ped_agent_server.run_service import (
    CancellationCheck,
    EventEmitter,
    RunExecutionContext,
    RunExecutionResult,
)


class HybridLocalEvidenceRetriever:
    def __init__(self, hybrid: HybridRetriever) -> None:
        self.hybrid = hybrid

    async def retrieve(self, query: str) -> RetrievalBatch:
        result = await self.hybrid.retrieve(query)
        return RetrievalBatch(
            items=result.items,
            sufficient=retrieval_is_sufficient(query, result.items),
            degraded=result.degraded,
            degradation_reason=result.degradation_reason,
        )


class LangGraphRunExecutor:
    def __init__(self, graph: EvidenceGraph) -> None:
        self.graph = graph

    async def execute(
        self,
        context: RunExecutionContext,
        emit: EventEmitter,
        is_cancelled: CancellationCheck,
    ) -> RunExecutionResult:
        result = await self.graph.execute(context, emit, is_cancelled)
        return RunExecutionResult(answer=result.answer, evidence=result.evidence)
