from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Protocol

import pandas as pd

from ped_video_analysis.analysis.vision_schemas import (
    DensityPoint,
    FundamentalDiagramPoint,
    SpeedProfileCell,
    VectorFieldCell,
    VoronoiDensityPoint,
)
from ped_video_analysis.vision.contracts import ProcessedWorldTrackSet, SceneProfile


class SpatialProfile(Protocol):
    time_window_seconds: float
    speed_difference_window_seconds: float
    spatial_grid_metres: float


@dataclass(frozen=True)
class PedPySpatialMetrics:
    classic_density: tuple[DensityPoint, ...]
    voronoi_density: tuple[VoronoiDensityPoint, ...] | None
    vector_field: tuple[VectorFieldCell, ...]
    speed_profile: tuple[SpeedProfileCell, ...]
    fundamental_diagram: tuple[FundamentalDiagramPoint, ...]


def try_compute_pedpy_spatial(
    source: ProcessedWorldTrackSet,
    scene: SceneProfile,
    profile: SpatialProfile,
) -> PedPySpatialMetrics | None:
    try:
        import pedpy
    except ImportError:
        return None

    rows = [
        {
            "id": track.track_id,
            "frame": item.frame_index,
            "x": item.point.x,
            "y": item.point.y,
        }
        for track in source.tracks
        for item in track.observations
    ]
    if not rows:
        return None
    frame_rate = source.video.fps
    try:
        trajectory = pedpy.TrajectoryData(pd.DataFrame(rows), frame_rate)
        measurement_area = pedpy.MeasurementArea(scene.roi)
        classic_frame = pedpy.compute_classic_density(
            traj_data=trajectory,
            measurement_area=measurement_area,
        )
        frame_step = max(
            1,
            round(profile.speed_difference_window_seconds * frame_rate / 2),
        )
        individual_speed = pedpy.compute_individual_speed(
            traj_data=trajectory,
            frame_step=frame_step,
            compute_velocity=True,
            speed_calculation=pedpy.SpeedCalculation.BORDER_ADAPTIVE,
        )
    except Exception:
        return None

    row_frame = pd.DataFrame(rows)
    max_bin = max(int((item["frame"] / frame_rate) // profile.time_window_seconds) for item in rows)
    counts_by_bin: dict[int, set[int]] = defaultdict(set)
    for item in rows:
        time_bin = int((item["frame"] / frame_rate) // profile.time_window_seconds)
        counts_by_bin[time_bin].add(int(item["id"]))

    classic_frame["time_bin"] = (
        classic_frame["frame"] / frame_rate / profile.time_window_seconds
    ).astype(int)
    classic_mean = classic_frame.groupby("time_bin")["density"].mean().to_dict()
    classic_density = tuple(
        DensityPoint(
            time_bin=time_bin,
            timestamp_s=time_bin * profile.time_window_seconds,
            count=len(counts_by_bin.get(time_bin, set())),
            density_per_m2=float(classic_mean.get(time_bin, 0.0)),
        )
        for time_bin in range(max_bin + 1)
    )

    speed_data = individual_speed.merge(row_frame, on=["id", "frame"], how="left")
    speed_data["time_bin"] = (
        speed_data["frame"] / frame_rate / profile.time_window_seconds
    ).astype(int)
    speed_data["x_index"] = (speed_data["x"] / profile.spatial_grid_metres).map(math.floor)
    speed_data["y_index"] = (speed_data["y"] / profile.spatial_grid_metres).map(math.floor)
    vector_field = tuple(
        VectorFieldCell(
            x_index=int(x_index),
            y_index=int(y_index),
            count=len(group),
            mean_vx_mps=float(group["v_x"].mean()),
            mean_vy_mps=float(group["v_y"].mean()),
            mean_speed_mps=float(group["speed"].mean()),
        )
        for (x_index, y_index), group in speed_data.groupby(["x_index", "y_index"])
    )
    speed_profile = tuple(
        SpeedProfileCell(
            x_index=item.x_index,
            y_index=item.y_index,
            count=item.count,
            mean_speed_mps=item.mean_speed_mps,
        )
        for item in vector_field
    )
    speed_by_bin = speed_data.groupby("time_bin")["speed"].mean().to_dict()
    fundamental_diagram = tuple(
        FundamentalDiagramPoint(
            time_bin=item.time_bin,
            timestamp_s=item.timestamp_s,
            density_per_m2=item.density_per_m2,
            mean_speed_mps=float(speed_by_bin.get(item.time_bin, 0.0)),
            specific_flow_per_m_s=(
                item.density_per_m2 * float(speed_by_bin.get(item.time_bin, 0.0))
            ),
        )
        for item in classic_density
    )

    voronoi_density = _try_voronoi(
        pedpy,
        trajectory,
        scene,
        profile,
        frame_rate,
        max_bin,
    )
    return PedPySpatialMetrics(
        classic_density=classic_density,
        voronoi_density=voronoi_density,
        vector_field=vector_field,
        speed_profile=speed_profile,
        fundamental_diagram=fundamental_diagram,
    )


def _try_voronoi(
    pedpy,
    trajectory,
    scene: SceneProfile,
    profile: SpatialProfile,
    frame_rate: float,
    max_bin: int,
) -> tuple[VoronoiDensityPoint, ...] | None:
    try:
        individual = pedpy.compute_individual_voronoi_polygons(
            traj_data=trajectory,
            walkable_area=pedpy.WalkableArea(scene.roi),
        )
    except Exception:
        return None
    individual["time_bin"] = (
        individual["frame"] / frame_rate / profile.time_window_seconds
    ).astype(int)
    grouped = {int(time_bin): group for time_bin, group in individual.groupby("time_bin")}
    return tuple(
        VoronoiDensityPoint(
            time_bin=time_bin,
            timestamp_s=time_bin * profile.time_window_seconds,
            count=int(grouped[time_bin]["id"].nunique()) if time_bin in grouped else 0,
            mean_local_density_per_m2=(
                float(grouped[time_bin]["density"].mean()) if time_bin in grouped else 0.0
            ),
            max_local_density_per_m2=(
                float(grouped[time_bin]["density"].max()) if time_bin in grouped else 0.0
            ),
        )
        for time_bin in range(max_bin + 1)
    )


__all__ = ["PedPySpatialMetrics", "try_compute_pedpy_spatial"]
