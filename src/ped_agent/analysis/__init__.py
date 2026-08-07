"""Compatibility aliases for the extracted ``ped_video_analysis.analysis`` package."""

from importlib import import_module
from sys import modules

_SUBMODULES = (
    "fundamental_diagram",
    "metrics",
    "od_matrix",
    "pedpy_adapter",
    "pipeline",
    "schemas",
    "statistics",
    "vision_exports",
    "vision_pipeline",
    "vision_schemas",
    "vision_visualizer",
    "visualizer",
)

for _submodule in _SUBMODULES:
    modules[f"{__name__}.{_submodule}"] = import_module(
        f"ped_video_analysis.analysis.{_submodule}"
    )

from ped_video_analysis.analysis import (  # noqa: E402
    AnalysisPipeline,
    AnalysisResult,
    DensityMetrics,
    FlowMetrics,
    VelocityMetrics,
)

__all__ = [
    "AnalysisPipeline",
    "AnalysisResult",
    "DensityMetrics",
    "FlowMetrics",
    "VelocityMetrics",
]
