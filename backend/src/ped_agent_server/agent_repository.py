from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from ped_agent.agent.contracts import RunStatus

TERMINAL_STATUSES = {
    RunStatus.COMPLETED.value,
    RunStatus.FAILED.value,
    RunStatus.CANCELLED.value,
    RunStatus.INTERRUPTED.value,
}
ACTIVE_STATUSES = {RunStatus.QUEUED.value, RunStatus.RUNNING.value}


class ActiveRunError(RuntimeError):
    pass


class AgentRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 30000")
        return connection

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                )
                """
            )
            applied = {
                row["version"]
                for row in connection.execute("SELECT version FROM schema_migrations")
            }
            for version, script_path in self._migration_files():
                if version in applied:
                    continue
                connection.executescript(script_path.read_text(encoding="utf-8"))
                connection.execute(
                    "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)",
                    (version, _now()),
                )

    def _migration_files(self) -> list[tuple[int, Path]]:
        root = Path(__file__).with_name("migrations")
        return [(int(path.name.split("_", 1)[0]), path) for path in sorted(root.glob("*.sql"))]

    def journal_mode(self) -> str:
        with self.connect() as connection:
            return str(connection.execute("PRAGMA journal_mode").fetchone()[0]).lower()

    def schema_version(self) -> int:
        with self.connect() as connection:
            row = connection.execute("SELECT MAX(version) FROM schema_migrations").fetchone()
        return int(row[0] or 0)

    def create_conversation(self, title: str | None = None) -> dict[str, Any]:
        conversation_id = str(uuid4())
        timestamp = _now()
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO conversations(id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (conversation_id, title, timestamp, timestamp),
            )
        return self.get_conversation_summary(conversation_id)

    def get_conversation_summary(self, conversation_id: str) -> dict[str, Any]:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()
        if row is None:
            raise KeyError(conversation_id)
        return dict(row)

    def list_conversations(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT c.*,
                       (SELECT status FROM runs r WHERE r.conversation_id = c.id
                        ORDER BY r.created_at DESC LIMIT 1) AS latest_run_status
                FROM conversations c
                ORDER BY c.updated_at DESC, c.id DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_conversation(self, conversation_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            conversation = connection.execute(
                "SELECT * FROM conversations WHERE id = ?",
                (conversation_id,),
            ).fetchone()
            if conversation is None:
                return None
            messages = connection.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at, id",
                (conversation_id,),
            ).fetchall()
            runs = connection.execute(
                "SELECT * FROM runs WHERE conversation_id = ? ORDER BY created_at, id",
                (conversation_id,),
            ).fetchall()
            result = dict(conversation)
            result["messages"] = [self._hydrate_message(connection, row) for row in messages]
            result["runs"] = [self._hydrate_run(row) for row in runs]
            return result

    def add_message(
        self,
        conversation_id: str,
        *,
        role: str,
        content: str,
        answer_document: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        message_id = str(uuid4())
        timestamp = _now()
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO messages(id, conversation_id, role, content, answer_document, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    message_id,
                    conversation_id,
                    role,
                    content,
                    _dump(answer_document) if answer_document is not None else None,
                    timestamp,
                ),
            )
            connection.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (timestamp, conversation_id),
            )
            row = connection.execute(
                "SELECT * FROM messages WHERE id = ?", (message_id,)
            ).fetchone()
        return self._hydrate_message_without_citations(row)

    def create_run(self, conversation_id: str, *, query: str) -> dict[str, Any]:
        run_id = str(uuid4())
        timestamp = _now()
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            if (
                connection.execute(
                    "SELECT 1 FROM conversations WHERE id = ?", (conversation_id,)
                ).fetchone()
                is None
            ):
                raise KeyError(conversation_id)
            active = connection.execute(
                "SELECT id FROM runs WHERE conversation_id = ? AND status IN ('queued', 'running')",
                (conversation_id,),
            ).fetchone()
            if active is not None:
                raise ActiveRunError(f"conversation already has active run {active['id']}")
            connection.execute(
                """
                INSERT INTO runs(id, conversation_id, query, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (run_id, conversation_id, query, RunStatus.QUEUED.value, timestamp, timestamp),
            )
        run = self.get_run(run_id)
        if run is None:
            raise RuntimeError("created run was not persisted")
        return run

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        return self._hydrate_run(row) if row is not None else None

    def set_run_status(
        self,
        run_id: str,
        status: RunStatus,
        *,
        error: str | None = None,
    ) -> None:
        timestamp = _now()
        started_at = timestamp if status is RunStatus.RUNNING else None
        completed_at = timestamp if status.value in TERMINAL_STATUSES else None
        with self.connect() as connection:
            connection.execute(
                """
                UPDATE runs SET status = ?, error = ?, updated_at = ?,
                    started_at = COALESCE(started_at, ?),
                    completed_at = COALESCE(?, completed_at)
                WHERE id = ?
                """,
                (status.value, error, timestamp, started_at, completed_at, run_id),
            )

    def start_run(self, run_id: str) -> bool:
        timestamp = _now()
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                """
                UPDATE runs SET status = ?, started_at = ?, updated_at = ?
                WHERE id = ? AND status = 'queued' AND cancel_requested = 0
                """,
                (RunStatus.RUNNING.value, timestamp, timestamp, run_id),
            )
            if cursor.rowcount != 1:
                return False
            connection.execute(
                "INSERT INTO run_events(run_id, event, payload, created_at) VALUES (?, ?, ?, ?)",
                (
                    run_id,
                    "run.started",
                    _dump({"run_id": run_id, "status": RunStatus.RUNNING.value}),
                    timestamp,
                ),
            )
        return True

    def request_cancel(self, run_id: str) -> bool:
        timestamp = _now()
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                """
                UPDATE runs SET status = ?, cancel_requested = 1,
                    completed_at = ?, updated_at = ?
                WHERE id = ? AND status IN ('queued', 'running')
                """,
                (RunStatus.CANCELLED.value, timestamp, timestamp, run_id),
            )
            if cursor.rowcount != 1:
                return False
            connection.execute(
                "INSERT INTO run_events(run_id, event, payload, created_at) VALUES (?, ?, ?, ?)",
                (run_id, "run.cancelled", _dump({"run_id": run_id}), timestamp),
            )
        return True

    def complete_run(
        self,
        run_id: str,
        *,
        answer_document: dict[str, Any],
        evidence_items: list[dict[str, Any]],
    ) -> str | None:
        timestamp = _now()
        message_id = str(uuid4())
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                """
                UPDATE runs SET status = ?, error = NULL,
                    completed_at = ?, updated_at = ?
                WHERE id = ? AND status = 'running' AND cancel_requested = 0
                """,
                (RunStatus.COMPLETED.value, timestamp, timestamp, run_id),
            )
            if cursor.rowcount != 1:
                return None
            run = connection.execute(
                "SELECT conversation_id FROM runs WHERE id = ?",
                (run_id,),
            ).fetchone()
            conversation_id = str(run["conversation_id"])
            self._save_evidence(connection, run_id, evidence_items)
            connection.execute(
                """
                INSERT INTO messages(
                    id, conversation_id, role, content, answer_document, created_at
                ) VALUES (?, ?, 'assistant', ?, ?, ?)
                """,
                (
                    message_id,
                    conversation_id,
                    str(answer_document["answer_markdown"]),
                    _dump(answer_document),
                    timestamp,
                ),
            )
            for citation in answer_document.get("citations", []):
                connection.execute(
                    """
                    INSERT OR REPLACE INTO message_citations(
                        message_id, label, evidence_id, claim_ids
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        message_id,
                        citation["label"],
                        citation["evidence_id"],
                        _dump(citation.get("claim_ids", [])),
                    ),
                )
            connection.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (timestamp, conversation_id),
            )
            connection.execute(
                "INSERT INTO run_events(run_id, event, payload, created_at) VALUES (?, ?, ?, ?)",
                (
                    run_id,
                    "answer.delta",
                    _dump(
                        {
                            "delta": answer_document["answer_markdown"],
                            "verified": True,
                        }
                    ),
                    timestamp,
                ),
            )
            connection.execute(
                "INSERT INTO run_events(run_id, event, payload, created_at) VALUES (?, ?, ?, ?)",
                (
                    run_id,
                    "run.completed",
                    _dump({"run_id": run_id, "message_id": message_id}),
                    timestamp,
                ),
            )
        return message_id

    def fail_run(self, run_id: str, *, error: str) -> bool:
        timestamp = _now()
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                """
                UPDATE runs SET status = ?, error = ?,
                    completed_at = ?, updated_at = ?
                WHERE id = ? AND status = 'running' AND cancel_requested = 0
                """,
                (RunStatus.FAILED.value, error, timestamp, timestamp, run_id),
            )
            if cursor.rowcount != 1:
                return False
            connection.execute(
                "INSERT INTO run_events(run_id, event, payload, created_at) VALUES (?, ?, ?, ?)",
                (
                    run_id,
                    "run.failed",
                    _dump({"run_id": run_id, "error": "run execution failed"}),
                    timestamp,
                ),
            )
        return True

    def is_cancel_requested(self, run_id: str) -> bool:
        run = self.get_run(run_id)
        return bool(run and run["cancel_requested"])

    def append_event(self, run_id: str, event: str, payload: dict[str, Any]) -> dict[str, Any]:
        timestamp = _now()
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO run_events(run_id, event, payload, created_at) VALUES (?, ?, ?, ?)",
                (run_id, event, _dump(payload), timestamp),
            )
            event_id = int(cursor.lastrowid)
        return {
            "id": event_id,
            "run_id": run_id,
            "event": event,
            "payload": payload,
            "created_at": timestamp,
        }

    def list_events(self, run_id: str, *, after_id: int = 0) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM run_events WHERE run_id = ? AND id > ? ORDER BY id",
                (run_id, after_id),
            ).fetchall()
        return [self._hydrate_event(row) for row in rows]

    def interrupt_active_runs(self) -> list[str]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT id FROM runs WHERE status IN ('queued', 'running') ORDER BY created_at"
            ).fetchall()
        run_ids = [str(row["id"]) for row in rows]
        for run_id in run_ids:
            self.set_run_status(run_id, RunStatus.INTERRUPTED, error="server restarted")
            self.append_event(
                run_id,
                "run.failed",
                {"run_id": run_id, "status": RunStatus.INTERRUPTED.value, "reason": "restart"},
            )
        return run_ids

    def save_evidence(self, run_id: str | None, items: list[dict[str, Any]]) -> None:
        with self.connect() as connection:
            self._save_evidence(connection, run_id, items)

    def link_citation(
        self,
        message_id: str,
        label: str,
        evidence_id: str,
        claim_ids: list[str],
    ) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO message_citations(message_id, label, evidence_id, claim_ids)
                VALUES (?, ?, ?, ?)
                """,
                (message_id, label, evidence_id, _dump(claim_ids)),
            )

    @staticmethod
    def _save_evidence(
        connection: sqlite3.Connection,
        run_id: str | None,
        items: list[dict[str, Any]],
    ) -> None:
        connection.executemany(
            """
            INSERT OR REPLACE INTO evidence_items(
                evidence_id, run_id, origin, title, quote, locator, url, doi,
                resource_id, version_id, chunk_id, publisher, authority,
                retrieved_at, content_hash, score, payload
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    item["evidence_id"],
                    run_id,
                    item["origin"],
                    item["title"],
                    item["quote"],
                    item.get("locator"),
                    item.get("url"),
                    item.get("doi"),
                    item.get("resource_id"),
                    item.get("version_id"),
                    item.get("chunk_id"),
                    item.get("publisher"),
                    item.get("authority", "primary"),
                    str(item["retrieved_at"]),
                    item["content_hash"],
                    float(item.get("score", 0.0)),
                    _dump(item),
                )
                for item in items
            ],
        )

    def _hydrate_message(
        self,
        connection: sqlite3.Connection,
        row: sqlite3.Row,
    ) -> dict[str, Any]:
        result = self._hydrate_message_without_citations(row)
        citations = connection.execute(
            """
            SELECT mc.label, mc.claim_ids, ei.payload
            FROM message_citations mc
            JOIN evidence_items ei ON ei.evidence_id = mc.evidence_id
            WHERE mc.message_id = ? ORDER BY mc.label
            """,
            (row["id"],),
        ).fetchall()
        result["citations"] = [
            {
                "label": citation["label"],
                "claim_ids": json.loads(citation["claim_ids"]),
                "evidence": json.loads(citation["payload"]),
            }
            for citation in citations
        ]
        return result

    @staticmethod
    def _hydrate_message_without_citations(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["answer_document"] = (
            json.loads(result["answer_document"]) if result["answer_document"] else None
        )
        result.setdefault("citations", [])
        return result

    @staticmethod
    def _hydrate_run(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["cancel_requested"] = bool(result["cancel_requested"])
        return result

    @staticmethod
    def _hydrate_event(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["payload"] = json.loads(result["payload"])
        return result


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)
