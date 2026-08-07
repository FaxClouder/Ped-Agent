from __future__ import annotations

from pathlib import Path

from ped_video_analysis.vision.contracts import (
    ContactPointQuality,
    KeypointObservation,
    ModelManifest,
    SemanticClass,
    VideoMetadata,
)
from ped_video_analysis.vision.runner import (
    DecodedDetection,
    TrackedDetection,
    VideoFrame,
    VisionInferenceRunner,
)


def manifest() -> ModelManifest:
    return ModelManifest(
        model_id="mixed-flow-v1",
        name="Mixed flow detector",
        version="1.0.0",
        backend="ultralytics",
        weights_path=Path("mixed.pt"),
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
        keypoint_names=("left_foot", "right_foot", "front_wheel", "rear_wheel"),
    )


class FakeFrames:
    metadata = VideoMetadata(
        source="source.mp4",
        fps=25,
        total_frames=2,
        resolution=(640, 480),
        duration=0.08,
    )

    def __iter__(self):
        yield VideoFrame(index=0, timestamp=0.0, image=object(), size=(640, 480))
        yield VideoFrame(index=1, timestamp=0.04, image=object(), size=(640, 480))


class FakeDetector:
    def detect(self, frame: object) -> tuple[DecodedDetection, ...]:
        if not hasattr(self, "called"):
            self.called = True
            return (
                DecodedDetection(
                    raw_class_id=0,
                    bbox_xyxy=(10, 20, 30, 60),
                    confidence=0.8,
                    keypoints={
                        "left_foot": KeypointObservation(x=18, y=58, confidence=0.9),
                        "right_foot": KeypointObservation(x=22, y=58, confidence=0.9),
                    },
                ),
            )
        return (
            DecodedDetection(
                raw_class_id=1,
                bbox_xyxy=(12, 20, 32, 60),
                confidence=0.9,
                keypoints={},
            ),
        )


class FakeTracker:
    def update(
        self,
        detections: tuple[DecodedDetection, ...],
        semantic_classes: tuple[SemanticClass, ...],
        frame: object,
    ) -> tuple[TrackedDetection, ...]:
        return (TrackedDetection(track_id=7, detection_index=0, confidence=0.95),)


def test_runner_extracts_contacts_marks_fallback_and_votes_final_class() -> None:
    runner = VisionInferenceRunner(
        manifest(),
        detector=FakeDetector(),
        tracker=FakeTracker(),
    )

    artifact = runner.run(
        task_id="task-1",
        source_video_sha256="b" * 64,
        model_manifest_sha256="c" * 64,
        frames=FakeFrames(),
    )

    track = artifact.tracks[0]
    assert track.track_id == 7
    assert track.semantic_class is SemanticClass.PEDESTRIAN_UMBRELLA
    assert track.observations[0].point.x == 20
    assert track.observations[0].contact_quality is ContactPointQuality.KEYPOINT
    assert track.observations[1].point.x == 22
    assert track.observations[1].contact_quality is ContactPointQuality.FALLBACK
