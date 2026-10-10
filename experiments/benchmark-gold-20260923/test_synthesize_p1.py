"""Synthesis keeps intent pairs and rejects silent missing results."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from synthesize_p1 import index_rows, guard_output, verify_aggregate


def test_index_rows_rejects_duplicate_query_method() -> None:
    row = {"question_id": "i-en", "method": "bm25"}
    with pytest.raises(ValueError, match="duplicate"):
        index_rows([row, row])


def test_synthesis_refuses_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "existing"
    output.mkdir()
    with pytest.raises(FileExistsError):
        guard_output(output)


def test_summary_must_match_per_query_metrics() -> None:
    rows = [{"question_id": "i-en", "method": "bm25", "language": "en",
             "metrics": {"complete_evidence_at_5": 1.0}}]
    verify_aggregate(rows, {"bm25/en": {"complete_evidence_at_5": 1.0}})
    with pytest.raises(ValueError, match="summary"):
        verify_aggregate(rows, {"bm25/en": {"complete_evidence_at_5": 0.0}})
