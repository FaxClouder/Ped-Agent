"""Stable data contracts exposed by :mod:`ped_video_analysis`."""

from ped_video_analysis.analysis.vision_pipeline import AnalysisProfile
from ped_video_analysis.analysis.vision_schemas import AnalysisBundle
from ped_video_analysis.vision.contracts import (
    CalibrationMode,
    CalibrationReport,
    DetectorManifest,
    ModelManifest,
    PixelTrackSet,
    ProcessedWorldTrackSet,
    ReviewedPixelTrackSet,
    SceneProfile,
    SemanticClass,
    TrackerManifest,
    VideoTaskSpec,
    WorldTrackSet,
)
from ped_video_analysis.vision.postprocessing import PostprocessProfile

__all__ = [
    "AnalysisBundle",
    "AnalysisProfile",
    "CalibrationMode",
    "CalibrationReport",
    "DetectorManifest",
    "ModelManifest",
    "PixelTrackSet",
    "PostprocessProfile",
    "ProcessedWorldTrackSet",
    "ReviewedPixelTrackSet",
    "SceneProfile",
    "SemanticClass",
    "TrackerManifest",
    "VideoTaskSpec",
    "WorldTrackSet",
]
