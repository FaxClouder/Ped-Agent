from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

from pydantic import ValidationError

from ped_agent_server.models import (
    CitationSource,
    QualityTier,
    ResourceManifest,
    ResourceType,
    normalize_doi,
)
from ped_agent_server.vault import sha256_file


class ManifestPreflightError(ValueError):
    pass


def load_and_preflight(
    path: Path,
    *,
    as_of: date | None = None,
) -> list[ResourceManifest]:
    records: list[ResourceManifest] = []
    seen_ids: set[str] = set()
    seen_dois: set[str] = set()
    seen_hashes: set[str] = set()
    errors: list[str] = []
    reference_date = as_of or datetime.now(UTC).date()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = ResourceManifest.model_validate(json.loads(line))
        except (json.JSONDecodeError, ValidationError) as exc:
            errors.append(f"line {line_number}: {exc}")
            continue
        line_error_count = len(errors)
        if record.resource_id in seen_ids:
            errors.append(f"line {line_number}: duplicate resource_id {record.resource_id}")
        else:
            seen_ids.add(record.resource_id)
        normalized_doi = normalize_doi(record.doi)
        if normalized_doi:
            if normalized_doi in seen_dois:
                errors.append(f"line {line_number}: duplicate DOI {normalized_doi}")
            else:
                seen_dois.add(normalized_doi)
        if record.sha256 in seen_hashes:
            errors.append(f"line {line_number}: duplicate SHA-256 {record.sha256}")
        else:
            seen_hashes.add(record.sha256)
        if not record.source_path.is_file():
            errors.append(f"line {line_number}: missing file {record.source_path}")
        elif sha256_file(record.source_path) != record.sha256:
            errors.append(f"line {line_number}: SHA-256 mismatch for {record.source_path}")
        errors.extend(_quality_errors(record, line_number=line_number, as_of=reference_date))
        if len(errors) == line_error_count:
            records.append(record)
    if errors:
        raise ManifestPreflightError("; ".join(errors))
    return records


def _quality_errors(
    record: ResourceManifest,
    *,
    line_number: int,
    as_of: date,
) -> list[str]:
    if record.resource_type is not ResourceType.LITERATURE or not record.include:
        return []
    errors: list[str] = []
    if record.citation_checked_at is not None:
        citation_age = (as_of - record.citation_checked_at).days
        if citation_age < 0:
            errors.append(f"line {line_number}: citation snapshot is dated in the future")
        elif citation_age > 90:
            errors.append(f"line {line_number}: citation snapshot is older than 90 days")
    if record.jci_year is not None and record.jci_year < as_of.year - 1:
        errors.append(f"line {line_number}: JCI snapshot is older than 12 months")
    if record.cas_year is not None and record.cas_year < as_of.year - 1:
        errors.append(f"line {line_number}: CAS snapshot is older than 12 months")
    if record.metrics_checked_at is not None:
        metric_age = (as_of - record.metrics_checked_at).days
        if metric_age < 0:
            errors.append(f"line {line_number}: journal metric snapshot is dated in the future")
        elif metric_age > 365:
            errors.append(
                f"line {line_number}: journal metric snapshot is older than 12 months"
            )
    if record.citation_source not in {
        CitationSource.WEB_OF_SCIENCE,
        CitationSource.SCOPUS,
    }:
        errors.append(
            f"line {line_number}: formal citation counts require Web of Science or Scopus"
        )
    if record.published_date is not None and record.published_date > as_of:
        errors.append(f"line {line_number}: published_date is in the future")
    if record.quality_tier is QualityTier.A and not is_high_impact(record, as_of=as_of):
        errors.append(f"line {line_number}: A-tier literature does not meet age-adjusted citation threshold")
    if record.quality_tier is QualityTier.B:
        age_months = age_in_months(record.published_date, as_of)
        if age_months is not None and age_months <= 18:
            errors.append(
                f"line {line_number}: literature up to 18 months old must be A-tier"
            )
        elif age_months is not None and age_months > 36 and not is_high_impact(
            record,
            as_of=as_of,
        ):
            errors.append(
                f"line {line_number}: B-tier literature is neither recent nor highly cited"
            )
    return errors


def is_high_impact(record: ResourceManifest, *, as_of: date) -> bool:
    age_months = age_in_months(record.published_date, as_of)
    if age_months is None or record.citation_count is None:
        return False
    if age_months <= 18:
        return record.quality_tier is QualityTier.A
    if age_months <= 36:
        return record.citation_count >= 20
    if age_months <= 84:
        return record.citation_count >= 100
    return record.citation_count >= 500


def age_in_months(published_date: date | None, as_of: date) -> int | None:
    if published_date is None or published_date > as_of:
        return None
    months = (as_of.year - published_date.year) * 12 + as_of.month - published_date.month
    if as_of.day < published_date.day:
        months -= 1
    return months
