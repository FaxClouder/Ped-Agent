"""Public interface for Ped-Agent video detection and flow analysis."""

from ped_video_analysis.api import (
    AnalysisBundle,
    AnalysisProfile,
    PostprocessProfile,
    analyze_trajectories,
    apply_review_patch,
    calibrate_charuco_images,
    create_model_registry,
    export_analysis_bundle,
    load_analysis_profile,
    load_postprocess_profile,
    postprocess_trajectories,
    project_reviewed_tracks,
    render_analysis_figures,
    run_video_inference,
    solve_full_camera_from_ground_points,
    solve_homography,
)
from ped_video_analysis.paths import DEFAULT_PATHS, VideoAnalysisPaths
from ped_video_analysis.pipeline import VideoInferencePipeline
from ped_video_analysis.registry import ModelManifestRegistry, ModelWeightsMismatchError
from ped_video_analysis.schemas import DetectorManifest, ModelManifest, TrackerManifest

__all__ = [
    "AnalysisBundle",
    "AnalysisProfile",
    "DEFAULT_PATHS",
    "DetectorManifest",
    "ModelManifest",
    "ModelManifestRegistry",
    "ModelWeightsMismatchError",
    "PostprocessProfile",
    "VideoAnalysisPaths",
    "VideoInferencePipeline",
    "TrackerManifest",
    "analyze_trajectories",
    "apply_review_patch",
    "calibrate_charuco_images",
    "create_model_registry",
    "export_analysis_bundle",
    "load_analysis_profile",
    "load_postprocess_profile",
    "postprocess_trajectories",
    "project_reviewed_tracks",
    "render_analysis_figures",
    "run_video_inference",
    "solve_full_camera_from_ground_points",
    "solve_homography",
]
