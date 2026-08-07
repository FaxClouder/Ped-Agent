from __future__ import annotations

import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient
from ped_video_analysis.vision.artifacts import PixelTrackParquetStore
from ped_video_analysis.vision.calibration import CameraIntrinsics
from ped_video_analysis.vision.contracts import (
    CalibrationMode,
    ContactPointQuality,
    ModelManifest,
    PixelPoint,
    PixelTrackObservation,
    SceneProfile,
    SemanticClass,
    VideoMetadata,
)
from ped_video_analysis.vision.inference import TrackAssignment, assemble_pixel_tracks
from ped_video_analysis.vision.model_registry import ModelManifestRegistry

import ped_agent_server.vision_api as vision_api_module
from ped_agent_server.api import create_app
from ped_agent_server.catalog import Catalog
from ped_agent_server.index import FTSIndex
from ped_agent_server.scene_registry import SceneProfileRegistry
from ped_agent_server.vision_repository import VisionRepository
from ped_agent_server.vision_storage import VisionStorage


def build_client(tmp_path: Path) -> tuple[
    TestClient,
    VisionRepository,
    VisionStorage,
    SceneProfileRegistry,
]:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    index = FTSIndex(tmp_path / "fts.sqlite3")
    index.rebuild([], source_fingerprint=catalog.official_fingerprint())
    storage = VisionStorage(tmp_path / "vision")
    storage.ensure_dirs()
    weights = storage.paths.model_manifests_dir / "mixed.pt"
    weights.write_bytes(b"weights")
    digest = hashlib.sha256(weights.read_bytes()).hexdigest()
    manifest = ModelManifest(
        model_id="mixed-flow-v1",
        name="Mixed flow detector",
        version="1.0.0",
        backend="ultralytics",
        weights_path=Path("mixed.pt"),
        sha256=digest,
        input_size=1280,
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
    (storage.paths.model_manifests_dir / "mixed.json").write_text(
        manifest.model_dump_json(), encoding="utf-8"
    )
    scenes = SceneProfileRegistry(storage.paths.scenes_dir)
    scenes.save(
        SceneProfile(
            scene_id="scene-1",
            version=1,
            name="Test scene",
            camera_fingerprint="camera-1",
            resolution=(640, 480),
            calibration_mode=CalibrationMode.HOMOGRAPHY,
            roi=((0, 0), (10, 0), (10, 10), (0, 10)),
        )
    )
    repository = VisionRepository(tmp_path / "vision.sqlite3")
    repository.initialize()
    app = create_app(
        catalog_path=catalog.path,
        index_path=index.path,
        vision_repository=repository,
        vision_storage=storage,
        model_registry=ModelManifestRegistry(storage.paths.model_manifests_dir),
        scene_registry=scenes,
    )
    return TestClient(app), repository, storage, scenes


def test_vision_resources_and_upload_task_api(tmp_path: Path) -> None:
    client, repository, _, _ = build_client(tmp_path)

    assert client.get("/api/vision/models").json()[0]["model_id"] == "mixed-flow-v1"
    assert client.get("/api/vision/scenes").json()[0]["scene_id"] == "scene-1"

    response = client.post(
        "/api/vision/tasks",
        data={
            "task_name": "Morning flow",
            "model_id": "mixed-flow-v1",
            "scene_id": "scene-1",
        },
        files={"video": ("sample.mp4", b"fake-video", "video/mp4")},
    )

    assert response.status_code == 202
    payload = response.json()
    task = repository.get_task(payload["task_id"])
    assert task["status"] == "queued"
    assert Path(task["source_video_path"]).read_bytes() == b"fake-video"
    assert payload["events_url"].endswith("/events")
    assert client.get("/api/vision/tasks").json()[0]["id"] == payload["task_id"]


def pixel_observation() -> PixelTrackObservation:
    return PixelTrackObservation(
        frame_index=0,
        timestamp=0,
        point=PixelPoint(x=20, y=60),
        bbox_xyxy=(10, 20, 30, 60),
        detection_confidence=0.9,
        tracking_confidence=0.8,
        semantic_class=SemanticClass.PEDESTRIAN,
        contact_quality=ContactPointQuality.FALLBACK,
    )


def prepare_review_task(
    repository: VisionRepository,
    storage: VisionStorage,
    tmp_path: Path,
) -> str:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"fake-video")
    stored_video = storage.ingest_video("review-task", source)
    from ped_video_analysis.vision.contracts import VideoTaskSpec

    repository.create_task(
        task_id="review-task",
        spec=VideoTaskSpec(
            task_name="Review",
            source_video=source,
            model_id="mixed-flow-v1",
            scene_id="scene-1",
        ),
        source_video_path=stored_video.path,
        source_video_sha256=stored_video.sha256,
    )
    repository.transition("review-task", "preflighted")
    repository.transition("review-task", "queued")
    repository.transition("review-task", "inference_running")
    raw = assemble_pixel_tracks(
        task_id="review-task",
        source_video_sha256=stored_video.sha256,
        model_manifest_sha256="c" * 64,
        video=VideoMetadata(
            source=str(stored_video.path),
            fps=25,
            total_frames=1,
            resolution=(640, 480),
            duration=0.04,
        ),
        assignments=(TrackAssignment(1, pixel_observation()),),
    )
    stored = PixelTrackParquetStore(storage.paths.artifacts_dir / "review-task").write(raw)
    repository.register_artifact(
        task_id="review-task",
        artifact_id=raw.artifact_id,
        stage="inference",
        artifact_type="pixel_tracks",
        path=stored.artifact_dir,
        sha256="d" * 64,
    )
    repository.transition("review-task", "awaiting_review")
    return raw.artifact_id


def test_review_calibration_results_exports_and_sse_api(tmp_path: Path) -> None:
    client, repository, storage, _ = build_client(tmp_path)
    raw_id = prepare_review_task(repository, storage, tmp_path)
    before_review = client.get("/api/vision/tasks/review-task/results").json()
    assert before_review["review_queue"][0]["contact_quality"] == "fallback"
    assert before_review["track_summary"][0]["track_id"] == 1

    reviewed = client.post(
        "/api/vision/tasks/review-task/review",
        json={
            "patch_id": "patch-1",
            "parent_artifact_id": raw_id,
            "operations": [
                {
                    "operation": "move_point",
                    "track_id": 1,
                    "frame_index": 0,
                    "point": {"x": 21, "y": 59},
                }
            ],
        },
    )
    assert reviewed.status_code == 201
    assert reviewed.json()["status"] == "awaiting_calibration"
    assert reviewed.json()["reviewed_artifact_id"].startswith("reviewed-")

    rejected = client.post(
        "/api/vision/tasks/review-task/calibration",
        json={
            "calibration_id": "cal-rejected",
            "scene_id": "scene-1",
            "scene_version": 1,
            "mode": "homography",
            "image_reprojection_rmse_px": 0.8,
            "world_checkpoint_rmse_m": 0.11,
            "checkpoint_count": 4,
            "matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        },
    )
    assert rejected.status_code == 201
    assert rejected.json()["accepted"] is False
    results = client.get("/api/vision/tasks/review-task/results").json()
    assert results["physical_metrics_available"] is False
    assert results["analysis"] is None

    repository.cancel("review-task")
    events = client.get("/api/vision/tasks/review-task/events")
    assert events.status_code == 200
    assert "event: status" in events.text
    assert "cancelled" in events.text
    exports = client.get("/api/vision/tasks/review-task/exports")
    assert exports.status_code == 200
    assert exports.json() == []


def test_scene_versions_are_immutable_and_latest_is_returned(tmp_path: Path) -> None:
    _, _, _, scenes = build_client(tmp_path)
    scene = scenes.get("scene-1")
    scenes.save(scene.model_copy(update={"version": 2, "name": "Updated"}))

    assert scenes.get("scene-1").version == 2
    assert [item.version for item in scenes.list()] == [2]
    assert json.loads(
        (scenes.root / "scene-1.v1.json").read_text(encoding="utf-8")
    )["version"] == 1


def test_homography_calibration_wizard_returns_bound_quality_report(tmp_path: Path) -> None:
    client, _, _, _ = build_client(tmp_path)
    fit = [
        {"pixel": [x * 10 + 50, y * 10 + 50], "world": [x, y]}
        for x, y in ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (2, 2))
    ]
    checkpoints = [
        {"pixel": [x * 10 + 50, y * 10 + 50], "world": [x, y]}
        for x, y in ((0.5, 0.5), (1.5, 0.5), (0.5, 1.5), (1.5, 1.5))
    ]

    response = client.post(
        "/api/vision/scenes/scene-1/calibrate/homography",
        json={"fit_points": fit, "checkpoints": checkpoints},
    )

    assert response.status_code == 200
    report = response.json()
    assert report["scene_id"] == "scene-1"
    assert report["scene_version"] == 1
    assert report["accepted"] is True
    assert report["world_checkpoint_rmse_m"] < 1e-8


def test_pixel_geometry_scene_api_projects_and_saves_world_geometry(
    tmp_path: Path,
) -> None:
    client, _, _, scenes = build_client(tmp_path)

    response = client.post(
        "/api/vision/scenes/from-pixel-geometry",
        json={
            "scene_id": "station-east",
            "version": 1,
            "name": "Station east",
            "camera_fingerprint": "cam-east-001",
            "resolution": [1000, 500],
            "calibration_report": {
                "calibration_id": "cal-scene",
                "scene_id": "station-east",
                "scene_version": 1,
                "mode": "homography",
                "image_reprojection_rmse_px": 0.2,
                "world_checkpoint_rmse_m": 0.05,
                "checkpoint_count": 4,
                "matrix": [[0.01, 0, 0], [0, 0.01, 0], [0, 0, 1]],
            },
            "roi": [[0, 0], [1000, 0], [1000, 500], [0, 500]],
            "zones": {"platform": [[100, 100], [300, 100], [300, 300], [100, 300]]},
            "counting_lines": {"gate": [[500, 0], [500, 500]]},
            "entrances": {},
            "conflict_zones": {},
            "exclusion_zones": {},
        },
    )

    assert response.status_code == 201
    scene = scenes.get("station-east")
    assert scene.roi == ((0.0, 0.0), (10.0, 0.0), (10.0, 5.0), (0.0, 5.0))
    assert scene.zones["platform"] == ((1.0, 1.0), (3.0, 1.0), (3.0, 3.0), (1.0, 3.0))
    assert scene.counting_lines["gate"] == ((5.0, 0.0), (5.0, 5.0))


def test_charuco_upload_api_returns_camera_intrinsics(
    tmp_path: Path,
    monkeypatch,
) -> None:
    client, _, _, _ = build_client(tmp_path)
    captured: dict[str, object] = {}

    def fake_calibrate(image_paths, board_spec):
        captured["image_count"] = len(image_paths)
        captured["board_spec"] = board_spec
        assert all(path.exists() for path in image_paths)
        return CameraIntrinsics(
            camera_matrix=((1000, 0, 320), (0, 1000, 240), (0, 0, 1)),
            distortion=(0.1, -0.05, 0, 0, 0),
            image_size=(640, 480),
            rms_reprojection_error_px=0.3,
            valid_view_count=5,
        )

    monkeypatch.setattr(vision_api_module, "calibrate_charuco_images", fake_calibrate)
    response = client.post(
        "/api/vision/scenes/calibrate/charuco",
        data={
            "squares_x": "7",
            "squares_y": "5",
            "square_length_m": "0.04",
            "marker_length_m": "0.02",
            "dictionary_id": "0",
            "minimum_views": "3",
            "minimum_corners_per_view": "4",
        },
        files=[
            ("images", (f"view-{index}.png", b"image", "image/png"))
            for index in range(3)
        ],
    )

    assert response.status_code == 200
    assert captured["image_count"] == 3
    assert captured["board_spec"].squares_x == 7
    assert response.json()["valid_view_count"] == 5
    assert response.json()["camera_matrix"][0][0] == 1000
