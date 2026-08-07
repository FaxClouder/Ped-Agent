from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from ped_video_analysis.vision.contracts import VideoTaskSpec

from ped_agent_server.vision_repository import VisionRepository
from ped_agent_server.vision_service import VisionTaskService
from ped_agent_server.vision_storage import VisionStorage


def add_task(repository: VisionRepository, tmp_path: Path, task_id: str) -> None:
    source = tmp_path / f"{task_id}.mp4"
    source.write_bytes(task_id.encode())
    stored = VisionStorage(tmp_path / "storage").ingest_video(task_id, source)
    repository.create_task(
        task_id=task_id,
        spec=VideoTaskSpec(
            task_name=task_id,
            source_video=source,
            model_id="mixed-flow-v1",
            scene_id="scene-1",
        ),
        source_video_path=stored.path,
        source_video_sha256=stored.sha256,
    )


class SerialProcessor:
    def __init__(self):
        self.running = 0
        self.max_running = 0
        self.calls: list[tuple[str, str]] = []

    async def run(
        self,
        task_id: str,
        start_status: str,
        repository: VisionRepository,
    ) -> None:
        self.running += 1
        self.max_running = max(self.max_running, self.running)
        self.calls.append((task_id, start_status))
        await asyncio.sleep(0.02)
        if repository.get_task(task_id)["status"] != "cancelled":
            repository.transition(task_id, "awaiting_review")
        self.running -= 1


@pytest.mark.asyncio
async def test_service_runs_tasks_through_one_worker(tmp_path: Path) -> None:
    repository = VisionRepository(tmp_path / "vision.sqlite3")
    repository.initialize()
    add_task(repository, tmp_path, "task-1")
    add_task(repository, tmp_path, "task-2")
    processor = SerialProcessor()
    service = VisionTaskService(repository, processor)
    await service.start()

    await service.submit("task-1")
    await service.submit("task-2")
    await service.wait_until_idle()
    await service.shutdown()

    assert processor.max_running == 1
    assert processor.calls == [
        ("task-1", "inference_running"),
        ("task-2", "inference_running"),
    ]
    assert repository.get_task("task-1")["status"] == "awaiting_review"
    assert repository.get_task("task-2")["status"] == "awaiting_review"


class FailingProcessor:
    async def run(
        self,
        task_id: str,
        start_status: str,
        repository: VisionRepository,
    ) -> None:
        raise RuntimeError("inference failed")


@pytest.mark.asyncio
async def test_service_records_failure_and_requeues_from_checkpoint(tmp_path: Path) -> None:
    repository = VisionRepository(tmp_path / "vision.sqlite3")
    repository.initialize()
    add_task(repository, tmp_path, "task-1")
    failing = VisionTaskService(repository, FailingProcessor())
    await failing.start()
    await failing.submit("task-1")
    await failing.wait_until_idle()
    await failing.shutdown()

    assert repository.get_task("task-1")["status"] == "failed"
    assert repository.get_task("task-1")["resume_status"] == "inference_running"

    processor = SerialProcessor()
    retrying = VisionTaskService(repository, processor)
    await retrying.start()
    await retrying.retry("task-1")
    await retrying.wait_until_idle()
    await retrying.shutdown()

    assert processor.calls == [("task-1", "inference_running")]
    assert repository.get_task("task-1")["status"] == "awaiting_review"


class BlockingProcessor:
    def __init__(self):
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def run(
        self,
        task_id: str,
        start_status: str,
        repository: VisionRepository,
    ) -> None:
        self.started.set()
        await self.release.wait()


@pytest.mark.asyncio
async def test_cancel_keeps_terminal_state_when_running_stage_returns(tmp_path: Path) -> None:
    repository = VisionRepository(tmp_path / "vision.sqlite3")
    repository.initialize()
    add_task(repository, tmp_path, "task-1")
    processor = BlockingProcessor()
    service = VisionTaskService(repository, processor)
    await service.start()
    await service.submit("task-1")
    await processor.started.wait()

    await service.cancel("task-1")
    processor.release.set()
    await service.wait_until_idle()
    await service.shutdown()

    task = repository.get_task("task-1")
    assert task["status"] == "cancelled"
    assert task["resume_status"] == "inference_running"


@pytest.mark.asyncio
async def test_service_marks_rendering_interrupted_by_restart_as_failed(
    tmp_path: Path,
) -> None:
    repository = VisionRepository(tmp_path / "vision.sqlite3")
    repository.initialize()
    add_task(repository, tmp_path, "task-1")
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

    service = VisionTaskService(repository, SerialProcessor())
    await service.start()
    await service.shutdown()

    task = repository.get_task("task-1")
    assert task["status"] == "failed"
    assert task["resume_status"] == "rendering"
