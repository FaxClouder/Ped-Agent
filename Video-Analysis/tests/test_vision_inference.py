from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from ped_video_analysis.vision.artifacts import PixelTrackParquetStore
from ped_video_analysis.vision.contracts import (
    ContactPointQuality,
    ModelManifest,
    PixelPoint,
    PixelTrackObservation,
    SemanticClass,
    VideoMetadata,
)
from ped_video_analysis.vision.inference import (
    TrackAssignment,
    assemble_pixel_tracks,
    build_bytetrack_config,
)
from ped_video_analysis.vision.model_registry import (
    ModelManifestRegistry,
    ModelWeightsMismatchError,
)


def manifest(weights_path: Path, digest: str) -> ModelManifest:
    return ModelManifest(
        model_id="mixed-flow-v1",
        name="Mixed flow detector",
        version="1.0.0",
        backend="ultralytics",
        weights_path=weights_path,
        sha256=digest,
        input_size=1280,
        class_map={
            0: SemanticClass.PEDESTRIAN,
            1: SemanticClass.PEDESTRIAN_UMBRELLA,
            2: SemanticClass.BICYCLE_RIDER,
            3: SemanticClass.EBIKE_RIDER,
        },
        contact_keypoints={
            SemanticClass.PEDESTRIAN: ("left_foot", "right_foot"),
            SemanticClass.PEDESTRIAN_UMBRELLA: ("left_foot", "right_foot"),
            SemanticClass.BICYCLE_RIDER: ("front_wheel", "rear_wheel"),
            SemanticClass.EBIKE_RIDER: ("front_wheel", "rear_wheel"),
        },
    )


def observation(
    frame: int,
    semantic_class: SemanticClass,
    confidence: float,
) -> PixelTrackObservation:
    return PixelTrackObservation(
        frame_index=frame,
        timestamp=frame / 25,
        point=PixelPoint(x=100 + frame, y=200),
        bbox_xyxy=(90 + frame, 100, 110 + frame, 200),
        detection_confidence=confidence,
        tracking_confidence=confidence,
        semantic_class=semantic_class,
        contact_quality=ContactPointQuality.KEYPOINT,
    )


def test_model_registry_resolves_relative_weights_and_verifies_hash(tmp_path: Path) -> None:
    weights = tmp_path / "weights" / "mixed.pt"
    weights.parent.mkdir()
    weights.write_bytes(b"custom-ultralytics-weights")
    digest = hashlib.sha256(weights.read_bytes()).hexdigest()
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    payload = manifest(Path("../weights/mixed.pt"), digest).model_dump(mode="json")
    (manifests / "mixed-flow-v1.json").write_text(json.dumps(payload), encoding="utf-8")

    registry = ModelManifestRegistry(manifests)

    loaded = registry.get("mixed-flow-v1")
    assert loaded.weights_path == weights.resolve()
    assert registry.list()[0].model_id == "mixed-flow-v1"
    assert (
        registry.manifest_sha256("mixed-flow-v1")
        == hashlib.sha256(loaded.model_dump_json(exclude={"weights_path"}).encode()).hexdigest()
    )


def test_model_registry_combines_separate_model_and_tracker_resources(tmp_path: Path) -> None:
    model_dir = tmp_path / "models" / "mixed"
    weights = model_dir / "weights" / "mixed.pt"
    weights.parent.mkdir(parents=True)
    weights.write_bytes(b"separate-model-and-tracker")
    digest = hashlib.sha256(weights.read_bytes()).hexdigest()
    payload = manifest(Path("weights/mixed.pt"), digest).model_dump(mode="json")
    payload.pop("tracker")
    (model_dir / "model.json").write_text(json.dumps(payload), encoding="utf-8")

    tracker_dir = tmp_path / "trackers" / "bytetrack"
    tracker_dir.mkdir(parents=True)
    (tracker_dir / "tracker.json").write_text(
        json.dumps(
            {
                "tracker_id": "bytetrack",
                "name": "ByteTrack",
                "version": "1.0.0",
                "backend": "bytetrack",
                "settings": {
                    "backend": "bytetrack",
                    "match_threshold": 0.72,
                },
            }
        ),
        encoding="utf-8",
    )

    registry = ModelManifestRegistry(tmp_path / "models", trackers_dir=tmp_path / "trackers")
    loaded = registry.get("mixed-flow-v1")

    assert loaded.weights_path == weights.resolve()
    assert loaded.tracker.match_threshold == pytest.approx(0.72)


def test_model_registry_rejects_changed_weights(tmp_path: Path) -> None:
    weights = tmp_path / "mixed.pt"
    weights.write_bytes(b"changed")
    payload = manifest(Path("mixed.pt"), "0" * 64).model_dump(mode="json")
    (tmp_path / "mixed.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ModelWeightsMismatchError, match="SHA-256"):
        ModelManifestRegistry(tmp_path).get("mixed-flow-v1")


def test_bytetrack_runtime_config_converts_seconds_to_processed_frames(tmp_path: Path) -> None:
    model = manifest(tmp_path / "mixed.pt", "a" * 64)

    config = build_bytetrack_config(model, source_fps=25.0)

    assert config == {
        "tracker_type": "bytetrack",
        "track_high_thresh": 0.25,
        "track_low_thresh": 0.10,
        "new_track_thresh": 0.25,
        "track_buffer": 30,
        "match_thresh": 0.80,
        "fuse_score": True,
    }


def test_track_assembly_uses_weighted_class_vote_within_compatible_group() -> None:
    artifact = assemble_pixel_tracks(
        task_id="task-1",
        source_video_sha256="b" * 64,
        model_manifest_sha256="c" * 64,
        video=VideoMetadata(
            source="source.mp4",
            fps=25,
            total_frames=3,
            resolution=(1920, 1080),
            duration=0.12,
        ),
        assignments=(
            TrackAssignment(7, observation(0, SemanticClass.PEDESTRIAN, 0.4)),
            TrackAssignment(7, observation(1, SemanticClass.PEDESTRIAN_UMBRELLA, 0.9)),
            TrackAssignment(7, observation(2, SemanticClass.PEDESTRIAN_UMBRELLA, 0.8)),
        ),
    )

    assert artifact.tracks[0].semantic_class is SemanticClass.PEDESTRIAN_UMBRELLA
    assert {item.semantic_class for item in artifact.tracks[0].observations} == {
        SemanticClass.PEDESTRIAN_UMBRELLA
    }


def test_track_assembly_rejects_pedestrian_rider_identity_mix() -> None:
    with pytest.raises(ValueError, match="incompatible association groups"):
        assemble_pixel_tracks(
            task_id="task-1",
            source_video_sha256="b" * 64,
            model_manifest_sha256="c" * 64,
            video=VideoMetadata(
                source="source.mp4",
                fps=25,
                total_frames=2,
                resolution=(1920, 1080),
                duration=0.08,
            ),
            assignments=(
                TrackAssignment(7, observation(0, SemanticClass.PEDESTRIAN, 0.9)),
                TrackAssignment(7, observation(1, SemanticClass.BICYCLE_RIDER, 0.8)),
            ),
        )


def test_pixel_track_parquet_store_round_trips_and_refuses_overwrite(tmp_path: Path) -> None:
    artifact = assemble_pixel_tracks(
        task_id="task-1",
        source_video_sha256="b" * 64,
        model_manifest_sha256="c" * 64,
        video=VideoMetadata(
            source="source.mp4",
            fps=25,
            total_frames=1,
            resolution=(1920, 1080),
            duration=0.04,
        ),
        assignments=(TrackAssignment(1, observation(0, SemanticClass.PEDESTRIAN, 0.9)),),
    )
    store = PixelTrackParquetStore(tmp_path)

    stored = store.write(artifact)

    assert stored.parquet_path.suffix == ".parquet"
    assert stored.metadata_path.exists()
    assert store.read(artifact.artifact_id) == artifact
    with pytest.raises(FileExistsError, match="immutable"):
        store.write(artifact)
    assert not list(tmp_path.rglob("*.mp4"))
