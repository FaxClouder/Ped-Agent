"""Build a non-importable literature manifest readiness snapshot.

This module only reads research inputs. Its CSV is not an IngestionManifest.
"""

from __future__ import annotations

import csv
import hashlib
import io
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pymupdf


ALGORITHM_VERSION = "manifest-readiness-v1"
VENUE_ALIASES = {
    "transportation letters": "transportation letters-the international journal of transportation research",
    "transportation research part c: emerging technologies": "transportation research part c emerging technologies",
    "physica a statistical mechanics and its applications": "physica a: statistical mechanics and its applications",
    "physica a": "physica a: statistical mechanics and its applications",
}
READINESS_FIELDS = (
    "batch",
    "resource_id",
    "doi",
    "title",
    "language",
    "venue",
    "source_url",
    "source_path",
    "inventory_sha256",
    "actual_sha256",
    "hash_status",
    "pdf_status",
    "page_count",
    "primary_topic",
    "topics",
    "publication_status",
    "content_score",
    "content_decision",
    "citation_count",
    "citation_source",
    "citation_checked_at",
    "journal_match_status",
    "journal_best_rank",
    "integrity_status",
    "rights_status",
    "quality_tier",
    "manual_review_status",
    "blocker_codes",
)


class ReadinessConflictError(ValueError):
    """Input conflict that stops the snapshot but can be rendered as a report."""

    def render_report(self) -> str:
        return (
            "# 文献 Manifest 准备表输入冲突\n\n"
            "_五批文献离线核查 · status: current_\n\n"
            "准备表未生成；请先修复以下输入冲突，再重新构建。\n\n"
            f"- {self}\n"
        )


@dataclass(frozen=True)
class ReadinessBuild:
    rows: tuple[dict[str, str], ...]
    excluded_count: int
    input_hashes: dict[str, str]

    def render_csv(self) -> str:
        output = io.StringIO(newline="")
        writer = csv.DictWriter(output, fieldnames=READINESS_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(self.rows)
        return output.getvalue()

    def render_report(self) -> str:
        by_batch = Counter(row["batch"] for row in self.rows)
        blockers = Counter(
            code
            for row in self.rows
            for code in row["blocker_codes"].split(";")
            if code
        )
        lines = [
            "# 文献 Manifest 准备表构建核对",
            "",
            "_五批文献离线核查快照 · status: current · 2026-09-23_",
            "",
            "本报告对应 [`manifest_readiness_2026-09-23.csv`](../literature/records/manifest_readiness_2026-09-23.csv)。",
            f"构建算法版本：`{ALGORITHM_VERSION}`。准备表不是技术导入 Manifest；仅只读检查 PDF 可读性，未运行项目导入、派生解析或索引流程。",
            "",
            "## 数量",
            "",
            f"- 准备表：{len(self.rows)} 篇。",
            f"- 原记录中暂不使用、未构建条目：{self.excluded_count} 篇。",
            "",
            "| 批次 | 准备表行数 |",
            "| --- | ---: |",
        ]
        for batch in range(1, 6):
            lines.append(f"| {batch} | {by_batch[str(batch)]} |")
        lines.extend(["", "## 待核实项", "", "| 阻断代码 | 篇数 |", "| --- | ---: |"])
        for code, count in sorted(blockers.items()):
            lines.append(f"| `{code}` | {count} |")
        lines.extend(
            [
                "",
                "`blocker_codes` 混合技术异常与旧精选规则的元数据缺口，须按代码分别解释；治理标记不阻断技术预检或明确标记的探索实验。",
                "期刊匹配仅是来源记录关联，可作为语料分层变量。",
                "",
                "## 输入指纹",
                "",
                "| 输入文件（仓库相对路径） | SHA-256 |",
                "| --- | --- |",
            ]
        )
        for path, digest in sorted(self.input_hashes.items()):
            lines.append(f"| `{path}` | `{digest}` |")
        lines.extend(
            [
                "",
                "四篇暂不使用文献只在原候选和筛选记录中保留；此报告不另建逐篇条目。",
                "技术预检以实际 PDF、哈希、格式和身份冲突检查为准；探索实验可单独生成技术 Manifest。",
                "来源权限限制、撤稿及 PDF/DOI 身份冲突应定向处理，并在实验报告中披露排除范围。",
                "",
            ]
        )
        return "\n".join(lines)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def _doi(value: str) -> str:
    normalized = value.strip().casefold()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        normalized = normalized.removeprefix(prefix)
    return normalized


def _unique_by_doi(rows: list[dict[str, str]], *, source: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        doi = _doi(row.get("doi", ""))
        if not doi:
            raise ValueError(f"missing {source} DOI")
        if doi in result:
            raise ValueError(f"duplicate {source} DOI {doi}")
        result[doi] = row
    return result


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _pdf_evidence(path: Path, *, batch_dir: Path, inventory_sha: str) -> tuple[str, str, str, str]:
    if not path.is_relative_to(batch_dir.resolve()):
        return "", "invalid_path", "not_checked", ""
    if not path.is_file():
        return "", "missing", "missing", ""
    actual_sha = _file_hash(path)
    hash_status = "match" if actual_sha == inventory_sha.casefold() else "mismatch"
    try:
        with pymupdf.open(path) as document:
            if document.needs_pass or document.page_count < 1:
                return actual_sha, hash_status, "unreadable", ""
            for page in document:
                page.get_text("text")
            return actual_sha, hash_status, "readable", str(document.page_count)
    except (OSError, RuntimeError, ValueError):
        return actual_sha, hash_status, "unreadable", ""


def _venue_key(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value.strip().casefold())
    return VENUE_ALIASES.get(normalized, normalized)


def _journal_evidence(
    venue: str, journal_rows: list[dict[str, str]]
) -> tuple[str, str]:
    matches = [
        row for row in journal_rows
        if _venue_key(row.get("venue", "")) == _venue_key(venue)
        and row.get("verified_at", "").strip()
        and re.fullmatch(r"\d{4}", row.get("jcr_year", "").strip())
        and row.get("jcr_year", "").strip() == row.get("cas_year", "").strip()
    ]
    if not matches:
        return "pending", ""
    ranks: list[int] = []
    for row in matches:
        for field in ("cas_major_zone", "cas_minor_zone"):
            value = row.get(field, "").strip()
            if value in {"1", "2", "3", "4"}:
                ranks.append(int(value))
        for field in ("jci_quartile", "jif_quartile"):
            value = row.get(field, "").strip().upper()
            if value in {"Q1", "Q2", "Q3", "Q4"}:
                ranks.append(int(value[1]))
    return "matched", str(min(ranks)) if ranks else ""


def build_readiness(root: Path) -> ReadinessBuild:
    """Read research inputs or raise a renderable conflict; never write files."""
    try:
        return _build_readiness(root)
    except ValueError as exc:
        raise ReadinessConflictError(str(exc)) from exc


def _build_readiness(root: Path) -> ReadinessBuild:
    root = root.resolve()
    knowledge = root / "memPed" / "knowledge"
    records = knowledge / "literature" / "records"
    input_paths = [
        knowledge / f"batch-{batch}-incoming" / f"batch{batch}_inventory.csv"
        for batch in range(1, 6)
    ] + [
        records / "candidates.csv",
        records / "screening.csv",
        records / "citation_snapshots.csv",
        records / "journal_metrics.csv",
    ]
    input_hashes = {
        path.relative_to(root).as_posix(): _file_hash(path) for path in input_paths
    }
    inventories: list[tuple[int, Path, dict[str, str]]] = []
    for batch, path in enumerate(input_paths[:5], start=1):
        for row in _read_csv(path):
            inventories.append((batch, path.parent, row))
    inventory_by_doi = _unique_by_doi(
        [item[2] for item in inventories], source="inventory"
    )
    candidates = _unique_by_doi(_read_csv(records / "candidates.csv"), source="candidate")
    screening = _unique_by_doi(_read_csv(records / "screening.csv"), source="screening")
    citations = _unique_by_doi(
        _read_csv(records / "citation_snapshots.csv"), source="citation"
    )
    journal_rows = _read_csv(records / "journal_metrics.csv")
    rows: list[dict[str, str]] = []
    excluded_count = 0
    seen_resource_ids: set[str] = set()
    seen_hashes: set[str] = set()
    for batch, batch_dir, inventory in inventories:
        doi = _doi(inventory["doi"])
        screen = screening.get(doi)
        if screen is None:
            raise ValueError(f"missing screening DOI {doi}")
        candidate = candidates.get(doi)
        if candidate is None:
            raise ValueError(f"missing candidate DOI {doi}")
        resource_id = candidate.get("resource_id", "")
        if not resource_id or resource_id != screen.get("resource_id"):
            raise ValueError(f"resource_id mismatch for DOI {doi}")
        if resource_id in seen_resource_ids:
            raise ValueError(f"duplicate resource_id {resource_id}")
        seen_resource_ids.add(resource_id)
        try:
            score = int(screen["total_score"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid content score for DOI {doi}") from exc
        held = screen.get("decision", "").startswith("temporarily_not_used")
        if held:
            if score > 65 or screen.get("fulltext_screen") != "fail":
                raise ValueError(f"inconsistent held screening DOI {doi}")
            excluded_count += 1
            continue
        if score <= 65 or screen.get("fulltext_screen") != "pass":
            raise ValueError(f"inconsistent passed screening DOI {doi}")
        inventory_sha = inventory.get("sha256", "").strip().casefold()
        if inventory_sha in seen_hashes:
            raise ValueError(f"duplicate inventory SHA-256 {inventory_sha}")
        seen_hashes.add(inventory_sha)
        source_path = (batch_dir / inventory.get("filename", "")).resolve()
        actual_sha, hash_status, pdf_status, page_count = _pdf_evidence(
            source_path, batch_dir=batch_dir, inventory_sha=inventory_sha
        )
        citation = citations.get(doi, {})
        if citation and citation.get("resource_id") != resource_id:
            citation = {}
        journal_match, journal_rank = _journal_evidence(
            candidate.get("venue", ""), journal_rows
        )
        blockers = ["integrity_unverified", "rights_unverified"]
        if hash_status != "match":
            blockers.append("hash_mismatch" if hash_status == "mismatch" else "pdf_missing")
        if pdf_status != "readable":
            blockers.append("pdf_unreadable")
        if candidate.get("publication_status", "") not in {
            "version_of_record", "early_access"
        }:
            blockers.append("publication_unverified")
        if not all(
            citation.get(field, "").strip()
            for field in ("citation_count", "citation_source", "citation_checked_at")
        ):
            blockers.append("citation_missing")
        if journal_match != "matched" or not journal_rank:
            blockers.append("journal_match_pending")
        elif int(journal_rank) > 2:
            blockers.append("journal_rank_below_threshold")
        if not screen.get("quality_tier", "").strip():
            blockers.append("quality_tier_unassigned")
        decision = screen.get("decision", "")
        if decision == "pending_manual_content_review":
            blockers.append("manual_content_review")
        elif decision == "pending_scope_review":
            blockers.append("scope_review")
        elif decision == "pending_pdf_doi_identity_review":
            blockers.append("pdf_doi_identity_review")
        topics = candidate.get("topics", "")
        primary_topic = candidate.get("primary_topic", "")
        if not primary_topic or primary_topic not in topics.split(";"):
            blockers.append("topic_pending")
        rows.append(
            {
                "batch": str(batch),
                "resource_id": resource_id,
                "doi": doi,
                "title": candidate.get("title", ""),
                "language": candidate.get("language", ""),
                "venue": candidate.get("venue", ""),
                "source_url": candidate.get("source_url", ""),
                "source_path": source_path.relative_to(root).as_posix()
                if source_path.is_relative_to(root) else str(source_path),
                "inventory_sha256": inventory_sha,
                "actual_sha256": actual_sha,
                "hash_status": hash_status,
                "pdf_status": pdf_status,
                "page_count": page_count,
                "primary_topic": primary_topic,
                "topics": topics,
                "publication_status": candidate.get("publication_status", ""),
                "content_score": str(score),
                "content_decision": decision,
                "citation_count": citation.get("citation_count", ""),
                "citation_source": citation.get("citation_source", ""),
                "citation_checked_at": citation.get("citation_checked_at", ""),
                "journal_match_status": journal_match,
                "journal_best_rank": journal_rank,
                "integrity_status": "pending",
                "rights_status": "pending",
                "quality_tier": screen.get("quality_tier", ""),
                "manual_review_status": "pending" if "review" in decision else "not_flagged",
                "blocker_codes": ";".join(blockers),
            }
        )
    if set(screening).difference(inventory_by_doi):
        missing = sorted(set(screening).difference(inventory_by_doi))
        raise ValueError(f"screening DOI absent from inventory: {missing[:3]}")
    return ReadinessBuild(tuple(rows), excluded_count, input_hashes)
