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
