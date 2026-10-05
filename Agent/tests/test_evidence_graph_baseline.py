"""Behavior snapshot of the fixed EvidenceGraph baseline (G-existing).

The graph is frozen as the control arm for Agentic RAG ablations. Refactors that extract
prompts, packing, structured output or the answer chain must leave this snapshot unchanged.
An intentional behavior change regenerates it with PED_UPDATE_SNAPSHOTS=1 and must be
called out in the commit message.
"""

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path

import pytest

from ped_contracts.evidence import (
    AnswerDraft,
    EvidenceItem,
    EvidenceOrigin,
    ModelOutput,
    RetrievalBatch,
    SemanticReview,
)
from ped_research_agent.context import ResearchQuery
from ped_research_agent.evidence_graph import EvidenceGraph, VerificationFailed

SNAPSHOT_PATH = Path(__file__).parent / "snapshots" / "evidence_graph_baseline.json"
FIXED_TIME = datetime(2026, 1, 1, tzinfo=UTC)


def evidence(evidence_id: str, origin: EvidenceOrigin, quote: str) -> EvidenceItem:
    return EvidenceItem(
        evidence_id=evidence_id,
        origin=origin,
        title=f"Title {evidence_id}",
        quote=quote,
        locator="p.1" if origin is EvidenceOrigin.LOCAL_OFFICIAL else None,
        resource_id=evidence_id if origin is EvidenceOrigin.LOCAL_OFFICIAL else None,
        url=None
        if origin is EvidenceOrigin.LOCAL_OFFICIAL
        else f"https://example.org/{evidence_id}",
        retrieved_at=FIXED_TIME,
        content_hash=hashlib.sha256(evidence_id.encode("utf-8")).hexdigest(),
        score=0.5,
    )


def local(evidence_id: str) -> EvidenceItem:
    return evidence(evidence_id, EvidenceOrigin.LOCAL_OFFICIAL, f"Local quote {evidence_id}.")


def academic(evidence_id: str) -> EvidenceItem:
    return evidence(evidence_id, EvidenceOrigin.EXTERNAL_ACADEMIC, f"Abstract {evidence_id}.")


def two_claim_draft(*, second_label: str = "A1", second_id: str = "academic-1") -> str:
    return json.dumps(
        {
            "answer_markdown": f"Density rises [L1]. External agrees [{second_label}].",
            "claims": [
                {"claim_id": "c1", "text": "Density rises", "citation_labels": ["L1"]},
                {"claim_id": "c2", "text": "External agrees", "citation_labels": [second_label]},
            ],
            "citations": [
                {"label": "L1", "evidence_id": "refined-1", "claim_ids": ["c1"]},
                {"label": second_label, "evidence_id": second_id, "claim_ids": ["c2"]},
            ],
            "inferences": [],
            "limitations": ["Fixture limitation"],
        }
    )


def one_claim_draft(evidence_id: str) -> str:
    return json.dumps(
        {
            "answer_markdown": "Density rises [L1].",
            "claims": [{"claim_id": "c1", "text": "Density rises", "citation_labels": ["L1"]}],
            "citations": [{"label": "L1", "evidence_id": evidence_id, "claim_ids": ["c1"]}],
            "inferences": [],
            "limitations": [],
        }
    )


def review(*statuses: str) -> str:
    return json.dumps(
        {"claims": [{"claim_id": f"c{i}", "status": s} for i, s in enumerate(statuses, 1)]}
    )


class Recorder:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []
        self.calls: list[dict[str, object]] = []
        self.retrieval_queries: list[str] = []
        self.external_queries: list[str] = []

    async def emit(self, event: str, payload: dict[str, object]) -> None:
        self.events.append(
            {"event": event, **{k: v for k, v in payload.items() if k != "duration_ms"}}
        )


class ScriptedGateway:
    def __init__(
        self,
        recorder: Recorder,
        generated: list[str],
        verified: list[str],
        *,
        verification_enabled: bool = True,
    ) -> None:
        self.recorder = recorder
        self.generated = list(generated)
        self.verified = list(verified)
        self._verification_enabled = verification_enabled

    @property
    def verification_enabled(self) -> bool:
        return self._verification_enabled

    async def generate(self, prompt: str) -> ModelOutput:
        self.recorder.calls.append({"kind": "generate", "prompt": prompt})
        return ModelOutput(content=self.generated.pop(0), model="fake-answer")

    async def verify(self, prompt: str) -> ModelOutput:
        self.recorder.calls.append({"kind": "verify", "prompt": prompt})
        return ModelOutput(content=self.verified.pop(0), model="fake-verify")


class NativeStructuredGateway(ScriptedGateway):
    async def generate_structured(self, prompt: str, schema):
        self.recorder.calls.append(
            {"kind": "generate_structured", "schema": schema.__name__, "prompt": prompt}
        )
        content = self.generated.pop(0)
        return AnswerDraft.model_validate_json(content), ModelOutput(
            content=content, model="native-answer"
        )

    async def verify_structured(self, prompt: str, schema):
        self.recorder.calls.append(
            {"kind": "verify_structured", "schema": schema.__name__, "prompt": prompt}
        )
        content = self.verified.pop(0)
        return SemanticReview.model_validate_json(content), ModelOutput(
            content=content, model="native-verify"
        )


class ScriptedRetriever:
    def __init__(self, recorder: Recorder, batches: list[RetrievalBatch]) -> None:
        self.recorder = recorder
        self.batches = list(batches)

    async def retrieve(self, query: str) -> RetrievalBatch:
        self.recorder.retrieval_queries.append(query)
        return self.batches.pop(0)


class ScriptedSearcher:
    def __init__(self, recorder: Recorder, items: list[EvidenceItem]) -> None:
        self.recorder = recorder
        self.items = items

    async def search(self, query: str) -> list[EvidenceItem]:
        self.recorder.external_queries.append(query)
        return list(self.items)


def query() -> ResearchQuery:
    return ResearchQuery(
        run_id="22222222-2222-2222-2222-222222222222",
        query="How does density change near a bottleneck?",
        recent_messages=[{"role": "user", "content": "Tell me about bottlenecks."}],
        previous_evidence_ids=["preflight-1"],
    )


def scenario_external_with_revision(recorder: Recorder) -> EvidenceGraph:
    # Preflight is insufficient, so external search runs. The refined batch fills the
    # local cap of 8, which displaces the preflight item (current behavior, gap #4).
    refined = [local(f"refined-{i}") for i in range(1, 9)]
    return EvidenceGraph(
        ScriptedGateway(
            recorder,
            ["standalone bottleneck density query", two_claim_draft(), two_claim_draft()],
            [review("supported", "partial"), review("supported", "supported")],
        ),
        ScriptedRetriever(
            recorder,
            [
                RetrievalBatch(items=[local("preflight-1")], sufficient=False),
                RetrievalBatch(
                    items=refined,
                    sufficient=True,
                    degraded=True,
                    degradation_reason="vector index unavailable",
                ),
            ],
        ),
        ScriptedSearcher(recorder, [academic("academic-1")]),
    )


def scenario_fail_closed(recorder: Recorder) -> EvidenceGraph:
    bad = two_claim_draft(second_label="A9", second_id="missing-evidence")
    return EvidenceGraph(
        ScriptedGateway(recorder, ["rewritten", bad, bad], []),
        ScriptedRetriever(
            recorder,
            [
                RetrievalBatch(items=[local("preflight-1")], sufficient=False),
                RetrievalBatch(items=[local("refined-1")], sufficient=True),
            ],
        ),
        ScriptedSearcher(recorder, [academic("academic-1")]),
    )


def scenario_rules_only(recorder: Recorder) -> EvidenceGraph:
    return EvidenceGraph(
        ScriptedGateway(
            recorder, ["rewritten", one_claim_draft("refined-1")], [], verification_enabled=False
        ),
        ScriptedRetriever(
            recorder,
            [
                RetrievalBatch(items=[local("preflight-1")], sufficient=True),
                RetrievalBatch(items=[local("refined-1")], sufficient=True),
            ],
        ),
        ScriptedSearcher(recorder, []),
        allow_rules_only=True,
    )


def scenario_insufficient(recorder: Recorder) -> EvidenceGraph:
    return EvidenceGraph(
        ScriptedGateway(recorder, [], []),
        ScriptedRetriever(recorder, [RetrievalBatch(items=[], sufficient=False)]),
        ScriptedSearcher(recorder, []),
    )


def scenario_native_structured(recorder: Recorder) -> EvidenceGraph:
    return EvidenceGraph(
        NativeStructuredGateway(
            recorder, ["rewritten", one_claim_draft("refined-1")], [review("supported")]
        ),
        ScriptedRetriever(
            recorder,
            [
                RetrievalBatch(items=[local("preflight-1")], sufficient=True),
                RetrievalBatch(items=[local("refined-1")], sufficient=True),
            ],
        ),
        ScriptedSearcher(recorder, []),
    )


SCENARIOS = {
    "external_with_revision": scenario_external_with_revision,
    "fail_closed": scenario_fail_closed,
    "rules_only": scenario_rules_only,
    "insufficient_evidence": scenario_insufficient,
    "native_structured": scenario_native_structured,
}


async def run_scenario(name: str) -> dict[str, object]:
    recorder = Recorder()
    graph = SCENARIOS[name](recorder)
    try:
        result = await graph.execute(query(), recorder.emit, lambda: False)
    except VerificationFailed as exc:
        outcome: dict[str, object] = {"error": f"{type(exc).__name__}: {exc}"}
    else:
        outcome = {
            "answer": result.answer.model_dump(mode="json"),
            "evidence_ids": [item.evidence_id for item in result.evidence],
            "metrics": result.metrics.model_dump(mode="json"),
        }
    return json.loads(
        json.dumps(
            {
                "retrieval_queries": recorder.retrieval_queries,
                "external_queries": recorder.external_queries,
                "events": recorder.events,
                "model_calls": recorder.calls,
                "outcome": outcome,
            },
            default=str,
        )
    )


async def build_snapshot() -> dict[str, object]:
    return {name: await run_scenario(name) for name in SCENARIOS}


@pytest.mark.asyncio
async def test_evidence_graph_matches_baseline_snapshot() -> None:
    actual = await build_snapshot()
    if os.environ.get("PED_UPDATE_SNAPSHOTS") == "1":
        SNAPSHOT_PATH.parent.mkdir(exist_ok=True)
        SNAPSHOT_PATH.write_text(
            json.dumps(actual, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    assert SNAPSHOT_PATH.is_file(), "snapshot missing; run once with PED_UPDATE_SNAPSHOTS=1"
    expected = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    for name in SCENARIOS:
        assert actual[name] == expected[name], f"baseline behavior changed in scenario {name}"
    assert set(expected) == set(SCENARIOS)
