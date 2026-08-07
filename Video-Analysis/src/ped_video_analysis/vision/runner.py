from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Protocol

from ped_video_analysis.vision.contact_points import extract_contact_point
from ped_video_analysis.vision.contracts import (
    KeypointObservation,
    ModelManifest,
    PixelTrackObservation,
    PixelTrackSet,
    SemanticClass,
    VideoMetadata,
)
from ped_video_analysis.vision.inference import TrackAssignment, assemble_pixel_tracks


@dataclass(frozen=True)
class VideoFrame:
    index: int
    timestamp: float
    image: Any
    size: tuple[int, int]


@dataclass(frozen=True)
class DecodedDetection:
    raw_class_id: int
    bbox_xyxy: tuple[float, float, float, float]
    confidence: float
    keypoints: dict[str, KeypointObservation]


@dataclass(frozen=True)
class TrackedDetection:
    track_id: int
    detection_index: int
    confidence: float


class FrameSequence(Protocol):
    metadata: VideoMetadata

    def __iter__(self) -> Iterable[VideoFrame]: ...


class Detector(Protocol):
    def detect(self, frame: Any) -> tuple[DecodedDetection, ...]: ...


class Tracker(Protocol):
    def update(
        self,
        detections: tuple[DecodedDetection, ...],
        semantic_classes: tuple[SemanticClass, ...],
        frame: Any,
    ) -> tuple[TrackedDetection, ...]: ...


class VisionInferenceRunner:
    def __init__(
        self,
        manifest: ModelManifest,
        *,
        detector: Detector,
        tracker: Tracker,
    ):
        self.manifest = manifest
        self.detector = detector
        self.tracker = tracker

    def run(
        self,
        *,
        task_id: str,
        source_video_sha256: str,
        model_manifest_sha256: str,
        frames: FrameSequence,
    ) -> PixelTrackSet:
        assignments: list[TrackAssignment] = []
        stride = self.manifest.inference.frame_stride
        for frame in frames:
            if frame.index % stride:
                continue
            decoded = tuple(
                item
                for item in self.detector.detect(frame.image)
                if item.raw_class_id in self.manifest.class_map
            )
            semantic_classes = tuple(self.manifest.class_map[item.raw_class_id] for item in decoded)
            tracked = self.tracker.update(decoded, semantic_classes, frame.image)
            for tracked_item in tracked:
                detection = decoded[tracked_item.detection_index]
                semantic_class = semantic_classes[tracked_item.detection_index]
                contact = extract_contact_point(
                    semantic_class=semantic_class,
                    bbox_xyxy=detection.bbox_xyxy,
                    keypoints=detection.keypoints,
                    minimum_confidence=self.manifest.inference.keypoint_confidence,
                )
                assignments.append(
                    TrackAssignment(
                        track_id=tracked_item.track_id,
                        observation=PixelTrackObservation(
                            frame_index=frame.index,
                            timestamp=frame.timestamp,
                            point=contact.point,
                            bbox_xyxy=detection.bbox_xyxy,
                            detection_confidence=detection.confidence,
                            tracking_confidence=tracked_item.confidence,
                            semantic_class=semantic_class,
                            contact_quality=contact.quality,
                        ),
                    )
                )
        return assemble_pixel_tracks(
            task_id=task_id,
            source_video_sha256=source_video_sha256,
            model_manifest_sha256=model_manifest_sha256,
            video=frames.metadata,
            assignments=tuple(assignments),
        )


__all__ = [
    "DecodedDetection",
    "Detector",
    "FrameSequence",
    "TrackedDetection",
    "Tracker",
    "VideoFrame",
    "VisionInferenceRunner",
]
