"""A candidate lexical rerun must preserve RRF rank arithmetic and output isolation."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare_lexical_candidate import fuse_rrf, guard_output


def test_rrf_uses_child_rank_from_both_lists() -> None:
    result = fuse_rrf(["a", "b"], ["b", "c"], rrf_k=60)
    assert result[0] == "b"
    assert set(result) == {"a", "b", "c"}


def test_existing_output_is_preserved(tmp_path: Path) -> None:
    output = tmp_path / "run"
    output.mkdir()
    with pytest.raises(FileExistsError):
        guard_output(output)
