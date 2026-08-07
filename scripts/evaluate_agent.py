from __future__ import annotations

import argparse

from ped_agent.agent.graph import build_agent_graph
from ped_agent.utils.config import load_project_env


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test the Ped-Agent routing graph.")
    parser.add_argument("query")
    args = parser.parse_args()

    load_project_env()
    graph = build_agent_graph()
    result = graph.invoke({"query": args.query})
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
