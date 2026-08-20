from __future__ import annotations

import argparse
from pathlib import Path

from ped_video_analysis import create_model_registry, run_video_inference


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one video inference experiment.")
    parser.add_argument("video_path", type=Path)
    parser.add_argument("--task-id", default="vision-experiment")
    parser.add_argument("--model-id", default="mixed-flow-yolo26-bytetrack")
    parser.add_argument("--tracker-id", default="bytetrack")
    args = parser.parse_args()

    registry = create_model_registry(tracker_id=args.tracker_id)
    result = run_video_inference(
        args.video_path,
        task_id=args.task_id,
        model_id=args.model_id,
        registry=registry,
    )
    print(result.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
