"""Legacy Phase 1 compatibility CLI.

The authoritative application CLI and server runtime live in ped_agent_server.
Verified answers are executed by EvidenceGraph through the server Run lifecycle.
This module remains only for scaffold compatibility and reads the repository .env.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from ped_agent.agent.graph import build_agent_graph
from ped_agent.utils.config import load_project_env
from ped_agent.utils.logging import configure_logging, get_logger

logger = get_logger(__name__)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Ped-Agent scaffold.")
    parser.add_argument("query", nargs="?", help="Question or task to route through the agent.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    load_project_env()
    configure_logging()

    if not args.query:
        logger.info("Ped-Agent scaffold is ready. Pass a query to exercise the routing graph.")
        return 0

    graph = build_agent_graph()
    result = graph.invoke({"query": args.query})
    print(result.get("answer") or result.get("result") or result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
