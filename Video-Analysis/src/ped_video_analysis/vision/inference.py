from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256

from ped_video_analysis.vision.contracts import (
    ModelManifest,
    PixelTrack,
    PixelTrackObservation,
    PixelTrackSet,
    SemanticClass,
    VideoMetadata,
)


@dataclass(frozen=True)
class TrackAssignment:
    track_id: int
    observation: PixelTrackObservation


def build_bytetrack_config(
    manifest: ModelManifest,
    *,
    source_fps: float,
) -> dict[str, str | int | float | bool]:
    processed_fps = source_fps / manifest.inference.frame_stride
    tracker = manifest.tracker
    return {
        "tracker_type": "bytetrack",
        "track_high_thresh": tracker.high_threshold,
        "track_low_thresh": tracker.low_threshold,
        "new_track_thresh": tracker.new_track_threshold,
        "track_buffer": tracker.buffer_frames(processed_fps),
        "match_thresh": tracker.match_threshold,
        "fuse_score": tracker.fuse_score,
    }


def assemble_pixel_tracks(
    *,
    task_id: str,
    source_video_sha256: str,
    model_manifest_sha256: str,
    video: VideoMetadata,
    assignments: tuple[TrackAssignment, ...],
) -> PixelTrackSet:
    grouped: dict[int, list[PixelTrackObservation]] = defaultdict(list)
    for assignment in assignments:
        grouped[assignment.track_id].append(assignment.observation)

    tracks = []
    for track_id in sorted(grouped):
        observations = sorted(grouped[track_id], key=lambda item: item.frame_index)
        groups = {ModelManifest.tracking_group(item.semantic_class) for item in observations}
        if len(groups) > 1:
            raise ValueError(f"track {track_id} contains incompatible association groups")
        semantic_class = _weighted_class_vote(observations)
        normalized = tuple(
            item.model_copy(update={"semantic_class": semantic_class}) for item in observations
        )
        tracks.append(
            PixelTrack(
                track_id=track_id,
                semantic_class=semantic_class,
                observations=normalized,
            )
        )

    payload = json.dumps(
        {
            "task_id": task_id,
            "source_video_sha256": source_video_sha256,
            "model_manifest_sha256": model_manifest_sha256,
            "tracks": [track.model_dump(mode="json") for track in tracks],
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    artifact_id = f"pixel-{sha256(payload.encode()).hexdigest()[:16]}"
    return PixelTrackSet(
        artifact_id=artifact_id,
        task_id=task_id,
        source_video_sha256=source_video_sha256,
        model_manifest_sha256=model_manifest_sha256,
        video=video,
        tracks=tuple(tracks),
    )


def _weighted_class_vote(observations: list[PixelTrackObservation]) -> SemanticClass:
    weights: dict[SemanticClass, float] = defaultdict(float)
    for item in observations:
        weights[item.semantic_class] += item.detection_confidence * item.tracking_confidence
    return min(weights, key=lambda item: (-weights[item], item.value))


__all__ = [
    "TrackAssignment",
    "assemble_pixel_tracks",
    "build_bytetrack_config",
]
