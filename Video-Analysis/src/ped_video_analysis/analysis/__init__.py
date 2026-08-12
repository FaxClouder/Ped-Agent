"""Trajectory analysis block and compatibility exports.

The analysis block can consume any trajectory set that satisfies its public input contract; it
does not require extraction or projection to have been executed by this package.
"""

from ped_video_analysis.analysis.pipeline import AnalysisPipeline
from ped_video_analysis.analysis.schemas import (
    AnalysisResult,
    DensityMetrics,
    FlowMetrics,
    VelocityMetrics,
)

__all__ = ["AnalysisPipeline", "AnalysisResult", "DensityMetrics", "FlowMetrics", "VelocityMetrics"]
