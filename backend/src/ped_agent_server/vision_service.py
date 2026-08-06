from __future__ import annotations

import asyncio
from typing import Protocol

from ped_agent_server.vision_repository import (
    VISION_TERMINAL_STATUSES,
    VisionRepository,
)


class VisionTaskProcessor(Protocol):
    async def run(
        self,
        task_id: str,
        start_status: str,
        repository: VisionRepository,
    ) -> None: ...


class VisionTaskService:
    def __init__(self, repository: VisionRepository, processor: VisionTaskProcessor):
        self.repository = repository
        self.processor = processor
        self.queue: asyncio.Queue[str | None] = asyncio.Queue()
        self.worker: asyncio.Task[None] | None = None

    async def start(self) -> None:
        if self.worker is not None:
            return
        for task in self.repository.list_tasks():
            status = str(task["status"])
            if status == "queued":
                await self.queue.put(str(task["id"]))
            elif status.endswith("_running") or status == "rendering":
                self.repository.mark_failed(str(task["id"]), "process interrupted by restart")
        self.worker = asyncio.create_task(self._worker_loop())

    async def submit(self, task_id: str) -> dict[str, object]:
        task = self._require_task(task_id)
        if task["status"] == "uploaded":
            task = self.repository.transition(task_id, "preflighted")
        if task["status"] == "preflighted":
            task = self.repository.transition(task_id, "queued")
        if task["status"] != "queued":
            raise ValueError(f"task cannot be submitted from {task['status']}")
        await self.queue.put(task_id)
        return task

    async def retry(self, task_id: str) -> dict[str, object]:
        task = self.repository.queue_retry(task_id)
        await self.queue.put(task_id)
        return task

    async def enqueue_queued(self, task_id: str) -> None:
        task = self._require_task(task_id)
        if task["status"] != "queued":
            raise ValueError(f"task is not queued: {task['status']}")
        await self.queue.put(task_id)

    async def cancel(self, task_id: str) -> dict[str, object]:
        return self.repository.cancel(task_id)

    async def wait_until_idle(self) -> None:
        await self.queue.join()

    async def shutdown(self) -> None:
        if self.worker is None:
            return
        await self.queue.put(None)
        await self.worker
        self.worker = None

    async def _worker_loop(self) -> None:
        while True:
            task_id = await self.queue.get()
            try:
                if task_id is None:
                    return
                task = self.repository.get_task(task_id)
                if task is None or task["status"] != "queued":
                    continue
                started = self.repository.start_queued_stage(task_id)
                try:
                    await self.processor.run(task_id, str(started["status"]), self.repository)
                except Exception as exc:  # noqa: BLE001 - task failures must not stop the queue
                    current = self.repository.get_task(task_id)
                    if current is not None and current["status"] not in VISION_TERMINAL_STATUSES:
                        self.repository.mark_failed(task_id, str(exc))
            finally:
                self.queue.task_done()

    def _require_task(self, task_id: str) -> dict[str, object]:
        task = self.repository.get_task(task_id)
        if task is None:
            raise KeyError(task_id)
        return task


__all__ = ["VisionTaskProcessor", "VisionTaskService"]
