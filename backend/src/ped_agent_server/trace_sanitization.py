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


def safe_query_inputs(inputs: dict[str, Any]) -> dict[str, str]:
    return {"query": str(inputs.get("query", ""))}


def safe_candidate_inputs(inputs: dict[str, Any]) -> dict[str, Any]:
    candidate = inputs.get("candidate")
    if candidate is None:
        return {"candidate": None}
    return {"candidate": safe_candidate_outputs([candidate])["candidates"][0]}


def _evidence_summary(item: Any) -> dict[str, Any]:
    value = item.model_dump(mode="json") if hasattr(item, "model_dump") else dict(item)
    return {
        "evidence_id": value.get("evidence_id"),
        "origin": value.get("origin"),
        "title": value.get("title"),
        "locator": value.get("locator"),
        "content_hash": value.get("content_hash"),
    }


def safe_evidence_outputs(items: list[Any]) -> dict[str, Any]:
    return {
        "count": len(items),
        "evidence": [_evidence_summary(item) for item in items],
    }


def safe_optional_evidence_output(item: Any | None) -> dict[str, Any]:
    return safe_evidence_outputs([] if item is None else [item])


def safe_retrieval_outputs(batch: Any) -> dict[str, Any]:
    return {
        **safe_evidence_outputs(list(batch.items)),
        "sufficient": bool(batch.sufficient),
        "degraded": bool(batch.degraded),
        "degradation_reason": batch.degradation_reason,
    }


def safe_candidate_outputs(items: list[Any]) -> dict[str, Any]:
    return {
        "count": len(items),
        "candidates": [
            {
                "source": item.source,
                "title": item.title,
                "url": item.url,
                "doi": item.doi,
            }
            for item in items
        ],
    }


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
