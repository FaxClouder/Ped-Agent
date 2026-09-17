"""Deterministic token counters used by chunking and retrieval policies."""

from __future__ import annotations

import hashlib
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
    ) -> "HuggingFaceTokenCounter":
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


__all__ = [
    "HuggingFaceTokenCounter",
    "RegexTokenCounter",
    "TOKEN_PATTERN",
    "TokenCounter",
]
