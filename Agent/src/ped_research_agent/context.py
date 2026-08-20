from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True)
class ResearchQuery:
    """One reproducible question-answering experiment input."""

    query: str
    run_id: str = field(default_factory=lambda: str(uuid4()))
    recent_messages: list[dict[str, object]] = field(default_factory=list)
    previous_evidence_ids: list[str] = field(default_factory=list)

    def validated_run_id(self) -> UUID:
        return UUID(self.run_id)
