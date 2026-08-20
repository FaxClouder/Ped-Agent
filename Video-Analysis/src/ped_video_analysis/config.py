from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def select(config: Any, key: str, default: Any = None) -> Any:
    """Read a dotted key from mapping-style experiment configuration."""

    current = config
    for part in key.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return default
        current = current[part]
    return current
