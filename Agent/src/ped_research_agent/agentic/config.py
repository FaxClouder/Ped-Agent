"""Strict JSON/TOML research profiles; loading never creates outputs or calls providers."""

from __future__ import annotations

import hashlib
import json
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProfileModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


class AgentPolicy(ProfileModel):
    max_rounds: int = Field(default=3, gt=0, le=100, strict=True)
    max_replans: int = Field(default=2, ge=0, le=100, strict=True)
    max_requirements: int = Field(default=12, gt=0, le=100, strict=True)
    max_new_requirements_per_replan: int = Field(default=3, gt=0, strict=True)
    no_gain_limit: int = Field(default=2, gt=0, strict=True)
    external_policy: Literal["disabled"] = "disabled"
    invalid_plan: Literal["fail"] = "fail"
    non_quality_stop: Literal["gaps_only"] = "gaps_only"


class HarnessPolicy(ProfileModel):
    max_tool_calls: int = Field(default=8, gt=0, strict=True)
    max_model_calls: int = Field(default=12, gt=0, strict=True)
    max_total_input_tokens: int = Field(default=60000, gt=0, strict=True)
    max_total_output_tokens: int = Field(default=12000, gt=0, strict=True)
    deadline_seconds: float = Field(default=300, gt=0)
    tool_timeout_seconds: float = Field(default=60, gt=0)
    retry_readonly: int = Field(default=1, ge=0, strict=True)
    max_parallel: int = Field(default=1, gt=0, strict=True)
    tool_allowlist: tuple[str, ...] = ("knowledge.search", "knowledge.read_evidence")

    @field_validator("tool_allowlist")
    @classmethod
    def valid_tools(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        known = {"knowledge.search", "knowledge.read_evidence"}
        if not value or len(set(value)) != len(value) or not set(value) <= known:
            raise ValueError("allowlist must contain unique implemented knowledge tools")
        return value


class KnowledgeSnapshot(ProfileModel):
    manifest: Path
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class RunProfile(ProfileModel):
    schema_version: Literal["agent-core-v1"] = "agent-core-v1"
    profile_id: str = Field(min_length=1)
    agent: AgentPolicy = Field(default_factory=AgentPolicy)
    harness: HarnessPolicy = Field(default_factory=HarnessPolicy)
    knowledge: KnowledgeSnapshot
    output_dir: Path

    def frozen_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), sort_keys=True, ensure_ascii=False)

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(self.frozen_json().encode()).hexdigest()

    def validate_assets(self) -> None:
        if self.output_dir.exists():
            raise ValueError("output directory already exists")
        if (
            hashlib.sha256(self.knowledge.manifest.read_bytes()).hexdigest()
            != self.knowledge.sha256
        ):
            raise ValueError("knowledge manifest hash mismatch")


def _merge(base: dict[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        previous = result.get(key)
        result[key] = (
            _merge(previous, value)
            if isinstance(previous, dict) and isinstance(value, dict)
            else value
        )
    return result


def _read(path: Path, active: set[Path]) -> dict[str, Any]:
    path = path.resolve()
    if path in active:
        raise ValueError("profile inheritance cycle")
    if len(active) >= 16:
        raise ValueError("profile inheritance exceeds 16 files")
    if path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    elif path.suffix == ".toml":
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    else:
        raise ValueError("profile must be JSON or TOML")
    if not isinstance(data, dict):
        raise ValueError("profile root must be an object")
    parent = data.pop("extends", None)
    # Resolve file-valued fields at their defining profile, including inherited values.
    for container, key in ((data, "output_dir"), (data.get("knowledge", {}), "manifest")):
        if isinstance(container, dict) and key in container and isinstance(container[key], str):
            container[key] = str((path.parent / container[key]).resolve())
    if parent is None:
        return data
    if not isinstance(parent, str) or not parent:
        raise ValueError("extends must name a profile file")
    return _merge(_read(path.parent / parent, active | {path}), data)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate profile field: {key}")
        result[key] = value
    return result


def load_profile(path: str | Path, *, overrides: Mapping[str, Any] | None = None) -> RunProfile:
    source = Path(path).resolve()
    data = _read(source, set())
    if overrides:
        if not set(overrides) <= {"agent", "harness", "output_dir"}:
            raise ValueError("only agent, harness and output_dir overrides are allowed")
        data = _merge(data, overrides)
    profile = RunProfile.model_validate(data)
    # CLI output paths resolve relative to the selected profile, never a saved local machine path.
    output = (source.parent / profile.output_dir).resolve()
    profile = profile.model_copy(update={"output_dir": output})
    profile.validate_assets()
    return profile
