from __future__ import annotations

import re
from typing import Any

REDACTED = "[REDACTED]"
BLOCKED_KEYS = {
    "content",
    "credentials",
    "draft",
    "evidence_pack",
    "errors",
    "generations",
    "header",
    "headers",
    "history",
    "messages",
    "recent_messages",
    "request_header",
    "request_headers",
    "response_header",
    "response_headers",
    "review",
    "revised_text",
    "secrets",
}
SECRET_KEYS = {
    "access_token",
    "api_key",
    "auth",
    "authorization",
    "client_secret",
    "cookie",
    "cookies",
    "password",
    "private_key",
    "refresh_token",
    "secret",
    "set_cookie",
    "token",
}
FINAL_ANSWER_KEY = "final_answer"
CAMEL_CASE_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
KEY_SEPARATOR = re.compile(r"[^A-Za-z0-9]+")
EVIDENCE_BLOCK = re.compile(
    r"<evidence>(?:(?=.*</evidence>).*</evidence>|.*\Z)",
    re.DOTALL | re.IGNORECASE,
)
HISTORY_BLOCK = re.compile(
    r"Recent messages:.*(?=\nLatest query:)",
    re.DOTALL | re.IGNORECASE,
)
DRAFT_BLOCK = re.compile(
    r"Draft:.*(?=\n(?:Rules:|Review:|<evidence>))",
    re.DOTALL | re.IGNORECASE,
)
RULES_BLOCK = re.compile(
    r"Rules:.*(?=\n(?:Review:|<evidence>))",
    re.DOTALL | re.IGNORECASE,
)
REVIEW_BLOCK = re.compile(
    r"Review:.*(?=\n<evidence>)",
    re.DOTALL | re.IGNORECASE,
)
INVALID_RESPONSE_BLOCK = re.compile(
    r"Invalid response:.*\Z",
    re.DOTALL | re.IGNORECASE,
)


def _normalize_key(key: str) -> str:
    separated = CAMEL_CASE_BOUNDARY.sub("_", key)
    return KEY_SEPARATOR.sub("_", separated).strip("_").casefold()


def _is_private_key(key: str) -> bool:
    if key in BLOCKED_KEYS or key in SECRET_KEYS or key == "quote":
        return True
    return key.endswith(
        (
            "_api_key",
            "_auth",
            "_authorization",
            "_cookie",
            "_cookies",
            "_credentials",
            "_header",
            "_headers",
            "_password",
            "_private_key",
            "_secret",
            "_token",
        )
    )


def redact_trace_payload(value: Any, *, key: str | None = None) -> Any:
    return _redact_trace_payload(value, key=key, path=())


def _redact_trace_payload(
    value: Any,
    *,
    key: str | None,
    path: tuple[str, ...],
) -> Any:
    normalized_key = _normalize_key(key or "")
    current_path = (*path, normalized_key) if normalized_key else path
    if _is_private_key(normalized_key):
        return REDACTED
    if normalized_key == "text" and FINAL_ANSWER_KEY not in current_path:
        return REDACTED
    if isinstance(value, dict):
        return {
            str(item_key): _redact_trace_payload(
                item_value,
                key=str(item_key),
                path=current_path,
            )
            for item_key, item_value in value.items()
        }
    if isinstance(value, list):
        return [_redact_trace_payload(item, key=None, path=current_path) for item in value]
    if isinstance(value, tuple):
        return [_redact_trace_payload(item, key=None, path=current_path) for item in value]
    if isinstance(value, str):
        if FINAL_ANSWER_KEY in current_path:
            return value
        redacted = HISTORY_BLOCK.sub("Recent messages: [REDACTED]", value)
        redacted = DRAFT_BLOCK.sub("Draft: [REDACTED]", redacted)
        redacted = RULES_BLOCK.sub("Rules: [REDACTED]", redacted)
        redacted = REVIEW_BLOCK.sub("Review: [REDACTED]", redacted)
        redacted = EVIDENCE_BLOCK.sub("<evidence>[REDACTED]</evidence>", redacted)
        return INVALID_RESPONSE_BLOCK.sub("Invalid response: [REDACTED]", redacted)
    return value
