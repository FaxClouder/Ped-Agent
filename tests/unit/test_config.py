from __future__ import annotations

import os
from pathlib import Path

from ped_agent.utils.config import load_project_env, select

ROOT = Path(__file__).resolve().parents[2]


def test_project_env_loads_without_overriding_process_environment(
    tmp_path, monkeypatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "PED_AGENT_APP__LOG_LEVEL=DEBUG\nPED_AGENT_VISION__BACKEND=yolo26_deepsort\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PED_AGENT_APP__LOG_LEVEL", "WARNING")
    monkeypatch.delenv("PED_AGENT_VISION__BACKEND", raising=False)

    assert load_project_env(env_file) is True
    assert os.environ["PED_AGENT_APP__LOG_LEVEL"] == "WARNING"
    assert os.environ["PED_AGENT_VISION__BACKEND"] == "yolo26_deepsort"


def test_select_reads_only_explicit_nested_mapping() -> None:
    config = {"analysis": {"fundamental_diagram": {"enabled": False}}}

    assert select(config, "analysis.fundamental_diagram.enabled") is False
    assert select(config, "analysis.missing", "fallback") == "fallback"


def test_legacy_yaml_configuration_directory_is_removed() -> None:
    assert not (ROOT / "config").exists()
