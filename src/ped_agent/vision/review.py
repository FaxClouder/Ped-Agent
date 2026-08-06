from __future__ import annotations

import json
from hashlib import sha256
from typing import Annotated, Literal

from pydantic import Field

from ped_agent.vision.contracts import (
    ContactPointQuality,
    FrozenModel,
    PixelPoint,
    PixelTrack,
    PixelTrackSet,
    ReviewedPixelTrackSet,
    SemanticClass,
)


class DeleteTrack(FrozenModel):
    operation: Literal["delete_track"] = "delete_track"
    track_id: int = Field(ge=0)


class RelabelTrack(FrozenModel):
    operation: Literal["relabel_track"] = "relabel_track"
    track_id: int = Field(ge=0)
    semantic_class: SemanticClass


class SplitTrack(FrozenModel):
    operation: Literal["split_track"] = "split_track"
    track_id: int = Field(ge=0)
    split_before_frame: int = Field(ge=0)
    new_track_id: int = Field(ge=0)


class MergeTracks(FrozenModel):
    operation: Literal["merge_tracks"] = "merge_tracks"
    track_ids: tuple[int, ...] = Field(min_length=2)
    new_track_id: int = Field(ge=0)


class MovePoint(FrozenModel):
    operation: Literal["move_point"] = "move_point"
    track_id: int = Field(ge=0)
    frame_index: int = Field(ge=0)
    point: PixelPoint


ReviewOperation = Annotated[
    DeleteTrack | RelabelTrack | SplitTrack | MergeTracks | MovePoint,
    Field(discriminator="operation"),
]


class ReviewPatch(FrozenModel):
    patch_id: str = Field(min_length=1)
    parent_artifact_id: str = Field(min_length=1)
    operations: tuple[ReviewOperation, ...]


def apply_review_patch(raw: PixelTrackSet, patch: ReviewPatch) -> ReviewedPixelTrackSet:
    if patch.parent_artifact_id != raw.artifact_id:
        raise ValueError("review patch parent artifact does not match pixel track artifact")
    tracks = {track.track_id: track for track in raw.tracks}
    for operation in patch.operations:
        if isinstance(operation, DeleteTrack):
            _require_track(tracks, operation.track_id)
            del tracks[operation.track_id]
        elif isinstance(operation, RelabelTrack):
            track = _require_track(tracks, operation.track_id)
            tracks[operation.track_id] = track.model_copy(
                update={
                    "semantic_class": operation.semantic_class,
                    "observations": tuple(
                        item.model_copy(update={"semantic_class": operation.semantic_class})
                        for item in track.observations
                    ),
                }
            )
        elif isinstance(operation, MovePoint):
            track = _require_track(tracks, operation.track_id)
            found = False
            observations = []
            for item in track.observations:
                if item.frame_index == operation.frame_index:
                    found = True
                    observations.append(
                        item.model_copy(
                            update={
                                "point": operation.point,
                                "contact_quality": ContactPointQuality.MANUAL,
                            }
                        )
                    )
                else:
                    observations.append(item)
            if not found:
                raise ValueError("review point frame does not exist in track")
            tracks[operation.track_id] = track.model_copy(
                update={"observations": tuple(observations)}
            )
        elif isinstance(operation, SplitTrack):
            track = _require_track(tracks, operation.track_id)
            if operation.new_track_id in tracks:
                raise ValueError("split target track id already exists")
            before = tuple(
                item
                for item in track.observations
                if item.frame_index < operation.split_before_frame
            )
            after = tuple(
                item
                for item in track.observations
                if item.frame_index >= operation.split_before_frame
            )
            if not before or not after:
                raise ValueError("split frame must divide a track into two non-empty parts")
            tracks[operation.track_id] = track.model_copy(update={"observations": before})
            tracks[operation.new_track_id] = track.model_copy(
                update={"track_id": operation.new_track_id, "observations": after}
            )
        elif isinstance(operation, MergeTracks):
            selected = [_require_track(tracks, track_id) for track_id in operation.track_ids]
            if (
                operation.new_track_id in tracks
                and operation.new_track_id not in operation.track_ids
            ):
                raise ValueError("merge target track id already exists")
            groups = {
                "pedestrian"
                if track.semantic_class
                in {SemanticClass.PEDESTRIAN, SemanticClass.PEDESTRIAN_UMBRELLA}
                else "rider"
                for track in selected
            }
            if len(groups) != 1:
                raise ValueError("tracks from incompatible semantic groups cannot be merged")
            observations = sorted(
                (item for track in selected for item in track.observations),
                key=lambda item: item.frame_index,
            )
            frames = [item.frame_index for item in observations]
            if len(frames) != len(set(frames)):
                raise ValueError("tracks with overlapping frames cannot be merged")
            for track_id in operation.track_ids:
                del tracks[track_id]
            semantic_class = selected[0].semantic_class
            tracks[operation.new_track_id] = PixelTrack(
                track_id=operation.new_track_id,
                semantic_class=semantic_class,
                observations=tuple(
                    item.model_copy(update={"semantic_class": semantic_class})
                    for item in observations
                ),
            )
    serialized = json.dumps(patch.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    digest = sha256(serialized.encode("utf-8")).hexdigest()[:16]
    return ReviewedPixelTrackSet(
        artifact_id=f"reviewed-{digest}",
        task_id=raw.task_id,
        source_video_sha256=raw.source_video_sha256,
        model_manifest_sha256=raw.model_manifest_sha256,
        video=raw.video,
        tracks=tuple(sorted(tracks.values(), key=lambda track: track.track_id)),
        parent_artifact_id=raw.artifact_id,
        review_revision=1,
        applied_patch_ids=(patch.patch_id,),
    )


def _require_track(tracks: dict[int, PixelTrack], track_id: int) -> PixelTrack:
    if track_id not in tracks:
        raise ValueError(f"track {track_id} does not exist")
    return tracks[track_id]


__all__ = [
    "DeleteTrack",
    "MergeTracks",
    "MovePoint",
    "RelabelTrack",
    "ReviewPatch",
    "SplitTrack",
    "apply_review_patch",
]
