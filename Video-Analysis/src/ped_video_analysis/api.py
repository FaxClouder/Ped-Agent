from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ped_video_analysis.analysis.vision_exports import export_analysis_bundle
from ped_video_analysis.analysis.vision_pipeline import AnalysisProfile, analyze_world_tracks
from ped_video_analysis.analysis.vision_schemas import AnalysisBundle
from ped_video_analysis.analysis.vision_visualizer import render_analysis_figures
from ped_video_analysis.paths import DEFAULT_PATHS
from ped_video_analysis.pipeline import VideoInferencePipeline
from ped_video_analysis.registry import ModelManifestRegistry
from ped_video_analysis.vision.calibration import (
    calibrate_charuco_images,
    solve_full_camera_from_ground_points,
    solve_homography,
)
from ped_video_analysis.vision.contracts import (
    PixelTrackSet,
    ProcessedWorldTrackSet,
    SceneProfile,
    WorldTrackSet,
)
from ped_video_analysis.vision.postprocessing import (
    PostprocessProfile,
    postprocess_world_tracks,
)
from ped_video_analysis.vision.projection import project_reviewed_tracks
from ped_video_analysis.vision.review import apply_review_patch


def create_model_registry(
    manifests_dir: str | Path | None = None,
    weights_dir: str | Path | None = None,
    *,
    trackers_dir: str | Path | None = None,
    tracker_id: str = "bytetrack",
) -> ModelManifestRegistry:
    """Create a registry from module-owned model and tracker resources."""

    return ModelManifestRegistry(
        Path(manifests_dir) if manifests_dir is not None else DEFAULT_PATHS.models,
        trackers_dir=Path(trackers_dir) if trackers_dir is not None else DEFAULT_PATHS.trackers,
        tracker_id=tracker_id,
        weights_dir=Path(weights_dir) if weights_dir is not None else None,
    )


def load_analysis_profile(path: str | Path | None = None) -> AnalysisProfile:
    target = Path(path) if path is not None else DEFAULT_PATHS.analysis_configs / "default.yaml"
    return AnalysisProfile.model_validate(_load_yaml_mapping(target))


def load_postprocess_profile(path: str | Path | None = None) -> PostprocessProfile:
    target = Path(path) if path is not None else DEFAULT_PATHS.postprocess_configs / "default.yaml"
    return PostprocessProfile.model_validate(_load_yaml_mapping(target))


def run_video_inference(
    video_path: str | Path,
    *,
    task_id: str,
    model_id: str,
    tracker_id: str = "bytetrack",
    registry: ModelManifestRegistry | None = None,
) -> PixelTrackSet:
    """Run the detector and tracker without requiring the Ped-Agent server."""

    model_registry = registry or create_model_registry(tracker_id=tracker_id)
    return VideoInferencePipeline(model_registry).run(
        video_path,
        task_id=task_id,
        model_id=model_id,
    )


def postprocess_trajectories(
    source: WorldTrackSet,
    profile: PostprocessProfile | None = None,
) -> ProcessedWorldTrackSet:
    return postprocess_world_tracks(source, profile or load_postprocess_profile())


def analyze_trajectories(
    source: ProcessedWorldTrackSet,
    scene: SceneProfile,
    profile: AnalysisProfile | None = None,
) -> AnalysisBundle:
    return analyze_world_tracks(source, scene, profile or load_analysis_profile())


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"configuration must contain a YAML mapping: {path}")
    return payload


__all__ = [
    "AnalysisBundle",
    "AnalysisProfile",
    "PostprocessProfile",
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
