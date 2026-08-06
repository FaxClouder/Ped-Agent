from __future__ import annotations

from typing import Literal

from pydantic import Field

from ped_agent.vision.contracts import FrozenModel, SemanticClass


class QualitySummary(FrozenModel):
    track_count: int = Field(ge=0)
    point_count: int = Field(ge=0)
    short_track_count: int = Field(ge=0)
    fallback_point_count: int = Field(ge=0)
    interpolated_point_count: int = Field(ge=0)
    outlier_candidate_count: int = Field(ge=0)
    degraded_point_count: int = Field(ge=0)
    manual_revision_point_count: int = Field(ge=0)
    gap_count: int = Field(ge=0)
    coverage_ratio: float = Field(ge=0, le=1)
    mean_projection_error_m: float = Field(ge=0)
    calibration_id: str


class IndividualMetric(FrozenModel):
    track_id: int
    semantic_class: SemanticClass
    duration_s: float = Field(ge=0)
    path_length_m: float = Field(ge=0)
    displacement_m: float = Field(ge=0)
    tortuosity: float = Field(ge=1)
    mean_speed_mps: float = Field(ge=0)
    max_speed_mps: float = Field(ge=0)
    mean_acceleration_mps2: float
    stop_duration_s: float = Field(ge=0)
    stop_event_count: int = Field(ge=0)
    zone_dwell_seconds: dict[str, float]
    total_turning_radians: float = Field(ge=0)


class FlowMetric(FrozenModel):
    line_id: str
    semantic_class: SemanticClass
    direction: Literal["positive", "negative"]
    count: int = Field(ge=0)
    rate_per_second: float = Field(ge=0)
    specific_flow_per_m_s: float = Field(ge=0)


class DensityPoint(FrozenModel):
    time_bin: int = Field(ge=0)
    timestamp_s: float = Field(ge=0)
    count: int = Field(ge=0)
    density_per_m2: float = Field(ge=0)


class HeatmapCell(FrozenModel):
    x_index: int
    y_index: int
    count: int = Field(ge=0)
    kde_intensity: float = Field(default=0, ge=0)


class VoronoiDensityPoint(FrozenModel):
    time_bin: int = Field(ge=0)
    timestamp_s: float = Field(ge=0)
    count: int = Field(ge=0)
    mean_local_density_per_m2: float = Field(ge=0)
    max_local_density_per_m2: float = Field(ge=0)


class VectorFieldCell(FrozenModel):
    x_index: int
    y_index: int
    count: int = Field(ge=1)
    mean_vx_mps: float
    mean_vy_mps: float
    mean_speed_mps: float = Field(ge=0)


class SpeedProfileCell(FrozenModel):
    x_index: int
    y_index: int
    count: int = Field(ge=1)
    mean_speed_mps: float = Field(ge=0)


class FundamentalDiagramPoint(FrozenModel):
    time_bin: int = Field(ge=0)
    timestamp_s: float = Field(ge=0)
    density_per_m2: float = Field(ge=0)
    mean_speed_mps: float = Field(ge=0)
    specific_flow_per_m_s: float = Field(ge=0)


class SpatialAnalysis(FrozenModel):
    classic_density: tuple[DensityPoint, ...]
    voronoi_density: tuple[VoronoiDensityPoint, ...]
    heatmap: tuple[HeatmapCell, ...]
    vector_field: tuple[VectorFieldCell, ...]
    speed_profile: tuple[SpeedProfileCell, ...]
    fundamental_diagram: tuple[FundamentalDiagramPoint, ...]
    grid_size_m: float = Field(gt=0)
    method: str = "classic_kde_vector"
    voronoi_method: str = "bounded_half_plane"


class ODRecord(FrozenModel):
    origin: str
    destination: str
    semantic_class: SemanticClass
    count: int = Field(ge=1)


class InteractionEvent(FrozenModel):
    event_id: str
    track_a_id: int
    track_b_id: int
    class_a: SemanticClass
    class_b: SemanticClass
    minimum_distance_m: float = Field(ge=0)
    relative_speed_mps: float = Field(ge=0)
    ttc_seconds: float | None = Field(default=None, ge=0)
    pet_seconds: float | None = Field(default=None, ge=0)
    encounter_angle_degrees: float = Field(ge=0, le=180)
    interaction_type: Literal["following", "overtaking", "opposing", "crossing"]
    x: float
    y: float
    timestamp_s: float = Field(ge=0)
    safety_conclusion: None = None


class FigureArtifact(FrozenModel):
    figure_id: str
    title: str
    plotly_json_path: str
    svg_path: str
    pdf_path: str
    png_path: str
    manifest_path: str


class AnalysisBundle(FrozenModel):
    analysis_id: str
    task_id: str
    source_artifact_id: str
    scene_id: str
    scene_version: int
    quality: QualitySummary
    individual: tuple[IndividualMetric, ...]
    flows: tuple[FlowMetric, ...]
    spatial: SpatialAnalysis
    od: tuple[ODRecord, ...]
    interactions: tuple[InteractionEvent, ...]
    profile: dict[str, float | int]
    provenance: dict[str, str]


__all__ = [
    "AnalysisBundle",
    "DensityPoint",
    "FigureArtifact",
    "FlowMetric",
    "FundamentalDiagramPoint",
    "HeatmapCell",
    "IndividualMetric",
    "InteractionEvent",
    "ODRecord",
    "QualitySummary",
    "SpeedProfileCell",
    "SpatialAnalysis",
    "VectorFieldCell",
    "VoronoiDensityPoint",
]
