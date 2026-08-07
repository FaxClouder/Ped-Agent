from __future__ import annotations

from pathlib import Path

import pytest
from ped_video_analysis.vision.contracts import VideoTaskSpec

from ped_agent_server.vision_repository import (
    InvalidVisionTransition,
    VisionRepository,
)
from ped_agent_server.vision_storage import VisionStorage


def create_task(repository: VisionRepository, tmp_path: Path) -> dict[str, object]:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"video-content")
    stored = VisionStorage(tmp_path / "vision").ingest_video("task-1", source)
    return repository.create_task(
        task_id="task-1",
        spec=VideoTaskSpec(
            task_name="Morning flow",
            source_video=source,
            model_id="mixed-flow-v1",
            scene_id="scene-1",
        ),
        source_video_path=stored.path,
        source_video_sha256=stored.sha256,
    )


def test_repository_persists_state_events_and_immutable_artifacts(tmp_path: Path) -> None:
    repository = VisionRepository(tmp_path / "vision.sqlite3")
    repository.initialize()
    task = create_task(repository, tmp_path)

    repository.transition("task-1", "preflighted")
    repository.transition("task-1", "queued")
    repository.register_artifact(
        task_id="task-1",
        artifact_id="pixel-1",
        stage="inference",
        artifact_type="pixel_tracks",
        path=tmp_path / "pixel-1" / "metadata.json",
        sha256="a" * 64,
    )

    assert task["status"] == "uploaded"
    assert repository.get_task("task-1")["status"] == "queued"
    status_events = [
        event for event in repository.list_events("task-1") if event["event"] == "status"
    ]
    assert [event["status"] for event in status_events] == [
        "uploaded",
        "preflighted",
        "queued",
    ]
    assert repository.list_artifacts("task-1")[0]["active"] is True
    with pytest.raises(ValueError, match="immutable"):
        repository.register_artifact(
            task_id="task-1",
            artifact_id="pixel-1",
            stage="inference",
            artifact_type="pixel_tracks",
            path=tmp_path / "changed.json",
            sha256="b" * 64,
        )


def test_repository_enforces_status_flow_and_preserves_retry_checkpoint(tmp_path: Path) -> None:
    repository = VisionRepository(tmp_path / "vision.sqlite3")
    repository.initialize()
    create_task(repository, tmp_path)

    with pytest.raises(InvalidVisionTransition, match="uploaded.*analysis_running"):
        repository.transition("task-1", "analysis_running")

    repository.transition("task-1", "preflighted")
    repository.transition("task-1", "queued")
    repository.transition("task-1", "inference_running")
    repository.mark_failed("task-1", "GPU out of memory")

    failed = repository.get_task("task-1")
    assert failed["status"] == "failed"
    assert failed["resume_status"] == "inference_running"
    assert failed["error"] == "GPU out of memory"

    retried = repository.queue_retry("task-1")
    assert retried["status"] == "queued"
    assert retried["resume_status"] == "inference_running"
    assert retried["error"] is None


def test_calibration_revision_only_invalidates_projection_and_downstream(tmp_path: Path) -> None:
    repository = VisionRepository(tmp_path / "vision.sqlite3")
    repository.initialize()
    create_task(repository, tmp_path)
    artifacts = (
        ("pixel-1", "inference", "pixel_tracks"),
        ("reviewed-1", "review", "reviewed_pixel_tracks"),
        ("cal-1", "calibration", "calibration_report"),
        ("world-1", "projection", "world_tracks"),
        ("processed-1", "postprocess", "processed_world_tracks"),
        ("analysis-1", "analysis", "analysis_bundle"),
        ("figures-1", "rendering", "figure_manifest"),
    )
    for artifact_id, stage, artifact_type in artifacts:
        repository.register_artifact(
            task_id="task-1",
            artifact_id=artifact_id,
            stage=stage,
            artifact_type=artifact_type,
            path=tmp_path / artifact_id,
            sha256="a" * 64,
        )

    repository.invalidate_downstream("task-1", from_stage="calibration")

    active = {
        item["artifact_id"]: item["active"]
        for item in repository.list_artifacts("task-1", active_only=False)
    }
    assert active["pixel-1"] is True
    assert active["reviewed-1"] is True
    assert active["cal-1"] is True
    assert active["world-1"] is False
    assert active["processed-1"] is False
    assert active["analysis-1"] is False
    assert active["figures-1"] is False


def test_cancelled_task_is_terminal_until_explicit_retry(tmp_path: Path) -> None:
    repository = VisionRepository(tmp_path / "vision.sqlite3")
    repository.initialize()
    create_task(repository, tmp_path)
    repository.transition("task-1", "preflighted")
    repository.transition("task-1", "queued")

    repository.cancel("task-1")

    assert repository.get_task("task-1")["status"] == "cancelled"
    with pytest.raises(InvalidVisionTransition):
        repository.transition("task-1", "inference_running")
    assert repository.queue_retry("task-1")["status"] == "queued"


def test_storage_copies_source_video_but_has_no_result_video_directory(tmp_path: Path) -> None:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"video-content")
    storage = VisionStorage(tmp_path / "vision")

    stored = storage.ingest_video("task-1", source)

    assert stored.path.read_bytes() == b"video-content"
    assert stored.path != source
    assert stored.sha256 == "b4367c8908484308c443753ed4d99261251cb04f8707b1d1d189c7a87b556141"
    assert not list((tmp_path / "vision").rglob("annotated*.mp4"))
