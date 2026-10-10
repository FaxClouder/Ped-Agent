"""Focused checks for the saved V1 development-rank diagnosis."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnose_v1_dev import classify_sparse_miss, first_complete_rank, write_outputs


def test_sparse_failure_modes_are_distinct() -> None:
    assert classify_sparse_miss([], [{"g1": {"r1"}}], k=5) == "no_fts_candidates"
    wrong = [{"resource_id": "r2"}]
    assert classify_sparse_miss(wrong, [{"g1": {"r1"}}], k=5) == "candidate_wrong_resource"
    late = [{"resource_id": f"other{x}"} for x in range(5)] + [{"resource_id": "r1"}]
    assert classify_sparse_miss(late, [{"g1": {"r1"}}], k=5) == "relevant_below_k"


def test_complete_rank_requires_every_evidence_group() -> None:
    groups = [{"g1": {"r1"}}, {"g2": {"r2", "r3"}}]
    assert first_complete_rank([{"resource_id": "r1"}, {"resource_id": "r3"}], groups) == 2
    assert first_complete_rank([{"resource_id": "r1"}], groups) is None


def test_diagnosis_refuses_existing_directory(tmp_path: Path) -> None:
    output = tmp_path / "run"
    output.mkdir()
    (output / "keep").write_text("unchanged", encoding="utf-8")
    with pytest.raises(FileExistsError):
        write_outputs(output, [], {})
    assert (output / "keep").read_text(encoding="utf-8") == "unchanged"


def test_output_allows_unknown_dense_rank_shift(tmp_path: Path) -> None:
    row = {
        "question_id": "i1-zh", "intent_id": "i1", "language": "zh", "topic": "t",
        "evidence_group_count": 1, "method": "rrf", "complete_evidence_at_5": 1.0,
        "complete_locator_at_5": 1.0, "mrr": 1.0, "ndcg_at_5": 1.0,
        "first_complete_resource_rank": None, "rank_shift_vs_dense": None,
    }
    write_outputs(tmp_path / "run", [row], {"status": "candidate_only"})
    assert (tmp_path / "run" / "failure_cases.md").exists()
