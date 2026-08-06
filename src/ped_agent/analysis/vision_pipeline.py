from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations

import numpy as np
from pydantic import Field

from ped_agent.analysis.pedpy_adapter import try_compute_pedpy_spatial
from ped_agent.analysis.vision_schemas import (
    AnalysisBundle,
    DensityPoint,
    FlowMetric,
    FundamentalDiagramPoint,
    HeatmapCell,
    IndividualMetric,
    InteractionEvent,
    ODRecord,
    QualitySummary,
    SpatialAnalysis,
    SpeedProfileCell,
    VectorFieldCell,
    VoronoiDensityPoint,
)
from ped_agent.vision.contracts import (
    ContactPointQuality,
    FrozenModel,
    ProcessedWorldTrackSet,
    SceneProfile,
    SemanticClass,
    WorldTrack,
    WorldTrackObservation,
)


class AnalysisProfile(FrozenModel):
    time_window_seconds: float = Field(default=1.0, gt=0)
    speed_difference_window_seconds: float = Field(default=0.4, gt=0)
    spatial_grid_metres: float = Field(default=0.25, gt=0)
    kde_bandwidth_metres: float = Field(default=0.50, gt=0)
    stop_speed_metres_per_second: float = Field(default=0.10, ge=0)
    stop_minimum_duration_seconds: float = Field(default=1.0, ge=0)
    interaction_radius_metres: float = Field(default=5.0, gt=0)
    ttc_horizon_seconds: float = Field(default=5.0, gt=0)
    minimum_track_duration_seconds: float = Field(default=2.0, ge=0)


def analyze_world_tracks(
    source: ProcessedWorldTrackSet,
    scene: SceneProfile,
    profile: AnalysisProfile,
) -> AnalysisBundle:
    if not scene.matches_camera(scene.camera_fingerprint, source.video.resolution):
        raise ValueError("scene resolution does not match trajectory video")
    quality = _quality(source, profile)
    individual = tuple(_individual(track, profile, scene) for track in source.tracks)
    flows = _flows(source, scene)
    spatial = _spatial(source, scene, profile)
    od = _od(source, scene)
    interactions = _interactions(source, profile)
    serialized = json.dumps(
        {
            "artifact": source.artifact_id,
            "scene": [scene.scene_id, scene.version],
            "profile": profile.model_dump(mode="json"),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = sha256(serialized.encode("utf-8")).hexdigest()[:16]
    return AnalysisBundle(
        analysis_id=f"analysis-{digest}",
        task_id=source.task_id,
        source_artifact_id=source.artifact_id,
        scene_id=scene.scene_id,
        scene_version=scene.version,
        quality=quality,
        individual=individual,
        flows=flows,
        spatial=spatial,
        od=od,
        interactions=interactions,
        profile=profile.model_dump(mode="json"),
        provenance={
            "calibration_id": source.calibration_id,
            "postprocess_profile_sha256": source.postprocess_profile_sha256,
            "coordinate_space": source.coordinate_space,
        },
    )


def _quality(source: ProcessedWorldTrackSet, profile: AnalysisProfile) -> QualitySummary:
    observations = [item for track in source.tracks for item in track.observations]
    short_tracks = sum(
        1
        for track in source.tracks
        if _duration(track) < profile.minimum_track_duration_seconds
    )
    expected_points = sum(
        max(item.frame_index for item in track.observations)
        - min(item.frame_index for item in track.observations)
        + 1
        for track in source.tracks
        if track.observations
    )
    gap_count = sum(
        max(0, following.frame_index - current.frame_index - 1)
        for track in source.tracks
        for current, following in zip(
            sorted(track.observations, key=lambda item: item.frame_index),
            sorted(track.observations, key=lambda item: item.frame_index)[1:],
            strict=False,
        )
    )
    return QualitySummary(
        track_count=len(source.tracks),
        point_count=len(observations),
        short_track_count=short_tracks,
        fallback_point_count=sum(
            item.contact_quality is ContactPointQuality.FALLBACK for item in observations
        ),
        interpolated_point_count=sum(item.interpolated for item in observations),
        outlier_candidate_count=sum(item.outlier_candidate for item in observations),
        degraded_point_count=sum(
            item.contact_quality
            in {ContactPointQuality.ESTIMATED, ContactPointQuality.FALLBACK}
            for item in observations
        ),
        manual_revision_point_count=sum(
            item.contact_quality is ContactPointQuality.MANUAL for item in observations
        ),
        gap_count=gap_count,
        coverage_ratio=len(observations) / expected_points if expected_points else 0,
        mean_projection_error_m=(
            float(np.mean([item.projection_error_estimate_m for item in observations]))
            if observations
            else 0
        ),
        calibration_id=source.calibration_id,
    )


def _individual(
    track: WorldTrack,
    profile: AnalysisProfile,
    scene: SceneProfile,
) -> IndividualMetric:
    ordered = sorted(track.observations, key=lambda item: item.timestamp)
    duration = _duration(track)
    if len(ordered) < 2:
        return IndividualMetric(
            track_id=track.track_id,
            semantic_class=track.semantic_class,
            duration_s=duration,
            path_length_m=0,
            displacement_m=0,
            tortuosity=1,
            mean_speed_mps=0,
            max_speed_mps=0,
            mean_acceleration_mps2=0,
            stop_duration_s=duration,
            stop_event_count=1 if duration >= profile.stop_minimum_duration_seconds else 0,
            zone_dwell_seconds=_zone_dwell(ordered, scene, profile),
            total_turning_radians=0,
        )
    positions = np.asarray([[item.point.x, item.point.y] for item in ordered], dtype=float)
    timestamps = np.asarray([item.timestamp for item in ordered], dtype=float)
    deltas = np.diff(positions, axis=0)
    distances = np.linalg.norm(deltas, axis=1)
    dt = np.diff(timestamps)
    valid = dt > 0
    speeds = np.divide(distances[valid], dt[valid])
    speed_timestamps = ((timestamps[:-1] + timestamps[1:]) / 2)[valid]
    path_length = float(distances.sum())
    displacement = float(np.linalg.norm(positions[-1] - positions[0]))
    tortuosity = path_length / displacement if displacement > 1e-12 else 1.0
    acceleration_dt = np.diff(speed_timestamps)
    acceleration_valid = acceleration_dt > 0
    accelerations = (
        np.divide(np.diff(speeds)[acceleration_valid], acceleration_dt[acceleration_valid])
        if speeds.size > 1
        else np.array([])
    )
    stop_duration = float(dt[valid][speeds <= profile.stop_speed_metres_per_second].sum())
    stopped = speeds <= profile.stop_speed_metres_per_second
    turning = _total_turning(deltas)
    return IndividualMetric(
        track_id=track.track_id,
        semantic_class=track.semantic_class,
        duration_s=duration,
        path_length_m=path_length,
        displacement_m=displacement,
        tortuosity=max(1.0, tortuosity),
        mean_speed_mps=float(speeds.mean()) if speeds.size else 0,
        max_speed_mps=float(speeds.max()) if speeds.size else 0,
        mean_acceleration_mps2=float(accelerations.mean()) if accelerations.size else 0,
        stop_duration_s=stop_duration,
        stop_event_count=_count_stop_events(
            stopped,
            dt[valid],
            profile.stop_minimum_duration_seconds,
        ),
        zone_dwell_seconds=_zone_dwell(ordered, scene, profile),
        total_turning_radians=turning,
    )


def _flows(source: ProcessedWorldTrackSet, scene: SceneProfile) -> tuple[FlowMetric, ...]:
    counts: Counter[tuple[str, SemanticClass, str]] = Counter()
    for track in source.tracks:
        ordered = sorted(track.observations, key=lambda item: item.timestamp)
        for first, second in zip(ordered, ordered[1:], strict=False):
            movement = ((first.point.x, first.point.y), (second.point.x, second.point.y))
            for line_id, line in scene.counting_lines.items():
                if _segments_intersect(movement[0], movement[1], line[0], line[1]):
                    side_first = _side_of_line(movement[0], line)
                    side_second = _side_of_line(movement[1], line)
                    direction = "positive" if side_first < side_second else "negative"
                    counts[(line_id, track.semantic_class, direction)] += 1
    duration = max(source.video.duration, 1e-12)
    result = []
    for (line_id, semantic_class, direction), count in sorted(
        counts.items(), key=lambda item: (item[0][0], item[0][1].value, item[0][2])
    ):
        line = scene.counting_lines[line_id]
        width = math.dist(line[0], line[1])
        rate = count / duration
        result.append(
            FlowMetric(
                line_id=line_id,
                semantic_class=semantic_class,
                direction=direction,
                count=count,
                rate_per_second=rate,
                specific_flow_per_m_s=rate / width if width > 0 else 0,
            )
        )
    return tuple(result)


def _spatial(
    source: ProcessedWorldTrackSet,
    scene: SceneProfile,
    profile: AnalysisProfile,
) -> SpatialAnalysis:
    area = _polygon_area(scene.roi)
    bins: dict[int, set[int]] = defaultdict(set)
    positions_by_bin: dict[int, list[tuple[int, tuple[float, float]]]] = defaultdict(list)
    heatmap: Counter[tuple[int, int]] = Counter()
    all_points: list[tuple[float, float]] = []
    for track in source.tracks:
        for item in track.observations:
            point = (item.point.x, item.point.y)
            if _point_in_polygon(point, scene.roi):
                bin_index = int(item.timestamp // profile.time_window_seconds)
                bins[bin_index].add(track.track_id)
                positions_by_bin[bin_index].append((track.track_id, point))
                all_points.append(point)
                heatmap[
                    (
                        math.floor(item.point.x / profile.spatial_grid_metres),
                        math.floor(item.point.y / profile.spatial_grid_metres),
                    )
                ] += 1
    max_bin = max(bins, default=-1)
    density = tuple(
        DensityPoint(
            time_bin=index,
            timestamp_s=index * profile.time_window_seconds,
            count=len(bins.get(index, set())),
            density_per_m2=len(bins.get(index, set())) / area if area else 0,
        )
        for index in range(max_bin + 1)
    )
    cells = tuple(
        HeatmapCell(
            x_index=x,
            y_index=y,
            count=count,
            kde_intensity=_kde_intensity(
                (
                    (x + 0.5) * profile.spatial_grid_metres,
                    (y + 0.5) * profile.spatial_grid_metres,
                ),
                all_points,
                profile.kde_bandwidth_metres,
            ),
        )
        for (x, y), count in sorted(heatmap.items())
    )
    voronoi = tuple(
        _voronoi_point(
            index,
            positions_by_bin.get(index, []),
            scene.roi,
            profile.time_window_seconds,
        )
        for index in range(max_bin + 1)
    )
    vector_field, speed_profile = _spatial_velocity_fields(source, profile)
    fundamental = _fundamental_diagram(source, density, profile)
    standard_method = "classic_kde_vector"
    voronoi_method = "bounded_half_plane"
    pedpy_metrics = try_compute_pedpy_spatial(source, scene, profile)
    if pedpy_metrics is not None:
        density = pedpy_metrics.classic_density
        vector_field = pedpy_metrics.vector_field
        speed_profile = pedpy_metrics.speed_profile
        fundamental = pedpy_metrics.fundamental_diagram
        standard_method = "pedpy_classic_speed"
        if pedpy_metrics.voronoi_density is not None:
            voronoi = pedpy_metrics.voronoi_density
            voronoi_method = "pedpy"
    return SpatialAnalysis(
        classic_density=density,
        voronoi_density=voronoi,
        heatmap=cells,
        vector_field=vector_field,
        speed_profile=speed_profile,
        fundamental_diagram=fundamental,
        grid_size_m=profile.spatial_grid_metres,
        method=standard_method,
        voronoi_method=voronoi_method,
    )


def _od(source: ProcessedWorldTrackSet, scene: SceneProfile) -> tuple[ODRecord, ...]:
    counts: Counter[tuple[str, str, SemanticClass]] = Counter()
    for track in source.tracks:
        if len(track.observations) < 2:
            continue
        ordered = sorted(track.observations, key=lambda item: item.timestamp)
        origin = _containing_region(ordered[0], scene.entrances)
        destination = _containing_region(ordered[-1], scene.entrances)
        if origin and destination and origin != destination:
            counts[(origin, destination, track.semantic_class)] += 1
    return tuple(
        ODRecord(origin=origin, destination=destination, semantic_class=semantic_class, count=count)
        for (origin, destination, semantic_class), count in sorted(
            counts.items(), key=lambda item: (item[0][0], item[0][1], item[0][2].value)
        )
    )


def _interactions(
    source: ProcessedWorldTrackSet,
    profile: AnalysisProfile,
) -> tuple[InteractionEvent, ...]:
    events = []
    for first, second in combinations(source.tracks, 2):
        first_by_frame = {item.frame_index: item for item in first.observations}
        second_by_frame = {item.frame_index: item for item in second.observations}
        shared_frames = sorted(set(first_by_frame) & set(second_by_frame))
        if not shared_frames:
            continue
        distances = [
            math.dist(
                (first_by_frame[frame].point.x, first_by_frame[frame].point.y),
                (second_by_frame[frame].point.x, second_by_frame[frame].point.y),
            )
            for frame in shared_frames
        ]
        minimum_index = int(np.argmin(distances))
        minimum_frame = shared_frames[minimum_index]
        minimum_distance = distances[minimum_index]
        if minimum_distance > profile.interaction_radius_metres:
            continue
        velocity_a = _velocity_at_frame(first, minimum_frame)
        velocity_b = _velocity_at_frame(second, minimum_frame)
        relative_speed = float(np.linalg.norm(velocity_b - velocity_a))
        ttc = _minimum_ttc(first, second, profile.ttc_horizon_seconds)
        pet = _pet(first, second)
        angle = _angle_degrees(velocity_a, velocity_b)
        interaction_type = _interaction_type(angle, velocity_a, velocity_b)
        point_a = first_by_frame[minimum_frame]
        point_b = second_by_frame[minimum_frame]
        event_digest = sha256(
            f"{source.artifact_id}:{first.track_id}:{second.track_id}".encode()
        ).hexdigest()[:12]
        events.append(
            InteractionEvent(
                event_id=f"interaction-{event_digest}",
                track_a_id=first.track_id,
                track_b_id=second.track_id,
                class_a=first.semantic_class,
                class_b=second.semantic_class,
                minimum_distance_m=minimum_distance,
                relative_speed_mps=relative_speed,
                ttc_seconds=ttc,
                pet_seconds=pet,
                encounter_angle_degrees=angle,
                interaction_type=interaction_type,
                x=(point_a.point.x + point_b.point.x) / 2,
                y=(point_a.point.y + point_b.point.y) / 2,
                timestamp_s=(point_a.timestamp + point_b.timestamp) / 2,
            )
        )
    return tuple(events)


def _duration(track: WorldTrack) -> float:
    if len(track.observations) < 2:
        return 0.0
    timestamps = [item.timestamp for item in track.observations]
    return max(timestamps) - min(timestamps)


def _zone_dwell(
    observations: list[WorldTrackObservation],
    scene: SceneProfile,
    profile: AnalysisProfile,
) -> dict[str, float]:
    dwell = {name: 0.0 for name in scene.zones}
    for item in observations:
        point = (item.point.x, item.point.y)
        for name, polygon in scene.zones.items():
            if _point_in_polygon(point, polygon):
                dwell[name] += profile.time_window_seconds
    return dwell


def _count_stop_events(
    stopped: np.ndarray,
    durations: np.ndarray,
    minimum_duration: float,
) -> int:
    count = 0
    accumulated = 0.0
    for is_stopped, duration in zip(stopped, durations, strict=True):
        if is_stopped:
            accumulated += float(duration)
        else:
            if accumulated >= minimum_duration:
                count += 1
            accumulated = 0.0
    if accumulated >= minimum_duration:
        count += 1
    return count


def _kde_intensity(
    cell_center: tuple[float, float],
    points: list[tuple[float, float]],
    bandwidth: float,
) -> float:
    if not points:
        return 0.0
    squared = np.sum((np.asarray(points) - np.asarray(cell_center)) ** 2, axis=1)
    normalization = 2 * math.pi * bandwidth**2
    return float(np.exp(-squared / (2 * bandwidth**2)).sum() / normalization)


def _voronoi_point(
    time_bin: int,
    positioned_tracks: list[tuple[int, tuple[float, float]]],
    roi: tuple[tuple[float, float], ...],
    window_seconds: float,
) -> VoronoiDensityPoint:
    multiplicities = Counter(point for _, point in positioned_tracks)
    local_density: list[float] = []
    for point, multiplicity in multiplicities.items():
        cell = list(roi)
        point_array = np.asarray(point, dtype=float)
        for other in multiplicities:
            if other == point:
                continue
            other_array = np.asarray(other, dtype=float)
            normal = other_array - point_array
            offset = (float(other_array @ other_array) - float(point_array @ point_array)) / 2
            cell = _clip_polygon_half_plane(cell, normal, offset)
            if not cell:
                break
        area = _polygon_area(tuple(cell)) if len(cell) >= 3 else 0.0
        density = multiplicity / area if area > 1e-12 else 0.0
        local_density.extend([density] * multiplicity)
    return VoronoiDensityPoint(
        time_bin=time_bin,
        timestamp_s=time_bin * window_seconds,
        count=len(positioned_tracks),
        mean_local_density_per_m2=float(np.mean(local_density)) if local_density else 0,
        max_local_density_per_m2=max(local_density, default=0),
    )


def _clip_polygon_half_plane(
    polygon: list[tuple[float, float]],
    normal: np.ndarray,
    offset: float,
) -> list[tuple[float, float]]:
    if not polygon:
        return []
    result: list[tuple[float, float]] = []
    previous = np.asarray(polygon[-1], dtype=float)
    previous_value = float(normal @ previous - offset)
    for raw_current in polygon:
        current = np.asarray(raw_current, dtype=float)
        current_value = float(normal @ current - offset)
        previous_inside = previous_value <= 1e-12
        current_inside = current_value <= 1e-12
        if current_inside != previous_inside:
            denominator = previous_value - current_value
            ratio = previous_value / denominator if abs(denominator) > 1e-12 else 0.0
            intersection = previous + ratio * (current - previous)
            result.append((float(intersection[0]), float(intersection[1])))
        if current_inside:
            result.append((float(current[0]), float(current[1])))
        previous = current
        previous_value = current_value
    return result


def _spatial_velocity_fields(
    source: ProcessedWorldTrackSet,
    profile: AnalysisProfile,
) -> tuple[tuple[VectorFieldCell, ...], tuple[SpeedProfileCell, ...]]:
    velocities: dict[tuple[int, int], list[tuple[float, float]]] = defaultdict(list)
    for track in source.tracks:
        ordered = sorted(track.observations, key=lambda item: item.timestamp)
        for first, second in zip(ordered, ordered[1:], strict=False):
            dt = second.timestamp - first.timestamp
            if dt <= 0:
                continue
            midpoint = (
                (first.point.x + second.point.x) / 2,
                (first.point.y + second.point.y) / 2,
            )
            cell = (
                math.floor(midpoint[0] / profile.spatial_grid_metres),
                math.floor(midpoint[1] / profile.spatial_grid_metres),
            )
            velocities[cell].append(
                (
                    (second.point.x - first.point.x) / dt,
                    (second.point.y - first.point.y) / dt,
                )
            )
    vectors = []
    speeds = []
    for (x_index, y_index), values in sorted(velocities.items()):
        array = np.asarray(values, dtype=float)
        mean_velocity = array.mean(axis=0)
        mean_speed = float(np.linalg.norm(array, axis=1).mean())
        vectors.append(
            VectorFieldCell(
                x_index=x_index,
                y_index=y_index,
                count=len(values),
                mean_vx_mps=float(mean_velocity[0]),
                mean_vy_mps=float(mean_velocity[1]),
                mean_speed_mps=mean_speed,
            )
        )
        speeds.append(
            SpeedProfileCell(
                x_index=x_index,
                y_index=y_index,
                count=len(values),
                mean_speed_mps=mean_speed,
            )
        )
    return tuple(vectors), tuple(speeds)


def _fundamental_diagram(
    source: ProcessedWorldTrackSet,
    density: tuple[DensityPoint, ...],
    profile: AnalysisProfile,
) -> tuple[FundamentalDiagramPoint, ...]:
    result = []
    for density_point in density:
        speeds = []
        for track in source.tracks:
            for item in track.observations:
                if int(item.timestamp // profile.time_window_seconds) == density_point.time_bin:
                    speeds.append(
                        float(np.linalg.norm(_velocity_at_frame(track, item.frame_index)))
                    )
        mean_speed = float(np.mean(speeds)) if speeds else 0.0
        result.append(
            FundamentalDiagramPoint(
                time_bin=density_point.time_bin,
                timestamp_s=density_point.timestamp_s,
                density_per_m2=density_point.density_per_m2,
                mean_speed_mps=mean_speed,
                specific_flow_per_m_s=density_point.density_per_m2 * mean_speed,
            )
        )
    return tuple(result)


def _total_turning(deltas: np.ndarray) -> float:
    if len(deltas) < 2:
        return 0.0
    angles = np.arctan2(deltas[:, 1], deltas[:, 0])
    differences = np.diff(np.unwrap(angles))
    return float(np.abs(differences).sum())


def _velocity_at_frame(track: WorldTrack, frame: int) -> np.ndarray:
    ordered = sorted(track.observations, key=lambda item: item.frame_index)
    index = next(i for i, item in enumerate(ordered) if item.frame_index == frame)
    if index < len(ordered) - 1:
        first, second = ordered[index], ordered[index + 1]
    elif index > 0:
        first, second = ordered[index - 1], ordered[index]
    else:
        return np.zeros(2)
    dt = second.timestamp - first.timestamp
    if dt <= 0:
        return np.zeros(2)
    return np.array(
        [(second.point.x - first.point.x) / dt, (second.point.y - first.point.y) / dt]
    )


def _minimum_ttc(first: WorldTrack, second: WorldTrack, horizon: float) -> float | None:
    first_by_frame = {item.frame_index: item for item in first.observations}
    second_by_frame = {item.frame_index: item for item in second.observations}
    values = []
    for frame in sorted(set(first_by_frame) & set(second_by_frame)):
        point_a = first_by_frame[frame]
        point_b = second_by_frame[frame]
        relative_position = np.array(
            [point_b.point.x - point_a.point.x, point_b.point.y - point_a.point.y]
        )
        relative_velocity = _velocity_at_frame(second, frame) - _velocity_at_frame(first, frame)
        denominator = float(relative_velocity @ relative_velocity)
        if denominator <= 1e-12:
            continue
        value = -float(relative_position @ relative_velocity) / denominator
        if 0 < value <= horizon:
            values.append(value)
    return min(values) if values else None


def _pet(first: WorldTrack, second: WorldTrack) -> float | None:
    values = []
    first_ordered = sorted(first.observations, key=lambda item: item.timestamp)
    second_ordered = sorted(second.observations, key=lambda item: item.timestamp)
    for first_a, first_b in zip(first_ordered, first_ordered[1:], strict=False):
        for second_a, second_b in zip(second_ordered, second_ordered[1:], strict=False):
            intersection = _segment_intersection_point(
                (first_a.point.x, first_a.point.y),
                (first_b.point.x, first_b.point.y),
                (second_a.point.x, second_a.point.y),
                (second_b.point.x, second_b.point.y),
            )
            if intersection is None:
                continue
            first_time = _time_at_point(first_a, first_b, intersection)
            second_time = _time_at_point(second_a, second_b, intersection)
            values.append(abs(first_time - second_time))
    return min(values) if values else None


def _time_at_point(
    first: WorldTrackObservation,
    second: WorldTrackObservation,
    point: tuple[float, float],
) -> float:
    segment_length = math.dist((first.point.x, first.point.y), (second.point.x, second.point.y))
    if segment_length <= 1e-12:
        return first.timestamp
    ratio = math.dist((first.point.x, first.point.y), point) / segment_length
    return first.timestamp + ratio * (second.timestamp - first.timestamp)


def _angle_degrees(first: np.ndarray, second: np.ndarray) -> float:
    norms = float(np.linalg.norm(first) * np.linalg.norm(second))
    if norms <= 1e-12:
        return 0.0
    cosine = float(np.clip((first @ second) / norms, -1.0, 1.0))
    return math.degrees(math.acos(cosine))


def _interaction_type(angle: float, first: np.ndarray, second: np.ndarray) -> str:
    if angle >= 135:
        return "opposing"
    if angle <= 30:
        return "overtaking" if np.linalg.norm(first - second) > 0.2 else "following"
    return "crossing"


def _containing_region(
    observation: WorldTrackObservation,
    regions: dict[str, tuple[tuple[float, float], ...]],
) -> str | None:
    point = (observation.point.x, observation.point.y)
    return next(
        (name for name, polygon in regions.items() if _point_in_polygon(point, polygon)),
        None,
    )


def _polygon_area(polygon: tuple[tuple[float, float], ...]) -> float:
    return abs(
        sum(
            first[0] * second[1] - second[0] * first[1]
            for first, second in zip(polygon, polygon[1:] + polygon[:1], strict=True)
        )
    ) / 2.0


def _point_in_polygon(point: tuple[float, float], polygon: tuple[tuple[float, float], ...]) -> bool:
    x, y = point
    inside = False
    previous = polygon[-1]
    for current in polygon:
        x1, y1 = previous
        x2, y2 = current
        if _point_on_segment(point, previous, current):
            return True
        intersects = (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1
        if intersects:
            inside = not inside
        previous = current
    return inside


def _side_of_line(
    point: tuple[float, float],
    line: tuple[tuple[float, float], tuple[float, float]],
) -> float:
    (x1, y1), (x2, y2) = line
    return (x2 - x1) * (point[1] - y1) - (y2 - y1) * (point[0] - x1)


def _segments_intersect(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
    d: tuple[float, float],
) -> bool:
    return _segment_intersection_point(a, b, c, d) is not None


def _segment_intersection_point(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
    d: tuple[float, float],
) -> tuple[float, float] | None:
    r = np.array([b[0] - a[0], b[1] - a[1]], dtype=float)
    s = np.array([d[0] - c[0], d[1] - c[1]], dtype=float)
    denominator = _cross_2d(r, s)
    if abs(denominator) < 1e-12:
        return None
    delta = np.array([c[0] - a[0], c[1] - a[1]], dtype=float)
    t = _cross_2d(delta, s) / denominator
    u = _cross_2d(delta, r) / denominator
    if -1e-12 <= t <= 1 + 1e-12 and -1e-12 <= u <= 1 + 1e-12:
        return (a[0] + t * r[0], a[1] + t * r[1])
    return None


def _cross_2d(first: np.ndarray, second: np.ndarray) -> float:
    return float(first[0] * second[1] - first[1] * second[0])


def _point_on_segment(
    point: tuple[float, float],
    first: tuple[float, float],
    second: tuple[float, float],
) -> bool:
    cross = (point[1] - first[1]) * (second[0] - first[0]) - (
        point[0] - first[0]
    ) * (second[1] - first[1])
    if abs(cross) > 1e-9:
        return False
    return (
        min(first[0], second[0]) - 1e-9 <= point[0] <= max(first[0], second[0]) + 1e-9
        and min(first[1], second[1]) - 1e-9
        <= point[1]
        <= max(first[1], second[1]) + 1e-9
    )


__all__ = ["AnalysisProfile", "analyze_world_tracks"]
