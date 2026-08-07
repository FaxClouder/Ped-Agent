from __future__ import annotations

import logging
import os

from ped_agent.utils.config import load_project_env


def configure_logging() -> None:
    load_project_env()
    level_name = os.getenv("PED_AGENT_APP__LOG_LEVEL", "INFO")
    level = getattr(logging, str(level_name).upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
