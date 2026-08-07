from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

from ped_video_analysis.vision.contracts import VideoTaskSpec

VISION_STATUSES = (
    "uploaded",
    "preflighted",
    "queued",
    "inference_running",
    "awaiting_review",
    "awaiting_calibration",
    "projection_running",
    "postprocess_running",
    "analysis_running",
    "rendering",
    "completed",
    "failed",
    "cancelled",
)
VISION_TERMINAL_STATUSES = frozenset({"completed", "failed", "cancelled"})
STAGE_ORDER = (
    "inference",
    "review",
    "calibration",
    "projection",
    "postprocess",
    "analysis",
    "rendering",
)

_ALLOWED_TRANSITIONS = {
    "uploaded": {"preflighted", "failed", "cancelled"},
    "preflighted": {"queued", "failed", "cancelled"},
    "queued": {"inference_running", "failed", "cancelled"},
    "inference_running": {"awaiting_review", "failed", "cancelled"},
    "awaiting_review": {
        "awaiting_calibration",
        "projection_running",
        "failed",
        "cancelled",
    },
    "awaiting_calibration": {"projection_running", "failed", "cancelled"},
    "projection_running": {"postprocess_running", "failed", "cancelled"},
    "postprocess_running": {"analysis_running", "failed", "cancelled"},
    "analysis_running": {"rendering", "failed", "cancelled"},
    "rendering": {"completed", "failed", "cancelled"},
    "completed": set(),
    "failed": set(),
    "cancelled": set(),
}


class InvalidVisionTransition(ValueError):
    pass


class VisionRepository:
    def __init__(self, path: Path):
        self.path = path.resolve()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        migration = Path(__file__).parent / "vision_migrations" / "001_initial.sql"
        with closing(self.connect()) as connection, connection:
            connection.executescript(migration.read_text(encoding="utf-8"))

    def create_task(
        self,
        *,
        task_id: str,
        spec: VideoTaskSpec,
        source_video_path: Path,
        source_video_sha256: str,
    ) -> dict[str, object]:
        now = _now()
        with closing(self.connect()) as connection, connection:
            connection.execute(
                """
                INSERT INTO vision_tasks(
                    id, task_name, status, resume_status, error, spec_json,
                    source_video_path, source_video_sha256, model_id, scene_id,
                    created_at, updated_at
                ) VALUES (?, ?, 'uploaded', NULL, NULL, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    spec.task_name,
                    spec.model_dump_json(),
                    str(source_video_path),
                    source_video_sha256,
                    spec.model_id,
                    spec.scene_id,
                    now,
                    now,
                ),
            )
            self._add_event(connection, task_id, "uploaded", "status", {})
        task = self.get_task(task_id)
        if task is None:
            raise RuntimeError("task insert failed")
        return task

    def get_task(self, task_id: str) -> dict[str, object] | None:
        with closing(self.connect()) as connection:
            row = connection.execute(
                "SELECT * FROM vision_tasks WHERE id = ?", (task_id,)
            ).fetchone()
        return self._task(row) if row is not None else None

    def list_tasks(self) -> list[dict[str, object]]:
        with closing(self.connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM vision_tasks ORDER BY created_at DESC"
            ).fetchall()
        return [self._task(row) for row in rows]

    def transition(
        self,
        task_id: str,
        new_status: str,
        *,
        payload: dict[str, object] | None = None,
    ) -> dict[str, object]:
        if new_status not in VISION_STATUSES:
            raise ValueError(f"unknown vision status: {new_status}")
        with closing(self.connect()) as connection, connection:
            row = self._require_task(connection, task_id)
            current = str(row["status"])
            if new_status not in _ALLOWED_TRANSITIONS[current]:
                raise InvalidVisionTransition(f"{current} cannot transition to {new_status}")
            connection.execute(
                "UPDATE vision_tasks SET status = ?, updated_at = ? WHERE id = ?",
                (new_status, _now(), task_id),
            )
            self._add_event(connection, task_id, new_status, "status", payload or {})
        return self._require_result(task_id)

    def mark_failed(self, task_id: str, error: str) -> dict[str, object]:
        with closing(self.connect()) as connection, connection:
            row = self._require_task(connection, task_id)
            current = str(row["status"])
            if current in VISION_TERMINAL_STATUSES:
                raise InvalidVisionTransition(f"terminal task cannot fail from {current}")
            connection.execute(
                """
                UPDATE vision_tasks
                SET status = 'failed', resume_status = ?, error = ?, updated_at = ?
                WHERE id = ?
                """,
                (current, error, _now(), task_id),
            )
            self._add_event(connection, task_id, "failed", "error", {"message": error})
        return self._require_result(task_id)

    def cancel(self, task_id: str) -> dict[str, object]:
        with closing(self.connect()) as connection, connection:
            row = self._require_task(connection, task_id)
            current = str(row["status"])
            if current in VISION_TERMINAL_STATUSES:
                raise InvalidVisionTransition(f"terminal task cannot cancel from {current}")
            connection.execute(
                """
                UPDATE vision_tasks
                SET status = 'cancelled', resume_status = ?, updated_at = ?
                WHERE id = ?
                """,
                (current, _now(), task_id),
            )
            self._add_event(connection, task_id, "cancelled", "status", {})
        return self._require_result(task_id)

    def queue_retry(self, task_id: str) -> dict[str, object]:
        with closing(self.connect()) as connection, connection:
            row = self._require_task(connection, task_id)
            current = str(row["status"])
            if current not in {"failed", "cancelled"}:
                raise InvalidVisionTransition(f"retry is not allowed from {current}")
            connection.execute(
                """
                UPDATE vision_tasks
                SET status = 'queued', error = NULL, updated_at = ?
                WHERE id = ?
                """,
                (_now(), task_id),
            )
            self._add_event(
                connection,
                task_id,
                "queued",
                "retry",
                {"resume_status": row["resume_status"]},
            )
        return self._require_result(task_id)

    def start_queued_stage(self, task_id: str) -> dict[str, object]:
        with closing(self.connect()) as connection, connection:
            row = self._require_task(connection, task_id)
            if row["status"] != "queued":
                raise InvalidVisionTransition("task is not queued")
            target = str(row["resume_status"] or "inference_running")
            if target not in {
                "inference_running",
                "projection_running",
                "postprocess_running",
                "analysis_running",
                "rendering",
            }:
                target = "inference_running"
            connection.execute(
                "UPDATE vision_tasks SET status = ?, updated_at = ? WHERE id = ?",
                (target, _now(), task_id),
            )
            self._add_event(connection, task_id, target, "status", {"resumed": True})
        return self._require_result(task_id)

    def queue_stage(self, task_id: str, *, resume_status: str) -> dict[str, object]:
        if resume_status not in {
            "inference_running",
            "projection_running",
            "postprocess_running",
            "analysis_running",
            "rendering",
        }:
            raise ValueError(f"invalid resumable status: {resume_status}")
        with closing(self.connect()) as connection, connection:
            row = self._require_task(connection, task_id)
            current = str(row["status"])
            if current not in {
                "awaiting_review",
                "awaiting_calibration",
                "completed",
                "failed",
                "cancelled",
            }:
                raise InvalidVisionTransition(f"cannot queue stage from {current}")
            connection.execute(
                """
                UPDATE vision_tasks
                SET status = 'queued', resume_status = ?, error = NULL, updated_at = ?
                WHERE id = ?
                """,
                (resume_status, _now(), task_id),
            )
            self._add_event(
                connection,
                task_id,
                "queued",
                "rerun",
                {"resume_status": resume_status},
            )
        return self._require_result(task_id)

    def register_artifact(
        self,
        *,
        task_id: str,
        artifact_id: str,
        stage: str,
        artifact_type: str,
        path: Path,
        sha256: str,
        parent_artifact_id: str | None = None,
    ) -> dict[str, object]:
        if stage not in STAGE_ORDER:
            raise ValueError(f"unknown artifact stage: {stage}")
        with closing(self.connect()) as connection, connection:
            self._require_task(connection, task_id)
            existing = connection.execute(
                "SELECT artifact_id FROM vision_artifacts WHERE artifact_id = ?",
                (artifact_id,),
            ).fetchone()
            if existing is not None:
                raise ValueError(f"immutable artifact already indexed: {artifact_id}")
            connection.execute(
                """
                INSERT INTO vision_artifacts(
                    artifact_id, task_id, stage, artifact_type, path, sha256,
                    parent_artifact_id, active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
                """,
                (
                    artifact_id,
                    task_id,
                    stage,
                    artifact_type,
                    str(path),
                    sha256,
                    parent_artifact_id,
                    _now(),
                ),
            )
            self._add_event(
                connection,
                task_id,
                str(self._require_task(connection, task_id)["status"]),
                "artifact",
                {"artifact_id": artifact_id, "artifact_type": artifact_type},
            )
        return self.get_artifact(artifact_id) or {}

    def get_artifact(self, artifact_id: str) -> dict[str, object] | None:
        with closing(self.connect()) as connection:
            row = connection.execute(
                "SELECT * FROM vision_artifacts WHERE artifact_id = ?", (artifact_id,)
            ).fetchone()
        return self._artifact(row) if row is not None else None

    def latest_artifact(
        self, task_id: str, artifact_type: str
    ) -> dict[str, object] | None:
        with closing(self.connect()) as connection:
            row = connection.execute(
                """
                SELECT * FROM vision_artifacts
                WHERE task_id = ? AND artifact_type = ? AND active = 1
                ORDER BY created_at DESC, artifact_id DESC LIMIT 1
                """,
                (task_id, artifact_type),
            ).fetchone()
        return self._artifact(row) if row is not None else None

    def save_review_patch(
        self,
        *,
        task_id: str,
        patch_id: str,
        parent_artifact_id: str,
        patch_json: str,
    ) -> None:
        with closing(self.connect()) as connection, connection:
            self._require_task(connection, task_id)
            connection.execute(
                """
                INSERT INTO vision_review_patches(
                    patch_id, task_id, parent_artifact_id, patch_json, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (patch_id, task_id, parent_artifact_id, patch_json, _now()),
            )

    def list_artifacts(
        self, task_id: str, *, active_only: bool = True
    ) -> list[dict[str, object]]:
        query = "SELECT * FROM vision_artifacts WHERE task_id = ?"
        if active_only:
            query += " AND active = 1"
        query += " ORDER BY created_at, artifact_id"
        with closing(self.connect()) as connection:
            rows = connection.execute(query, (task_id,)).fetchall()
        return [self._artifact(row) for row in rows]

    def invalidate_downstream(self, task_id: str, *, from_stage: str) -> None:
        if from_stage not in STAGE_ORDER:
            raise ValueError(f"unknown stage: {from_stage}")
        downstream = STAGE_ORDER[STAGE_ORDER.index(from_stage) + 1 :]
        if not downstream:
            return
        placeholders = ",".join("?" for _ in downstream)
        with closing(self.connect()) as connection, connection:
            self._require_task(connection, task_id)
            connection.execute(
                f"""
                UPDATE vision_artifacts SET active = 0
                WHERE task_id = ? AND stage IN ({placeholders}) AND active = 1
                """,
                (task_id, *downstream),
            )
            self._add_event(
                connection,
                task_id,
                str(self._require_task(connection, task_id)["status"]),
                "artifacts_invalidated",
                {"from_stage": from_stage},
            )

    def invalidate_from(self, task_id: str, *, from_stage: str) -> None:
        if from_stage not in STAGE_ORDER:
            raise ValueError(f"unknown stage: {from_stage}")
        stages = STAGE_ORDER[STAGE_ORDER.index(from_stage) :]
        placeholders = ",".join("?" for _ in stages)
        with closing(self.connect()) as connection, connection:
            self._require_task(connection, task_id)
            connection.execute(
                f"""
                UPDATE vision_artifacts SET active = 0
                WHERE task_id = ? AND stage IN ({placeholders}) AND active = 1
                """,
                (task_id, *stages),
            )
            self._add_event(
                connection,
                task_id,
                str(self._require_task(connection, task_id)["status"]),
                "artifacts_invalidated",
                {"from_stage": from_stage, "inclusive": True},
            )

    def list_events(self, task_id: str, *, after_id: int = 0) -> list[dict[str, object]]:
        with closing(self.connect()) as connection:
            rows = connection.execute(
                """
                SELECT * FROM vision_events
                WHERE task_id = ? AND id > ? ORDER BY id
                """,
                (task_id, after_id),
            ).fetchall()
        return [
            {
                "id": int(row["id"]),
                "task_id": row["task_id"],
                "status": row["status"],
                "event": row["event"],
                "payload": json.loads(row["payload_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    @staticmethod
    def _add_event(
        connection: sqlite3.Connection,
        task_id: str,
        status: str,
        event: str,
        payload: dict[str, object],
    ) -> None:
        connection.execute(
            """
            INSERT INTO vision_events(task_id, status, event, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (task_id, status, event, json.dumps(payload), _now()),
        )

    @staticmethod
    def _require_task(connection: sqlite3.Connection, task_id: str) -> sqlite3.Row:
        row = connection.execute(
            "SELECT * FROM vision_tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if row is None:
            raise KeyError(task_id)
        return row

    def _require_result(self, task_id: str) -> dict[str, object]:
        task = self.get_task(task_id)
        if task is None:
            raise KeyError(task_id)
        return task

    @staticmethod
    def _task(row: sqlite3.Row) -> dict[str, object]:
        return {
            "id": row["id"],
            "task_name": row["task_name"],
            "status": row["status"],
            "resume_status": row["resume_status"],
            "error": row["error"],
            "spec": json.loads(row["spec_json"]),
            "source_video_path": row["source_video_path"],
            "source_video_sha256": row["source_video_sha256"],
            "model_id": row["model_id"],
            "scene_id": row["scene_id"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    @staticmethod
    def _artifact(row: sqlite3.Row) -> dict[str, object]:
        return {
            "artifact_id": row["artifact_id"],
            "task_id": row["task_id"],
            "stage": row["stage"],
            "artifact_type": row["artifact_type"],
            "path": row["path"],
            "sha256": row["sha256"],
            "parent_artifact_id": row["parent_artifact_id"],
            "active": bool(row["active"]),
            "created_at": row["created_at"],
        }


def _now() -> str:
    return datetime.now(UTC).isoformat()


__all__ = [
    "STAGE_ORDER",
    "VISION_STATUSES",
    "VISION_TERMINAL_STATUSES",
    "InvalidVisionTransition",
    "VisionRepository",
]
