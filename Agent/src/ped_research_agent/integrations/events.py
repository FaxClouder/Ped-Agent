"""Bridge the fixed graph's async event callback to an explicitly supplied recorder."""

from __future__ import annotations

from pydantic import JsonValue, TypeAdapter

from ped_agent_harness.recorder import Recorder
from ped_contracts.evidence import EvidenceItem

_PAYLOAD = TypeAdapter(dict[str, JsonValue])


class AgentEventBridge:
    def __init__(self, recorder: Recorder, *, run_id: str) -> None:
        self.recorder = recorder
        self.run_id = run_id

    async def emit(self, event_type: str, payload: dict[str, object]) -> None:
        self.recorder.emit(self.run_id, event_type, _PAYLOAD.validate_python(payload))


class DisabledExternalSearch:
    """Explicit policy for offline/local-only compositions, not an error fallback."""

    async def search(self, query: str) -> list[EvidenceItem]:
        return []
