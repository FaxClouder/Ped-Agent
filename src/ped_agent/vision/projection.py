from __future__ import annotations

from hashlib import sha256
from typing import Protocol

from ped_agent.vision.contracts import (
    CalibrationReport,
    ReviewedPixelTrackSet,
    WorldPoint,
    WorldTrack,
    WorldTrackObservation,
    WorldTrackSet,
)


class PointTransformer(Protocol):
    def transform(self, pixel: tuple[float, float]) -> tuple[float, float]: ...


class CalibrationRejectedError(ValueError):
    pass


def project_reviewed_tracks(
    reviewed: ReviewedPixelTrackSet,
    transformer: PointTransformer,
    report: CalibrationReport,
) -> WorldTrackSet:
    if not report.accepted:
        raise CalibrationRejectedError(
            "calibration exceeds the 10 cm world-coordinate checkpoint RMSE gate"
        )
    tracks = []
    for track in reviewed.tracks:
        observations = []
        for item in track.observations:
            x, y = transformer.transform((item.point.x, item.point.y))
            observations.append(
                WorldTrackObservation(
                    frame_index=item.frame_index,
                    timestamp=item.timestamp,
                    point=WorldPoint(x=x, y=y),
                    source_pixel=item.point,
                    projection_error_estimate_m=report.world_checkpoint_rmse_m,
                    contact_quality=item.contact_quality,
                )
            )
        tracks.append(
            WorldTrack(
                track_id=track.track_id,
                semantic_class=track.semantic_class,
                observations=tuple(observations),
            )
        )
    digest = sha256(f"{reviewed.artifact_id}:{report.calibration_id}".encode()).hexdigest()[:16]
    return WorldTrackSet(
        artifact_id=f"world-{digest}",
        task_id=reviewed.task_id,
        parent_artifact_id=reviewed.artifact_id,
        calibration_id=report.calibration_id,
        video=reviewed.video,
        tracks=tuple(tracks),
    )


__all__ = ["CalibrationRejectedError", "PointTransformer", "project_reviewed_tracks"]
