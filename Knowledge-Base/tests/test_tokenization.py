from __future__ import annotations

from pathlib import Path

import pytest

from ped_knowledge.tokenization import HuggingFaceTokenCounter, RegexTokenCounter


def test_regex_counter_preserves_v1_counting_semantics() -> None:
    counter = RegexTokenCounter()

    assert counter.count("abc 中文!") == 4
    assert counter.fingerprint == "regex-token-v1"


def test_local_tokenizer_rejects_a_mismatched_fingerprint(tmp_path: Path) -> None:
    tokenizer_file = tmp_path / "tokenizer.json"
    tokenizer_file.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        HuggingFaceTokenCounter.from_local_path(
            tmp_path,
            expected_sha256="0" * 64,
        )
