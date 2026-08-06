from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from ped_agent.vision.contracts import (
    ContactPointQuality,
    PixelPoint,
    PixelTrack,
    PixelTrackObservation,
    PixelTrackSet,
    ProcessedWorldTrackSet,
    ReviewedPixelTrackSet,
    SemanticClass,
    VideoMetadata,
    WorldPoint,
    WorldTrack,
    WorldTrackObservation,
    WorldTrackSet,
)


@dataclass(frozen=True)
class StoredPixelArtifact:
    artifact_dir: Path
    parquet_path: Path
    metadata_path: Path


StoredWorldArtifact = StoredPixelArtifact


class PixelTrackParquetStore:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def write(self, artifact: PixelTrackSet) -> StoredPixelArtifact:
        paths = self.paths(artifact.artifact_id)
        if paths.artifact_dir.exists():
            raise FileExistsError(f"immutable artifact already exists: {artifact.artifact_id}")
        paths.artifact_dir.mkdir(parents=True)
        rows = [
            {
                "track_id": track.track_id,
                "track_class": track.semantic_class.value,
                "frame_index": item.frame_index,
                "timestamp": item.timestamp,
                "point_x": item.point.x,
                "point_y": item.point.y,
                "bbox_x1": item.bbox_xyxy[0],
                "bbox_y1": item.bbox_xyxy[1],
                "bbox_x2": item.bbox_xyxy[2],
                "bbox_y2": item.bbox_xyxy[3],
                "detection_confidence": item.detection_confidence,
                "tracking_confidence": item.tracking_confidence,
                "semantic_class": item.semantic_class.value,
                "contact_quality": item.contact_quality.value,
            }
            for track in artifact.tracks
            for item in track.observations
        ]
        table = pa.Table.from_pylist(rows, schema=_pixel_schema())
        pq.write_table(table, paths.parquet_path, compression="zstd")
        metadata = artifact.model_dump(mode="json", exclude={"tracks"})
        paths.metadata_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return paths

    def read(
        self,
        artifact_id: str,
        *,
        model_type: type[PixelTrackSet] = PixelTrackSet,
    ) -> PixelTrackSet:
        paths = self.paths(artifact_id)
        metadata = json.loads(paths.metadata_path.read_text(encoding="utf-8"))
        rows = pq.read_table(paths.parquet_path).to_pylist()
        grouped: dict[int, list[PixelTrackObservation]] = {}
        track_classes: dict[int, SemanticClass] = {}
        for row in rows:
            track_id = int(row["track_id"])
            track_classes[track_id] = SemanticClass(row["track_class"])
            grouped.setdefault(track_id, []).append(
                PixelTrackObservation(
                    frame_index=int(row["frame_index"]),
                    timestamp=float(row["timestamp"]),
                    point=PixelPoint(x=float(row["point_x"]), y=float(row["point_y"])),
                    bbox_xyxy=(
                        float(row["bbox_x1"]),
                        float(row["bbox_y1"]),
                        float(row["bbox_x2"]),
                        float(row["bbox_y2"]),
                    ),
                    detection_confidence=float(row["detection_confidence"]),
                    tracking_confidence=float(row["tracking_confidence"]),
                    semantic_class=SemanticClass(row["semantic_class"]),
                    contact_quality=ContactPointQuality(row["contact_quality"]),
                )
            )
        tracks = tuple(
            PixelTrack(
                track_id=track_id,
                semantic_class=track_classes[track_id],
                observations=tuple(
                    sorted(grouped[track_id], key=lambda item: item.frame_index)
                ),
            )
            for track_id in sorted(grouped)
        )
        metadata["video"] = VideoMetadata.model_validate(metadata["video"])
        metadata["tracks"] = tracks
        return model_type.model_validate(metadata)

    def read_reviewed(self, artifact_id: str) -> ReviewedPixelTrackSet:
        artifact = self.read(artifact_id, model_type=ReviewedPixelTrackSet)
        if not isinstance(artifact, ReviewedPixelTrackSet):
            raise TypeError("stored artifact is not a reviewed pixel track set")
        return artifact

    def paths(self, artifact_id: str) -> StoredPixelArtifact:
        artifact_dir = self.root / artifact_id
        return StoredPixelArtifact(
            artifact_dir=artifact_dir,
            parquet_path=artifact_dir / "observations.parquet",
            metadata_path=artifact_dir / "metadata.json",
        )


class WorldTrackParquetStore:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def write(self, artifact: WorldTrackSet) -> StoredWorldArtifact:
        paths = self.paths(artifact.artifact_id)
        if paths.artifact_dir.exists():
            raise FileExistsError(f"immutable artifact already exists: {artifact.artifact_id}")
        paths.artifact_dir.mkdir(parents=True)
        rows = [
            {
                "track_id": track.track_id,
                "track_class": track.semantic_class.value,
                "frame_index": item.frame_index,
                "timestamp": item.timestamp,
                "world_x": item.point.x,
                "world_y": item.point.y,
                "pixel_x": item.source_pixel.x,
                "pixel_y": item.source_pixel.y,
                "projection_error_estimate_m": item.projection_error_estimate_m,
                "contact_quality": item.contact_quality.value,
                "interpolated": item.interpolated,
                "smoothed": item.smoothed,
                "outlier_candidate": item.outlier_candidate,
            }
            for track in artifact.tracks
            for item in track.observations
        ]
        pq.write_table(
            pa.Table.from_pylist(rows, schema=_world_schema()),
            paths.parquet_path,
            compression="zstd",
        )
        paths.metadata_path.write_text(
            json.dumps(
                artifact.model_dump(mode="json", exclude={"tracks"}),
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return paths

    def read(
        self,
        artifact_id: str,
        *,
        model_type: type[WorldTrackSet] = WorldTrackSet,
    ) -> WorldTrackSet:
        paths = self.paths(artifact_id)
        metadata = json.loads(paths.metadata_path.read_text(encoding="utf-8"))
        rows = pq.read_table(paths.parquet_path).to_pylist()
        grouped: dict[int, list[WorldTrackObservation]] = {}
        track_classes: dict[int, SemanticClass] = {}
        for row in rows:
            track_id = int(row["track_id"])
            track_classes[track_id] = SemanticClass(row["track_class"])
            grouped.setdefault(track_id, []).append(
                WorldTrackObservation(
                    frame_index=int(row["frame_index"]),
                    timestamp=float(row["timestamp"]),
                    point=WorldPoint(
                        x=float(row["world_x"]), y=float(row["world_y"])
                    ),
                    source_pixel=PixelPoint(
                        x=float(row["pixel_x"]), y=float(row["pixel_y"])
                    ),
                    projection_error_estimate_m=float(
                        row["projection_error_estimate_m"]
                    ),
                    contact_quality=ContactPointQuality(row["contact_quality"]),
                    interpolated=bool(row["interpolated"]),
                    smoothed=bool(row["smoothed"]),
                    outlier_candidate=bool(row["outlier_candidate"]),
                )
            )
        metadata["video"] = VideoMetadata.model_validate(metadata["video"])
        metadata["tracks"] = tuple(
            WorldTrack(
                track_id=track_id,
                semantic_class=track_classes[track_id],
                observations=tuple(
                    sorted(grouped[track_id], key=lambda item: item.frame_index)
                ),
            )
            for track_id in sorted(grouped)
        )
        return model_type.model_validate(metadata)

    def read_processed(self, artifact_id: str) -> ProcessedWorldTrackSet:
        artifact = self.read(artifact_id, model_type=ProcessedWorldTrackSet)
        if not isinstance(artifact, ProcessedWorldTrackSet):
            raise TypeError("stored artifact is not a processed world track set")
        return artifact

    def paths(self, artifact_id: str) -> StoredWorldArtifact:
        artifact_dir = self.root / artifact_id
        return StoredWorldArtifact(
            artifact_dir=artifact_dir,
            parquet_path=artifact_dir / "observations.parquet",
            metadata_path=artifact_dir / "metadata.json",
        )


def _pixel_schema() -> pa.Schema:
    return pa.schema(
        [
            ("track_id", pa.int64()),
            ("track_class", pa.string()),
            ("frame_index", pa.int64()),
            ("timestamp", pa.float64()),
            ("point_x", pa.float64()),
            ("point_y", pa.float64()),
            ("bbox_x1", pa.float64()),
            ("bbox_y1", pa.float64()),
            ("bbox_x2", pa.float64()),
            ("bbox_y2", pa.float64()),
            ("detection_confidence", pa.float64()),
            ("tracking_confidence", pa.float64()),
            ("semantic_class", pa.string()),
            ("contact_quality", pa.string()),
        ]
    )


def _world_schema() -> pa.Schema:
    return pa.schema(
        [
            ("track_id", pa.int64()),
            ("track_class", pa.string()),
            ("frame_index", pa.int64()),
            ("timestamp", pa.float64()),
            ("world_x", pa.float64()),
            ("world_y", pa.float64()),
            ("pixel_x", pa.float64()),
            ("pixel_y", pa.float64()),
            ("projection_error_estimate_m", pa.float64()),
            ("contact_quality", pa.string()),
            ("interpolated", pa.bool_()),
            ("smoothed", pa.bool_()),
            ("outlier_candidate", pa.bool_()),
        ]
    )


__all__ = [
    "PixelTrackParquetStore",
    "StoredPixelArtifact",
    "StoredWorldArtifact",
    "WorldTrackParquetStore",
]
