from __future__ import annotations

from langsmith import traceable
from ped_agent.agent.contracts import RetrievalBatch
from ped_agent.agent.evidence_graph import EvidenceGraph
from ped_knowledge.retrieval import HybridRetriever, retrieval_is_sufficient

from ped_agent_server.run_service import (
    CancellationCheck,
    EventEmitter,
    RunExecutionContext,
    RunExecutionResult,
)
from ped_agent_server.trace_sanitization import (
    safe_local_query_inputs,
    safe_retrieval_outputs,
)


class HybridLocalEvidenceRetriever:
    def __init__(self, hybrid: HybridRetriever) -> None:
        self.hybrid = hybrid

    @traceable(
        name="hybrid_retrieval",
        run_type="retriever",
        process_inputs=safe_local_query_inputs,
        process_outputs=safe_retrieval_outputs,
    )
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
        return RunExecutionResult(
            answer=result.answer,
            evidence=result.evidence,
            metrics=result.metrics,
        )
