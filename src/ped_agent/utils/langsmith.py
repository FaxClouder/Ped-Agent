from __future__ import annotations

import os
from typing import Any

from ped_agent.utils.config import select


def configure_langsmith(config: Any) -> None:
    if not select(config, "langsmith.enabled", False):
        os.environ["LANGSMITH_TRACING"] = "false"
        return

    tracing_enabled = select(config, "langsmith.tracing.enabled", True)
    os.environ["LANGSMITH_TRACING"] = "true" if tracing_enabled else "false"
    if api_key := select(config, "langsmith.api_key"):
        os.environ["LANGSMITH_API_KEY"] = str(api_key)
    if project := select(config, "langsmith.project_name"):
        os.environ["LANGSMITH_PROJECT"] = str(project)
