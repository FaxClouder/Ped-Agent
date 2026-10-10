from __future__ import annotations

from pathlib import Path

import pytest

from ped_knowledge.tokenization import (
    EnglishLexicalAnalyzer,
    HuggingFaceTokenCounter,
    RegexTokenCounter,
)


def test_english_analyzer_matches_the_fixed_protocol_samples() -> None:
    analyzer = EnglishLexicalAnalyzer()

    assert analyzer.analyze("Bottleneck width 0.9 m") == [
        "bottleneck",
        "width",
        "0",
        "9",
        "m",
    ]
    assert analyzer.analyze("BGE-M3 reranker-v2") == [
        "bge",
        "m",
        "3",
        "reranker",
        "v",
        "2",
    ]


def test_english_analyzer_normalizes_nfkc_before_tokenizing() -> None:
    analyzer = EnglishLexicalAnalyzer()

    # U+FB02 LATIN SMALL LIGATURE FL and a fullwidth digit both fold under NFKC.
    assert analyzer.analyze("ﬂow １.2 persons/m/s") == [
        "flow",
        "1",
        "2",
        "persons",
        "m",
        "s",
    ]


def test_english_analyzer_applies_no_stopwords_or_stemming() -> None:
    analyzer = EnglishLexicalAnalyzer()

    assert analyzer.analyze("the studies of the evacuations") == [
        "the",
        "studies",
        "of",
        "the",
        "evacuations",
    ]


def test_english_analyzer_drops_non_latin_script() -> None:
    analyzer = EnglishLexicalAnalyzer()

    assert analyzer.analyze("density 密度 2.5") == ["density", "2", "5"]


def test_english_analyzer_fingerprint_is_stable_and_versioned() -> None:
    first = EnglishLexicalAnalyzer().fingerprint
    second = EnglishLexicalAnalyzer().fingerprint

    assert first == second
    assert first.startswith("english-lexical-v1:")
    assert first != EnglishLexicalAnalyzer(version="english-lexical-v2").fingerprint


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
