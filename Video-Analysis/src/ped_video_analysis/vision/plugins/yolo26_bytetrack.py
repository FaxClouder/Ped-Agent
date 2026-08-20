from __future__ import annotations

from pathlib import Path
from typing import Any

from ped_contracts.trajectory import TrajectoryData
from ped_video_analysis.vision.pipeline import VisionPipeline
from ped_video_analysis.vision.registry import VisionRegistry
from ped_video_analysis.vision.schemas import ROI, Detection


@VisionRegistry.register("yolo26_bytetrack")
class YOLO26ByteTrackBackend:
    def __init__(self, config: dict | None = None):
        merged = dict(config or {})
        merged.setdefault("tracker", {}).setdefault("algorithm", "bytetrack")
        self.config = merged
        self._pipeline: VisionPipeline | None = None

    @property
    def pipeline(self) -> VisionPipeline:
        if self._pipeline is None:
            self._pipeline = VisionPipeline(self.config)
        return self._pipeline

    def configure(self, config: dict) -> None:
        self.config = config
        self.config.setdefault("tracker", {}).setdefault("algorithm", "bytetrack")
        self._pipeline = None

    def process_video(self, video_path: str | Path, roi: ROI | None = None) -> TrajectoryData:
        return self.pipeline.process_video(video_path, roi)

    def process_frame(self, frame: Any) -> list[Detection]:
        return self.pipeline.detector.detect(frame)

    @property
    def capabilities(self) -> set[str]:
        return {"detection", "tracking", "coordinate_transform"}
