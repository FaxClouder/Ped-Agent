from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Protocol

import numpy as np
from ped_video_analysis.analysis.vision_exports import export_analysis_bundle
from ped_video_analysis.analysis.vision_pipeline import AnalysisProfile, analyze_world_tracks
from ped_video_analysis.analysis.vision_schemas import AnalysisBundle, FigureArtifact
from ped_video_analysis.analysis.vision_visualizer import render_analysis_figures
from ped_video_analysis.vision.adapters import (
    BoxMotByteTrackAdapter,
    OpenCVFrameSequence,
    UltralyticsDetector,
)
from ped_video_analysis.vision.artifacts import PixelTrackParquetStore, WorldTrackParquetStore
from ped_video_analysis.vision.calibration import FullCameraCalibration, HomographyCalibration
from ped_video_analysis.vision.contracts import (
    CalibrationMode,
    CalibrationReport,
    ModelManifest,
    PixelTrackSet,
)
from ped_video_analysis.vision.model_registry import ModelManifestRegistry
from ped_video_analysis.vision.postprocessing import PostprocessProfile, postprocess_world_tracks
from ped_video_analysis.vision.projection import project_reviewed_tracks
from ped_video_analysis.vision.runner import VisionInferenceRunner

from ped_agent_server.scene_registry import SceneProfileRegistry
from ped_agent_server.vision_repository import VisionRepository
from ped_agent_server.vision_storage import VisionStorage


class InferenceExecutor(Protocol):
    def run(
        self,
        *,
        task: dict[str, object],
        manifest: ModelManifest,
        manifest_sha256: str,
    ) -> PixelTrackSet: ...


class UltralyticsInferenceExecutor:
    def run(
        self,
        *,
        task: dict[str, object],
        manifest: ModelManifest,
        manifest_sha256: str,
    ) -> PixelTrackSet:
        frames = OpenCVFrameSequence(Path(str(task["source_video_path"])))
        runner = VisionInferenceRunner(
            manifest,
            detector=UltralyticsDetector(manifest),
            tracker=BoxMotByteTrackAdapter(
                manifest,
                source_fps=frames.metadata.fps,
            ),
        )
        return runner.run(
            task_id=str(task["id"]),
            source_video_sha256=str(task["source_video_sha256"]),
            model_manifest_sha256=manifest_sha256,
            frames=frames,
        )


class VisionPipelineProcessor:
    def __init__(
        self,
        *,
        storage: VisionStorage,
        model_registry: ModelManifestRegistry,
        scene_registry: SceneProfileRegistry,
        inference_executor: InferenceExecutor | None = None,
    ):
        self.storage = storage
        self.model_registry = model_registry
        self.scene_registry = scene_registry
        self.inference_executor = inference_executor or UltralyticsInferenceExecutor()

    async def run(
        self,
        task_id: str,
        start_status: str,
        repository: VisionRepository,
    ) -> None:
        await asyncio.to_thread(
            self._run_sync,
            task_id,
            start_status,
            repository,
        )

    def _run_sync(
        self,
        task_id: str,
        start_status: str,
        repository: VisionRepository,
    ) -> None:
        if start_status == "inference_running":
            self._inference(task_id, repository)
            return
        if start_status == "projection_running":
            self._projection(task_id, repository)
            if not self._active(task_id, repository):
                return
            repository.transition(task_id, "postprocess_running")
            start_status = "postprocess_running"
        if start_status == "postprocess_running":
            self._postprocess(task_id, repository)
            if not self._active(task_id, repository):
                return
            repository.transition(task_id, "analysis_running")
            start_status = "analysis_running"
        if start_status == "analysis_running":
            self._analysis(task_id, repository)
            if not self._active(task_id, repository):
                return
            repository.transition(task_id, "rendering")
            start_status = "rendering"
        if start_status == "rendering":
            self._render(task_id, repository)
            if self._active(task_id, repository):
                repository.transition(task_id, "completed")

    def _inference(self, task_id: str, repository: VisionRepository) -> None:
        if repository.latest_artifact(task_id, "pixel_tracks") is not None:
            if self._active(task_id, repository):
                repository.transition(task_id, "awaiting_review")
            return
        task = self._task(repository, task_id)
        manifest = self.model_registry.get(str(task["model_id"]))
        artifact = self.inference_executor.run(
            task=task,
            manifest=manifest,
            manifest_sha256=self.model_registry.manifest_sha256(manifest.model_id),
        )
        root = self.storage.paths.artifacts_dir / task_id
        stored = PixelTrackParquetStore(root).write(artifact)
        repository.register_artifact(
            task_id=task_id,
            artifact_id=artifact.artifact_id,
            stage="inference",
            artifact_type="pixel_tracks",
            path=stored.artifact_dir,
            sha256=_directory_sha256(stored.artifact_dir),
        )
        if self._active(task_id, repository):
            repository.transition(task_id, "awaiting_review")

    def _projection(self, task_id: str, repository: VisionRepository) -> None:
        if repository.latest_artifact(task_id, "world_tracks") is not None:
            return
        reviewed_index = self._artifact(repository, task_id, "reviewed_pixel_tracks")
        calibration_index = self._artifact(repository, task_id, "calibration_report")
        root = self.storage.paths.artifacts_dir / task_id
        reviewed = PixelTrackParquetStore(root).read_reviewed(
            str(reviewed_index["artifact_id"])
        )
        report = CalibrationReport.model_validate_json(
            Path(str(calibration_index["path"])).read_text(encoding="utf-8")
        )
        world = project_reviewed_tracks(reviewed, _transformer(report), report)
        stored = WorldTrackParquetStore(root).write(world)
        repository.register_artifact(
            task_id=task_id,
            artifact_id=world.artifact_id,
            stage="projection",
            artifact_type="world_tracks",
            path=stored.artifact_dir,
            sha256=_directory_sha256(stored.artifact_dir),
            parent_artifact_id=world.parent_artifact_id,
        )

    def _postprocess(self, task_id: str, repository: VisionRepository) -> None:
        if repository.latest_artifact(task_id, "processed_world_tracks") is not None:
            return
        source_index = self._artifact(repository, task_id, "world_tracks")
        root = self.storage.paths.artifacts_dir / task_id
        source = WorldTrackParquetStore(root).read(str(source_index["artifact_id"]))
        processed = postprocess_world_tracks(source, PostprocessProfile())
        stored = WorldTrackParquetStore(root).write(processed)
        repository.register_artifact(
            task_id=task_id,
            artifact_id=processed.artifact_id,
            stage="postprocess",
            artifact_type="processed_world_tracks",
            path=stored.artifact_dir,
            sha256=_directory_sha256(stored.artifact_dir),
            parent_artifact_id=processed.parent_artifact_id,
        )

    def _analysis(self, task_id: str, repository: VisionRepository) -> None:
        if repository.latest_artifact(task_id, "analysis_bundle") is not None:
            return
        task = self._task(repository, task_id)
        processed_index = self._artifact(repository, task_id, "processed_world_tracks")
        root = self.storage.paths.artifacts_dir / task_id
        processed = WorldTrackParquetStore(root).read_processed(
            str(processed_index["artifact_id"])
        )
        if not task["scene_id"]:
            raise ValueError("scene profile is required for world-coordinate analysis")
        scene = self.scene_registry.get(str(task["scene_id"]))
        bundle = analyze_world_tracks(processed, scene, AnalysisProfile())
        artifact_dir = self.storage.artifact_dir(task_id, bundle.analysis_id)
        artifact_dir.mkdir(parents=True)
        path = artifact_dir / "analysis.json"
        path.write_text(bundle.model_dump_json(indent=2), encoding="utf-8")
        repository.register_artifact(
            task_id=task_id,
            artifact_id=bundle.analysis_id,
            stage="analysis",
            artifact_type="analysis_bundle",
            path=path,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            parent_artifact_id=bundle.source_artifact_id,
        )

    def _render(self, task_id: str, repository: VisionRepository) -> None:
        figure_index = repository.latest_artifact(task_id, "figure_manifest")
        export_index = repository.latest_artifact(task_id, "export_manifest")
        if figure_index is not None and export_index is not None:
            return
        analysis_index = self._artifact(repository, task_id, "analysis_bundle")
        processed_index = self._artifact(repository, task_id, "processed_world_tracks")
        bundle = AnalysisBundle.model_validate_json(
            Path(str(analysis_index["path"])).read_text(encoding="utf-8")
        )
        root = self.storage.paths.artifacts_dir / task_id
        processed = WorldTrackParquetStore(root).read_processed(
            str(processed_index["artifact_id"])
        )
        if figure_index is None:
            figure_id = f"figures-{bundle.analysis_id.removeprefix('analysis-')}"
            figure_dir = self.storage.artifact_dir(task_id, figure_id)
            figures = render_analysis_figures(bundle, processed, figure_dir)
            figure_manifest_path = figure_dir / "figures.json"
            figure_manifest_path.write_text(
                json.dumps(
                    [item.model_dump(mode="json") for item in figures],
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            repository.register_artifact(
                task_id=task_id,
                artifact_id=figure_id,
                stage="rendering",
                artifact_type="figure_manifest",
                path=figure_manifest_path,
                sha256=hashlib.sha256(figure_manifest_path.read_bytes()).hexdigest(),
                parent_artifact_id=bundle.analysis_id,
            )
        else:
            figures = tuple(
                FigureArtifact.model_validate(item)
                for item in json.loads(
                    Path(str(figure_index["path"])).read_text(encoding="utf-8")
                )
            )
        if export_index is not None:
            return
        export_dir = self.storage.export_dir(task_id) / bundle.analysis_id
        export_analysis_bundle(
            bundle=bundle,
            tracks=processed,
            figures=figures,
            output_dir=export_dir,
        )
        export_manifest_path = export_dir / "export-manifest.json"
        export_id = f"export-{bundle.analysis_id.removeprefix('analysis-')}"
        repository.register_artifact(
            task_id=task_id,
            artifact_id=export_id,
            stage="rendering",
            artifact_type="export_manifest",
            path=export_manifest_path,
            sha256=hashlib.sha256(export_manifest_path.read_bytes()).hexdigest(),
            parent_artifact_id=bundle.analysis_id,
        )

    @staticmethod
    def _active(task_id: str, repository: VisionRepository) -> bool:
        task = repository.get_task(task_id)
        return task is not None and task["status"] != "cancelled"

    @staticmethod
    def _task(repository: VisionRepository, task_id: str) -> dict[str, object]:
        task = repository.get_task(task_id)
        if task is None:
            raise KeyError(task_id)
        return task

    @staticmethod
    def _artifact(
        repository: VisionRepository,
        task_id: str,
        artifact_type: str,
    ) -> dict[str, object]:
        artifact = repository.latest_artifact(task_id, artifact_type)
        if artifact is None:
            raise ValueError(f"required artifact is missing: {artifact_type}")
        return artifact


def _transformer(report: CalibrationReport):
    if not report.accepted:
        raise ValueError("calibration does not pass the 10 cm gate")
    if report.mode is CalibrationMode.HOMOGRAPHY:
        if report.matrix is None:
            raise ValueError("homography matrix is missing")
        return HomographyCalibration(matrix=np.asarray(report.matrix), report=report)
    if not all(
        (
            report.camera_matrix,
            report.rotation_world_to_camera,
            report.translation_world_to_camera,
        )
    ):
        raise ValueError("full camera calibration parameters are missing")
    calibration = FullCameraCalibration(
        camera_matrix=report.camera_matrix,
        distortion=report.distortion or (),
        rotation_world_to_camera=report.rotation_world_to_camera,
        translation_world_to_camera=report.translation_world_to_camera,
    )

    class FullCameraTransformer:
        def transform(self, pixel: tuple[float, float]) -> tuple[float, float]:
            return calibration.pixel_to_ground(pixel)

    return FullCameraTransformer()


def _directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
        digest.update(item.name.encode())
        digest.update(item.read_bytes())
    return digest.hexdigest()


__all__ = [
    "InferenceExecutor",
    "UltralyticsInferenceExecutor",
    "VisionPipelineProcessor",
]
