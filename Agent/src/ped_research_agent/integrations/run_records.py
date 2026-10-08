"""Credential-filtered run archives and deterministic domain-state replay, without dispatch."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, JsonValue, TypeAdapter

from ped_agent_harness.budget import BudgetUsage
from ped_agent_harness.contracts import TOOL_OUTCOME_ADAPTER, ToolCall, ToolSuccess, sha256_json
from ped_agent_harness.model_contracts import ModelReply, ModelRequest
from ped_agent_harness.recorder import JsonlRecorder, RunEvent
from ped_contracts.evidence import AnswerDraft, EvidenceItem, SemanticReview
from ped_research_agent.agentic.config import RunProfile
from ped_research_agent.agentic.state import AgenticResult, DecisionState, StopReason
from ped_research_agent.policy import ORIGIN_PREFIX, validate_draft

FORMAT_VERSION = "agent-core-run-v1"
_OBJECT = TypeAdapter(dict[str, JsonValue])
_SECRET = re.compile(
    r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}"
    r"|(?i:Bearer\s+)[A-Za-z0-9._-]+"
    r"|(?i:(?:api[_-]?key|password|secret)[\"']?\s*[=:]\s*[\"']?)[^\s,;\"']+"
    r"|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]*?-----END [^-]*PRIVATE KEY-----"
    r"|(?<=://)[^/\s:@]+:[^/\s@]+@"
)
_SECRET_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "password",
    "secret",
    "access_token",
    "refresh_token",
    "cookie",
    "client_secret",
}


class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    format_version: Literal["agent-core-run-v1"] = "agent-core-run-v1"
    run_id: str
    question: str
    resolved_config: dict[str, JsonValue]
    config_sha256: str
    provenance: dict[str, JsonValue]
    redaction_policy: str = "recognized-credentials-and-explicit-values-v1"


class ReplayError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _integer(value: JsonValue) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("expected nonnegative integer")
    return value


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: dict[str, JsonValue]) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique)


class RunArchive:
    """Construct before composition, open after preflight; never reuse an output directory."""

    def __init__(
        self,
        profile: RunProfile,
        question: str,
        run_id: str,
        *,
        redact_values: tuple[str, ...] = (),
    ) -> None:
        self.profile, self.path, self.run_id = profile, profile.output_dir, run_id
        self.question, self.redact_values = question, tuple(v for v in redact_values if v)
        self.redactions = 0
        self._writer: JsonlRecorder | None = None
        self._state = DecisionState(question=question).model_dump(mode="json")
        self.last_result: AgenticResult | None = None
        self._seq = 0

    def clean(self, value: Any) -> Any:
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                if key.lower() in _SECRET_KEYS:
                    self.redactions += 1
                    result[key] = "[REDACTED]"
                else:
                    safe_key = self.clean(key)
                    if safe_key in result:
                        raise ValueError("redaction would collapse object identities")
                    result[safe_key] = self.clean(item)
            return result
        if isinstance(value, (list, tuple)):
            return [self.clean(item) for item in value]
        if isinstance(value, str):
            for secret in self.redact_values:
                if secret in value:
                    self.redactions += 1
                    value = value.replace(secret, "[REDACTED]")
            value, count = _SECRET.subn("[REDACTED]", value)
            self.redactions += count
        return value

    def start(self, provenance: dict[str, JsonValue]) -> None:
        if self._writer is not None:
            raise ValueError("archive already started")
        config = _OBJECT.validate_python(self.clean(self.profile.model_dump(mode="json")))
        manifest = Manifest(
            run_id=self.run_id,
            question=self.clean(self.question),
            resolved_config=config,
            config_sha256=sha256_json(config),
            provenance=self.clean(provenance),
        )
        self.path.mkdir(parents=True, exist_ok=False)
        _write(self.path / "manifest.json", manifest.model_dump(mode="json"))
        self._state = DecisionState(question=manifest.question).model_dump(mode="json")
        self._writer = JsonlRecorder(self.path / "events.jsonl")
        self.emit(
            self.run_id, "run_start", {"manifest_sha256": _file_hash(self.path / "manifest.json")}
        )

    def _delta(self, state: dict[str, JsonValue]) -> None:
        patch = {key: value for key, value in state.items() if self._state.get(key) != value}
        if patch:
            payload: dict[str, JsonValue] = {
                "before_sha256": sha256_json(self._state),
                "after_sha256": sha256_json(state),
                "patch": patch,
            }
            self._emit("state_delta", payload)
            self._state = state

    def _emit(self, kind: str, payload: dict[str, JsonValue]) -> RunEvent:
        if self._writer is None:
            raise ValueError("archive was not opened")
        event = self._writer.emit(self.run_id, kind, payload)
        self._seq = event.seq
        return event

    def emit(self, run_id: str, event_type: str, payload: dict[str, JsonValue]) -> RunEvent:
        if run_id != self.run_id:
            raise ValueError("recorder run identity mismatch")
        safe = _OBJECT.validate_python(self.clean(payload))
        # Digests refer to the sanitized recorded view; source content_hash remains provenance.
        call = safe.get("call")
        if isinstance(call, dict) and "arguments" in call:
            call["arguments_sha256"] = sha256_json(call["arguments"])
        outcome = safe.get("outcome")
        if isinstance(outcome, dict):
            inner = outcome.get("call")
            if isinstance(inner, dict):
                inner["arguments_sha256"] = sha256_json(inner["arguments"])
            if outcome.get("status") == "ok":
                outcome["value_sha256"] = sha256_json(outcome["value"])
        state = safe if event_type == "plan" else safe.get("state")
        if event_type in {"plan", "round_end", "decision_end", "answer_end"} and isinstance(
            state, dict
        ):
            self._delta(state)
        if event_type in {"decision_end", "answer_end"}:
            self.last_result = AgenticResult.model_validate(safe)
        return self._emit(event_type, safe)

    def finish(self, result: AgenticResult, usage: BudgetUsage) -> AgenticResult:
        safe = AgenticResult.model_validate(self.clean(result.model_dump(mode="json")))
        self._delta(safe.state.model_dump(mode="json"))
        _write(self.path / "result.json", safe.model_dump(mode="json"))
        self.emit(
            self.run_id,
            "run_end",
            {
                "result_sha256": _file_hash(self.path / "result.json"),
                "usage": usage.model_dump(mode="json"),
            },
        )
        self.close()
        _write(
            self.path / "completion.json",
            {
                "format_version": FORMAT_VERSION,
                "run_id": self.run_id,
                "events": self._seq,
                "redactions": self.redactions,
                "files": {
                    name: _file_hash(self.path / name)
                    for name in ("manifest.json", "events.jsonl", "result.json")
                },
            },
        )
        return safe

    def close(self) -> None:
        if self._writer is not None:
            self._writer.close()
            self._writer = None


def _transition(
    before: DecisionState,
    after: DecisionState,
    profile: RunProfile,
    canonical: dict[str, list[EvidenceItem]],
) -> None:
    if before.question != after.question or not before.round <= after.round <= before.round + 1:
        raise ValueError("invalid question/round transition")
    if not before.replans_used <= after.replans_used <= profile.agent.max_replans:
        raise ValueError("invalid replan counter")
    if after.round > profile.agent.max_rounds or [r.round for r in after.rounds] != list(
        range(1, after.round + 1)
    ):
        raise ValueError("invalid round records")
    unplanned_stop = not after.requirements and after.stop_reason in (
        StopReason.CANCELLED,
        StopReason.BUDGET_EXHAUSTED,
        StopReason.EXECUTION_FAILED,
    )
    if after.stop_reason is not StopReason.PLAN_INVALID and not unplanned_stop:
        after.validate_plan(max_requirements=profile.agent.max_requirements)
    for key, node in before.requirements.items():
        new = after.requirements.get(key)
        if new is None or (node.statement, node.depends_on) != (new.statement, new.depends_on):
            raise ValueError("existing requirement identity changed")
        if new.queries_tried[: len(node.queries_tried)] != node.queries_tried:
            raise ValueError("query history was removed")
    if (
        before.requirements
        and len(after.requirements.keys() - before.requirements.keys())
        > profile.agent.max_new_requirements_per_replan
    ):
        raise ValueError("replan append cap exceeded")
    for key, item in after.evidence.items():
        if key != item.evidence_id or key not in canonical or item not in canonical[key]:
            raise ValueError("state evidence is not a canonical recorded tool result")
        if key in before.evidence and item != before.evidence[key]:
            raise ValueError("existing evidence changed")
        label = after.labels.get(key)
        if not label or not label.startswith(ORIGIN_PREFIX[item.origin]):
            raise ValueError("invalid stable label")
        if key in before.labels and label != before.labels[key]:
            raise ValueError("stable label changed")
        if (
            key in before.first_seen_round
            and after.first_seen_round.get(key) != before.first_seen_round[key]
        ):
            raise ValueError("first-seen round changed")
    if len(set(after.labels.values())) != len(after.labels) or set(after.labels) != set(
        after.evidence
    ):
        raise ValueError("invalid evidence label map")
    if set(after.first_seen_round) != set(after.evidence):
        raise ValueError("invalid first-seen map")
    for node in after.requirements.values():
        if not set(node.support_evidence_ids) <= after.evidence.keys():
            raise ValueError("support references uncollected evidence")
        if len(set(node.queries_tried)) != len(node.queries_tried):
            raise ValueError("duplicate query history")


def replay_run(path: str | Path) -> tuple[AgenticResult, BudgetUsage]:
    """Verify archive and rebuild state and answer proof without dispatch."""
    root = Path(path)
    required = ("manifest.json", "events.jsonl", "result.json", "completion.json")
    if any(not (root / name).is_file() for name in required):
        raise ReplayError("missing", "run is incomplete or required files are missing")
    try:
        completion = _read(root / "completion.json")
        raw_manifest = _read(root / "manifest.json")
        if (
            completion.get("format_version") != FORMAT_VERSION
            or raw_manifest.get("format_version") != FORMAT_VERSION
        ):
            raise ReplayError("incompatible", "unsupported run format")
        for name in required[:-1]:
            if completion["files"][name] != _file_hash(root / name):
                raise ReplayError("integrity", f"{name} digest mismatch")
        manifest = Manifest.model_validate(raw_manifest)
        model_contract = manifest.provenance.get("model_contracts")
        if (
            manifest.resolved_config.get("schema_version") != "agent-core-v1"
            or not isinstance(model_contract, dict)
            or model_contract.get("version") != "model-boundary-v1"
        ):
            raise ReplayError("incompatible", "unsupported profile/model contract version")
        if (
            completion["run_id"] != manifest.run_id
            or sha256_json(manifest.resolved_config) != manifest.config_sha256
        ):
            raise ValueError("manifest identity/config digest mismatch")
        profile = RunProfile.model_validate(
            manifest.resolved_config
        )  # No filesystem asset validation.
        events = [
            RunEvent.model_validate(json.loads(line, object_pairs_hook=_unique))
            for line in (root / "events.jsonl").read_text().splitlines()
        ]
        if (
            len(events) != completion["events"]
            or not events
            or events[0].type != "run_start"
            or events[-1].type != "run_end"
        ):
            raise ValueError("incomplete event boundaries")
        if events[0].payload["manifest_sha256"] != _file_hash(root / "manifest.json"):
            raise ValueError("run_start manifest mismatch")
        state = DecisionState(question=manifest.question)
        canonical: dict[str, list[EvidenceItem]] = {}
        calls: dict[str, ToolCall] = {}
        attempts: dict[tuple[str, int], dict[str, JsonValue]] = {}
        settled: dict[tuple[str, int], ModelReply | None] = {}
        tool_attempts = 0
        outcomes: set[str] = set()
        context: list[str] = []
        validation: dict[str, JsonValue] | None = None
        delta_count = 0
        for seq, event in enumerate(events, 1):
            if event.seq != seq or event.run_id != manifest.run_id:
                raise ValueError("event sequence/run identity mismatch")
            payload = event.payload
            if event.type == "tool_call":
                call = ToolCall.model_validate(payload["call"])
                if (
                    call.run_id != manifest.run_id
                    or call.call_id in calls
                    or sha256_json(call.arguments) != call.arguments_sha256
                ):
                    raise ValueError("invalid/duplicate tool call")
                calls[call.call_id] = call
            elif event.type == "tool_outcome":
                outcome = TOOL_OUTCOME_ADAPTER.validate_python(payload["outcome"])
                if (
                    calls.get(outcome.call.call_id) != outcome.call
                    or outcome.call.call_id in outcomes
                ):
                    raise ValueError("tool outcome has no unique matching call")
                outcomes.add(outcome.call.call_id)
                tool_attempts += outcome.provenance.attempts
                if isinstance(outcome, ToolSuccess):
                    if sha256_json(outcome.value) != outcome.value_sha256 or not isinstance(
                        outcome.value, dict
                    ):
                        raise ValueError("invalid canonical tool value")
                    raw_items = outcome.value.get("items", [])
                    if "evidence" in outcome.value:
                        raw_items = [outcome.value["evidence"]]
                    if not isinstance(raw_items, list):
                        raise ValueError("invalid canonical evidence list")
                    for raw in raw_items:
                        item = EvidenceItem.model_validate(raw)
                        canonical.setdefault(item.evidence_id, []).append(item)
            elif event.type == "model_call":
                request = payload["request"]
                if not isinstance(request, dict):
                    raise ValueError("invalid model request")
                typed_request = ModelRequest.model_validate(request)
                if (
                    typed_request.run_id != manifest.run_id
                    or typed_request.max_output_tokens != payload["output_cap"]
                ):
                    raise ValueError("model identity/output reservation mismatch")
                key = (str(request["call_id"]), _integer(payload["attempt"]))
                if key in attempts:
                    raise ValueError("duplicate model attempt")
                attempts[key] = payload
            elif event.type in {"model_reply", "model_failure"} and payload.get("attempt") != 0:
                key = (str(payload["call_id"]), _integer(payload["attempt"]))
                if key not in attempts or key in settled:
                    raise ValueError("model outcome has no unique attempt")
                settled[key] = (
                    ModelReply.model_validate(payload["reply"]) if payload.get("reply") else None
                )
            elif event.type == "state_delta":
                if payload["before_sha256"] != sha256_json(state.model_dump(mode="json")):
                    raise ValueError("state delta does not continue reconstructed state")
                patch = payload["patch"]
                if (
                    not isinstance(patch, dict)
                    or not set(patch) <= DecisionState.model_fields.keys()
                ):
                    raise ValueError("invalid state patch")
                candidate = DecisionState.model_validate({**state.model_dump(mode="json"), **patch})
                _transition(state, candidate, profile, canonical)
                if payload["after_sha256"] != sha256_json(candidate.model_dump(mode="json")):
                    raise ValueError("state delta digest mismatch")
                state = candidate
                delta_count += 1
            elif event.type == "context_selection":
                retained = payload["retained_ids"]
                if not isinstance(retained, list) or not all(
                    isinstance(key, str) for key in retained
                ):
                    raise ValueError("invalid retained context IDs")
                context = [str(key) for key in retained]
            elif event.type == "answer_validation":
                validation = payload
        result = AgenticResult.model_validate(_read(root / "result.json"))
        if (
            not delta_count
            or result.state != state
            or events[-1].payload["result_sha256"] != _file_hash(root / "result.json")
        ):
            raise ValueError("final result differs from reconstructed state")
        usage = BudgetUsage.model_validate(events[-1].payload["usage"])
        if usage.model_calls != len(attempts) or set(attempts) != set(settled):
            raise ValueError("model attempt accounting mismatch")
        known_in = known_out = estimated_in = estimated_out = unknown = 0
        for key, attempt in attempts.items():
            reply = settled[key]
            incoming = reply.usage.input_tokens if reply else None
            outgoing = reply.usage.output_tokens if reply else None
            known_in += incoming or 0
            known_out += outgoing or 0
            unknown += int(incoming is None or outgoing is None)
            if incoming is None:
                estimated_in += _integer(attempt["input_estimate"])
            if outgoing is None:
                estimated_out += _integer(attempt["output_cap"])
        if (
            usage.input_tokens,
            usage.output_tokens,
            usage.estimated_input_tokens,
            usage.estimated_output_tokens,
            usage.unknown_token_calls,
        ) != (known_in, known_out, estimated_in, estimated_out, unknown):
            raise ValueError("token accounting mismatch")
        interrupted = result.stop_reason in (StopReason.CANCELLED, StopReason.BUDGET_EXHAUSTED)
        if usage.tool_calls != tool_attempts and not (
            interrupted and len(outcomes) < len(calls) and usage.tool_calls >= tool_attempts
        ):
            raise ValueError("tool attempt accounting mismatch")
        if (
            usage.reserved_input_tokens
            or usage.reserved_output_tokens
            or usage.tool_calls > profile.harness.max_tool_calls
            or usage.model_calls > profile.harness.max_model_calls
        ):
            raise ValueError("invalid final reservations/call budgets")
        if result.answer is not None:
            _validate_answer(result, context, validation)
        elif result.stop_reason is StopReason.QUALITY_STOP:
            raise ValueError("backend quality stop is missing its final answer")
        return result, usage
    except ReplayError:
        raise
    except (ValueError, KeyError, TypeError, OSError) as exc:
        raise ReplayError("invalid", type(exc).__name__) from exc


def _validate_answer(
    result: AgenticResult, context: list[str], validation: dict[str, JsonValue] | None
) -> None:
    if validation is None or validation.get("next_step") != "final_persist":
        raise ValueError("answer has no successful validation proof")
    draft = AnswerDraft.model_validate(validation["draft"])
    required = {
        key for node in result.state.requirements.values() for key in node.support_evidence_ids
    }
    if not required <= set(context):
        raise ValueError("answer context lost required support")
    evidence = [result.state.evidence[key] for key in context]
    if not validate_draft(draft, evidence).passed or any(
        result.state.labels.get(c.evidence_id) != c.label for c in draft.citations
    ):
        raise ValueError("answer rules/bindings fail replay")
    review = SemanticReview.model_validate(validation["review"])
    statuses = {claim.claim_id: claim.status for claim in review.claims}
    if not all(statuses.get(claim.claim_id) == "supported" for claim in draft.claims):
        raise ValueError("answer lacks semantic support proof")
    answer = result.answer
    assert answer is not None
    if (
        answer.verification.status != "verified"
        or not answer.verification.rules_passed
        or not answer.verification.semantic_passed
    ):
        raise ValueError("answer is not verified")
    if answer.verification.repaired != (_integer(validation["revision_count"]) > 0):
        raise ValueError("answer revision provenance differs from validation")
    for field in ("answer_markdown", "citations", "inferences", "limitations"):
        if getattr(answer, field) != getattr(draft, field):
            raise ValueError("answer differs from validated draft")
