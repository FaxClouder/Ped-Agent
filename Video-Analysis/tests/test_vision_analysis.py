from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from ped_video_analysis.analysis.vision_pipeline import AnalysisProfile, analyze_world_tracks
from ped_video_analysis.analysis.vision_visualizer import render_analysis_figures
from ped_video_analysis.vision.contracts import (
    CalibrationMode,
    ContactPointQuality,
    PixelPoint,
    ProcessedWorldTrackSet,
    SceneProfile,
    SemanticClass,
    VideoMetadata,
    WorldPoint,
    WorldTrack,
    WorldTrackObservation,
)


def world_observation(frame: int, x: float, y: float) -> WorldTrackObservation:
    return WorldTrackObservation(
        frame_index=frame,
        timestamp=float(frame),
        point=WorldPoint(x=x, y=y),
        source_pixel=PixelPoint(x=x * 10 + 50, y=y * 10 + 50),
        projection_error_estimate_m=0.05,
        contact_quality=ContactPointQuality.KEYPOINT,
    )


def world_tracks() -> ProcessedWorldTrackSet:
    return ProcessedWorldTrackSet(
        artifact_id="processed-1",
        task_id="task-1",
        parent_artifact_id="world-1",
        calibration_id="cal-1",
        video=VideoMetadata(
            source="source.mp4",
            fps=1.0,
            total_frames=3,
            resolution=(100, 100),
            duration=3.0,
        ),
        tracks=(
            WorldTrack(
                track_id=1,
                semantic_class=SemanticClass.PEDESTRIAN,
                observations=(
                    world_observation(0, -1.0, 0.0),
                    world_observation(1, 0.0, 0.0),
                    world_observation(2, 1.0, 0.0),
                ),
            ),
            WorldTrack(
                track_id=2,
                semantic_class=SemanticClass.BICYCLE_RIDER,
                observations=(
                    world_observation(0, 0.0, -1.0),
                    world_observation(1, 0.0, 0.0),
                    world_observation(2, 0.0, 1.0),
                ),
            ),
        ),
        postprocess_profile_sha256="d" * 64,
    )


def scene_profile() -> SceneProfile:
    return SceneProfile(
        scene_id="scene-1",
        version=1,
        name="Crossing",
        camera_fingerprint="camera-1",
        resolution=(100, 100),
        calibration_mode=CalibrationMode.HOMOGRAPHY,
        roi=((-2.0, -2.0), (2.0, -2.0), (2.0, 2.0), (-2.0, 2.0)),
        zones={
            "west": ((-2.0, -2.0), (-0.5, -2.0), (-0.5, 2.0), (-2.0, 2.0)),
            "east": ((0.5, -2.0), (2.0, -2.0), (2.0, 2.0), (0.5, 2.0)),
        },
        counting_lines={"vertical": ((0.5, -2.0), (0.5, 2.0))},
        entrances={
            "west": ((-2.0, -2.0), (-0.5, -2.0), (-0.5, 2.0), (-2.0, 2.0)),
            "east": ((0.5, -2.0), (2.0, -2.0), (2.0, 2.0), (0.5, 2.0)),
            "south": ((-2.0, -2.0), (2.0, -2.0), (2.0, -0.5), (-2.0, -0.5)),
            "north": ((-2.0, 0.5), (2.0, 0.5), (2.0, 2.0), (-2.0, 2.0)),
        },
        conflict_zones={"center": ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5))},
    )


def test_analysis_computes_quality_and_individual_kinematics() -> None:
    bundle = analyze_world_tracks(world_tracks(), scene_profile(), AnalysisProfile())

    pedestrian = next(item for item in bundle.individual if item.track_id == 1)
    assert bundle.quality.track_count == 2
    assert bundle.quality.point_count == 6
    assert bundle.quality.coverage_ratio == pytest.approx(1.0)
    assert bundle.quality.gap_count == 0
    assert bundle.quality.mean_projection_error_m == pytest.approx(0.05)
    assert pedestrian.path_length_m == pytest.approx(2.0)
    assert pedestrian.duration_s == pytest.approx(2.0)
    assert pedestrian.mean_speed_mps == pytest.approx(1.0)
    assert pedestrian.max_speed_mps == pytest.approx(1.0)
    assert pedestrian.zone_dwell_seconds["west"] == pytest.approx(1.0)
    assert pedestrian.zone_dwell_seconds["east"] == pytest.approx(1.0)


def test_analysis_uses_segment_midpoints_for_irregular_acceleration() -> None:
    source = world_tracks().model_copy(
        update={
            "tracks": (
                WorldTrack(
                    track_id=3,
                    semantic_class=SemanticClass.PEDESTRIAN,
                    observations=(
                        world_observation(0, 0.0, 0.0).model_copy(update={"timestamp": 0.0}),
                        world_observation(1, 1.0, 0.0).model_copy(update={"timestamp": 1.0}),
                        world_observation(2, 5.0, 0.0).model_copy(update={"timestamp": 3.0}),
                    ),
                ),
            )
        }
    )

    bundle = analyze_world_tracks(source, scene_profile(), AnalysisProfile())

    assert bundle.individual[0].mean_acceleration_mps2 == pytest.approx(2 / 3)


def test_analysis_computes_directional_line_flow_and_od() -> None:
    bundle = analyze_world_tracks(world_tracks(), scene_profile(), AnalysisProfile())

    flow = next(item for item in bundle.flows if item.line_id == "vertical")
    assert flow.count == 1
    assert flow.rate_per_second == pytest.approx(1 / 3)
    assert flow.specific_flow_per_m_s == pytest.approx(1 / 12)
    assert {(item.origin, item.destination, item.count) for item in bundle.od} == {
        ("west", "east", 1),
        ("south", "north", 1),
    }


def test_analysis_computes_density_series_and_crossing_interaction_proxies() -> None:
    bundle = analyze_world_tracks(world_tracks(), scene_profile(), AnalysisProfile())

    assert bundle.spatial.classic_density[1].density_per_m2 == pytest.approx(2 / 16)
    assert len(bundle.interactions) == 1
    event = bundle.interactions[0]
    assert event.minimum_distance_m == pytest.approx(0.0)
    assert event.ttc_seconds == pytest.approx(1.0)
    assert event.pet_seconds == pytest.approx(0.0)
    assert event.interaction_type == "crossing"
    assert event.safety_conclusion is None
    assert bundle.spatial.voronoi_density
    assert bundle.spatial.vector_field
    assert bundle.spatial.speed_profile
    assert bundle.spatial.fundamental_diagram
    assert bundle.spatial.voronoi_method in {"bounded_half_plane", "pedpy"}


@pytest.mark.skipif(importlib.util.find_spec("pedpy") is None, reason="PedPy is optional")
def test_analysis_prefers_pedpy_for_standard_spatial_metrics_when_available() -> None:
    source = world_tracks().model_copy(
        update={
            "tracks": (
                world_tracks().tracks[0],
                world_tracks()
                .tracks[1]
                .model_copy(
                    update={
                        "observations": (
                            world_observation(0, 0.0, -1.0),
                            world_observation(1, 0.1, 0.0),
                            world_observation(2, 0.0, 1.0),
                        )
                    }
                ),
            )
        }
    )
    bundle = analyze_world_tracks(source, scene_profile(), AnalysisProfile())

    assert bundle.spatial.method == "pedpy_classic_speed"
    assert bundle.spatial.voronoi_method == "pedpy"
    assert bundle.spatial.classic_density[1].density_per_m2 == pytest.approx(2 / 16)


def test_analysis_uses_configured_default_screening_parameters() -> None:
    profile = AnalysisProfile()

    assert profile.time_window_seconds == pytest.approx(1.0)
    assert profile.speed_difference_window_seconds == pytest.approx(0.4)
    assert profile.spatial_grid_metres == pytest.approx(0.25)
    assert profile.kde_bandwidth_metres == pytest.approx(0.50)
    assert profile.stop_speed_metres_per_second == pytest.approx(0.10)
    assert profile.interaction_radius_metres == pytest.approx(5.0)
    assert profile.ttc_horizon_seconds == pytest.approx(5.0)
    assert profile.minimum_track_duration_seconds == pytest.approx(2.0)


def test_visualizer_exports_interactive_specs_and_publication_figures(tmp_path: Path) -> None:
    source = world_tracks()
    bundle = analyze_world_tracks(source, scene_profile(), AnalysisProfile())

    rendered = render_analysis_figures(bundle, source, tmp_path)

    assert {item.figure_id for item in rendered} >= {
        "trajectories",
        "speed_distribution",
        "density_time_series",
        "od_matrix",
        "interaction_hotspots",
        "flow_counts",
        "kde_heatmap",
        "vector_field",
        "fundamental_diagram",
    }
    for artifact in rendered:
        assert Path(artifact.plotly_json_path).exists()
        assert Path(artifact.svg_path).exists()
        assert Path(artifact.pdf_path).exists()
        assert Path(artifact.png_path).exists()
        assert Path(artifact.manifest_path).exists()
    assert not list(tmp_path.rglob("*.mp4"))
