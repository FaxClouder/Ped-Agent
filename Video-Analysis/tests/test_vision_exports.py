from __future__ import annotations

import json
from pathlib import Path

from ped_video_analysis.analysis.vision_exports import export_analysis_bundle
from ped_video_analysis.analysis.vision_pipeline import AnalysisProfile, analyze_world_tracks
from ped_video_analysis.analysis.vision_visualizer import render_analysis_figures
from ped_video_analysis.vision.artifacts import WorldTrackParquetStore
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


def processed_tracks() -> ProcessedWorldTrackSet:
    observations = tuple(
        WorldTrackObservation(
            frame_index=frame,
            timestamp=float(frame),
            point=WorldPoint(x=float(frame), y=0),
            source_pixel=PixelPoint(x=frame * 10, y=20),
            projection_error_estimate_m=0.05,
            contact_quality=ContactPointQuality.KEYPOINT,
        )
        for frame in range(3)
    )
    return ProcessedWorldTrackSet(
        artifact_id="processed-1",
        task_id="task-1",
        parent_artifact_id="world-1",
        calibration_id="cal-1",
        video=VideoMetadata(
            source="source.mp4",
            fps=1,
            total_frames=3,
            resolution=(100, 100),
            duration=3,
        ),
        tracks=(
            WorldTrack(
                track_id=1,
                semantic_class=SemanticClass.PEDESTRIAN,
                observations=observations,
            ),
        ),
        postprocess_profile_sha256="d" * 64,
    )


def scene() -> SceneProfile:
    return SceneProfile(
        scene_id="scene-1",
        version=1,
        name="Scene",
        camera_fingerprint="camera-1",
        resolution=(100, 100),
        calibration_mode=CalibrationMode.HOMOGRAPHY,
        roi=((-1, -1), (3, -1), (3, 1), (-1, 1)),
        entrances={
            "west": ((-1, -1), (0.5, -1), (0.5, 1), (-1, 1)),
            "east": ((1.5, -1), (3, -1), (3, 1), (1.5, 1)),
        },
    )


def test_world_track_parquet_store_round_trips_processed_lineage(tmp_path: Path) -> None:
    source = processed_tracks()
    store = WorldTrackParquetStore(tmp_path)

    stored = store.write(source)

    assert stored.parquet_path.exists()
    assert store.read_processed(source.artifact_id) == source


def test_analysis_export_writes_tables_figures_manifest_and_no_video(tmp_path: Path) -> None:
    source = processed_tracks()
    bundle = analyze_world_tracks(source, scene(), AnalysisProfile())
    figures = render_analysis_figures(bundle, source, tmp_path / "figures")

    manifest = export_analysis_bundle(
        bundle=bundle,
        tracks=source,
        figures=figures,
        output_dir=tmp_path / "export",
    )

    formats = {Path(item.path).suffix for item in manifest.files}
    assert {".csv", ".json", ".parquet", ".png", ".svg", ".pdf"} <= formats
    exported_names = {Path(item.path).name for item in manifest.files}
    assert {
        "voronoi-density.csv",
        "vector-field.csv",
        "speed-profile.csv",
        "fundamental-diagram.csv",
    } <= exported_names
    provenance = json.loads((tmp_path / "export" / "provenance.json").read_text("utf-8"))
    assert provenance["analysis_id"] == bundle.analysis_id
    assert provenance["units"]["speed"] == "m/s"
    assert provenance["sample_tracks"] == 1
    assert not list((tmp_path / "export").rglob("*.mp4"))
