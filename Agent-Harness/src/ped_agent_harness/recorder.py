"""Append-only run event records with a monotonic sequence number."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, JsonValue


class RunEvent(BaseModel):
    seq: int
    run_id: str
    type: str
    at: datetime
    payload: dict[str, JsonValue]


class Recorder(Protocol):
    def emit(self, run_id: str, event_type: str, payload: dict[str, JsonValue]) -> RunEvent: ...


class MemoryRecorder:
    def __init__(self) -> None:
        self.events: list[RunEvent] = []

    def emit(self, run_id: str, event_type: str, payload: dict[str, JsonValue]) -> RunEvent:
        event = RunEvent(
            seq=len(self.events) + 1,
            run_id=run_id,
            type=event_type,
            at=datetime.now(UTC),
            payload=payload,
        )
        self.events.append(event)
        return event


class JsonlRecorder:
    """Writes events.jsonl; refuses to append to an existing file."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("x", encoding="utf-8")
        self._seq = 0

    def emit(self, run_id: str, event_type: str, payload: dict[str, JsonValue]) -> RunEvent:
        self._seq += 1
        event = RunEvent(
            seq=self._seq,
            run_id=run_id,
            type=event_type,
            at=datetime.now(UTC),
            payload=payload,
        )
        self._handle.write(event.model_dump_json() + "\n")
        self._handle.flush()
        return event

    def close(self) -> None:
        self._handle.close()

    def __enter__(self) -> JsonlRecorder:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


def read_events(path: str | Path) -> list[RunEvent]:
    with Path(path).open(encoding="utf-8") as handle:
        return [RunEvent.model_validate(json.loads(line)) for line in handle if line.strip()]
