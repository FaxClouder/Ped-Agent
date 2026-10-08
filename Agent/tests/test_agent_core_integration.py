"""Small synthetic SQLite corpus; no PDFs, model calls, network or evaluation question set."""

from __future__ import annotations

import hashlib
import json
from uuid import uuid4

import pytest
from pydantic import ValidationError

from ped_agent_harness import MemoryRecorder, ToolCall, ToolFailure, ToolSuccess
from ped_agent_harness.model_contracts import (
    ModelCapabilities,
    ModelReply,
    ModelRequest,
    ModelUsage,
)
from ped_knowledge.contracts import IngestionManifest, KnowledgeChunk
from ped_knowledge.indexing import FTSIndex
from ped_knowledge.retrieval import HybridRetriever, retrieval_is_sufficient
from ped_knowledge.storage import Catalog
from ped_research_agent.agentic.config import load_profile
from ped_research_agent.agentic.state import AgenticResult, DecisionState, Requirement, StopReason
from ped_research_agent.context import ResearchQuery
from ped_research_agent.integrations.knowledge import (
    EvidenceReadError,
    KnowledgeAdapter,
    KnowledgeSnapshotError,
    ReadEvidenceInput,
    SearchInput,
    SnapshotIdentity,
)
from ped_research_agent.integrations.runtime import build_baseline


@pytest.fixture
def source(tmp_path):
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    record = IngestionManifest(
        resource_id="synthetic",
        resource_type="literature",
        title="Density",
        language="en",
        source_path=tmp_path / "not-read.pdf",
        sha256="c" * 64,
    )
    catalog.upsert_resource(record, version_id=record.sha256, vault_path="unused")
    fields = dict(
        resource_id=record.resource_id,
        version_id=record.sha256,
        page_start=1,
        page_end=1,
        locator="p.1",
        parser_version="synthetic",
    )
    chunks = [
        KnowledgeChunk(
            **fields,
            chunk_id="parent",
            ordinal=0,
            chunk_level="parent",
            text="Density rises near the bottleneck. Parent context.",
        ),
        KnowledgeChunk(
            **fields,
            chunk_id="child",
            ordinal=1,
            parent_chunk_id="parent",
            text="Density rises near the bottleneck.",
        ),
    ]
    catalog.replace_chunks(record.sha256, chunks, policy_version="parent-child-v1")
    catalog_hash = catalog.official_fingerprint(policy_version="parent-child-v1")
    fts = FTSIndex(tmp_path / "fts.sqlite3")
    fts.rebuild(
        catalog.list_official_chunks(policy_version="parent-child-v1"),
        source_fingerprint=catalog_hash,
    )
    snapshot = SnapshotIdentity(
        policy_version="parent-child-v1",
        catalog_fingerprint=catalog_hash,
        index_fingerprint=fts.source_fingerprint(),
    )
    adapter = KnowledgeAdapter(
        HybridRetriever(catalog, fts, None, embedding_fingerprint="unused"),
        catalog,
        snapshot=snapshot,
        current_index_fingerprint=fts.source_fingerprint,
        baseline_sufficiency=lambda query, items: retrieval_is_sufficient(query, list(items)),
    )
    manifest = tmp_path / "snapshot.json"
    manifest.write_text(snapshot.model_dump_json())
    profile = tmp_path / "profile.json"
    profile.write_text(
        json.dumps(
            {
                "profile_id": "synthetic",
                "knowledge": {
                    "manifest": "snapshot.json",
                    "sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
                },
                "output_dir": "run",
            }
        )
    )
    return adapter, catalog, profile


@pytest.mark.parametrize(
    "patch",
    [
        {"harness": {"max_tool_calls": 0}},
        {"harness": {"tool_allowlist": ["shell"]}},
        {"agent": {"external_policy": "enabled"}},
        {"api_key": "not-a-secret"},
    ],
)
def test_profile_rejects_invalid_or_secret_fields(source, patch):
    _, _, path = source
    data = json.loads(path.read_text())
    data.update(patch)
    path.write_text(json.dumps(data))
    with pytest.raises(ValidationError):
        load_profile(path)


def test_profile_inheritance_paths_and_asset_validation(source, tmp_path):
    _, _, base = source
    sub = tmp_path / "child"
    sub.mkdir()
    path = sub / "profile.toml"
    path.write_text('extends = "../profile.json"\n[harness]\nmax_tool_calls = 2\n')
    profile = load_profile(path)
    assert profile.output_dir == tmp_path / "run"
    assert profile.knowledge.manifest == tmp_path / "snapshot.json"
    assert profile.harness.max_tool_calls == 2
    assert profile.harness.max_model_calls == 12
    assert not profile.output_dir.exists()
    profile.knowledge.manifest.write_text("changed")
    with pytest.raises(ValueError, match="hash mismatch"):
        load_profile(path)


@pytest.mark.parametrize("dependencies", [["absent"], ["root"]])
def test_requirement_graph_rejects_missing_or_cyclic_dependencies(dependencies):
    state = DecisionState(
        question="q",
        requirements={
            "root": Requirement(id="root", statement="fact", depends_on=dependencies),
        },
    )
    with pytest.raises(ValueError):
        state.validate_plan(max_requirements=12)


def test_quality_stop_requires_support_and_other_stops_return_gaps():
    state = DecisionState(question="q", stop_reason=StopReason.NO_GAIN_STOP)
    stopped = AgenticResult(state=state, stop_reason=StopReason.NO_GAIN_STOP, outcome="stopped")
    assert stopped.answer is None
    state.stop_reason = StopReason.QUALITY_STOP
    with pytest.raises(ValidationError, match="requirement count"):
        AgenticResult(state=state, stop_reason=StopReason.QUALITY_STOP, outcome="stopped")


@pytest.mark.asyncio
async def test_real_sparse_retrieval_preserves_identity_and_explicit_parent(source):
    adapter, catalog, _ = source
    result = await adapter.search(SearchInput(query="density"))
    assert result.degraded and result.degradation_reason
    item = result.items[0]
    assert item.evidence_id == "local:child" and item.version_id == "c" * 64
    parent = adapter.read(ReadEvidenceInput(evidence_id=item.evidence_id, expand="parent"))
    assert parent.evidence.content_hash == item.content_hash
    assert parent.parent_text == result.parent_contexts[item.evidence_id]
    assert parent.parent_chunk_id == "parent"
    assert parent.parent_content_hash == hashlib.sha256(parent.parent_text.encode()).hexdigest()
    with catalog.connect() as connection:
        connection.execute("UPDATE chunks SET text = 'changed parent' WHERE chunk_id = 'parent'")
    with pytest.raises(KnowledgeSnapshotError, match="frozen retrieval context"):
        adapter.read(ReadEvidenceInput(chunk_id="child", expand="parent"))
    with catalog.connect() as connection:
        connection.execute(
            "UPDATE chunks SET text = ? WHERE chunk_id = 'parent'", (parent.parent_text,)
        )
    empty = await adapter.retrieve("nonexistentterm")
    assert empty.items == [] and not empty.sufficient
    with pytest.raises(EvidenceReadError):
        adapter.read(ReadEvidenceInput(chunk_id="unknown"))
    with catalog.connect() as connection:
        connection.execute("DELETE FROM chunks WHERE chunk_id = 'parent'")
    with pytest.raises(EvidenceReadError, match="missing"):
        adapter.read(ReadEvidenceInput(chunk_id="child", expand="parent"))
    with catalog.connect() as connection:
        connection.execute("UPDATE chunks SET text = 'changed' WHERE chunk_id = 'child'")
    with pytest.raises(KnowledgeSnapshotError, match="fingerprint"):
        await adapter.search(SearchInput(query="density"))


class ScriptedGateway:
    def capabilities(self, role: str) -> ModelCapabilities:
        return ModelCapabilities(structured=True, tools=True)

    async def invoke(self, request: ModelRequest) -> ModelReply:
        value = None
        if request.response_schema and request.role == "answer":
            value = {
                "answer_markdown": "Density rises [L1]",
                "claims": [{"claim_id": "c1", "text": "Density rises", "citation_labels": ["L1"]}],
                "citations": [{"label": "L1", "evidence_id": "local:child", "claim_ids": ["c1"]}],
            }
        elif request.response_schema:
            value = {"claims": [{"claim_id": "c1", "status": "supported"}]}
        return ModelReply(
            content=json.dumps(value) if value else "density",
            model="synthetic",
            structured=value,
            finish_reason="stop",
            usage=ModelUsage(input_tokens=10, output_tokens=5),
        )


@pytest.mark.asyncio
async def test_baseline_tools_events_and_budget_form_one_offline_run(source):
    adapter, _, path = source
    run_id = str(uuid4())
    recorder = MemoryRecorder()
    runtime = build_baseline(
        load_profile(path),
        adapter,
        ScriptedGateway(),
        recorder,
        run_id=run_id,
    )
    result = await runtime.execute(ResearchQuery(query="Density", run_id=run_id))
    assert result.answer.verification.status == "verified"
    assert result.metrics.retrieval_degraded
    assert runtime.meter.usage().tool_calls == 2
    assert runtime.meter.usage().model_calls == 3
    assert runtime.meter.usage().input_tokens == 30
    assert [e.seq for e in recorder.events] == list(range(1, len(recorder.events) + 1))
    assert {e.run_id for e in recorder.events} == {run_id}
    assert {e.type for e in recorder.events} >= {"tool_call", "tool_outcome", "stage.completed"}
    outcomes = await runtime.scheduler.run_batch(
        [
            ToolCall.create(
                run_id=run_id,
                tool_name="knowledge.read_evidence",
                arguments={"chunk_id": "child", "expand": "parent"},
            ),
            ToolCall.create(run_id=run_id, tool_name="knowledge.search", arguments={"query": ""}),
        ]
    )
    assert isinstance(outcomes[0], ToolSuccess)
    assert isinstance(outcomes[1], ToolFailure) and not outcomes[1].dispatched
    assert runtime.meter.usage().tool_calls == 3
    with pytest.raises(ValueError, match="fresh knowledge adapter"):
        build_baseline(load_profile(path), adapter, ScriptedGateway(), recorder, run_id=run_id)
    adapter.current_index_fingerprint = lambda: "f" * 64
    failure = (
        await runtime.scheduler.run_batch(
            [
                ToolCall.create(
                    run_id=run_id, tool_name="knowledge.search", arguments={"query": "density"}
                ),
            ]
        )
    )[0]
    assert isinstance(failure, ToolFailure)
    assert failure.code == "tool_error" and "KnowledgeSnapshotError" in failure.message


@pytest.mark.asyncio
@pytest.mark.parametrize("allowed", [2, 4])
async def test_json_repair_is_metered_and_call_limit_prevents_answer(source, allowed):
    from ped_agent_harness.models import ModelErrorCode, ModelExecutionError

    class RepairPort(ScriptedGateway):
        repair_value = None

        async def invoke(self, request):
            reply = await super().invoke(request)
            if request.response_schema and request.role == "answer":
                self.repair_value = reply.structured
                return reply.model_copy(update={"content": "invalid JSON", "structured": None})
            if self.repair_value is not None:
                value = self.repair_value
                self.repair_value = None
                return reply.model_copy(update={"content": json.dumps(value)})
            return reply

    adapter, _, path = source
    run_id = str(uuid4())
    profile = load_profile(path, overrides={"harness": {"max_model_calls": allowed}})
    runtime = build_baseline(profile, adapter, RepairPort(), MemoryRecorder(), run_id=run_id)
    if allowed == 2:
        with pytest.raises(ModelExecutionError) as failure:
            await runtime.execute(ResearchQuery(query="Density", run_id=run_id))
        assert failure.value.code is ModelErrorCode.BUDGET_EXHAUSTED
    else:
        result = await runtime.execute(ResearchQuery(query="Density", run_id=run_id))
        assert result.answer.verification.status == "verified"
    assert runtime.meter.usage().model_calls == allowed


@pytest.mark.asyncio
async def test_run_deadline_drains_model_and_cannot_return_verified(source):
    import asyncio

    from ped_agent_harness.models import ModelErrorCode, ModelExecutionError

    class BlockingPort(ScriptedGateway):
        settled = False

        async def invoke(self, request):
            try:
                await asyncio.Event().wait()
            finally:
                self.settled = True

    adapter, _, path = source
    run_id = str(uuid4())
    profile = load_profile(path, overrides={"harness": {"deadline_seconds": 0.03}})
    port = BlockingPort()
    runtime = build_baseline(profile, adapter, port, MemoryRecorder(), run_id=run_id)
    with pytest.raises(ModelExecutionError) as failure:
        await runtime.execute(ResearchQuery(query="Density", run_id=run_id))
    assert failure.value.code in (ModelErrorCode.BUDGET_EXHAUSTED, ModelErrorCode.TIMEOUT)
    usage = runtime.meter.usage()
    # A cold graph may consume the deadline before dispatch; that is also a valid hard stop.
    assert port.settled or usage.model_calls == 0
    assert usage.reserved_output_tokens == 0


# Stage 4: synthetic decisions exercise state semantics, not planning quality.
class ScriptedDecisions:
    def __init__(self, plan, *, judgments=(), patches=()):
        self.initial = plan
        self.judgments = iter(judgments)
        self.patches = iter(patches)
        self.triggers = []

    async def plan(self, question):
        return self.initial

    async def judge(self, state, requirement_id):
        return next(self.judgments)

    async def replan(self, state, trigger):
        from ped_research_agent.agentic.decisions import Replan

        self.triggers.append(trigger)
        return next(self.patches, Replan(rationale="scripted empty patch"))


def _decision_plan(*nodes):
    from ped_research_agent.agentic.decisions import RequirementSpec, ResearchPlan

    return ResearchPlan(requirements=[RequirementSpec(**node) for node in nodes])


def _decision_runtime(source, policy, *, limits=None, tool_budget=40):
    import asyncio

    from ped_agent_harness import BudgetMeter, RunBudget, ToolExecutor, ToolRegistry
    from ped_research_agent.agentic.config import AgentPolicy
    from ped_research_agent.agentic.controller import EvidenceController
    from ped_research_agent.integrations.decisions import HarnessEvidenceActions
    from ped_research_agent.integrations.knowledge import KnowledgeReadTool, KnowledgeSearchTool

    adapter, _, _ = source
    run_id = str(uuid4())
    adapter.bind_run(run_id)
    recorder = MemoryRecorder()
    meter = BudgetMeter(RunBudget(max_tool_calls=tool_budget, max_model_calls=20))
    cancel = asyncio.Event()
    executor = ToolExecutor(
        ToolRegistry([KnowledgeSearchTool(adapter), KnowledgeReadTool(adapter)]),
        meter,
        recorder,
        allowlist=("knowledge.search", "knowledge.read_evidence"),
    )
    actions = HarnessEvidenceActions(executor, run_id=run_id, cancel_event=cancel)
    controller = EvidenceController(
        policy,
        actions,
        limits or AgentPolicy(),
        recorder,
        run_id=run_id,
        cancel_event=cancel,
        remaining_seconds=meter.remaining_seconds,
    )
    return controller, actions, meter, recorder, cancel


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid", ["missing", "cycle", "duplicate", "too_many"])
async def test_dynamic_initial_plan_fails_without_dispatch(source, invalid):
    from ped_research_agent.agentic.config import AgentPolicy

    node = dict(id="root", statement="fact", queries=["density"])
    nodes = [node | {"depends_on": ["absent" if invalid == "missing" else "root"]}]
    if invalid in ("duplicate", "too_many"):
        nodes = [node, node | {"id": "root" if invalid == "duplicate" else "second"}]
    controller, _, meter, _, _ = _decision_runtime(
        source, ScriptedDecisions(_decision_plan(*nodes)), limits=AgentPolicy(max_requirements=1)
    )
    result = await controller.execute("synthetic question")
    assert result.stop_reason is StopReason.PLAN_INVALID and result.outcome == "failed"
    assert meter.usage().tool_calls == 0 and result.answer is None


@pytest.mark.asyncio
async def test_dynamic_failed_parent_replans_and_unblocks_child_with_metered_decisions(source):
    from ped_agent_harness.models import ModelExecutor
    from ped_research_agent.agentic.decisions import Replan, RequirementSpec
    from ped_research_agent.integrations.decisions import MeteredDecisionPolicy

    plan = _decision_plan(
        dict(id="root", statement="density fact", queries=["first fails"]),
        dict(id="child", statement="condition", depends_on=["root"], queries=["bottleneck"]),
    )

    class DecisionPort:
        def __init__(self):
            self.snapshots = []

        def capabilities(self, role):
            return ModelCapabilities(structured=True)

        async def invoke(self, request):
            payload = json.loads(request.messages[-1].content)
            if request.role == "planner":
                decision = plan.model_dump(mode="json")
            elif request.role == "replan":
                self.snapshots.append(payload["state"])
                replacement = {"root": ["density"]} if payload["trigger"] == "action_failed" else {}
                decision = Replan(
                    replace_queries=replacement,
                    additions=[]
                    if replacement
                    else [
                        RequirementSpec(
                            id="audit",
                            statement="independent condition",
                            depends_on=["root"],
                            queries=["density"],
                        )
                    ],
                    rationale="scripted bounded patch",
                ).model_dump(mode="json")
            else:
                from ped_research_agent.agentic.decisions import SupportJudgment

                decision = SupportJudgment(
                    status="satisfied",
                    support_evidence_ids=list(payload["state"]["evidence"]),
                    rationale="synthetic direct support",
                ).model_dump(mode="json")
            return ModelReply(
                content="",
                model="script",
                structured=decision,
                usage=ModelUsage(input_tokens=10, output_tokens=5),
            )

    controller, actions, meter, recorder, cancel = _decision_runtime(source, None)
    port = DecisionPort()
    models = ModelExecutor(port, meter, recorder)
    controller.policy = MeteredDecisionPolicy(
        models,
        run_id=controller.run_id,
        cancel_event=cancel,
        limits=controller.limits,
        max_output_tokens=32,
    )
    # Failure is injected at the real retriever port; calls still pass through Harness.
    retriever = source[0].retriever
    retrieve = retriever.retrieve

    async def flaky(query, **kwargs):
        if query == "first fails":
            raise OSError("synthetic unavailable index")
        return await retrieve(query, **kwargs)

    retriever.retrieve = flaky
    result = await controller.execute("synthetic question")
    assert port.snapshots[0]["requirements"]["child"]["status"] == "blocked"
    assert result.stop_reason is StopReason.QUALITY_STOP and result.answer is None
    assert result.state.requirements["root"].queries_tried == ["first fails", "density"]
    assert result.state.requirements["child"].queries_tried == ["bottleneck"]
    assert result.state.replans_used == 2
    assert meter.usage().model_calls == 6  # planner, two replans and three judgments
    assert meter.usage().tool_calls == 5  # failed search, search, read, two downstream searches
    assert list(result.state.labels.values()) == ["L1"]
    assert result.state.rounds[-1].duplicate_ids and not result.state.rounds[-1].new_ids
    assert result.state.rounds[-1].support_gain_ids == ["child", "audit"]


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_patch", [False, True])
async def test_dynamic_duplicate_evidence_and_changed_rationale_do_not_reset_no_gain(
    source,
    invalid_patch,
):
    from ped_research_agent.agentic.config import AgentPolicy
    from ped_research_agent.agentic.decisions import Replan, SupportJudgment

    plan = _decision_plan(
        dict(id="root", statement="missing fact", queries=["density", "bottleneck", "rises"])
    )
    judgments = [
        SupportJudgment(status="unknown", rationale=f"no factual support {i}") for i in range(3)
    ]
    patches = (
        [Replan(additions=plan.requirements, rationale="invalid duplicate")]
        if invalid_patch
        else []
    )
    controller, _, _, recorder, _ = _decision_runtime(
        source,
        ScriptedDecisions(plan, judgments=judgments, patches=patches),
        limits=AgentPolicy(max_rounds=5),
    )
    result = await controller.execute("synthetic question")
    assert result.stop_reason is StopReason.NO_GAIN_STOP and result.answer is None
    assert result.state.no_gain_rounds == 2
    assert len(result.state.evidence) == 1 and result.state.labels == {
        next(iter(result.state.evidence)): "L1"
    }
    assert result.state.first_seen_round == {next(iter(result.state.evidence)): 1}
    assert all(not r.support_gain_ids for r in result.state.rounds)
    assert len(result.state.rounds[-1].duplicate_ids) == 1
    assert list(result.state.requirements) == ["root"]
    assert len(result.state.rounds) == (2 if invalid_patch else 3)
    assert any(e.type == "replan_parse_failed" for e in recorder.events) == invalid_patch


def test_dynamic_replans_validate_atomically_and_reject_conflicts():
    from ped_research_agent.agentic.config import AgentPolicy
    from ped_research_agent.agentic.controller import merge_plan
    from ped_research_agent.agentic.decisions import Replan, RequirementSpec, SupportJudgment

    state = DecisionState(
        question="q",
        requirements={
            "root": Requirement(id="root", statement="fact", queries=["q"]),
        },
    )
    original = state.model_dump()

    def spec(key, deps=()):
        return RequirementSpec(id=key, statement="fact", queries=["q"], depends_on=list(deps))

    patches = [
        Replan(additions=[spec("root")], rationale="duplicate"),
        Replan(additions=[spec("new", ["absent"])], rationale="dangling"),
        Replan(additions=[spec("b", ["c"]), spec("c", ["b"])], rationale="cycle"),
        Replan(additions=[spec(str(i)) for i in range(4)], rationale="append cap"),
        Replan(additions=[spec("new")], replace_queries={"absent": ["new"]}, rationale="atomic"),
    ]
    for patch in patches:
        with pytest.raises(ValueError):
            merge_plan(state, patch, AgentPolicy())
        assert state.model_dump() == original
    with pytest.raises(ValueError):
        merge_plan(
            state,
            Replan(additions=[spec("new")], rationale="total cap"),
            AgentPolicy(max_requirements=1),
        )
    with pytest.raises(ValueError, match="contradictory"):
        SupportJudgment(
            status="satisfied",
            support_evidence_ids=["e"],
            contradictions=["conflict"],
            rationale="conflicted",
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "limit,expected",
    [
        ("round", StopReason.ROUND_LIMIT),
        ("replan", StopReason.REPLAN_LIMIT),
        ("tool", StopReason.BUDGET_EXHAUSTED),
        ("blocked", StopReason.ALL_BLOCKED),
    ],
)
async def test_dynamic_hard_bounds_return_gaps(source, limit, expected):
    from ped_research_agent.agentic.config import AgentPolicy
    from ped_research_agent.agentic.decisions import SupportJudgment

    plan = _decision_plan(
        dict(id="root", statement="missing", queries=["density"]),
        dict(id="child", statement="dependent", depends_on=["root"], queries=["bottleneck"]),
    )
    policy = ScriptedDecisions(plan, judgments=[SupportJudgment(status="unknown", rationale="gap")])
    limits = (
        AgentPolicy(max_rounds=1)
        if limit == "round"
        else AgentPolicy()
        if limit == "blocked"
        else AgentPolicy(max_replans=0)
    )
    controller, _, meter, _, _ = _decision_runtime(
        source, policy, limits=limits, tool_budget=1 if limit == "tool" else 40
    )
    result = await controller.execute("synthetic question")
    assert result.stop_reason is expected and result.answer is None
    assert not result.state.requirements["child"].queries_tried
    assert meter.usage().tool_calls <= meter.budget.max_tool_calls


@pytest.mark.asyncio
@pytest.mark.parametrize("reason", [StopReason.CANCELLED, StopReason.BUDGET_EXHAUSTED])
async def test_dynamic_cancel_and_deadline_drain_policy_and_report_stop(source, reason):
    import asyncio

    class BlockingPolicy:
        def __init__(self):
            self.started = asyncio.Event()
            self.drained = False

        async def plan(self, question):
            self.started.set()
            try:
                await asyncio.Event().wait()
            finally:
                self.drained = True

    policy = BlockingPolicy()
    controller, _, _, recorder, cancel = _decision_runtime(source, policy)
    if reason is StopReason.BUDGET_EXHAUSTED:
        controller.remaining_seconds = lambda: 0.05
    task = asyncio.create_task(controller.execute("synthetic question"))
    await policy.started.wait()
    if reason is StopReason.CANCELLED:
        cancel.set()
    result = await task
    assert result.stop_reason is reason and result.answer is None and policy.drained
    assert recorder.events[-1].type == "decision_end"


class ScriptedTailPort:
    """Scripted malformed draft plus semantic failure; not a provider quality check."""

    def __init__(self, evidence_id, label, *, repair_revision=False):
        self.draft = {
            "answer_markdown": f"Synthetic conclusion [{label}]",
            "claims": [
                {"claim_id": "c1", "text": "Synthetic conclusion", "citation_labels": [label]}
            ],
            "citations": [{"label": label, "evidence_id": evidence_id, "claim_ids": ["c1"]}],
            "inferences": [],
            "limitations": ["Synthetic offline fixture"],
        }
        self.repair_revision = repair_revision
        self.answers = self.verifies = 0

    def capabilities(self, role):
        return ModelCapabilities(structured=True)

    async def invoke(self, request):
        if request.role == "verify":
            self.verifies += 1
            data = {
                "claims": [
                    {
                        "claim_id": "c1",
                        "status": (
                            "unsupported"
                            if self.repair_revision and self.verifies == 1
                            else "supported"
                        ),
                    }
                ]
            }
        else:
            self.answers += 1
            data = self.draft
            if self.repair_revision and self.answers == 1:
                return ModelReply(
                    content="malformed",
                    model="script",
                    usage=ModelUsage(input_tokens=10, output_tokens=5),
                )
        return ModelReply(
            content=json.dumps(data),
            model="script",
            structured=data if request.response_schema else None,
            usage=ModelUsage(input_tokens=10, output_tokens=5),
        )


async def _collected_tail(source):
    controller, actions, meter, recorder, cancel = _decision_runtime(source, None)
    items = (await actions.search("density", 1)).items
    item = items[0]
    state = DecisionState(
        question="synthetic",
        requirements={
            "root": Requirement(
                id="root",
                statement="fixture fact",
                status="satisfied",
                support_evidence_ids=[item.evidence_id],
                rationale="synthetic declaration",
                queries=["density"],
                queries_tried=["density"],
            )
        },
        evidence={item.evidence_id: item},
        labels={item.evidence_id: "L7"},
        first_seen_round={item.evidence_id: 1},
        stop_reason=StopReason.QUALITY_STOP,
    )
    collected = AgenticResult(state=state, stop_reason=StopReason.QUALITY_STOP, outcome="stopped")
    return collected, controller, meter, recorder, cancel


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["retained", "cap", "lost"])
async def test_dynamic_tail_context_cap_and_support_reconfirmation(source, mode):
    from ped_agent_harness.models import ModelExecutor
    from ped_research_agent.agentic.answer import DynamicAnswerChain
    from ped_research_agent.agentic.config import AgentPolicy
    from ped_research_agent.agentic.decisions import SupportJudgment

    collected, controller, meter, recorder, cancel = await _collected_tail(source)
    item = next(iter(collected.state.evidence.values()))
    extra = item.model_copy(update={"evidence_id": "optional"})
    collected.state.evidence[extra.evidence_id] = extra
    collected.state.labels[extra.evidence_id] = "L8"
    collected.state.first_seen_round[extra.evidence_id] = 1
    decisions = ScriptedDecisions(
        None,
        judgments=[
            SupportJudgment(
                status="satisfied" if mode != "lost" else "unknown",
                support_evidence_ids=[item.evidence_id] if mode != "lost" else [],
                rationale="scripted retained support judgment",
            )
        ],
    )
    port = ScriptedTailPort(item.evidence_id, "L7")
    tail = DynamicAnswerChain(
        ModelExecutor(port, meter, recorder),
        decisions,
        AgentPolicy(max_context_items=1, max_context_tokens=1 if mode == "cap" else 16000),
        recorder,
        run_id=controller.run_id,
        cancel_event=cancel,
        max_output_tokens=32,
    )
    result = await tail.execute(collected)
    selection = next(event for event in recorder.events if event.type == "context_selection")
    assert "optional" in selection.payload["dropped_ids"]
    assert collected.state.labels[item.evidence_id] == "L7"
    if mode == "retained":
        assert result.answer.verification.status == "verified"
        assert result.answer.citations[0].label == "L7"
        assert meter.usage().model_calls == 2
    else:
        assert result.answer is None and result.gaps
        assert result.stop_reason is (
            StopReason.CONTEXT_LIMIT if mode == "cap" else StopReason.SUPPORT_LOST
        )
        assert meter.usage().model_calls == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("model_budget", [3, 5])
async def test_dynamic_tail_reuses_repair_revision_and_shared_budget(source, model_budget):
    from ped_agent_harness.models import ModelExecutor
    from ped_research_agent.agentic.answer import DynamicAnswerChain
    from ped_research_agent.agentic.config import AgentPolicy

    collected, controller, meter, recorder, cancel = await _collected_tail(source)
    meter.budget = meter.budget.model_copy(update={"max_model_calls": model_budget})
    key = next(iter(collected.state.evidence))
    port = ScriptedTailPort(key, "L7", repair_revision=True)
    tail = DynamicAnswerChain(
        ModelExecutor(port, meter, recorder),
        ScriptedDecisions(None),
        AgentPolicy(),
        recorder,
        run_id=controller.run_id,
        cancel_event=cancel,
        max_output_tokens=32,
    )
    result = await tail.execute(collected)
    assert meter.usage().model_calls == model_budget
    if model_budget == 5:
        assert (
            result.answer.verification.status == "verified" and result.answer.verification.repaired
        )
        assert port.answers == 3 and port.verifies == 2
    else:
        assert (
            result.stop_reason is StopReason.BUDGET_EXHAUSTED
            and result.answer is None
            and result.gaps
        )
