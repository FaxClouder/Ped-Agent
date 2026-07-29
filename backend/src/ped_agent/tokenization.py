from __future__ import annotations

import re

import jieba


def tokenize_for_search(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    tokens: list[str] = []
    for token in jieba.cut(normalized):
        cleaned = token.strip()
        if cleaned and re.search(r"[0-9a-z\u4e00-\u9fff]", cleaned):
            tokens.append(cleaned)
    return " ".join(tokens)
