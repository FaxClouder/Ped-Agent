from __future__ import annotations

import numpy as np
import pytest

from ped_agent.vision.calibration import CalibrationPoint, solve_homography
from ped_agent.vision.contracts import (
    CalibrationReport,
    ContactPointQuality,
    PixelPoint,
    PixelTrack,
    PixelTrackObservation,
    PixelTrackSet,
    SemanticClass,
    VideoMetadata,
)
from ped_agent.vision.postprocessing import PostprocessProfile, postprocess_world_tracks
from ped_agent.vision.projection import CalibrationRejectedError, project_reviewed_tracks
from ped_agent.vision.review import (
    DeleteTrack,
    MergeTracks,
    MovePoint,
    RelabelTrack,
    ReviewPatch,
    SplitTrack,
    apply_review_patch,
)


def observation(frame: int, x: float, y: float) -> PixelTrackObservation:
    return PixelTrackObservation(
        frame_index=frame,
        timestamp=frame / 10.0,
        point=PixelPoint(x=x, y=y),
        bbox_xyxy=(x - 1.0, y - 2.0, x + 1.0, y),
        detection_confidence=0.9,
        tracking_confidence=0.8,
        semantic_class=SemanticClass.PEDESTRIAN,
        contact_quality=ContactPointQuality.KEYPOINT,
    )


def pixel_tracks() -> PixelTrackSet:
    return PixelTrackSet(
        artifact_id="pixel-raw",
        task_id="task-1",
        source_video_sha256="a" * 64,
        model_manifest_sha256="b" * 64,
        video=VideoMetadata(
            source="source.mp4",
            fps=10.0,
            total_frames=20,
            resolution=(200, 200),
            duration=2.0,
        ),
        tracks=(
            PixelTrack(
                track_id=1,
                semantic_class=SemanticClass.PEDESTRIAN,
                observations=(observation(0, 10.0, 10.0), observation(2, 12.0, 10.0)),
            ),
            PixelTrack(
                track_id=2,
                semantic_class=SemanticClass.BICYCLE_RIDER,
                observations=(observation(0, 30.0, 30.0), observation(1, 32.0, 30.0)),
            ),
        ),
    )


def accepted_calibration() -> tuple[object, CalibrationReport]:
    matrix = np.array([[0.1, 0.0, 0.0], [0.0, 0.1, 0.0], [0.0, 0.0, 1.0]])

    def world(pixel: tuple[float, float]) -> tuple[float, float]:
        value = matrix @ np.array([pixel[0], pixel[1], 1.0])
        return (float(value[0]), float(value[1]))

    fit_pixels = (
        (0.0, 0.0),
        (50.0, 0.0),
        (100.0, 0.0),
        (0.0, 50.0),
        (50.0, 50.0),
        (100.0, 50.0),
        (0.0, 100.0),
        (100.0, 100.0),
    )
    checkpoints = ((25.0, 25.0), (75.0, 25.0), (25.0, 75.0), (75.0, 75.0))
    calibration = solve_homography(
        tuple(CalibrationPoint(pixel=pixel, world=world(pixel)) for pixel in fit_pixels),
        tuple(CalibrationPoint(pixel=pixel, world=world(pixel)) for pixel in checkpoints),
    )
    report = calibration.report.model_copy(
        update={"scene_id": "scene-1", "scene_version": 1}
    )
    return calibration, report


def test_review_patch_creates_new_artifact_without_mutating_raw_tracks() -> None:
    raw = pixel_tracks()
    patch = ReviewPatch(
        patch_id="patch-1",
        parent_artifact_id=raw.artifact_id,
        operations=(
            DeleteTrack(track_id=2),
            RelabelTrack(track_id=1, semantic_class=SemanticClass.PEDESTRIAN_UMBRELLA),
            MovePoint(track_id=1, frame_index=2, point=PixelPoint(x=13.0, y=11.0)),
        ),
    )

    reviewed = apply_review_patch(raw, patch)

    assert len(raw.tracks) == 2
    assert len(reviewed.tracks) == 1
    assert reviewed.parent_artifact_id == raw.artifact_id
    assert reviewed.applied_patch_ids == ("patch-1",)
    assert reviewed.tracks[0].semantic_class is SemanticClass.PEDESTRIAN_UMBRELLA
    assert reviewed.tracks[0].observations[-1].point == PixelPoint(x=13.0, y=11.0)
    assert reviewed.tracks[0].observations[-1].contact_quality is ContactPointQuality.MANUAL


def test_review_patch_rejects_wrong_parent_artifact() -> None:
    raw = pixel_tracks()
    patch = ReviewPatch(
        patch_id="patch-1",
        parent_artifact_id="another-artifact",
        operations=(DeleteTrack(track_id=2),),
    )

    with pytest.raises(ValueError, match="parent artifact"):
        apply_review_patch(raw, patch)


def test_review_patch_can_split_and_merge_tracks_without_overlapping_frames() -> None:
    raw = pixel_tracks()
    patch = ReviewPatch(
        patch_id="patch-1",
        parent_artifact_id=raw.artifact_id,
        operations=(
            SplitTrack(track_id=1, split_before_frame=2, new_track_id=3),
            RelabelTrack(track_id=3, semantic_class=SemanticClass.BICYCLE_RIDER),
            MergeTracks(track_ids=(2, 3), new_track_id=4),
        ),
    )

    reviewed = apply_review_patch(raw, patch)

    assert [track.track_id for track in reviewed.tracks] == [1, 4]
    assert [item.frame_index for item in reviewed.tracks[1].observations] == [0, 1, 2]


def test_projection_requires_accepted_calibration_report() -> None:
    raw = pixel_tracks()
    reviewed = apply_review_patch(
        raw,
        ReviewPatch(patch_id="patch-1", parent_artifact_id=raw.artifact_id, operations=()),
    )
    calibration, report = accepted_calibration()
    rejected = report.model_copy(update={"world_checkpoint_rmse_m": 0.11})

    with pytest.raises(CalibrationRejectedError, match="10 cm"):
        project_reviewed_tracks(reviewed, calibration, rejected)


def test_projection_creates_world_artifact_and_preserves_pixel_lineage() -> None:
    raw = pixel_tracks()
    reviewed = apply_review_patch(
        raw,
        ReviewPatch(patch_id="patch-1", parent_artifact_id=raw.artifact_id, operations=()),
    )
    calibration, report = accepted_calibration()

    world = project_reviewed_tracks(reviewed, calibration, report)

    assert world.coordinate_space == "world_m"
    assert world.parent_artifact_id == reviewed.artifact_id
    assert world.calibration_id == report.calibration_id
    assert (world.tracks[0].observations[0].point.x, world.tracks[0].observations[0].point.y) == (
        pytest.approx(1.0),
        pytest.approx(1.0),
    )
    assert world.tracks[0].observations[0].projection_error_estimate_m == pytest.approx(
        report.world_checkpoint_rmse_m
    )


def test_postprocessing_interpolates_only_short_gaps_and_keeps_parent_immutable() -> None:
    raw = pixel_tracks()
    reviewed = apply_review_patch(
        raw,
        ReviewPatch(patch_id="patch-1", parent_artifact_id=raw.artifact_id, operations=()),
    )
    calibration, report = accepted_calibration()
    world = project_reviewed_tracks(reviewed, calibration, report)

    processed = postprocess_world_tracks(
        world,
        PostprocessProfile(max_interpolation_gap_seconds=0.4, smoothing_window_seconds=0.4),
    )

    assert len(world.tracks[0].observations) == 2
    assert [item.frame_index for item in processed.tracks[0].observations] == [0, 1, 2]
    assert processed.tracks[0].observations[1].interpolated is True
    assert processed.parent_artifact_id == world.artifact_id


def test_postprocessing_does_not_bridge_long_gaps() -> None:
    raw = pixel_tracks()
    long_gap_track = raw.tracks[0].model_copy(
        update={"observations": (observation(0, 10.0, 10.0), observation(10, 20.0, 10.0))}
    )
    raw = raw.model_copy(update={"tracks": (long_gap_track,)})
    reviewed = apply_review_patch(
        raw,
        ReviewPatch(patch_id="patch-1", parent_artifact_id=raw.artifact_id, operations=()),
    )
    calibration, report = accepted_calibration()
    world = project_reviewed_tracks(reviewed, calibration, report)

    processed = postprocess_world_tracks(world, PostprocessProfile())

    assert [item.frame_index for item in processed.tracks[0].observations] == [0, 10]
