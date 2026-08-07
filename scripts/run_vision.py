from __future__ import annotations

import argparse
import os

from ped_agent.utils.config import load_project_env
from ped_video_analysis.vision.registry import VisionRegistry


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a configured vision backend.")
    parser.add_argument("video_path")
    parser.add_argument("--backend", default=None)
    args = parser.parse_args()

    load_project_env()
    backend_name = args.backend or os.getenv(
        "PED_AGENT_VISION__BACKEND", "yolo26_bytetrack"
    )
    backend = VisionRegistry.get(backend_name)
    result = backend.process_video(args.video_path)
    print(result.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
