from __future__ import annotations

import hashlib
from pathlib import Path

from ped_video_analysis.registry import ModelManifestRegistry
from ped_video_analysis.schemas import PixelTrackSet
from ped_video_analysis.vision.adapters import (
    BoxMotByteTrackAdapter,
    OpenCVFrameSequence,
    UltralyticsDetector,
)
from ped_video_analysis.vision.runner import VisionInferenceRunner


class VideoInferencePipeline:
    """Stable orchestration boundary for the confirmed detection and tracking flow."""

    def __init__(self, registry: ModelManifestRegistry):
        self.registry = registry

    def run(
        self,
        video_path: str | Path,
        *,
        task_id: str,
        model_id: str,
    ) -> PixelTrackSet:
        source = Path(video_path).resolve()
        manifest = self.registry.get(model_id)
        frames = OpenCVFrameSequence(source)
        runner = VisionInferenceRunner(
            manifest,
            detector=UltralyticsDetector(manifest),
            tracker=BoxMotByteTrackAdapter(manifest, source_fps=frames.metadata.fps),
        )
        return runner.run(
            task_id=task_id,
            source_video_sha256=_file_sha256(source),
            model_manifest_sha256=self.registry.manifest_sha256(model_id),
            frames=frames,
        )


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


__all__ = ["VideoInferencePipeline"]
