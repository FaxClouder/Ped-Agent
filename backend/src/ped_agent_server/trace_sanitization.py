from __future__ import annotations

import re
from collections.abc import Mapping
from enum import Enum
from typing import Any
from urllib.parse import urlsplit, urlunsplit

REDACTED = "[REDACTED]"
BLOCKED_KEYS = {
    "abstract",
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
MISSING = object()
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


def _safe_field(value: Any, name: str) -> Any:
    try:
        if isinstance(value, Mapping):
            return value.get(name, MISSING)
        return getattr(value, name)
    except BaseException:  # noqa: BLE001 - trace processors must always fail closed.
        return MISSING


def _safe_string(value: Any, *, optional: bool = False) -> tuple[bool, str | None]:
    if value is MISSING:
        return False, None
    if value is None:
        return (True, None) if optional else (False, None)
    try:
        if isinstance(value, Enum):
            value = value.value
        if not isinstance(value, str):
            return False, None
        return True, str(value)
    except BaseException:  # noqa: BLE001 - trace processors must always fail closed.
        return False, None


def _safe_query(value: Any) -> str:
    if value is MISSING or value is None:
        return ""
    try:
        return str(value)
    except BaseException:  # noqa: BLE001 - trace processors must always fail closed.
        return ""


def _safe_items(value: Any) -> list[Any]:
    if value is None or isinstance(value, (str, bytes, bytearray, Mapping)):
        return []
    try:
        return list(value)
    except BaseException:  # noqa: BLE001 - trace processors must always fail closed.
        return []


def _safe_url(value: Any) -> str | None:
    present, text = _safe_string(value, optional=True)
    if not present or not text:
        return None
    try:
        parsed = urlsplit(text)
        hostname = parsed.hostname
        port = parsed.port
        if not parsed.scheme or not hostname:
            return None
        host = f"[{hostname}]" if ":" in hostname else hostname
        netloc = host if port is None else f"{host}:{port}"
        return urlunsplit((parsed.scheme, netloc, parsed.path, "", ""))
    except BaseException:  # noqa: BLE001 - trace processors must always fail closed.
        return None


def safe_query_inputs(inputs: Any) -> dict[str, str]:
    try:
        if not isinstance(inputs, Mapping):
            return {"query": ""}
        return {"query": _safe_query(_safe_field(inputs, "query"))}
    except BaseException:  # noqa: BLE001 - trace processors must always fail closed.
        return {"query": ""}


def safe_candidate_inputs(inputs: Any) -> dict[str, Any]:
    try:
        candidate = _safe_field(inputs, "candidate")
        summary = _candidate_summary(candidate)
    except BaseException:  # noqa: BLE001 - trace processors must always fail closed.
        summary = None
    if summary is None:
        return {"candidate": None}
    return {"candidate": summary}


def _evidence_summary(item: Any) -> dict[str, Any] | None:
    try:
        present_id, evidence_id = _safe_string(_safe_field(item, "evidence_id"))
        present_origin, origin = _safe_string(_safe_field(item, "origin"))
        present_title, title = _safe_string(_safe_field(item, "title"))
        present_locator, locator = _safe_string(
            _safe_field(item, "locator"),
            optional=True,
        )
        present_hash, content_hash = _safe_string(_safe_field(item, "content_hash"))
        if not all((present_id, present_origin, present_title, present_locator, present_hash)):
            return None
        return {
            "evidence_id": evidence_id,
            "origin": origin,
            "title": title,
            "locator": locator,
            "content_hash": content_hash,
        }
    except BaseException:  # noqa: BLE001 - trace processors must always fail closed.
        return None


def safe_evidence_outputs(items: Any) -> dict[str, Any]:
    try:
        evidence = [
            summary
            for item in _safe_items(items)
            if (summary := _evidence_summary(item)) is not None
        ]
        return {"count": len(evidence), "evidence": evidence}
    except BaseException:  # noqa: BLE001 - trace processors must always fail closed.
        return {"count": 0, "evidence": []}


def safe_optional_evidence_output(item: Any | None) -> dict[str, Any]:
    try:
        return safe_evidence_outputs([] if item is None else [item])
    except BaseException:  # noqa: BLE001 - trace processors must always fail closed.
        return {"count": 0, "evidence": []}


def safe_retrieval_outputs(batch: Any) -> dict[str, Any]:
    empty = {
        "count": 0,
        "evidence": [],
        "sufficient": False,
        "degraded": False,
        "degradation_reason": None,
    }
    try:
        items = _safe_field(batch, "items")
        if items is MISSING:
            return empty
        output = safe_evidence_outputs(items)
        sufficient = _safe_field(batch, "sufficient")
        degraded = _safe_field(batch, "degraded")
        _, degradation_reason = _safe_string(
            _safe_field(batch, "degradation_reason"),
            optional=True,
        )
        return {
            **output,
            "sufficient": False if sufficient is MISSING else bool(sufficient),
            "degraded": False if degraded is MISSING else bool(degraded),
            "degradation_reason": degradation_reason,
        }
    except BaseException:  # noqa: BLE001 - trace processors must always fail closed.
        return empty


def _candidate_summary(item: Any) -> dict[str, Any] | None:
    try:
        present_source, source = _safe_string(_safe_field(item, "source"))
        present_title, title = _safe_string(_safe_field(item, "title"))
        raw_url = _safe_field(item, "url")
        present_url, _ = _safe_string(raw_url, optional=True)
        present_doi, doi = _safe_string(_safe_field(item, "doi"), optional=True)
        if not all((present_source, present_title, present_url, present_doi)):
            return None
        return {
            "source": source,
            "title": title,
            "url": _safe_url(raw_url),
            "doi": doi,
        }
    except BaseException:  # noqa: BLE001 - trace processors must always fail closed.
        return None


def safe_candidate_outputs(items: Any) -> dict[str, Any]:
    try:
        candidates = [
            summary
            for item in _safe_items(items)
            if (summary := _candidate_summary(item)) is not None
        ]
        return {"count": len(candidates), "candidates": candidates}
    except BaseException:  # noqa: BLE001 - trace processors must always fail closed.
        return {"count": 0, "candidates": []}


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
