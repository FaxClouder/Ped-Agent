from __future__ import annotations

import asyncio
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Annotated, Literal, Protocol
from uuid import uuid4

import numpy as np
from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from ped_agent.vision.artifacts import PixelTrackParquetStore
from ped_agent.vision.calibration import (
    CalibrationPoint,
    CharucoBoardSpec,
    FullCameraCalibration,
    HomographyCalibration,
    calibrate_charuco_images,
    solve_homography,
)
from ped_agent.vision.contracts import (
    CalibrationMode,
    CalibrationReport,
    SceneProfile,
    VideoTaskSpec,
)
from ped_agent.vision.model_registry import ModelManifestRegistry
from ped_agent.vision.review import ReviewPatch, apply_review_patch
from pydantic import BaseModel, Field

from ped_agent_server.scene_registry import SceneProfileRegistry
from ped_agent_server.vision_repository import (
    VISION_TERMINAL_STATUSES,
    InvalidVisionTransition,
    VisionRepository,
)
from ped_agent_server.vision_service import VisionTaskService
from ped_agent_server.vision_storage import VisionStorage


class VisionRerunRequest(BaseModel):
    from_stage: Literal[
        "inference", "projection", "postprocess", "analysis", "rendering"
    ]


class CalibrationPointPayload(BaseModel):
    pixel: tuple[float, float]
    world: tuple[float, float]


class HomographyCalibrationRequest(BaseModel):
    fit_points: tuple[CalibrationPointPayload, ...]
    checkpoints: tuple[CalibrationPointPayload, ...]
    ransac_threshold_m: float = 0.10


class PixelSceneGeometryRequest(BaseModel):
    scene_id: str
    version: int
    name: str
    camera_fingerprint: str
    resolution: tuple[int, int]
    calibration_report: CalibrationReport
    roi: tuple[tuple[float, float], ...]
    exclusion_zones: dict[str, tuple[tuple[float, float], ...]] = Field(
        default_factory=dict
    )
    zones: dict[str, tuple[tuple[float, float], ...]] = Field(default_factory=dict)
    counting_lines: dict[
        str, tuple[tuple[float, float], tuple[float, float]]
    ] = Field(default_factory=dict)
    entrances: dict[str, tuple[tuple[float, float], ...]] = Field(default_factory=dict)
    conflict_zones: dict[str, tuple[tuple[float, float], ...]] = Field(
        default_factory=dict
    )


class PixelTransformer(Protocol):
    def transform(self, pixel: tuple[float, float]) -> tuple[float, float]: ...


def build_vision_router(
    *,
    repository: VisionRepository,
    storage: VisionStorage,
    model_registry: ModelManifestRegistry,
    scene_registry: SceneProfileRegistry,
    service: VisionTaskService | None,
) -> APIRouter:
    router = APIRouter(prefix="/api/vision", tags=["vision"])

    @router.get("/models")
    def list_models() -> list[dict[str, object]]:
        response = []
        for manifest in model_registry.list():
            available = True
            error = None
            try:
                model_registry.get(manifest.model_id)
            except (FileNotFoundError, ValueError) as exc:
                available = False
                error = str(exc)
            response.append(
                {
                    "model_id": manifest.model_id,
                    "name": manifest.name,
                    "version": manifest.version,
                    "backend": manifest.backend,
                    "sha256": manifest.sha256,
                    "input_size": manifest.input_size,
                    "class_map": {
                        str(key): value.value for key, value in manifest.class_map.items()
                    },
                    "inference": manifest.inference.model_dump(mode="json"),
                    "tracker": manifest.tracker.model_dump(mode="json"),
                    "available": available,
                    "error": error,
                }
            )
        return response

    @router.get("/scenes")
    def list_scenes() -> list[dict[str, object]]:
        return [scene.model_dump(mode="json") for scene in scene_registry.list()]

    @router.post("/scenes", status_code=status.HTTP_201_CREATED)
    def create_scene(scene: SceneProfile) -> dict[str, object]:
        try:
            path = scene_registry.save(scene)
        except FileExistsError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {**scene.model_dump(mode="json"), "path": str(path)}

    @router.post("/scenes/from-pixel-geometry", status_code=status.HTTP_201_CREATED)
    def create_scene_from_pixel_geometry(
        request: PixelSceneGeometryRequest,
    ) -> dict[str, object]:
        report = request.calibration_report
        if report.scene_id != request.scene_id or report.scene_version != request.version:
            raise HTTPException(
                status_code=422,
                detail="calibration report must target the same scene id and version",
            )
        try:
            transformer = _transformer(report)
            scene = SceneProfile(
                scene_id=request.scene_id,
                version=request.version,
                name=request.name,
                camera_fingerprint=request.camera_fingerprint,
                resolution=request.resolution,
                calibration_mode=report.mode,
                roi=_project_polygon(request.roi, transformer),
                exclusion_zones={
                    name: _project_polygon(points, transformer)
                    for name, points in request.exclusion_zones.items()
                },
                zones={
                    name: _project_polygon(points, transformer)
                    for name, points in request.zones.items()
                },
                counting_lines={
                    name: _project_line(points, transformer)
                    for name, points in request.counting_lines.items()
                },
                entrances={
                    name: _project_polygon(points, transformer)
                    for name, points in request.entrances.items()
                },
                conflict_zones={
                    name: _project_polygon(points, transformer)
                    for name, points in request.conflict_zones.items()
                },
            )
            path = scene_registry.save(scene)
        except FileExistsError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {**scene.model_dump(mode="json"), "path": str(path)}

    @router.post("/scenes/calibrate/charuco")
    async def calibrate_scene_charuco(
        images: Annotated[list[UploadFile], File()],
        squares_x: Annotated[int, Form(ge=2)],
        squares_y: Annotated[int, Form(ge=2)],
        square_length_m: Annotated[float, Form(gt=0)],
        marker_length_m: Annotated[float, Form(gt=0)],
        dictionary_id: Annotated[int, Form(ge=0)],
        minimum_views: Annotated[int, Form(ge=3)] = 5,
        minimum_corners_per_view: Annotated[int, Form(ge=4)] = 4,
    ) -> dict[str, object]:
        board_spec = CharucoBoardSpec(
            squares_x=squares_x,
            squares_y=squares_y,
            square_length_m=square_length_m,
            marker_length_m=marker_length_m,
            dictionary_id=dictionary_id,
            minimum_views=minimum_views,
            minimum_corners_per_view=minimum_corners_per_view,
        )
        try:
            with tempfile.TemporaryDirectory(dir=storage.paths.root) as temporary:
                image_paths = []
                for index, image in enumerate(images):
                    suffix = Path(image.filename or "image.png").suffix or ".png"
                    path = Path(temporary) / f"view-{index:04d}{suffix}"
                    with path.open("wb") as target:
                        while chunk := await image.read(1024 * 1024):
                            target.write(chunk)
                    image_paths.append(path)
                intrinsics = await asyncio.to_thread(
                    calibrate_charuco_images,
                    tuple(image_paths),
                    board_spec,
                )
        except (RuntimeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return intrinsics.model_dump(mode="json")

    @router.post("/scenes/{scene_id}/calibrate/homography")
    def calibrate_scene_homography(
        scene_id: str,
        request: HomographyCalibrationRequest,
    ) -> dict[str, object]:
        try:
            scene = scene_registry.get(scene_id)
            calibration = solve_homography(
                tuple(
                    CalibrationPoint(pixel=item.pixel, world=item.world)
                    for item in request.fit_points
                ),
                tuple(
                    CalibrationPoint(pixel=item.pixel, world=item.world)
                    for item in request.checkpoints
                ),
                ransac_threshold_m=request.ransac_threshold_m,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="scene not found") from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        report = calibration.report.model_copy(
            update={"scene_id": scene.scene_id, "scene_version": scene.version}
        )
        return report.model_dump(mode="json")

    @router.post("/tasks", status_code=status.HTTP_202_ACCEPTED)
    async def create_task(
        task_name: Annotated[str, Form(min_length=1)],
        model_id: Annotated[str, Form(min_length=1)],
        video: Annotated[UploadFile, File()],
        scene_id: Annotated[str | None, Form()] = None,
    ) -> dict[str, object]:
        try:
            model_registry.get(model_id)
            if scene_id:
                scene_registry.get(scene_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"resource not found: {exc}") from exc
        except (FileNotFoundError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        suffix = Path(video.filename or "upload.mp4").suffix.lower()
        if suffix not in {".mp4", ".mov", ".avi", ".mkv", ".m4v"}:
            raise HTTPException(status_code=422, detail="unsupported video extension")
        task_id = f"vision-{uuid4().hex}"
        with tempfile.TemporaryDirectory(dir=storage.paths.root) as temporary:
            temporary_path = Path(temporary) / Path(video.filename or "upload.mp4").name
            size = 0
            with temporary_path.open("wb") as target:
                while chunk := await video.read(1024 * 1024):
                    size += len(chunk)
                    target.write(chunk)
            if size == 0:
                raise HTTPException(status_code=422, detail="uploaded video is empty")
            stored = storage.ingest_video(task_id, temporary_path)
        task = repository.create_task(
            task_id=task_id,
            spec=VideoTaskSpec(
                task_name=task_name,
                source_video=Path(video.filename or "upload.mp4"),
                model_id=model_id,
                scene_id=scene_id,
            ),
            source_video_path=stored.path,
            source_video_sha256=stored.sha256,
        )
        if service is None:
            repository.transition(task_id, "preflighted")
            task = repository.transition(task_id, "queued")
        else:
            await service.start()
            task = await service.submit(task_id)
        return {
            "task_id": task_id,
            "status": task["status"],
            "events_url": f"/api/vision/tasks/{task_id}/events",
        }

    @router.get("/tasks")
    def list_tasks() -> list[dict[str, object]]:
        return repository.list_tasks()

    @router.get("/tasks/{task_id}")
    def get_task(task_id: str) -> dict[str, object]:
        task = repository.get_task(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="vision task not found")
        return task

    @router.get("/tasks/{task_id}/events")
    def stream_events(
        task_id: str,
        last_event_id: Annotated[str | None, Header(alias="Last-Event-ID")] = None,
    ) -> StreamingResponse:
        if repository.get_task(task_id) is None:
            raise HTTPException(status_code=404, detail="vision task not found")
        try:
            cursor = max(0, int(last_event_id or 0))
        except ValueError:
            cursor = 0

        async def event_stream():
            nonlocal cursor
            heartbeat_ticks = 0
            while True:
                events = repository.list_events(task_id, after_id=cursor)
                for event in events:
                    cursor = int(event["id"])
                    yield _format_sse(event)
                task = repository.get_task(task_id)
                if task is None or (
                    task["status"] in VISION_TERMINAL_STATUSES and not events
                ):
                    break
                heartbeat_ticks += 1
                if heartbeat_ticks >= 60:
                    heartbeat_ticks = 0
                    yield "event: heartbeat\ndata: {}\n\n"
                await asyncio.sleep(0.25)

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @router.post("/tasks/{task_id}/review", status_code=status.HTTP_201_CREATED)
    def review_task(task_id: str, patch: ReviewPatch) -> dict[str, object]:
        task = _task_or_404(repository, task_id)
        if task["status"] != "awaiting_review":
            raise HTTPException(status_code=409, detail="task is not awaiting review")
        raw_index = repository.latest_artifact(task_id, "pixel_tracks")
        if raw_index is None:
            raise HTTPException(status_code=409, detail="pixel track artifact is missing")
        root = Path(str(raw_index["path"])).parent
        raw = PixelTrackParquetStore(root).read(str(raw_index["artifact_id"]))
        try:
            reviewed = apply_review_patch(raw, patch)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        repository.invalidate_from(task_id, from_stage="review")
        stored = PixelTrackParquetStore(root).write(reviewed)
        repository.save_review_patch(
            task_id=task_id,
            patch_id=patch.patch_id,
            parent_artifact_id=patch.parent_artifact_id,
            patch_json=patch.model_dump_json(),
        )
        repository.register_artifact(
            task_id=task_id,
            artifact_id=reviewed.artifact_id,
            stage="review",
            artifact_type="reviewed_pixel_tracks",
            path=stored.artifact_dir,
            sha256=_directory_sha256(stored.artifact_dir),
            parent_artifact_id=reviewed.parent_artifact_id,
        )
        updated = repository.transition(task_id, "awaiting_calibration")
        return {
            "task_id": task_id,
            "status": updated["status"],
            "reviewed_artifact_id": reviewed.artifact_id,
        }

    @router.post("/tasks/{task_id}/calibration", status_code=status.HTTP_201_CREATED)
    async def save_calibration(
        task_id: str, report: CalibrationReport
    ) -> dict[str, object]:
        task = _task_or_404(repository, task_id)
        if task["status"] not in {"awaiting_review", "awaiting_calibration"}:
            raise HTTPException(status_code=409, detail="task is not awaiting calibration")
        repository.invalidate_from(task_id, from_stage="calibration")
        artifact_dir = storage.artifact_dir(task_id, report.calibration_id)
        if artifact_dir.exists():
            raise HTTPException(status_code=409, detail="calibration artifact already exists")
        artifact_dir.mkdir(parents=True)
        report_path = artifact_dir / "calibration.json"
        report_path.write_text(
            report.model_dump_json(indent=2, exclude_computed_fields=True),
            encoding="utf-8",
        )
        repository.register_artifact(
            task_id=task_id,
            artifact_id=report.calibration_id,
            stage="calibration",
            artifact_type="calibration_report",
            path=report_path,
            sha256=hashlib.sha256(report_path.read_bytes()).hexdigest(),
        )
        if task["status"] == "awaiting_review":
            repository.transition(task_id, "awaiting_calibration")
        if report.accepted:
            updated = repository.queue_stage(task_id, resume_status="projection_running")
            if service is not None:
                await service.start()
                await service.enqueue_queued(task_id)
        else:
            updated = _task_or_404(repository, task_id)
        return {
            "task_id": task_id,
            "status": updated["status"],
            "calibration_id": report.calibration_id,
            "accepted": report.accepted,
            "world_checkpoint_rmse_m": report.world_checkpoint_rmse_m,
        }

    @router.post("/tasks/{task_id}/rerun", status_code=status.HTTP_202_ACCEPTED)
    async def rerun_task(
        task_id: str, request: VisionRerunRequest
    ) -> dict[str, object]:
        _task_or_404(repository, task_id)
        resume_status = {
            "inference": "inference_running",
            "projection": "projection_running",
            "postprocess": "postprocess_running",
            "analysis": "analysis_running",
            "rendering": "rendering",
        }[request.from_stage]
        repository.invalidate_from(task_id, from_stage=request.from_stage)
        try:
            task = repository.queue_stage(task_id, resume_status=resume_status)
        except (InvalidVisionTransition, ValueError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        if service is not None:
            await service.start()
            await service.enqueue_queued(task_id)
        return {"task_id": task_id, "status": task["status"], "from_stage": request.from_stage}

    @router.post("/tasks/{task_id}/cancel", status_code=status.HTTP_202_ACCEPTED)
    async def cancel_task(task_id: str) -> dict[str, object]:
        _task_or_404(repository, task_id)
        try:
            task = (
                await service.cancel(task_id)
                if service is not None
                else repository.cancel(task_id)
            )
        except InvalidVisionTransition as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {"task_id": task_id, "status": task["status"]}

    @router.get("/tasks/{task_id}/results")
    def get_results(task_id: str) -> dict[str, object]:
        task = _task_or_404(repository, task_id)
        artifacts = repository.list_artifacts(task_id)
        pixel_index = repository.latest_artifact(task_id, "reviewed_pixel_tracks")
        reviewed_pixel = pixel_index is not None
        if pixel_index is None:
            pixel_index = repository.latest_artifact(task_id, "pixel_tracks")
        review_queue: list[dict[str, object]] = []
        track_summary: list[dict[str, object]] = []
        if pixel_index is not None:
            pixel_root = Path(str(pixel_index["path"])).parent
            pixel_store = PixelTrackParquetStore(pixel_root)
            pixel_tracks = (
                pixel_store.read_reviewed(str(pixel_index["artifact_id"]))
                if reviewed_pixel
                else pixel_store.read(str(pixel_index["artifact_id"]))
            )
            for track in pixel_tracks.tracks:
                degraded = [
                    item
                    for item in track.observations
                    if item.contact_quality.value in {"estimated", "fallback"}
                ]
                track_summary.append(
                    {
                        "track_id": track.track_id,
                        "semantic_class": track.semantic_class.value,
                        "point_count": len(track.observations),
                        "degraded_point_count": len(degraded),
                        "start_frame": (
                            min(item.frame_index for item in track.observations)
                            if track.observations
                            else None
                        ),
                        "end_frame": (
                            max(item.frame_index for item in track.observations)
                            if track.observations
                            else None
                        ),
                    }
                )
                review_queue.extend(
                    {
                        "track_id": track.track_id,
                        "frame_index": item.frame_index,
                        "timestamp": item.timestamp,
                        "semantic_class": item.semantic_class.value,
                        "point": item.point.model_dump(mode="json"),
                        "bbox_xyxy": list(item.bbox_xyxy),
                        "contact_quality": item.contact_quality.value,
                    }
                    for item in degraded
                )
        calibration = repository.latest_artifact(task_id, "calibration_report")
        report = None
        if calibration is not None:
            report = CalibrationReport.model_validate_json(
                Path(str(calibration["path"])).read_text(encoding="utf-8")
            )
        analysis_index = repository.latest_artifact(task_id, "analysis_bundle")
        analysis = None
        if analysis_index is not None:
            analysis = json.loads(
                Path(str(analysis_index["path"])).read_text(encoding="utf-8")
            )
        return {
            "task": task,
            "physical_metrics_available": bool(report and report.accepted),
            "calibration": report.model_dump(mode="json") if report else None,
            "analysis": analysis,
            "artifacts": artifacts,
            "review_queue": review_queue,
            "track_summary": track_summary,
        }

    @router.get("/tasks/{task_id}/exports")
    def list_exports(task_id: str) -> list[dict[str, object]]:
        _task_or_404(repository, task_id)
        root = storage.export_dir(task_id)
        if not root.exists():
            return []
        return [
            {
                "name": str(path.relative_to(root)).replace("\\", "/"),
                "format": path.suffix.lstrip(".").lower(),
                "size": path.stat().st_size,
                "path": str(path),
            }
            for path in sorted(item for item in root.rglob("*") if item.is_file())
        ]

    return router


def _task_or_404(repository: VisionRepository, task_id: str) -> dict[str, object]:
    task = repository.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="vision task not found")
    return task


def _transformer(report: CalibrationReport) -> PixelTransformer:
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
    return FullCameraCalibration(
        camera_matrix=report.camera_matrix,
        distortion=report.distortion or (),
        rotation_world_to_camera=report.rotation_world_to_camera,
        translation_world_to_camera=report.translation_world_to_camera,
    )


def _project_polygon(
    points: tuple[tuple[float, float], ...],
    transformer: PixelTransformer,
) -> tuple[tuple[float, float], ...]:
    return tuple(transformer.transform(point) for point in points)


def _project_line(
    points: tuple[tuple[float, float], tuple[float, float]],
    transformer: PixelTransformer,
) -> tuple[tuple[float, float], tuple[float, float]]:
    return (transformer.transform(points[0]), transformer.transform(points[1]))


def _directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for file_path in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(file_path.name.encode())
        digest.update(file_path.read_bytes())
    return digest.hexdigest()


def _format_sse(event: dict[str, object]) -> str:
    payload = json.dumps(
        {"status": event["status"], **dict(event["payload"])},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return f"id: {event['id']}\nevent: {event['event']}\ndata: {payload}\n\n"


__all__ = [
    "CalibrationPointPayload",
    "HomographyCalibrationRequest",
    "VisionRerunRequest",
    "build_vision_router",
]
