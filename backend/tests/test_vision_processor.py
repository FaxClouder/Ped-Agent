from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from ped_agent.vision.artifacts import PixelTrackParquetStore
from ped_agent.vision.contracts import (
    CalibrationMode,
    CalibrationReport,
    ContactPointQuality,
    ModelManifest,
    PixelPoint,
    PixelTrackObservation,
    SceneProfile,
    SemanticClass,
    VideoMetadata,
    VideoTaskSpec,
)
from ped_agent.vision.inference import TrackAssignment, assemble_pixel_tracks
from ped_agent.vision.model_registry import ModelManifestRegistry
from ped_agent.vision.review import ReviewPatch, apply_review_patch

from ped_agent_server.scene_registry import SceneProfileRegistry
from ped_agent_server.vision_processor import VisionPipelineProcessor
from ped_agent_server.vision_repository import VisionRepository
from ped_agent_server.vision_storage import VisionStorage


def setup_runtime(tmp_path: Path):
    storage = VisionStorage(tmp_path / "vision")
    storage.ensure_dirs()
    weights = storage.paths.model_manifests_dir / "mixed.pt"
    weights.write_bytes(b"weights")
    digest = hashlib.sha256(weights.read_bytes()).hexdigest()
    manifest = ModelManifest(
        model_id="mixed-flow-v1",
        name="Model",
        version="1",
        backend="ultralytics",
        weights_path=Path("mixed.pt"),
        sha256=digest,
        input_size=640,
        class_map={
            0: SemanticClass.PEDESTRIAN,
            1: SemanticClass.PEDESTRIAN_UMBRELLA,
            2: SemanticClass.BICYCLE_RIDER,
            3: SemanticClass.EBIKE_RIDER,
        },
        contact_keypoints={
            SemanticClass.PEDESTRIAN: ("left_foot", "right_foot"),
            SemanticClass.PEDESTRIAN_UMBRELLA: ("left_foot", "right_foot"),
            SemanticClass.BICYCLE_RIDER: ("front_wheel", "rear_wheel"),
            SemanticClass.EBIKE_RIDER: ("front_wheel", "rear_wheel"),
        },
    )
    (storage.paths.model_manifests_dir / "model.json").write_text(
        manifest.model_dump_json(), encoding="utf-8"
    )
    scenes = SceneProfileRegistry(storage.paths.scenes_dir)
    scenes.save(
        SceneProfile(
            scene_id="scene-1",
            version=1,
            name="Scene",
            camera_fingerprint="camera-1",
            resolution=(100, 100),
            calibration_mode=CalibrationMode.HOMOGRAPHY,
            roi=((-1, -1), (4, -1), (4, 2), (-1, 2)),
            entrances={
                "west": ((-1, -1), (0.5, -1), (0.5, 2), (-1, 2)),
                "east": ((1.5, -1), (4, -1), (4, 2), (1.5, 2)),
            },
        )
    )
    repository = VisionRepository(tmp_path / "vision.sqlite3")
    repository.initialize()
    source = tmp_path / "source.mp4"
    source.write_bytes(b"video")
    stored_video = storage.ingest_video("task-1", source)
    repository.create_task(
        task_id="task-1",
        spec=VideoTaskSpec(
            task_name="Task",
            source_video=source,
            model_id="mixed-flow-v1",
            scene_id="scene-1",
        ),
        source_video_path=stored_video.path,
        source_video_sha256=stored_video.sha256,
    )
    return repository, storage, ModelManifestRegistry(storage.paths.model_manifests_dir), scenes


def pixel_artifact(source_path: str, source_sha: str):
    observations = tuple(
        TrackAssignment(
            1,
            PixelTrackObservation(
                frame_index=frame,
                timestamp=float(frame),
                point=PixelPoint(x=float(frame), y=0),
                bbox_xyxy=(frame, 0, frame + 1, 2),
                detection_confidence=0.9,
                tracking_confidence=0.9,
                semantic_class=SemanticClass.PEDESTRIAN,
                contact_quality=ContactPointQuality.KEYPOINT,
            ),
        )
        for frame in range(3)
    )
    return assemble_pixel_tracks(
        task_id="task-1",
        source_video_sha256=source_sha,
        model_manifest_sha256="c" * 64,
        video=VideoMetadata(
            source=source_path,
            fps=1,
            total_frames=3,
            resolution=(100, 100),
            duration=3,
        ),
        assignments=observations,
    )


class FakeInference:
    def run(self, *, task: dict[str, object], manifest, manifest_sha256: str):
        return pixel_artifact(str(task["source_video_path"]), str(task["source_video_sha256"]))


class UnexpectedInference:
    def run(self, *, task: dict[str, object], manifest, manifest_sha256: str):
        raise AssertionError("existing inference artifact must be reused")


@pytest.mark.asyncio
async def test_processor_inference_creates_pixel_artifact_and_waits_for_review(
    tmp_path: Path,
) -> None:
    repository, storage, models, scenes = setup_runtime(tmp_path)
    repository.transition("task-1", "preflighted")
    repository.transition("task-1", "queued")
    repository.transition("task-1", "inference_running")
    processor = VisionPipelineProcessor(
        storage=storage,
        model_registry=models,
        scene_registry=scenes,
        inference_executor=FakeInference(),
    )

    await processor.run("task-1", "inference_running", repository)

    assert repository.get_task("task-1")["status"] == "awaiting_review"
    artifact = repository.latest_artifact("task-1", "pixel_tracks")
    assert artifact is not None
    assert Path(artifact["path"]).joinpath("observations.parquet").exists()


@pytest.mark.asyncio
async def test_processor_reuses_active_inference_artifact_on_retry(tmp_path: Path) -> None:
    repository, storage, models, scenes = setup_runtime(tmp_path)
    task = repository.get_task("task-1")
    raw = pixel_artifact(str(task["source_video_path"]), str(task["source_video_sha256"]))
    root = storage.paths.artifacts_dir / "task-1"
    stored = PixelTrackParquetStore(root).write(raw)
    repository.register_artifact(
        task_id="task-1",
        artifact_id=raw.artifact_id,
        stage="inference",
        artifact_type="pixel_tracks",
        path=stored.artifact_dir,
        sha256="a" * 64,
    )
    repository.transition("task-1", "preflighted")
    repository.transition("task-1", "queued")
    repository.transition("task-1", "inference_running")
    processor = VisionPipelineProcessor(
        storage=storage,
        model_registry=models,
        scene_registry=scenes,
        inference_executor=UnexpectedInference(),
    )

    await processor.run("task-1", "inference_running", repository)

    assert repository.get_task("task-1")["status"] == "awaiting_review"


@pytest.mark.asyncio
async def test_processor_reuses_completed_rendering_artifacts_on_retry(
    tmp_path: Path,
) -> None:
    repository, storage, models, scenes = setup_runtime(tmp_path)
    for status in (
        "preflighted",
        "queued",
        "inference_running",
        "awaiting_review",
        "awaiting_calibration",
        "projection_running",
        "postprocess_running",
        "analysis_running",
        "rendering",
    ):
        repository.transition("task-1", status)
    for artifact_id, artifact_type in (
        ("figures-existing", "figure_manifest"),
        ("export-existing", "export_manifest"),
    ):
        path = storage.artifact_dir("task-1", artifact_id) / f"{artifact_type}.json"
        path.parent.mkdir(parents=True)
        path.write_text("{}", encoding="utf-8")
        repository.register_artifact(
            task_id="task-1",
            artifact_id=artifact_id,
            stage="rendering",
            artifact_type=artifact_type,
            path=path,
            sha256="d" * 64,
        )
    processor = VisionPipelineProcessor(
        storage=storage,
        model_registry=models,
        scene_registry=scenes,
        inference_executor=UnexpectedInference(),
    )

    await processor.run("task-1", "rendering", repository)

    assert repository.get_task("task-1")["status"] == "completed"


@pytest.mark.parametrize(
    ("method_name", "artifact_type"),
    (
        ("_projection", "world_tracks"),
        ("_postprocess", "processed_world_tracks"),
        ("_analysis", "analysis_bundle"),
    ),
)
def test_processor_reuses_active_downstream_stage_artifact(
    tmp_path: Path,
    method_name: str,
    artifact_type: str,
) -> None:
    repository, storage, models, scenes = setup_runtime(tmp_path)
    path = storage.artifact_dir("task-1", artifact_type) / "existing.json"
    path.parent.mkdir(parents=True)
    path.write_text("{}", encoding="utf-8")
    repository.register_artifact(
        task_id="task-1",
        artifact_id=f"existing-{artifact_type}",
        stage={
            "world_tracks": "projection",
            "processed_world_tracks": "postprocess",
            "analysis_bundle": "analysis",
        }[artifact_type],
        artifact_type=artifact_type,
        path=path,
        sha256="e" * 64,
    )
    processor = VisionPipelineProcessor(
        storage=storage,
        model_registry=models,
        scene_registry=scenes,
        inference_executor=UnexpectedInference(),
    )

    getattr(processor, method_name)("task-1", repository)


@pytest.mark.asyncio
async def test_processor_resumes_after_review_and_generates_analysis_exports(
    tmp_path: Path,
) -> None:
    repository, storage, models, scenes = setup_runtime(tmp_path)
    task = repository.get_task("task-1")
    raw = pixel_artifact(str(task["source_video_path"]), str(task["source_video_sha256"]))
    root = storage.paths.artifacts_dir / "task-1"
    raw_stored = PixelTrackParquetStore(root).write(raw)
    repository.register_artifact(
        task_id="task-1",
        artifact_id=raw.artifact_id,
        stage="inference",
        artifact_type="pixel_tracks",
        path=raw_stored.artifact_dir,
        sha256="a" * 64,
    )
    reviewed = apply_review_patch(
        raw,
        ReviewPatch(
            patch_id="review-1",
            parent_artifact_id=raw.artifact_id,
            operations=(),
        ),
    )
    reviewed_stored = PixelTrackParquetStore(root).write(reviewed)
    repository.register_artifact(
        task_id="task-1",
        artifact_id=reviewed.artifact_id,
        stage="review",
        artifact_type="reviewed_pixel_tracks",
        path=reviewed_stored.artifact_dir,
        sha256="b" * 64,
    )
    report = CalibrationReport(
        calibration_id="cal-1",
        scene_id="scene-1",
        scene_version=1,
        mode=CalibrationMode.HOMOGRAPHY,
        image_reprojection_rmse_px=0,
        world_checkpoint_rmse_m=0.05,
        checkpoint_count=4,
        matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    )
    cal_dir = storage.artifact_dir("task-1", "cal-1")
    cal_dir.mkdir(parents=True)
    cal_path = cal_dir / "calibration.json"
    cal_path.write_text(
        report.model_dump_json(exclude_computed_fields=True), encoding="utf-8"
    )
    repository.register_artifact(
        task_id="task-1",
        artifact_id="cal-1",
        stage="calibration",
        artifact_type="calibration_report",
        path=cal_path,
        sha256="c" * 64,
    )
    repository.transition("task-1", "preflighted")
    repository.transition("task-1", "queued")
    repository.transition("task-1", "inference_running")
    repository.transition("task-1", "awaiting_review")
    repository.transition("task-1", "awaiting_calibration")
    repository.queue_stage("task-1", resume_status="projection_running")
    repository.start_queued_stage("task-1")
    processor = VisionPipelineProcessor(
        storage=storage,
        model_registry=models,
        scene_registry=scenes,
        inference_executor=FakeInference(),
    )

    await processor.run("task-1", "projection_running", repository)

    assert repository.get_task("task-1")["status"] == "completed"
    artifact_types = {
        item["artifact_type"] for item in repository.list_artifacts("task-1")
    }
    assert {
        "world_tracks",
        "processed_world_tracks",
        "analysis_bundle",
        "figure_manifest",
        "export_manifest",
    } <= artifact_types
    assert list(storage.export_dir("task-1").rglob("*.csv"))
    assert not list(storage.paths.root.rglob("annotated*.mp4"))
