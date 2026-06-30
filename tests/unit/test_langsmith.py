from __future__ import annotations

import os

from ped_agent.utils.langsmith import configure_langsmith


def test_configure_langsmith_disabled_sets_tracing_false(monkeypatch):
    monkeypatch.setenv("LANGSMITH_TRACING", "true")

    configure_langsmith({"langsmith": {"enabled": False}})

    assert os.environ["LANGSMITH_TRACING"] == "false"


def test_configure_langsmith_enabled_sets_runtime_env(monkeypatch):
    monkeypatch.delenv("LANGSMITH_TRACING", raising=False)
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)

    configure_langsmith(
        {
            "langsmith": {
                "enabled": True,
                "api_key": "test-key",
                "project_name": "ped-agent-test",
                "tracing": {"enabled": True},
            }
        }
    )

    assert os.environ["LANGSMITH_TRACING"] == "true"
    assert os.environ["LANGSMITH_API_KEY"] == "test-key"
    assert os.environ["LANGSMITH_PROJECT"] == "ped-agent-test"
