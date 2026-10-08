from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from time import perf_counter
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from ped_contracts.evidence import (
    AnswerDocument,
    AnswerDraft,
    EvidenceItem,
    EvidenceOrigin,
    EvidenceRunMetrics,
    RetrievalBatch,
    RuleValidation,
    SemanticReview,
    VerificationSummary,
)
from ped_research_agent.answer_chain import (  # noqa: F401 - re-export
    AnswerChain,
    VerificationFailed,
)
from ped_research_agent.context import ResearchQuery
from ped_research_agent.evidence_pack import origin_counts, pack_evidence, select_evidence
from ped_research_agent.ports import (
    ExternalEvidenceSearcher,
    LocalEvidenceRetriever,
    ModelGateway,
)
from ped_research_agent.prompts import draft_prompt as _draft_prompt  # noqa: F401
from ped_research_agent.prompts import revision_prompt as _revision_prompt  # noqa: F401
from ped_research_agent.prompts import rewrite_prompt
from ped_research_agent.structured import (
    StructuredModel,
    structured_generate,
    structured_verify,
)

EventEmitter = Callable[[str, dict[str, object]], Awaitable[None]]
CancellationCheck = Callable[[], bool]
INSUFFICIENT_EVIDENCE_MESSAGE = "当前知识库与外部检索未找到足够的可核验证据，暂时无法给出可靠回答。"


class RunCancelled(RuntimeError):
    pass


@dataclass(frozen=True)
class EvidenceGraphResult:
    answer: AnswerDocument
    evidence: list[EvidenceItem]
    metrics: EvidenceRunMetrics


class EvidenceState(TypedDict, total=False):
    original_query: str
    standalone_query: str
    preflight_query: str
    recent_messages: list[dict[str, object]]
    previous_evidence_ids: list[str]
    preflight_local_batch: RetrievalBatch
    local_batch: RetrievalBatch
    external_evidence: list[EvidenceItem]
    evidence: list[EvidenceItem]
    evidence_pack: str
    needs_external: bool
    draft: AnswerDraft
    rules: RuleValidation
    review: SemanticReview
    semantic_passed: bool
    insufficient_evidence: bool
    revision_count: int
    final_answer: AnswerDocument
    emit: EventEmitter
    is_cancelled: CancellationCheck


def _preflight_query(state: EvidenceState) -> str:
    current_query = state["original_query"].strip()
    historical_queries = [
        str(message.get("content", "")).strip()
        for message in state.get("recent_messages", [])
        if message.get("role") == "user" and str(message.get("content", "")).strip()
    ]
    unique = list(dict.fromkeys(query for query in historical_queries if query != current_query))
    if current_query:
        unique.append(current_query)
    return " ".join(unique[-3:]) or state["original_query"]


def _metrics(state: EvidenceState) -> EvidenceRunMetrics:
    evidence = state.get("evidence", [])
    preflight_batch = state.get("preflight_local_batch")
    refined_batch = state.get("local_batch")
    return EvidenceRunMetrics(
        local_evidence_count=sum(item.origin is EvidenceOrigin.LOCAL_OFFICIAL for item in evidence),
        academic_evidence_count=sum(
            item.origin is EvidenceOrigin.EXTERNAL_ACADEMIC for item in evidence
        ),
        web_evidence_count=sum(item.origin is EvidenceOrigin.EXTERNAL_WEB for item in evidence),
        external_search_used=bool(state.get("needs_external")),
        retrieval_degraded=bool(
            (preflight_batch and preflight_batch.degraded)
            or (refined_batch and refined_batch.degraded)
        ),
        citation_rules_passed=(state["rules"].passed if state.get("rules") is not None else None),
        semantic_verification_passed=state["final_answer"].verification.semantic_passed,
        revision_count=state.get("revision_count", 0),
        insufficient_evidence=bool(state.get("insufficient_evidence")),
    )


class EvidenceGraph:
    def __init__(
        self,
        gateway: ModelGateway,
        local_retriever: LocalEvidenceRetriever,
        external_searcher: ExternalEvidenceSearcher,
        *,
        allow_rules_only: bool = False,
    ) -> None:
        self.gateway = gateway
        self.local_retriever = local_retriever
        self.external_searcher = external_searcher
        self.allow_rules_only = allow_rules_only
        self.answer_chain = AnswerChain(gateway, allow_rules_only=allow_rules_only)
        self.compiled = self._build()

    async def execute(
        self,
        context: ResearchQuery,
        emit: EventEmitter,
        is_cancelled: CancellationCheck,
    ) -> EvidenceGraphResult:
        state = await self.compiled.ainvoke(
            {
                "original_query": context.query,
                "recent_messages": context.recent_messages,
                "previous_evidence_ids": context.previous_evidence_ids,
                "revision_count": 0,
                "emit": emit,
                "is_cancelled": is_cancelled,
            },
            config={
                "run_id": context.validated_run_id(),
                "run_name": "ped-agent.evidence-qa",
            },
        )
        return EvidenceGraphResult(
            answer=state["final_answer"],
            evidence=state["evidence"],
            metrics=_metrics(state),
        )

    def _build(self):
        builder = StateGraph(EvidenceState)
        builder.add_node("load_conversation", self._load_conversation)
        builder.add_node("preflight_local_retrieval", self._preflight_local_retrieval)
        builder.add_node("assess_evidence", self._assess_evidence)
        builder.add_node("external_search", self._external_search)
        builder.add_node("normalize_evidence", self._normalize_evidence)
        builder.add_node("handle_insufficient_evidence", self._handle_insufficient_evidence)
        builder.add_node("rewrite_query", self._rewrite_query)
        builder.add_node("refined_local_retrieval", self._refined_local_retrieval)
        builder.add_node("merge_refined_evidence", self._merge_refined_evidence)
        builder.add_node("generate_draft", self._generate_draft)
        builder.add_node("validate_rules", self._validate_rules)
        builder.add_node("semantic_verify", self._semantic_verify)
        builder.add_node("revise_once", self._revise_once)
        builder.add_node("fail_closed", self._fail_closed)
        builder.add_node("final_persist", self._final_persist)

        builder.add_edge(START, "load_conversation")
        builder.add_edge("load_conversation", "preflight_local_retrieval")
        builder.add_edge("preflight_local_retrieval", "assess_evidence")
        builder.add_conditional_edges(
            "assess_evidence",
            lambda state: "external_search" if state["needs_external"] else "normalize_evidence",
        )
        builder.add_edge("external_search", "normalize_evidence")
        builder.add_conditional_edges(
            "normalize_evidence",
            lambda state: (
                "handle_insufficient_evidence" if not state["evidence"] else "rewrite_query"
            ),
        )
        builder.add_edge("handle_insufficient_evidence", END)
        builder.add_edge("rewrite_query", "refined_local_retrieval")
        builder.add_edge("refined_local_retrieval", "merge_refined_evidence")
        builder.add_edge("merge_refined_evidence", "generate_draft")
        builder.add_edge("generate_draft", "validate_rules")
        builder.add_conditional_edges("validate_rules", self._after_rules)
        builder.add_conditional_edges("semantic_verify", self._after_semantic)
        builder.add_edge("revise_once", "validate_rules")
        builder.add_edge("fail_closed", END)
        builder.add_edge("final_persist", END)
        return builder.compile(name="ped-agent-evidence-chain")

    async def _load_conversation(self, state: EvidenceState) -> dict[str, object]:
        return await self._stage(state, "load_conversation", lambda: {})

    async def _preflight_local_retrieval(self, state: EvidenceState) -> dict[str, object]:
        async def action() -> dict[str, object]:
            query = _preflight_query(state)
            batch = await self.local_retriever.retrieve(query)
            if batch.degraded:
                await state["emit"](
                    "evidence.summary",
                    {"degraded": True, "reason": batch.degradation_reason},
                )
            return {
                "preflight_query": query,
                "preflight_local_batch": batch,
            }

        return await self._stage(state, "preflight_local_retrieval", action)

    async def _assess_evidence(self, state: EvidenceState) -> dict[str, object]:
        return await self._stage(
            state,
            "assess_evidence",
            lambda: {"needs_external": not state["preflight_local_batch"].sufficient},
        )

    async def _external_search(self, state: EvidenceState) -> dict[str, object]:
        async def action() -> dict[str, object]:
            items = await self.external_searcher.search(state["original_query"])
            return {"external_evidence": items}

        return await self._stage(state, "external_search", action)

    async def _normalize_evidence(self, state: EvidenceState) -> dict[str, object]:
        combined = [
            *state["preflight_local_batch"].items,
            *state.get("external_evidence", []),
        ]
        return await self._pack_evidence(state, "normalize_evidence", combined)

    async def _handle_insufficient_evidence(
        self,
        state: EvidenceState,
    ) -> dict[str, object]:
        async def action() -> dict[str, object]:
            return {
                "insufficient_evidence": True,
                "final_answer": AnswerDocument(
                    answer_markdown=INSUFFICIENT_EVIDENCE_MESSAGE,
                    citations=[],
                    inferences=[],
                    limitations=[INSUFFICIENT_EVIDENCE_MESSAGE],
                    verification=VerificationSummary(
                        status="insufficient_evidence",
                        rules_passed=True,
                        semantic_passed=None,
                    ),
                ),
            }

        return await self._stage(state, "handle_insufficient_evidence", action)

    async def _rewrite_query(self, state: EvidenceState) -> dict[str, object]:
        async def action() -> dict[str, object]:
            prompt = rewrite_prompt(state["recent_messages"], state["original_query"])
            output = await self.gateway.generate(prompt)
            return {
                "standalone_query": output.content.strip() or state["original_query"],
                "__trace__": {"model": output.model},
            }

        return await self._stage(state, "rewrite_query", action)

    async def _refined_local_retrieval(self, state: EvidenceState) -> dict[str, object]:
        async def action() -> dict[str, object]:
            batch = await self.local_retriever.retrieve(state["standalone_query"])
            if batch.degraded:
                await state["emit"](
                    "evidence.summary",
                    {"degraded": True, "reason": batch.degradation_reason},
                )
            return {"local_batch": batch}

        return await self._stage(state, "refined_local_retrieval", action)

    async def _merge_refined_evidence(self, state: EvidenceState) -> dict[str, object]:
        combined = [*state["local_batch"].items, *state["evidence"]]
        return await self._pack_evidence(state, "merge_refined_evidence", combined)

    async def _pack_evidence(
        self,
        state: EvidenceState,
        stage: str,
        items: list[EvidenceItem],
    ) -> dict[str, object]:
        async def action() -> dict[str, object]:
            evidence = select_evidence(items)
            counts = origin_counts(evidence)
            await state["emit"]("evidence.summary", {"total": len(evidence), **counts})
            return {
                "evidence": evidence,
                "evidence_pack": pack_evidence(evidence),
                "__trace__": {"evidence_ids": [item.evidence_id for item in evidence]},
            }

        return await self._stage(state, stage, action)

    async def _generate_draft(self, state: EvidenceState) -> dict[str, object]:
        async def action() -> dict[str, object]:
            draft, model = await self.answer_chain.draft(
                state["original_query"], state["evidence_pack"]
            )
            return {"draft": draft, "__trace__": {"model": model}}

        return await self._stage(state, "generate_draft", action)

    async def _validate_rules(self, state: EvidenceState) -> dict[str, object]:
        def action() -> dict[str, object]:
            rules = self.answer_chain.validate(state["draft"], state["evidence"])
            return {
                "rules": rules,
                "__trace__": {"rules_passed": rules.passed, "errors": rules.errors},
            }

        return await self._stage(state, "validate_rules", action)

    async def _semantic_verify(self, state: EvidenceState) -> dict[str, object]:
        async def action() -> dict[str, object]:
            outcome = await self.answer_chain.semantic_verify(
                state["draft"], state["evidence_pack"]
            )
            result: dict[str, object] = {
                "semantic_passed": outcome.passed,
                "review": outcome.review,
            }
            if outcome.model is not None:
                result["__trace__"] = {"model": outcome.model, "semantic_passed": outcome.passed}
            return result

        return await self._stage(state, "semantic_verify", action)

    async def _revise_once(self, state: EvidenceState) -> dict[str, object]:
        async def action() -> dict[str, object]:
            draft, model = await self.answer_chain.revise(
                state["draft"],
                state["rules"],
                state.get("review"),
                state["evidence_pack"],
            )
            return {
                "draft": draft,
                "revision_count": state["revision_count"] + 1,
                "__trace__": {"model": model, "revision": state["revision_count"] + 1},
            }

        return await self._stage(state, "revise_once", action)

    async def _fail_closed(self, state: EvidenceState) -> dict[str, object]:
        raise self.answer_chain.failure(state["rules"])

    async def _final_persist(self, state: EvidenceState) -> dict[str, object]:
        async def action() -> dict[str, object]:
            answer = self.answer_chain.final_answer(state["draft"], state["revision_count"])
            return {
                "final_answer": answer,
                "__trace__": {"verification": answer.verification.status},
            }

        return await self._stage(state, "final_persist", action)

    def _after_rules(self, state: EvidenceState) -> str:
        return self.answer_chain.after_rules(state["rules"], state["revision_count"])

    def _after_semantic(self, state: EvidenceState) -> str:
        return self.answer_chain.after_semantic(state["semantic_passed"], state["revision_count"])

    async def _stage(
        self,
        state: EvidenceState,
        name: str,
        action: Callable[[], Awaitable[dict[str, object]] | dict[str, object]],
    ) -> dict[str, object]:
        if state["is_cancelled"]():
            raise RunCancelled("run was cancelled")
        await state["emit"]("stage.started", {"stage": name})
        started = perf_counter()
        result = action()
        if hasattr(result, "__await__"):
            result = await result  # type: ignore[misc]
        trace = result.pop("__trace__", {})
        await state["emit"](
            "stage.completed",
            {
                "stage": name,
                "duration_ms": round((perf_counter() - started) * 1000, 3),
                **trace,
            },
        )
        return result

    async def _structured_generate(
        self,
        prompt: str,
        model: type[StructuredModel],
    ) -> tuple[StructuredModel, str]:
        return await structured_generate(self.gateway, prompt, model)

    async def _structured_verify(
        self,
        prompt: str,
        model: type[StructuredModel],
    ) -> tuple[StructuredModel, str]:
        return await structured_verify(self.gateway, prompt, model)
