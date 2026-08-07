from __future__ import annotations

import inspect
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import numpy as np

from ped_video_analysis.vision.contracts import KeypointObservation, ModelManifest, SemanticClass
from ped_video_analysis.vision.runner import DecodedDetection, TrackedDetection, VideoFrame


class OpenCVFrameSequence:
    def __init__(self, video_path: Path, *, cv2_module: Any | None = None):
        if cv2_module is None:
            try:
                import cv2 as cv2_module
            except ImportError as exc:
                raise RuntimeError("Install ped-agent-core[vision] to read video frames") from exc
        self.video_path = video_path.resolve()
        self.cv2 = cv2_module
        self.capture = self.cv2.VideoCapture(str(self.video_path))
        if not self.capture.isOpened():
            raise ValueError(f"unable to open video: {self.video_path}")
        fps = float(self.capture.get(self.cv2.CAP_PROP_FPS))
        total_frames = int(self.capture.get(self.cv2.CAP_PROP_FRAME_COUNT))
        width = int(self.capture.get(self.cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.capture.get(self.cv2.CAP_PROP_FRAME_HEIGHT))
        if fps <= 0 or width <= 0 or height <= 0:
            self.capture.release()
            raise ValueError("video metadata is incomplete")
        from ped_video_analysis.vision.contracts import VideoMetadata

        self.metadata = VideoMetadata(
            source=str(self.video_path),
            fps=fps,
            total_frames=total_frames,
            resolution=(width, height),
            duration=total_frames / fps,
        )

    def __iter__(self) -> Iterator[VideoFrame]:
        index = 0
        try:
            while True:
                ok, image = self.capture.read()
                if not ok:
                    break
                yield VideoFrame(
                    index=index,
                    timestamp=index / self.metadata.fps,
                    image=image,
                    size=self.metadata.resolution,
                )
                index += 1
        finally:
            self.capture.release()


class UltralyticsDetector:
    def __init__(
        self,
        manifest: ModelManifest,
        *,
        model_factory: Callable[[str], Any] | None = None,
        device_resolver: Callable[[str], str | int] | None = None,
    ):
        self.manifest = manifest
        if model_factory is None:
            try:
                from ultralytics import YOLO
            except ImportError as exc:
                raise RuntimeError(
                    "Install ped-agent-core[vision] to run Ultralytics inference"
                ) from exc
            model_factory = YOLO
        self.model = model_factory(str(manifest.weights_path))
        self.device = (device_resolver or _resolve_device)(manifest.inference.device)

    def detect(self, frame: Any) -> tuple[DecodedDetection, ...]:
        use_half = self.device != "cpu" and self.manifest.inference.cuda_precision == "fp16"
        results = self.model(
            frame,
            conf=self.manifest.inference.detection_confidence,
            iou=self.manifest.inference.nms_iou,
            imgsz=self.manifest.input_size,
            max_det=self.manifest.inference.max_detections,
            device=self.device,
            half=use_half,
            verbose=False,
        )
        result = results[0]
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            return ()
        keypoints = getattr(result, "keypoints", None)
        decoded = []
        for index in range(len(boxes)):
            xyxy = _to_numpy(boxes.xyxy[index]).reshape(-1)
            decoded.append(
                DecodedDetection(
                    raw_class_id=int(boxes.cls[index]),
                    bbox_xyxy=tuple(float(value) for value in xyxy[:4]),
                    confidence=float(boxes.conf[index]),
                    keypoints=self._decode_keypoints(keypoints, index),
                )
            )
        return tuple(decoded)

    def _decode_keypoints(self, keypoints: Any, index: int) -> dict[str, KeypointObservation]:
        if keypoints is None or not self.manifest.keypoint_names:
            return {}
        coordinates = _to_numpy(keypoints.xy[index])
        raw_confidence = getattr(keypoints, "conf", None)
        confidence = (
            _to_numpy(raw_confidence[index])
            if raw_confidence is not None
            else np.ones(len(coordinates))
        )
        return {
            name: KeypointObservation(
                x=float(coordinates[position][0]),
                y=float(coordinates[position][1]),
                confidence=float(confidence[position]),
            )
            for position, name in enumerate(self.manifest.keypoint_names)
            if position < len(coordinates)
        }


class BoxMotByteTrackAdapter:
    def __init__(
        self,
        manifest: ModelManifest,
        *,
        source_fps: float,
        tracker_factory: Callable[..., Any] | None = None,
    ):
        tracker = manifest.tracker
        processed_fps = source_fps / manifest.inference.frame_stride
        kwargs = {
            "track_thresh": tracker.high_threshold,
            "track_low_thresh": tracker.low_threshold,
            "new_track_thresh": tracker.new_track_threshold,
            "track_buffer": tracker.buffer_frames(processed_fps),
            "match_thresh": tracker.match_threshold,
            "frame_rate": processed_fps,
            "fuse_score": tracker.fuse_score,
            "per_class": False,
        }
        self.engine = (tracker_factory or _build_boxmot_tracker)(**kwargs)

    def update(
        self,
        detections: tuple[DecodedDetection, ...],
        semantic_classes: tuple[SemanticClass, ...],
        frame: Any,
    ) -> tuple[TrackedDetection, ...]:
        rows = np.asarray(
            [
                [
                    *detection.bbox_xyxy,
                    detection.confidence,
                    0 if ModelManifest.tracking_group(semantic_class) == "pedestrian" else 1,
                ]
                for detection, semantic_class in zip(detections, semantic_classes, strict=True)
            ],
            dtype=float,
        )
        if not len(rows):
            rows = np.empty((0, 6), dtype=float)
        tracked = np.asarray(self.engine.update(rows, frame), dtype=float)
        if tracked.size == 0:
            return ()
        tracked = np.atleast_2d(tracked)
        return tuple(
            TrackedDetection(
                track_id=int(row[4]),
                detection_index=int(row[7]) if len(row) > 7 else _nearest_detection(row, rows),
                confidence=float(row[5]) if len(row) > 5 else 1.0,
            )
            for row in tracked
        )


def _build_boxmot_tracker(**kwargs: Any) -> Any:
    try:
        from boxmot import ByteTrack
    except ImportError as exc:
        raise RuntimeError("Install ped-agent-core[vision] to use ByteTrack") from exc
    supported = inspect.signature(ByteTrack).parameters
    return ByteTrack(**{key: value for key, value in kwargs.items() if key in supported})


def _resolve_device(configured: str) -> str | int:
    if configured != "auto":
        return configured
    try:
        import torch
    except ImportError:
        return "cpu"
    return 0 if torch.cuda.is_available() else "cpu"


def _to_numpy(value: Any) -> np.ndarray:
    if hasattr(value, "cpu"):
        value = value.cpu()
    if hasattr(value, "numpy"):
        value = value.numpy()
    return np.asarray(value)


def _nearest_detection(track: np.ndarray, detections: np.ndarray) -> int:
    if not len(detections):
        raise ValueError("tracker returned an identity without a source detection")
    distances = np.linalg.norm(detections[:, :4] - track[:4], axis=1)
    return int(np.argmin(distances))


__all__ = ["BoxMotByteTrackAdapter", "OpenCVFrameSequence", "UltralyticsDetector"]
