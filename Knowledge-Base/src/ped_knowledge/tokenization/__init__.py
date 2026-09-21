"""Deterministic token counters used by chunking and retrieval policies."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Protocol

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+|[\u3400-\u9fff]|[^\s]")


class TokenCounter(Protocol):
    """Minimal tokenizer contract needed by the chunker."""

    @property
    def fingerprint(self) -> str: ...

    def encode(self, text: str) -> list[int]: ...

    def decode(self, token_ids: list[int]) -> str: ...

    def count(self, text: str) -> int: ...


class RegexTokenCounter:
    """Counter that preserves the repository's original regex semantics."""

    fingerprint = "regex-token-v1"

    def __init__(self) -> None:
        self._last_tokens: list[str] = []

    def encode(self, text: str) -> list[int]:
        self._last_tokens = [match.group(0) for match in TOKEN_PATTERN.finditer(text)]
        return list(range(len(self._last_tokens)))

    def decode(self, token_ids: list[int]) -> str:
        return "".join(self._last_tokens[token_id] for token_id in token_ids)

    def count(self, text: str) -> int:
        return len(TOKEN_PATTERN.findall(text))


class HuggingFaceTokenCounter:
    """Counter backed by a pinned local Hugging Face tokenizer file."""

    def __init__(self, tokenizer: object, *, tokenizer_sha256: str) -> None:
        self._tokenizer = tokenizer
        self._tokenizer_sha256 = tokenizer_sha256

    @property
    def fingerprint(self) -> str:
        return f"hf-tokenizer:{self._tokenizer_sha256}"

    @classmethod
    def from_local_path(
        cls,
        path: Path,
        *,
        expected_sha256: str | None = None,
    ) -> HuggingFaceTokenCounter:
        tokenizer_path = path / "tokenizer.json" if path.is_dir() else path
        if not tokenizer_path.is_file():
            raise FileNotFoundError(f"tokenizer file not found: {tokenizer_path}")
        actual_sha256 = hashlib.sha256(tokenizer_path.read_bytes()).hexdigest()
        if expected_sha256 is not None and actual_sha256 != expected_sha256:
            raise ValueError(
                "tokenizer SHA-256 mismatch: "
                f"expected {expected_sha256}, got {actual_sha256}"
            )

        from tokenizers import Tokenizer

        return cls(
            Tokenizer.from_file(str(tokenizer_path)),
            tokenizer_sha256=actual_sha256,
        )

    def encode(self, text: str) -> list[int]:
        return list(self._tokenizer.encode(text).ids)  # type: ignore[attr-defined]

    def decode(self, token_ids: list[int]) -> str:
        return str(self._tokenizer.decode(token_ids))  # type: ignore[attr-defined]

    def count(self, text: str) -> int:
        return len(self.encode(text))


class JiebaLexicalAnalyzer:
    """Versioned bilingual analyzer with isolated jieba state."""

    def __init__(
        self,
        *,
        domain_terms_path: Path | None = None,
        stopwords_path: Path | None = None,
        version: str = "jieba-lexical-v1",
    ) -> None:
        try:
            import jieba
        except ImportError as exc:
            raise RuntimeError("jieba is required for multilingual FTS tokenization") from exc

        self.version = version
        self.domain_terms_path = domain_terms_path
        self.stopwords_path = stopwords_path
        self._tokenizer = jieba.Tokenizer()
        self._domain_terms = _word_list(domain_terms_path)
        self._stopwords = set(_word_list(stopwords_path))
        for term in self._domain_terms:
            self._tokenizer.add_word(term, freq=10_000_000)
        payload = {
            "version": version,
            "domain_terms_sha256": _file_hash(domain_terms_path),
            "stopwords_sha256": _file_hash(stopwords_path),
        }
        normalized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        self._fingerprint = hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @property
    def fingerprint(self) -> str:
        return f"{self.version}:{self._fingerprint}"

    def analyze(self, text: str) -> list[str]:
        normalized = re.sub(r"\s+", " ", text.strip().lower())
        tokens: list[str] = []
        for token in self._tokenizer.cut(normalized):
            cleaned = token.strip()
            if (
                cleaned
                and cleaned not in self._stopwords
                and re.search(r"[0-9a-z\u3400-\u9fff]", cleaned)
            ):
                tokens.append(cleaned)
        return tokens


def _word_list(path: Path | None) -> list[str]:
    if path is None:
        return []
    if not path.is_file():
        raise FileNotFoundError(f"lexical resource not found: {path}")
    return [
        line.strip().lower()
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def _file_hash(path: Path | None) -> str:
    if path is None:
        return hashlib.sha256(b"").hexdigest()
    return hashlib.sha256(path.read_bytes()).hexdigest()


__all__ = [
    "HuggingFaceTokenCounter",
    "JiebaLexicalAnalyzer",
    "RegexTokenCounter",
    "TOKEN_PATTERN",
    "TokenCounter",
]
