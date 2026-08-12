from pathlib import Path

import pytest

from ped_agent_server.agent_runtime import build_agent_runtime
from ped_agent_server.paths import WorkspacePaths
from ped_agent_server.run_observer import NoOpRunObserver
from ped_agent_server.settings import load_settings


@pytest.mark.asyncio
async def test_runtime_wires_repository_graph_and_direct_clients(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PED_AGENT_ANSWER__MODEL", "gpt-test")
    monkeypatch.setenv("PED_AGENT_ANSWER__API_KEY", "answer-secret")
    monkeypatch.setenv("PED_AGENT_VERIFY__ENABLED", "false")
    monkeypatch.setenv("PED_AGENT_EMBEDDING__PROTOCOL", "openai_compatible")
    monkeypatch.setenv("PED_AGENT_EMBEDDING__MODEL", "embed-test")
    monkeypatch.setenv("PED_AGENT_EMBEDDING__API_KEY", "embedding-secret")
    monkeypatch.setenv("PED_AGENT_RUNTIME__AGENT_DB_PATH", "local/agent.sqlite3")
    monkeypatch.setenv("PED_AGENT_RUNTIME__CHROMA_PATH", "local/chroma")
    settings = load_settings(env_file=None)
    paths = WorkspacePaths.from_repo_root(tmp_path)

    runtime = build_agent_runtime(settings, paths)

    assert runtime.repository.path == tmp_path / "local" / "agent.sqlite3"
    assert runtime.run_service.repository is runtime.repository
    assert runtime.run_service.executor.graph.allow_rules_only is True
    assert isinstance(runtime.run_service.observer, NoOpRunObserver)
    await runtime.close()


@pytest.mark.asyncio
async def test_runtime_builds_langsmith_observer_with_model_roles(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    marker = NoOpRunObserver()
    captured = {}

    def fake_observer(settings, **kwargs):
        captured.update(kwargs)
        return marker

    monkeypatch.setattr(
        "ped_agent_server.agent_runtime.LangSmithObserver",
        fake_observer,
    )
    monkeypatch.setenv("PED_AGENT_ANSWER__MODEL", "deepseek-v4-flash")
    monkeypatch.setenv("PED_AGENT_ANSWER__API_KEY", "answer-secret")
    monkeypatch.setenv("PED_AGENT_VERIFY__MODEL", "deepseek-v4-pro")
    monkeypatch.setenv("PED_AGENT_EMBEDDING__PROTOCOL", "openai_compatible")
    monkeypatch.setenv("PED_AGENT_EMBEDDING__MODEL", "embed-test")
    monkeypatch.setenv("PED_AGENT_EMBEDDING__API_KEY", "embedding-secret")
    monkeypatch.setenv("PED_AGENT_LANGSMITH__ENABLED", "true")
    monkeypatch.setenv("PED_AGENT_LANGSMITH__API_KEY", "langsmith-secret")
    settings = load_settings(env_file=None)

    runtime = build_agent_runtime(settings, WorkspacePaths.from_repo_root(tmp_path))

    assert runtime.run_service.observer is marker
    assert captured == {
        "answer_model": "deepseek-v4-flash",
        "verify_model": "deepseek-v4-pro",
        "embedding_model": "embed-test",
        "external_search_enabled": True,
        "verification_required": True,
    }
    await runtime.close()
