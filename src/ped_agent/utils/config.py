from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


def load_project_env(
    env_file: str | Path | None = None,
    *,
    override: bool = False,
) -> bool:
    """Load the repository-root .env file for compatibility scripts.

    The server uses ``AgentSettings`` directly. This helper only keeps standalone
    repository scripts on the same environment source without reintroducing a
    second YAML configuration system.
    """

    target = PROJECT_ENV_FILE if env_file is None else Path(env_file)
    return load_dotenv(dotenv_path=target, override=override)


def select(config: Any, key: str, default: Any = None) -> Any:
    """Read a dotted path from an explicitly supplied mapping."""

    current = config
    for part in key.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return default
        current = current[part]
    return current
