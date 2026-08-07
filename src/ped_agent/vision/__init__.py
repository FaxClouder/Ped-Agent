"""Compatibility aliases for the extracted ``ped_video_analysis.vision`` package."""

from importlib import import_module
from sys import modules

_SUBMODULES = (
    "adapters",
    "artifacts",
    "calibration",
    "contact_points",
    "contracts",
    "detector",
    "inference",
    "interface",
    "model_registry",
    "pipeline",
    "plugins",
    "plugins.yolo26_bytetrack",
    "plugins.yolo26_deepsort",
    "postprocess",
    "postprocessing",
    "projection",
    "registry",
    "review",
    "runner",
    "schemas",
    "tracker",
    "transform",
)

for _submodule in _SUBMODULES:
    modules[f"{__name__}.{_submodule}"] = import_module(
        f"ped_video_analysis.vision.{_submodule}"
    )

from ped_video_analysis.vision import VisionBackend, VisionRegistry  # noqa: E402

__all__ = ["VisionBackend", "VisionRegistry"]
