from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ped_video_analysis.analysis.vision_schemas import AnalysisBundle, FigureArtifact
from ped_video_analysis.vision.contracts import ProcessedWorldTrackSet


def render_analysis_figures(
    bundle: AnalysisBundle,
    source: ProcessedWorldTrackSet,
    output_dir: Path,
) -> tuple[FigureArtifact, ...]:
    output_dir.mkdir(parents=True, exist_ok=True)
    definitions: tuple[tuple[str, str, Callable], ...] = (
        ("trajectories", "World trajectories", _plot_trajectories),
        ("speed_distribution", "Track mean-speed distribution", _plot_speed_distribution),
        ("density_time_series", "Classic density time series", _plot_density),
        ("flow_counts", "Directional counting-line flow", _plot_flow_counts),
        ("kde_heatmap", "Spatial KDE intensity", _plot_kde_heatmap),
        ("vector_field", "Mean velocity vector field", _plot_vector_field),
        ("fundamental_diagram", "Density-speed fundamental diagram", _plot_fundamental),
        ("od_matrix", "Origin-destination counts", _plot_od),
        ("interaction_hotspots", "Interaction proxy hotspots", _plot_interactions),
    )
    return tuple(
        _render_one(figure_id, title, plotter, bundle, source, output_dir)
        for figure_id, title, plotter in definitions
    )


def _render_one(
    figure_id: str,
    title: str,
    plotter: Callable,
    bundle: AnalysisBundle,
    source: ProcessedWorldTrackSet,
    output_dir: Path,
) -> FigureArtifact:
    base = output_dir / figure_id
    fig, ax = plt.subplots(figsize=(7.2, 4.8), constrained_layout=True)
    plotly_data = plotter(ax, bundle, source)
    ax.set_title(title)
    ax.grid(alpha=0.18)
    svg_path = base.with_suffix(".svg")
    pdf_path = base.with_suffix(".pdf")
    png_path = base.with_suffix(".png")
    fig.savefig(svg_path)
    fig.savefig(pdf_path)
    fig.savefig(png_path, dpi=300)
    plt.close(fig)

    plotly_path = base.with_suffix(".plotly.json")
    plotly_path.write_text(
        json.dumps(
            {"data": plotly_data, "layout": {"title": title}},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    manifest_path = base.with_suffix(".manifest.json")
    manifest_path.write_text(
        json.dumps(
            {
                "figure_id": figure_id,
                "title": title,
                "task_id": bundle.task_id,
                "analysis_id": bundle.analysis_id,
                "source_artifact_id": bundle.source_artifact_id,
                "scene_id": bundle.scene_id,
                "scene_version": bundle.scene_version,
                "calibration_id": bundle.provenance["calibration_id"],
                "sample_tracks": bundle.quality.track_count,
                "units": {"position": "m", "speed": "m/s", "density": "1/m^2"},
                "profile": bundle.profile,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return FigureArtifact(
        figure_id=figure_id,
        title=title,
        plotly_json_path=str(plotly_path),
        svg_path=str(svg_path),
        pdf_path=str(pdf_path),
        png_path=str(png_path),
        manifest_path=str(manifest_path),
    )


def _plot_trajectories(ax, bundle: AnalysisBundle, source: ProcessedWorldTrackSet) -> list[dict]:
    traces = []
    for track in source.tracks:
        x = [item.point.x for item in track.observations]
        y = [item.point.y for item in track.observations]
        ax.plot(x, y, marker=".", label=f"{track.semantic_class.value}:{track.track_id}")
        traces.append(
            {
                "type": "scatter",
                "mode": "lines+markers",
                "name": f"{track.semantic_class.value}:{track.track_id}",
                "x": x,
                "y": y,
            }
        )
    if source.tracks:
        ax.legend(fontsize=7)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_aspect("equal", adjustable="datalim")
    return traces


def _plot_speed_distribution(
    ax, bundle: AnalysisBundle, source: ProcessedWorldTrackSet
) -> list[dict]:
    values = [item.mean_speed_mps for item in bundle.individual]
    ax.hist(values, bins=min(10, max(1, len(values))))
    ax.set_xlabel("mean speed (m/s)")
    ax.set_ylabel("tracks")
    return [{"type": "histogram", "x": values, "name": "mean speed"}]


def _plot_density(ax, bundle: AnalysisBundle, source: ProcessedWorldTrackSet) -> list[dict]:
    x = [item.timestamp_s for item in bundle.spatial.classic_density]
    y = [item.density_per_m2 for item in bundle.spatial.classic_density]
    ax.plot(x, y, marker="o")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("density (1/m²)")
    return [{"type": "scatter", "mode": "lines+markers", "x": x, "y": y}]


def _plot_flow_counts(ax, bundle: AnalysisBundle, source: ProcessedWorldTrackSet) -> list[dict]:
    labels = [
        f"{item.line_id}:{item.direction}:{item.semantic_class.value}" for item in bundle.flows
    ]
    values = [item.count for item in bundle.flows]
    ax.bar(labels, values)
    ax.tick_params(axis="x", rotation=25)
    ax.set_ylabel("crossings")
    return [{"type": "bar", "x": labels, "y": values}]


def _plot_kde_heatmap(ax, bundle: AnalysisBundle, source: ProcessedWorldTrackSet) -> list[dict]:
    grid = bundle.spatial.grid_size_m
    x = [(item.x_index + 0.5) * grid for item in bundle.spatial.heatmap]
    y = [(item.y_index + 0.5) * grid for item in bundle.spatial.heatmap]
    intensity = [item.kde_intensity for item in bundle.spatial.heatmap]
    plotted = ax.scatter(x, y, c=intensity, cmap="viridis")
    if intensity:
        ax.figure.colorbar(plotted, ax=ax, label="KDE intensity (1/m²)")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    return [
        {
            "type": "scatter",
            "mode": "markers",
            "x": x,
            "y": y,
            "marker": {"color": intensity, "colorscale": "Viridis", "showscale": True},
        }
    ]


def _plot_vector_field(ax, bundle: AnalysisBundle, source: ProcessedWorldTrackSet) -> list[dict]:
    grid = bundle.spatial.grid_size_m
    x = [(item.x_index + 0.5) * grid for item in bundle.spatial.vector_field]
    y = [(item.y_index + 0.5) * grid for item in bundle.spatial.vector_field]
    u = [item.mean_vx_mps for item in bundle.spatial.vector_field]
    v = [item.mean_vy_mps for item in bundle.spatial.vector_field]
    ax.quiver(x, y, u, v, angles="xy", scale_units="xy", scale=1)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    return [
        {
            "type": "scatter",
            "mode": "markers",
            "x": x,
            "y": y,
            "customdata": [
                {"mean_vx_mps": vx, "mean_vy_mps": vy} for vx, vy in zip(u, v, strict=True)
            ],
        }
    ]


def _plot_fundamental(ax, bundle: AnalysisBundle, source: ProcessedWorldTrackSet) -> list[dict]:
    x = [item.density_per_m2 for item in bundle.spatial.fundamental_diagram]
    y = [item.mean_speed_mps for item in bundle.spatial.fundamental_diagram]
    flow = [item.specific_flow_per_m_s for item in bundle.spatial.fundamental_diagram]
    ax.scatter(x, y, c=flow, cmap="plasma")
    ax.set_xlabel("density (1/m²)")
    ax.set_ylabel("mean speed (m/s)")
    return [
        {
            "type": "scatter",
            "mode": "markers",
            "x": x,
            "y": y,
            "marker": {"color": flow, "colorscale": "Plasma", "showscale": True},
        }
    ]


def _plot_od(ax, bundle: AnalysisBundle, source: ProcessedWorldTrackSet) -> list[dict]:
    labels = [f"{item.origin}→{item.destination}" for item in bundle.od]
    values = [item.count for item in bundle.od]
    ax.bar(labels, values)
    ax.tick_params(axis="x", rotation=25)
    ax.set_ylabel("trips")
    return [{"type": "bar", "x": labels, "y": values}]


def _plot_interactions(ax, bundle: AnalysisBundle, source: ProcessedWorldTrackSet) -> list[dict]:
    x = [item.x for item in bundle.interactions]
    y = [item.y for item in bundle.interactions]
    sizes = [max(24.0, 120.0 / (1.0 + item.minimum_distance_m)) for item in bundle.interactions]
    ax.scatter(x, y, s=sizes, alpha=0.65)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    return [
        {
            "type": "scatter",
            "mode": "markers",
            "x": x,
            "y": y,
            "marker": {"size": sizes},
            "customdata": [
                {
                    "minimum_distance_m": item.minimum_distance_m,
                    "ttc_seconds": item.ttc_seconds,
                    "pet_seconds": item.pet_seconds,
                }
                for item in bundle.interactions
            ],
        }
    ]


__all__ = ["render_analysis_figures"]
