from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from ped_agent.vision.contracts import (
    CalibrationMode,
    CalibrationReport,
    ContactPointQuality,
    DetectionObservation,
    KeypointObservation,
    ModelManifest,
    PixelPoint,
    PixelTrack,
    PixelTrackSet,
    SceneProfile,
    SemanticClass,
    VideoMetadata,
    VideoTaskSpec,
)


def model_manifest() -> ModelManifest:
    return ModelManifest(
        model_id="mixed-flow-v1",
        name="Mixed flow detector",
        version="1.0.0",
        backend="ultralytics",
        weights_path=Path("models/mixed-flow-v1.pt"),
        sha256="a" * 64,
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


def test_model_manifest_requires_all_four_business_classes() -> None:
    payload = model_manifest().model_dump()
    payload["class_map"].pop(3)

    with pytest.raises(ValidationError, match="four required semantic classes"):
        ModelManifest.model_validate(payload)


def test_model_manifest_assigns_compatible_tracking_groups() -> None:
    manifest = model_manifest()

    assert manifest.tracking_group(SemanticClass.PEDESTRIAN) == "pedestrian"
    assert manifest.tracking_group(SemanticClass.PEDESTRIAN_UMBRELLA) == "pedestrian"
    assert manifest.tracking_group(SemanticClass.BICYCLE_RIDER) == "rider"
    assert manifest.tracking_group(SemanticClass.EBIKE_RIDER) == "rider"


def test_model_manifest_uses_research_detection_and_bytetrack_defaults() -> None:
    manifest = model_manifest()

    assert manifest.inference.batch == 1
    assert manifest.inference.frame_stride == 1
    assert manifest.inference.detection_confidence == pytest.approx(0.10)
    assert manifest.inference.nms_iou == pytest.approx(0.65)
    assert manifest.tracker.high_threshold == pytest.approx(0.25)
    assert manifest.tracker.low_threshold == pytest.approx(0.10)
    assert manifest.tracker.new_track_threshold == pytest.approx(0.25)
    assert manifest.tracker.match_threshold == pytest.approx(0.80)
    assert manifest.tracker.lost_buffer_seconds == pytest.approx(1.2)


def test_video_task_spec_keeps_source_copy_and_forbids_annotated_video() -> None:
    spec = VideoTaskSpec(
        task_name="Morning mixed flow",
        source_video=Path("uploads/morning.mp4"),
        model_id="mixed-flow-v1",
        scene_id="station-east",
    )

    assert spec.copy_source_video is True
    assert spec.render_annotated_video is False


def test_detection_observation_rejects_contact_point_outside_frame() -> None:
    with pytest.raises(ValidationError, match="contact point must be inside the frame"):
        DetectionObservation(
            frame_index=0,
            timestamp=0.0,
            detection_id="d-1",
            raw_class_id=0,
            semantic_class=SemanticClass.PEDESTRIAN,
            bbox_xyxy=(10.0, 20.0, 30.0, 60.0),
            confidence=0.9,
            frame_size=(100, 80),
            keypoints={
                "left_foot": KeypointObservation(x=20.0, y=58.0, confidence=0.9),
                "right_foot": KeypointObservation(x=24.0, y=58.0, confidence=0.9),
            },
            contact_point=PixelPoint(x=101.0, y=70.0),
            contact_quality=ContactPointQuality.KEYPOINT,
        )


def test_pixel_track_set_is_immutable_and_records_pixel_coordinate_space() -> None:
    artifact = PixelTrackSet(
        artifact_id="pixel-1",
        task_id="task-1",
        source_video_sha256="b" * 64,
        model_manifest_sha256="c" * 64,
        video=VideoMetadata(
            source="source.mp4",
            fps=25.0,
            total_frames=100,
            resolution=(1920, 1080),
            duration=4.0,
        ),
        tracks=(
            PixelTrack(
                track_id=1,
                semantic_class=SemanticClass.PEDESTRIAN,
                observations=(),
            ),
        ),
    )

    assert artifact.coordinate_space == "image_px"
    with pytest.raises(ValidationError):
        artifact.task_id = "changed"  # type: ignore[misc]


def test_scene_profile_binds_calibration_to_resolution_and_camera() -> None:
    scene = SceneProfile(
        scene_id="station-east",
        version=1,
        name="Station east entrance",
        camera_fingerprint="camera-01-35mm",
        resolution=(1920, 1080),
        calibration_mode=CalibrationMode.FULL_CAMERA,
        roi=((0.0, 0.0), (10.0, 0.0), (10.0, 8.0), (0.0, 8.0)),
    )

    assert scene.world_unit == "m"
    assert scene.matches_camera("camera-01-35mm", (1920, 1080)) is True
    assert scene.matches_camera("camera-01-35mm", (1280, 720)) is False


def test_calibration_report_accepts_only_world_rmse_within_ten_centimetres() -> None:
    accepted = CalibrationReport(
        calibration_id="cal-1",
        scene_id="station-east",
        scene_version=1,
        mode=CalibrationMode.HOMOGRAPHY,
        image_reprojection_rmse_px=0.8,
        world_checkpoint_rmse_m=0.099,
        checkpoint_count=4,
    )
    rejected = accepted.model_copy(update={"world_checkpoint_rmse_m": 0.101})

    assert accepted.accepted is True
    assert rejected.accepted is False


def test_calibration_report_requires_four_independent_checkpoints() -> None:
    with pytest.raises(ValidationError, match="at least four independent checkpoints"):
        CalibrationReport(
            calibration_id="cal-1",
            scene_id="station-east",
            scene_version=1,
            mode=CalibrationMode.HOMOGRAPHY,
            image_reprojection_rmse_px=0.8,
            world_checkpoint_rmse_m=0.05,
            checkpoint_count=3,
        )
