"""Persist one explicitly configured backend run; no provider credentials are loaded here."""

from __future__ import annotations

import asyncio
import hashlib
import importlib.metadata
import platform
import subprocess
from pathlib import Path
from uuid import uuid4

from pydantic import JsonValue

from ped_agent_harness.contracts import sha256_json
from ped_agent_harness.model_contracts import ModelPort, ModelReply, ModelRequest
from ped_research_agent.agentic.answer import stopped_result
from ped_research_agent.agentic.config import RunProfile
from ped_research_agent.agentic.decisions import DecisionPolicy
from ped_research_agent.agentic.state import AgenticResult, DecisionState, StopReason
from ped_research_agent.integrations.agentic_runtime import AgenticRuntime, build_agentic
from ped_research_agent.integrations.decisions import DECISION_PROMPT_VERSION
from ped_research_agent.integrations.knowledge import KnowledgeAdapter
from ped_research_agent.integrations.run_records import RunArchive
from ped_research_agent.prompts import PROMPT_SET_VERSION


def run_provenance(runtime: AgenticRuntime, knowledge: KnowledgeAdapter) -> dict[str, JsonValue]:
    root = Path(__file__).resolve().parents[4]
    sources: dict[str, JsonValue] = {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for module in ("Contracts", "Agent", "Agent-Harness")
        for path in sorted((root / module / "src").rglob("*.py"))
    }
    commit: str | None = None
    dirty: bool | None = None
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True))
    except (OSError, subprocess.CalledProcessError):
        pass  # Installed wheels may have no Git checkout; source digests remain available.
    versions: dict[str, JsonValue] = {}
    for package in ("pydantic", "langchain-core", "langgraph", "ped-agent-harness"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "unavailable"
    registry = runtime.execution.tools.registry
    schemas: list[JsonValue] = []
    for name in registry.names():
        tool = registry.get(name)
        assert tool is not None
        schemas.append(
            {
                "name": name,
                "version": tool.version,
                "input_sha256": sha256_json(tool.input_model.model_json_schema()),
                "output_sha256": sha256_json(tool.output_model.model_json_schema()),
            }
        )
    return {
        "code": {
            "git_commit": commit,
            "dirty": dirty,
            "source_sha256": sha256_json(sources),
            "python": platform.python_version(),
            "packages": versions,
        },
        "snapshot": knowledge.snapshot.model_dump(mode="json"),
        "fixture_or_index_fingerprint": knowledge.snapshot.index_fingerprint,
        "prompts": {"answer": PROMPT_SET_VERSION, "decisions": DECISION_PROMPT_VERSION},
        "tool_schemas": schemas,
        "model_contracts": {
            "version": "model-boundary-v1",
            "request_sha256": sha256_json(ModelRequest.model_json_schema()),
            "reply_sha256": sha256_json(ModelReply.model_json_schema()),
        },
    }


async def run_research(
    profile: RunProfile,
    knowledge: KnowledgeAdapter,
    provider: ModelPort,
    question: str,
    *,
    run_id: str | None = None,
    decisions: DecisionPolicy | None = None,
    redact_values: tuple[str, ...] = (),
) -> AgenticResult:
    """Preflight before directory creation; execution consumes one shared budget and deadline."""
    identity = run_id or str(uuid4())
    archive = RunArchive(profile, question, identity, redact_values=redact_values)
    runtime = build_agentic(
        profile, knowledge, provider, archive, run_id=identity, decisions=decisions
    )
    try:
        archive.start(run_provenance(runtime, knowledge))
        result = await runtime.execute(question)
        return archive.finish(result, runtime.execution.meter.usage())
    except asyncio.CancelledError:
        state = (
            archive.last_result.state if archive.last_result else DecisionState(question=question)
        )
        archive.finish(stopped_result(state, StopReason.CANCELLED), runtime.execution.meter.usage())
        raise
    finally:
        archive.close()
