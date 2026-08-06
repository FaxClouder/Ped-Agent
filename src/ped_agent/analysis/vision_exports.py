from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pandas as pd
from pydantic import Field

from ped_agent.analysis.vision_schemas import AnalysisBundle, FigureArtifact
from ped_agent.vision.artifacts import WorldTrackParquetStore
from ped_agent.vision.contracts import FrozenModel, ProcessedWorldTrackSet


class ExportFile(FrozenModel):
    path: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    size: int = Field(ge=0)


class ExportManifest(FrozenModel):
    task_id: str
    analysis_id: str
    files: tuple[ExportFile, ...]


def export_analysis_bundle(
    *,
    bundle: AnalysisBundle,
    tracks: ProcessedWorldTrackSet,
    figures: tuple[FigureArtifact, ...],
    output_dir: Path,
) -> ExportManifest:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"immutable export directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    analysis_path = output_dir / "analysis.json"
    analysis_path.write_text(bundle.model_dump_json(indent=2), encoding="utf-8")
    provenance_path = output_dir / "provenance.json"
    provenance_path.write_text(
        json.dumps(
            {
                "task_id": bundle.task_id,
                "analysis_id": bundle.analysis_id,
                "source_artifact_id": bundle.source_artifact_id,
                "scene_id": bundle.scene_id,
                "scene_version": bundle.scene_version,
                "sample_tracks": bundle.quality.track_count,
                "profile": bundle.profile,
                "provenance": bundle.provenance,
                "units": {
                    "position": "m",
                    "speed": "m/s",
                    "acceleration": "m/s^2",
                    "density": "1/m^2",
                    "flow": "1/s",
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    tables = {
        "quality.csv": [bundle.quality.model_dump(mode="json")],
        "individual.csv": [item.model_dump(mode="json") for item in bundle.individual],
        "flows.csv": [item.model_dump(mode="json") for item in bundle.flows],
        "density.csv": [
            item.model_dump(mode="json") for item in bundle.spatial.classic_density
        ],
        "voronoi-density.csv": [
            item.model_dump(mode="json") for item in bundle.spatial.voronoi_density
        ],
        "heatmap.csv": [item.model_dump(mode="json") for item in bundle.spatial.heatmap],
        "vector-field.csv": [
            item.model_dump(mode="json") for item in bundle.spatial.vector_field
        ],
        "speed-profile.csv": [
            item.model_dump(mode="json") for item in bundle.spatial.speed_profile
        ],
        "fundamental-diagram.csv": [
            item.model_dump(mode="json")
            for item in bundle.spatial.fundamental_diagram
        ],
        "od.csv": [item.model_dump(mode="json") for item in bundle.od],
        "interactions.csv": [
            item.model_dump(mode="json") for item in bundle.interactions
        ],
    }
    for name, rows in tables.items():
        pd.DataFrame(rows).to_csv(output_dir / name, index=False)

    WorldTrackParquetStore(output_dir / "tracks").write(tracks)
    figures_dir = output_dir / "figures"
    figures_dir.mkdir()
    for figure in figures:
        for source_path in (
            figure.plotly_json_path,
            figure.svg_path,
            figure.pdf_path,
            figure.png_path,
            figure.manifest_path,
        ):
            source = Path(source_path)
            shutil.copy2(source, figures_dir / source.name)

    paths = [
        path
        for path in output_dir.rglob("*")
        if path.is_file() and path.name != "export-manifest.json"
    ]
    files = tuple(_export_file(path) for path in sorted(paths))
    manifest = ExportManifest(
        task_id=bundle.task_id,
        analysis_id=bundle.analysis_id,
        files=files,
    )
    manifest_path = output_dir / "export-manifest.json"
    manifest_path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    return manifest


def _export_file(path: Path) -> ExportFile:
    return ExportFile(
        path=str(path),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        size=path.stat().st_size,
    )


__all__ = ["ExportFile", "ExportManifest", "export_analysis_bundle"]
