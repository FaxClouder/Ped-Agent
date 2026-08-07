from __future__ import annotations

import json
from hashlib import sha256

import numpy as np
from pydantic import Field
from scipy.signal import savgol_filter

from ped_video_analysis.vision.contracts import (
    FrozenModel,
    ProcessedWorldTrackSet,
    WorldPoint,
    WorldTrack,
    WorldTrackObservation,
    WorldTrackSet,
)


class PostprocessProfile(FrozenModel):
    max_interpolation_gap_seconds: float = Field(default=0.4, ge=0)
    smoothing_window_seconds: float = Field(default=0.4, ge=0)
    smoothing_polynomial_order: int = Field(default=2, ge=1)
    hampel_window_points: int = Field(default=5, ge=3)
    hampel_sigma: float = Field(default=3.0, gt=0)


def postprocess_world_tracks(
    source: WorldTrackSet,
    profile: PostprocessProfile,
) -> ProcessedWorldTrackSet:
    tracks = tuple(_postprocess_track(track, source.video.fps, profile) for track in source.tracks)
    serialized = json.dumps(profile.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    profile_digest = sha256(serialized.encode("utf-8")).hexdigest()
    artifact_digest = sha256(f"{source.artifact_id}:{profile_digest}".encode()).hexdigest()[:16]
    return ProcessedWorldTrackSet(
        artifact_id=f"processed-{artifact_digest}",
        task_id=source.task_id,
        parent_artifact_id=source.artifact_id,
        calibration_id=source.calibration_id,
        video=source.video,
        tracks=tracks,
        postprocess_profile_sha256=profile_digest,
    )


def _postprocess_track(
    track: WorldTrack,
    fps: float,
    profile: PostprocessProfile,
) -> WorldTrack:
    interpolated = _interpolate_short_gaps(track.observations, fps, profile)
    flagged = _mark_hampel_candidates(interpolated, profile)
    smoothed = _smooth(flagged, fps, profile)
    return track.model_copy(update={"observations": smoothed})


def _interpolate_short_gaps(
    observations: tuple[WorldTrackObservation, ...],
    fps: float,
    profile: PostprocessProfile,
) -> tuple[WorldTrackObservation, ...]:
    if len(observations) < 2:
        return observations
    result: list[WorldTrackObservation] = []
    ordered = sorted(observations, key=lambda item: item.frame_index)
    for current, following in zip(ordered, ordered[1:], strict=False):
        result.append(current)
        missing_frames = following.frame_index - current.frame_index - 1
        gap_seconds = following.timestamp - current.timestamp
        if missing_frames <= 0 or gap_seconds > profile.max_interpolation_gap_seconds:
            continue
        for step in range(1, missing_frames + 1):
            ratio = step / (missing_frames + 1)
            frame_index = current.frame_index + step
            result.append(
                WorldTrackObservation(
                    frame_index=frame_index,
                    timestamp=current.timestamp + ratio * gap_seconds,
                    point=WorldPoint(
                        x=current.point.x + ratio * (following.point.x - current.point.x),
                        y=current.point.y + ratio * (following.point.y - current.point.y),
                    ),
                    source_pixel=current.source_pixel.model_copy(
                        update={
                            "x": current.source_pixel.x
                            + ratio * (following.source_pixel.x - current.source_pixel.x),
                            "y": current.source_pixel.y
                            + ratio * (following.source_pixel.y - current.source_pixel.y),
                        }
                    ),
                    projection_error_estimate_m=max(
                        current.projection_error_estimate_m,
                        following.projection_error_estimate_m,
                    ),
                    contact_quality=current.contact_quality,
                    interpolated=True,
                )
            )
    result.append(ordered[-1])
    return tuple(result)


def _mark_hampel_candidates(
    observations: tuple[WorldTrackObservation, ...],
    profile: PostprocessProfile,
) -> tuple[WorldTrackObservation, ...]:
    if len(observations) < profile.hampel_window_points:
        return observations
    positions = np.asarray([[item.point.x, item.point.y] for item in observations], dtype=float)
    radius = profile.hampel_window_points // 2
    flags = np.zeros(len(observations), dtype=bool)
    for index in range(radius, len(observations) - radius):
        window = positions[index - radius : index + radius + 1]
        median = np.median(window, axis=0)
        distances = np.linalg.norm(window - median, axis=1)
        median_distance = float(np.median(distances))
        mad = float(np.median(np.abs(distances - median_distance)))
        threshold = profile.hampel_sigma * 1.4826 * max(mad, 1e-9)
        flags[index] = np.linalg.norm(positions[index] - median) > median_distance + threshold
    return tuple(
        item.model_copy(update={"outlier_candidate": bool(flags[index])})
        for index, item in enumerate(observations)
    )


def _smooth(
    observations: tuple[WorldTrackObservation, ...],
    fps: float,
    profile: PostprocessProfile,
) -> tuple[WorldTrackObservation, ...]:
    if profile.smoothing_window_seconds <= 0:
        return observations
    requested = max(3, round(profile.smoothing_window_seconds * fps))
    window = requested if requested % 2 == 1 else requested + 1
    if len(observations) < window or window <= profile.smoothing_polynomial_order:
        return observations
    positions = np.asarray([[item.point.x, item.point.y] for item in observations], dtype=float)
    filtered = savgol_filter(
        positions,
        window_length=window,
        polyorder=profile.smoothing_polynomial_order,
        axis=0,
        mode="interp",
    )
    return tuple(
        item.model_copy(
            update={
                "point": WorldPoint(x=float(filtered[index, 0]), y=float(filtered[index, 1])),
                "smoothed": True,
            }
        )
        for index, item in enumerate(observations)
    )


__all__ = ["PostprocessProfile", "postprocess_world_tracks"]
