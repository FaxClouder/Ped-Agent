from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from ped_agent.models import ResourceManifest
from ped_agent.vault import sha256_file


class ManifestPreflightError(ValueError):
    pass


def load_and_preflight(path: Path) -> list[ResourceManifest]:
    records: list[ResourceManifest] = []
    seen_ids: set[str] = set()
    errors: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = ResourceManifest.model_validate(json.loads(line))
        except (json.JSONDecodeError, ValidationError) as exc:
            errors.append(f"line {line_number}: {exc}")
            continue
        if record.resource_id in seen_ids:
            errors.append(f"line {line_number}: duplicate resource_id {record.resource_id}")
        elif not record.source_path.is_file():
            errors.append(f"line {line_number}: missing file {record.source_path}")
        elif sha256_file(record.source_path) != record.sha256:
            errors.append(f"line {line_number}: SHA-256 mismatch for {record.source_path}")
        else:
            seen_ids.add(record.resource_id)
            records.append(record)
    if errors:
        raise ManifestPreflightError("; ".join(errors))
    return records
