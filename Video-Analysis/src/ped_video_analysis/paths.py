from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VideoAnalysisPaths:
    root: Path
    models: Path
    trackers: Path
    analysis_configs: Path
    postprocess_configs: Path
    runtime: Path

    @classmethod
    def from_root(
        cls,
        root: Path,
        *,
        configs_root: Path | None = None,
    ) -> VideoAnalysisPaths:
        resolved = root.resolve()
        package_configs = (
            configs_root.resolve()
            if configs_root is not None
            else resolved / "src" / "ped_video_analysis" / "configs"
        )
        return cls(
            root=resolved,
            models=resolved / "models",
            trackers=resolved / "trackers",
            analysis_configs=package_configs / "analysis",
            postprocess_configs=package_configs / "postprocessing",
            runtime=resolved / "runtime",
        )

    def ensure_local_dirs(self) -> None:
        for directory in (self.models, self.trackers, self.runtime):
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def detector_configs(self) -> Path:
        """Compatibility alias for callers that still use the old path name."""

        return self.models

    @property
    def weights(self) -> Path:
        """Compatibility alias; weights now live below each model directory."""

        return self.models


_PACKAGE_ROOT = Path(__file__).resolve().parent
_SOURCE_ROOT = _PACKAGE_ROOT.parents[1]
_CONFIGURED_ROOT = os.getenv("PED_VIDEO_ANALYSIS_HOME")
if _CONFIGURED_ROOT:
    _DEFAULT_ROOT = Path(_CONFIGURED_ROOT).resolve()
elif _PACKAGE_ROOT.parent.name == "src":
    _DEFAULT_ROOT = _SOURCE_ROOT
else:
    _DEFAULT_ROOT = Path.cwd().resolve() / "Video-Analysis"
DEFAULT_PATHS = VideoAnalysisPaths.from_root(
    _DEFAULT_ROOT,
    configs_root=_PACKAGE_ROOT / "configs",
)


__all__ = ["DEFAULT_PATHS", "VideoAnalysisPaths"]
