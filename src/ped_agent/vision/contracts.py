from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from ped_agent.models.trajectory import VideoMetadata


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SemanticClass(StrEnum):
    PEDESTRIAN = "pedestrian"
    PEDESTRIAN_UMBRELLA = "pedestrian_umbrella"
    BICYCLE_RIDER = "bicycle_rider"
    EBIKE_RIDER = "ebike_rider"


REQUIRED_SEMANTIC_CLASSES = frozenset(SemanticClass)


class ContactPointQuality(StrEnum):
    KEYPOINT = "keypoint"
    ESTIMATED = "estimated"
    FALLBACK = "fallback"
    MANUAL = "manual"


class CalibrationMode(StrEnum):
    FULL_CAMERA = "full_camera"
    HOMOGRAPHY = "homography"


class InferenceDefaults(FrozenModel):
    batch: int = Field(default=1, ge=1)
    frame_stride: int = Field(default=1, ge=1)
    detection_confidence: float = Field(default=0.10, ge=0, le=1)
    nms_iou: float = Field(default=0.65, ge=0, le=1)
    max_detections: int = Field(default=1000, ge=1)
    keypoint_confidence: float = Field(default=0.35, ge=0, le=1)
    device: str = "auto"
    cuda_precision: Literal["fp16", "fp32"] = "fp16"
    cpu_precision: Literal["fp32"] = "fp32"


class ByteTrackDefaults(FrozenModel):
    backend: Literal["bytetrack"] = "bytetrack"
    high_threshold: float = Field(default=0.25, ge=0, le=1)
    low_threshold: float = Field(default=0.10, ge=0, le=1)
    new_track_threshold: float = Field(default=0.25, ge=0, le=1)
    match_threshold: float = Field(default=0.80, ge=0, le=1)
    lost_buffer_seconds: float = Field(default=1.2, gt=0)
    fuse_score: bool = True

    def buffer_frames(self, processed_fps: float) -> int:
        if processed_fps <= 0:
            raise ValueError("processed_fps must be positive")
        return max(1, round(self.lost_buffer_seconds * processed_fps))


class ModelManifest(FrozenModel):
    model_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]+$")
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    backend: Literal["ultralytics"]
    weights_path: Path
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    input_size: int = Field(ge=320)
    class_map: dict[int, SemanticClass]
    keypoint_names: tuple[str, ...] = ()
    contact_keypoints: dict[SemanticClass, tuple[str, ...]]
    inference: InferenceDefaults = Field(default_factory=InferenceDefaults)
    tracker: ByteTrackDefaults = Field(default_factory=ByteTrackDefaults)

    @model_validator(mode="after")
    def require_business_classes_and_contact_points(self) -> ModelManifest:
        if set(self.class_map.values()) != REQUIRED_SEMANTIC_CLASSES:
            raise ValueError("model manifest must map all four required semantic classes")
        if set(self.contact_keypoints) != REQUIRED_SEMANTIC_CLASSES:
            raise ValueError("model manifest must define contact keypoints for all classes")
        if any(len(names) != 2 for names in self.contact_keypoints.values()):
            raise ValueError("each semantic class requires exactly two contact keypoints")
        required_names = {
            name for names in self.contact_keypoints.values() for name in names
        }
        if self.keypoint_names and not required_names.issubset(self.keypoint_names):
            raise ValueError("contact keypoints must be present in keypoint_names")
        return self

    @staticmethod
    def tracking_group(semantic_class: SemanticClass) -> Literal["pedestrian", "rider"]:
        if semantic_class in {
            SemanticClass.PEDESTRIAN,
            SemanticClass.PEDESTRIAN_UMBRELLA,
        }:
            return "pedestrian"
        return "rider"


class PixelPoint(FrozenModel):
    x: float
    y: float


class VideoTaskSpec(FrozenModel):
    task_name: str = Field(min_length=1)
    source_video: Path
    model_id: str = Field(min_length=1)
    scene_id: str | None = None
    copy_source_video: Literal[True] = True
    render_annotated_video: Literal[False] = False


class KeypointObservation(PixelPoint):
    confidence: float = Field(ge=0, le=1)


class DetectionObservation(FrozenModel):
    frame_index: int = Field(ge=0)
    timestamp: float = Field(ge=0)
    detection_id: str = Field(min_length=1)
    raw_class_id: int = Field(ge=0)
    semantic_class: SemanticClass
    bbox_xyxy: tuple[float, float, float, float]
    confidence: float = Field(ge=0, le=1)
    frame_size: tuple[int, int]
    keypoints: dict[str, KeypointObservation] = Field(default_factory=dict)
    contact_point: PixelPoint
    contact_quality: ContactPointQuality

    @model_validator(mode="after")
    def validate_geometry(self) -> DetectionObservation:
        width, height = self.frame_size
        if width <= 0 or height <= 0:
            raise ValueError("frame size must be positive")
        x1, y1, x2, y2 = self.bbox_xyxy
        if x2 < x1 or y2 < y1:
            raise ValueError("bbox coordinates must be ordered")
        if not (0 <= self.contact_point.x < width and 0 <= self.contact_point.y < height):
            raise ValueError("contact point must be inside the frame")
        return self


class PixelTrackObservation(FrozenModel):
    frame_index: int = Field(ge=0)
    timestamp: float = Field(ge=0)
    point: PixelPoint
    bbox_xyxy: tuple[float, float, float, float]
    detection_confidence: float = Field(ge=0, le=1)
    tracking_confidence: float = Field(ge=0, le=1)
    semantic_class: SemanticClass
    contact_quality: ContactPointQuality


class PixelTrack(FrozenModel):
    track_id: int = Field(ge=0)
    semantic_class: SemanticClass
    observations: tuple[PixelTrackObservation, ...]


class PixelTrackSet(FrozenModel):
    artifact_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    source_video_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    model_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    video: VideoMetadata
    tracks: tuple[PixelTrack, ...]
    coordinate_space: Literal["image_px"] = "image_px"


class ReviewedPixelTrackSet(PixelTrackSet):
    parent_artifact_id: str = Field(min_length=1)
    review_revision: int = Field(ge=1)
    applied_patch_ids: tuple[str, ...] = ()


class WorldPoint(FrozenModel):
    x: float
    y: float


class WorldTrackObservation(FrozenModel):
    frame_index: int = Field(ge=0)
    timestamp: float = Field(ge=0)
    point: WorldPoint
    source_pixel: PixelPoint
    projection_error_estimate_m: float = Field(ge=0)
    contact_quality: ContactPointQuality
    interpolated: bool = False
    smoothed: bool = False
    outlier_candidate: bool = False


class WorldTrack(FrozenModel):
    track_id: int = Field(ge=0)
    semantic_class: SemanticClass
    observations: tuple[WorldTrackObservation, ...]


class WorldTrackSet(FrozenModel):
    artifact_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    parent_artifact_id: str = Field(min_length=1)
    calibration_id: str = Field(min_length=1)
    video: VideoMetadata
    tracks: tuple[WorldTrack, ...]
    coordinate_space: Literal["world_m"] = "world_m"


class ProcessedWorldTrackSet(WorldTrackSet):
    postprocess_profile_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class SceneProfile(FrozenModel):
    scene_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]+$")
    version: int = Field(ge=1)
    name: str = Field(min_length=1)
    camera_fingerprint: str = Field(min_length=1)
    resolution: tuple[int, int]
    calibration_mode: CalibrationMode
    roi: tuple[tuple[float, float], ...]
    world_unit: Literal["m"] = "m"
    exclusion_zones: dict[str, tuple[tuple[float, float], ...]] = Field(default_factory=dict)
    zones: dict[str, tuple[tuple[float, float], ...]] = Field(default_factory=dict)
    counting_lines: dict[str, tuple[tuple[float, float], tuple[float, float]]] = Field(
        default_factory=dict
    )
    entrances: dict[str, tuple[tuple[float, float], ...]] = Field(default_factory=dict)
    conflict_zones: dict[str, tuple[tuple[float, float], ...]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_scene(self) -> SceneProfile:
        width, height = self.resolution
        if width <= 0 or height <= 0:
            raise ValueError("scene resolution must be positive")
        if len(self.roi) < 3:
            raise ValueError("scene ROI requires at least three points")
        return self

    def matches_camera(self, camera_fingerprint: str, resolution: tuple[int, int]) -> bool:
        return self.camera_fingerprint == camera_fingerprint and self.resolution == resolution


class CalibrationReport(FrozenModel):
    calibration_id: str = Field(min_length=1)
    scene_id: str = Field(min_length=1)
    scene_version: int = Field(ge=1)
    mode: CalibrationMode
    image_reprojection_rmse_px: float = Field(ge=0)
    world_checkpoint_rmse_m: float = Field(ge=0)
    checkpoint_count: int = Field(ge=0)
    matrix: tuple[tuple[float, ...], ...] | None = None
    camera_matrix: tuple[tuple[float, float, float], ...] | None = None
    distortion: tuple[float, ...] | None = None
    rotation_world_to_camera: tuple[tuple[float, float, float], ...] | None = None
    translation_world_to_camera: tuple[float, float, float] | None = None

    @model_validator(mode="after")
    def require_independent_checkpoints(self) -> CalibrationReport:
        if self.checkpoint_count < 4:
            raise ValueError("calibration requires at least four independent checkpoints")
        return self

    @computed_field
    @property
    def accepted(self) -> bool:
        return self.world_checkpoint_rmse_m <= 0.10


__all__ = [
    "ByteTrackDefaults",
    "CalibrationMode",
    "CalibrationReport",
    "ContactPointQuality",
    "DetectionObservation",
    "InferenceDefaults",
    "KeypointObservation",
    "ModelManifest",
    "PixelPoint",
    "PixelTrack",
    "PixelTrackObservation",
    "PixelTrackSet",
    "ReviewedPixelTrackSet",
    "SceneProfile",
    "SemanticClass",
    "VideoMetadata",
    "VideoTaskSpec",
    "WorldPoint",
    "WorldTrack",
    "WorldTrackObservation",
    "WorldTrackSet",
    "ProcessedWorldTrackSet",
]
