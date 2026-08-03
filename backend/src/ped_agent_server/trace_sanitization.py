from __future__ import annotations

import re
from typing import Any

REDACTED = "[REDACTED]"
BLOCKED_KEYS = {
    "api_key",
    "authorization",
    "content",
    "draft",
    "evidence_pack",
    "errors",
    "generations",
    "recent_messages",
    "review",
    "revised_text",
}
SECRET_KEYS = {
    "access_token",
    "api_key",
    "authorization",
    "client_secret",
    "refresh_token",
    "secret",
}
EVIDENCE_BLOCK = re.compile(r"<evidence>.*?</evidence>", re.DOTALL | re.IGNORECASE)
HISTORY_BLOCK = re.compile(
    r"Recent messages:.*?(?=\nLatest query:)",
    re.DOTALL | re.IGNORECASE,
)
DRAFT_BLOCK = re.compile(
    r"Draft:.*?(?=\n(?:Rules:|Review:|<evidence>))",
    re.DOTALL | re.IGNORECASE,
)
RULES_BLOCK = re.compile(
    r"Rules:.*?(?=\n(?:Review:|<evidence>))",
    re.DOTALL | re.IGNORECASE,
)
REVIEW_BLOCK = re.compile(
    r"Review:.*?(?=\n<evidence>)",
    re.DOTALL | re.IGNORECASE,
)
INVALID_RESPONSE_BLOCK = re.compile(
    r"Invalid response:.*\Z",
    re.DOTALL | re.IGNORECASE,
)


def redact_trace_payload(value: Any, *, key: str | None = None) -> Any:
    normalized_key = (key or "").casefold()
    if normalized_key in BLOCKED_KEYS or normalized_key in SECRET_KEYS:
        return REDACTED
    if normalized_key == "quote":
        return REDACTED
    if isinstance(value, dict):
        return {
            str(item_key): redact_trace_payload(item_value, key=str(item_key))
            for item_key, item_value in value.items()
        }
    if isinstance(value, list):
        return [redact_trace_payload(item) for item in value]
    if isinstance(value, tuple):
        return [redact_trace_payload(item) for item in value]
    if isinstance(value, str):
        redacted = HISTORY_BLOCK.sub("Recent messages: [REDACTED]", value)
        redacted = DRAFT_BLOCK.sub("Draft: [REDACTED]", redacted)
        redacted = RULES_BLOCK.sub("Rules: [REDACTED]", redacted)
        redacted = REVIEW_BLOCK.sub("Review: [REDACTED]", redacted)
        redacted = EVIDENCE_BLOCK.sub("<evidence>[REDACTED]</evidence>", redacted)
        return INVALID_RESPONSE_BLOCK.sub("Invalid response: [REDACTED]", redacted)
    return value
