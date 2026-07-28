# Ped-Agent Knowledge Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Phase 1 local-first Ped-Agent knowledge foundation that imports governed pedestrian-flow literature and regulations, indexes approved evidence with FTS5/BM25, evaluates retrieval without an LLM, and exposes the library through a read-only API and unified frontend shell.

**Architecture:** A Python 3.12 modular monolith owns the local SQLite catalog, SHA-256 content vault, deterministic PDF parsing, FTS5 index, retrieval evidence packages, evaluation, CLI, and FastAPI endpoints. A Vue 3 frontend is the shared Ped-Agent workspace; Phase 1 implements only the knowledge-library route while reserving navigation for future QA and analysis modules. Mutable originals, catalog files, derived text, and indexes stay under `backend/storage/library/` and remain ignored by Git.

**Tech Stack:** Python 3.12, uv, Pydantic 2, FastAPI, Typer, SQLite/FTS5, PyMuPDF, jieba, pytest, Ruff, Vue 3, TypeScript, Vite, Vue Router, Vitest.

---

## Scope and file map

Create these focused units before adding pilot data:

```text
backend/
├─ pyproject.toml
├─ src/ped_agent/
│  ├─ __init__.py
│  ├─ paths.py                 # repository-local runtime paths
│  ├─ models.py                # shared domain and evidence contracts
│  ├─ catalog.py               # authoritative SQLite catalog access
│  ├─ vault.py                 # SHA-256 content-addressed originals
│  ├─ manifest.py              # JSONL loading and write-free preflight
│  ├─ parsing.py               # PDF cleaning and page-traceable chunking
│  ├─ importer.py              # governed import orchestration
│  ├─ tokenization.py          # bilingual lexical tokenization
│  ├─ index.py                 # rebuildable FTS5 index backend
│  ├─ retrieval.py             # candidate search and evidence hydration
│  ├─ evaluation.py            # Gold Set metrics and reports
│  ├─ api.py                   # read-only FastAPI application
│  └─ cli.py                   # local import/index/search/evaluate commands
└─ tests/                      # unit, integration, and end-to-end tests

frontend/
├─ package.json
├─ vite.config.ts
├─ src/
│  ├─ main.ts
│  ├─ router.ts
│  ├─ api.ts
│  ├─ types.ts
│  ├─ App.vue
│  └─ views/LibraryView.vue
└─ tests/App.spec.ts

research/
├─ manifests/                 # committed verified metadata; no PDFs
├─ sources/                   # search and access logs
└─ experiments/               # Gold Questions, configs, summary reports

scripts/
└─ validate_all.ps1           # complete local verification entry point
```

Do not add a memory implementation, online metadata editor, upload API, review dashboard, vector database, LLM provider, trajectory engine, or safety-analysis code in this plan.

### Task 1: Bootstrap the backend package and runtime paths

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/src/ped_agent/__init__.py`
- Create: `backend/src/ped_agent/paths.py`
- Create: `backend/tests/test_paths.py`

- [ ] **Step 1: Write the failing runtime-path test**

```python
# backend/tests/test_paths.py
from pathlib import Path

from ped_agent.paths import WorkspacePaths


def test_workspace_paths_keep_library_below_backend(tmp_path: Path) -> None:
    paths = WorkspacePaths.from_repo_root(tmp_path)

    assert paths.library_root == tmp_path / "backend" / "storage" / "library"
    assert paths.catalog_path == paths.library_root / "catalog" / "catalog.sqlite3"
    assert paths.index_path == paths.library_root / "indexes" / "fts.sqlite3"
    assert paths.inbox_dir == paths.library_root / "inbox"
```

- [ ] **Step 2: Run the test and verify the package does not exist yet**

Run from the repository root:

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_paths.py -q
```

Expected: FAIL before test collection because `backend/pyproject.toml` does not exist yet.

- [ ] **Step 3: Create the Python project and path object**

```toml
# backend/pyproject.toml
[project]
name = "ped-agent"
version = "0.1.0"
description = "Local-first pedestrian-flow knowledge foundation"
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.116,<1",
  "jieba>=0.42,<1",
  "pydantic>=2.11,<3",
  "pymupdf>=1.26,<2",
  "typer>=0.16,<1",
  "uvicorn>=0.35,<1",
]

[dependency-groups]
dev = [
  "httpx>=0.28,<1",
  "pytest>=8.4,<9",
  "ruff>=0.12,<1",
]

[project.scripts]
ped-agent = "ped_agent.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/ped_agent"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py312"
```

```python
# backend/src/ped_agent/__init__.py
"""Ped-Agent local knowledge foundation."""
```

```python
# backend/src/ped_agent/paths.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorkspacePaths:
    repo_root: Path
    library_root: Path
    inbox_dir: Path
    objects_dir: Path
    derived_dir: Path
    reports_dir: Path
    catalog_path: Path
    index_path: Path

    @classmethod
    def from_repo_root(cls, repo_root: Path) -> "WorkspacePaths":
        root = repo_root.resolve()
        library_root = root / "backend" / "storage" / "library"
        return cls(
            repo_root=root,
            library_root=library_root,
            inbox_dir=library_root / "inbox",
            objects_dir=library_root / "objects",
            derived_dir=library_root / "derived",
            reports_dir=library_root / "reports",
            catalog_path=library_root / "catalog" / "catalog.sqlite3",
            index_path=library_root / "indexes" / "fts.sqlite3",
        )

    def ensure_local_dirs(self) -> None:
        for directory in (
            self.inbox_dir,
            self.objects_dir,
            self.derived_dir,
            self.reports_dir,
            self.catalog_path.parent,
            self.index_path.parent,
        ):
            directory.mkdir(parents=True, exist_ok=True)
```

- [ ] **Step 4: Install dependencies and run the test**

```powershell
uv sync --project backend --group dev
uv run --project backend --group dev python -m pytest backend/tests/test_paths.py -q
```

Expected: `1 passed`.

- [ ] **Step 5: Commit the backend bootstrap**

```powershell
git add backend/pyproject.toml backend/src/ped_agent backend/tests/test_paths.py backend/uv.lock
git commit -m "build: bootstrap Ped-Agent backend"
```

### Task 2: Define stable resource, chunk, and evidence contracts

**Files:**
- Create: `backend/src/ped_agent/models.py`
- Create: `backend/tests/test_models.py`

- [ ] **Step 1: Write failing contract tests**

```python
# backend/tests/test_models.py
from pathlib import Path

import pytest
from pydantic import ValidationError

from ped_agent.models import (
    AdmissionStatus,
    ResourceManifest,
    ResourceType,
    RetrievalEligibility,
)


def test_regulation_requires_document_number_and_jurisdiction() -> None:
    with pytest.raises(ValidationError):
        ResourceManifest(
            resource_id="reg-cn-missing",
            resource_type=ResourceType.REGULATION,
            title="Missing fields",
            language="zh-CN",
            source_path=Path("missing.pdf"),
            sha256="0" * 64,
        )


def test_included_manifest_maps_to_approved_official() -> None:
    record = ResourceManifest(
        resource_id="paper-demo-2026",
        resource_type=ResourceType.LITERATURE,
        title="Pedestrian bottleneck experiment",
        language="en",
        source_path=Path("paper.pdf"),
        sha256="1" * 64,
        doi="10.1000/demo",
        include=True,
    )

    assert record.admission_status is AdmissionStatus.APPROVED
    assert record.retrieval_eligibility is RetrievalEligibility.OFFICIAL


def test_inactive_regulation_cannot_enter_official_retrieval() -> None:
    with pytest.raises(ValidationError, match="current effective_status"):
        ResourceManifest(
            resource_id="reg-expired-2026",
            resource_type=ResourceType.REGULATION,
            title="Expired regulation",
            language="zh-CN",
            source_path=Path("expired.pdf"),
            sha256="2" * 64,
            document_number="GB-DEMO-OLD",
            jurisdiction="CN",
            issuing_body="Demo authority",
            effective_status="superseded",
            published_date="2020-01-01",
            effective_date="2020-06-01",
            legal_level="national_standard",
            include=True,
        )
```

- [ ] **Step 2: Run the tests and verify they fail**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_models.py -q
```

Expected: FAIL with an import error for `ped_agent.models`.

- [ ] **Step 3: Implement the shared contracts**

```python
# backend/src/ped_agent/models.py
from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class ResourceType(StrEnum):
    LITERATURE = "literature"
    REGULATION = "regulation"
    STANDARD = "standard"


class AdmissionStatus(StrEnum):
    CANDIDATE = "candidate"
    METADATA_VERIFIED = "metadata_verified"
    CONTENT_VERIFIED = "content_verified"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    WITHDRAWN = "withdrawn"


class RetrievalEligibility(StrEnum):
    EXCLUDED = "excluded"
    STAGING = "staging"
    OFFICIAL = "official"


class ResourceManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resource_id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]+$")
    resource_type: ResourceType
    title: str = Field(min_length=3)
    language: str = Field(min_length=2)
    source_path: Path
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_url: HttpUrl | None = None
    doi: str | None = None
    document_number: str | None = None
    jurisdiction: str | None = None
    issuing_body: str | None = None
    effective_status: str | None = None
    published_date: str | None = None
    effective_date: str | None = None
    venue: str | None = None
    evidence_type: str | None = None
    methods: list[str] = Field(default_factory=list)
    scenarios: list[str] = Field(default_factory=list)
    applicable_scope: str | None = None
    legal_level: str | None = None
    accessed_date: str | None = None
    supersedes: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    datasets: list[str] = Field(default_factory=list)
    include: bool = False

    @model_validator(mode="after")
    def validate_domain_fields(self) -> "ResourceManifest":
        if self.resource_type in {ResourceType.REGULATION, ResourceType.STANDARD}:
            if not all(
                (
                    self.document_number,
                    self.jurisdiction,
                    self.issuing_body,
                    self.effective_status,
                    self.published_date,
                    self.effective_date,
                    self.legal_level,
                )
            ):
                raise ValueError(
                    "regulations and standards require identity, jurisdiction, issuing body, "
                    "dates, legal level, and effective status"
                )
            if self.include and self.effective_status != "current":
                raise ValueError("official regulations require current effective_status")
        if self.resource_type is ResourceType.LITERATURE and not self.doi and not self.source_url:
            raise ValueError("literature requires a DOI or stable source URL")
        return self

    @property
    def admission_status(self) -> AdmissionStatus:
        return AdmissionStatus.APPROVED if self.include else AdmissionStatus.CANDIDATE

    @property
    def retrieval_eligibility(self) -> RetrievalEligibility:
        return RetrievalEligibility.OFFICIAL if self.include else RetrievalEligibility.EXCLUDED


class CanonicalChunk(BaseModel):
    chunk_id: str
    resource_id: str
    version_id: str
    ordinal: int
    text: str = Field(min_length=1)
    page_start: int
    page_end: int
    locator: str
    section: str | None = None
    parser_version: str


class EvidenceHit(BaseModel):
    resource_id: str
    version_id: str
    chunk_id: str
    title: str
    resource_type: ResourceType
    text: str
    locator: str
    source_url: str | None
    doi: str | None
    document_number: str | None
    jurisdiction: str | None
    effective_status: str | None
    score: float
```

- [ ] **Step 4: Run the model tests**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_models.py -q
```

Expected: `3 passed`.

- [ ] **Step 5: Commit the contracts**

```powershell
git add backend/src/ped_agent/models.py backend/tests/test_models.py
git commit -m "feat: define knowledge resource contracts"
```

### Task 3: Implement the authoritative SQLite catalog

**Files:**
- Create: `backend/src/ped_agent/catalog.py`
- Create: `backend/tests/test_catalog.py`

- [ ] **Step 1: Write failing catalog tests**

```python
# backend/tests/test_catalog.py
from pathlib import Path

from ped_agent.catalog import Catalog
from ped_agent.models import CanonicalChunk, ResourceManifest, ResourceType


def literature(source_path: Path) -> ResourceManifest:
    return ResourceManifest(
        resource_id="paper-catalog-2026",
        resource_type=ResourceType.LITERATURE,
        title="Catalog test paper",
        language="en",
        source_path=source_path,
        sha256="a" * 64,
        doi="10.1000/catalog",
        datasets=["juelich-demo"],
        include=True,
    )


def test_catalog_persists_resource_version_and_chunks(tmp_path: Path) -> None:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    record = literature(tmp_path / "paper.pdf")
    catalog.upsert_resource(record, version_id=record.sha256, vault_path="objects/aa/file.pdf")
    catalog.replace_chunks(
        record.sha256,
        [
            CanonicalChunk(
                chunk_id="paper-catalog-2026:a:0000",
                resource_id=record.resource_id,
                version_id=record.sha256,
                ordinal=0,
                text="Pedestrian density and speed evidence.",
                page_start=3,
                page_end=3,
                locator="p.3",
                parser_version="pedestrian-pdf-v1",
            )
        ],
    )

    detail = catalog.get_resource(record.resource_id)
    assert detail["title"] == "Catalog test paper"
    assert catalog.list_official_chunks()[0]["locator"] == "p.3"
    assert catalog.list_relations(record.resource_id) == [
        {"relation_type": "uses_dataset", "target_ref": "juelich-demo"}
    ]
```

- [ ] **Step 2: Run the test and verify failure**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_catalog.py -q
```

Expected: FAIL with an import error for `ped_agent.catalog`.

- [ ] **Step 3: Implement the catalog schema and repository**

```python
# backend/src/ped_agent/catalog.py
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from ped_agent.models import CanonicalChunk, ResourceManifest


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS resources (
    resource_id TEXT PRIMARY KEY,
    resource_type TEXT NOT NULL,
    title TEXT NOT NULL,
    language TEXT NOT NULL,
    admission_status TEXT NOT NULL,
    retrieval_eligibility TEXT NOT NULL,
    canonical_metadata TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS resource_versions (
    version_id TEXT PRIMARY KEY,
    resource_id TEXT NOT NULL REFERENCES resources(resource_id),
    sha256 TEXT NOT NULL,
    vault_path TEXT NOT NULL,
    source_path TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS chunks (
    chunk_id TEXT PRIMARY KEY,
    resource_id TEXT NOT NULL REFERENCES resources(resource_id),
    version_id TEXT NOT NULL REFERENCES resource_versions(version_id),
    ordinal INTEGER NOT NULL,
    text TEXT NOT NULL,
    page_start INTEGER NOT NULL,
    page_end INTEGER NOT NULL,
    locator TEXT NOT NULL,
    section TEXT,
    parser_version TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_chunks_resource ON chunks(resource_id, version_id, ordinal);
CREATE TABLE IF NOT EXISTS resource_relations (
    source_resource_id TEXT NOT NULL REFERENCES resources(resource_id),
    relation_type TEXT NOT NULL,
    target_ref TEXT NOT NULL,
    PRIMARY KEY (source_resource_id, relation_type, target_ref)
);
"""


class Catalog:
    def __init__(self, path: Path) -> None:
        self.path = path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    def upsert_resource(
        self,
        record: ResourceManifest,
        *,
        version_id: str,
        vault_path: str,
    ) -> None:
        metadata = record.model_dump(mode="json")
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO resources VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(resource_id) DO UPDATE SET
                    resource_type=excluded.resource_type,
                    title=excluded.title,
                    language=excluded.language,
                    admission_status=excluded.admission_status,
                    retrieval_eligibility=excluded.retrieval_eligibility,
                    canonical_metadata=excluded.canonical_metadata
                """,
                (
                    record.resource_id,
                    record.resource_type.value,
                    record.title,
                    record.language,
                    record.admission_status.value,
                    record.retrieval_eligibility.value,
                    json.dumps(metadata, ensure_ascii=False),
                ),
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO resource_versions
                    (version_id, resource_id, sha256, vault_path, source_path)
                VALUES (?, ?, ?, ?, ?)
                """,
                (version_id, record.resource_id, record.sha256, vault_path, str(record.source_path)),
            )
            connection.execute(
                "DELETE FROM resource_relations WHERE source_resource_id = ?",
                (record.resource_id,),
            )
            connection.executemany(
                """
                INSERT INTO resource_relations (source_resource_id, relation_type, target_ref)
                VALUES (?, ?, ?)
                """,
                [
                    (record.resource_id, "supersedes", target)
                    for target in record.supersedes
                ]
                + [
                    (record.resource_id, "uses_dataset", target)
                    for target in record.datasets
                ],
            )

    def replace_chunks(self, version_id: str, chunks: list[CanonicalChunk]) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM chunks WHERE version_id = ?", (version_id,))
            connection.executemany(
                """
                INSERT INTO chunks
                    (chunk_id, resource_id, version_id, ordinal, text, page_start,
                     page_end, locator, section, parser_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        item.chunk_id,
                        item.resource_id,
                        item.version_id,
                        item.ordinal,
                        item.text,
                        item.page_start,
                        item.page_end,
                        item.locator,
                        item.section,
                        item.parser_version,
                    )
                    for item in chunks
                ],
            )

    def get_resource(self, resource_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM resources WHERE resource_id = ?", (resource_id,)
            ).fetchone()
            if row is None:
                return None
            result = dict(row)
            result["canonical_metadata"] = json.loads(result["canonical_metadata"])
            return result

    def list_resources(
        self,
        resource_type: str | None = None,
        *,
        topic: str | None = None,
        year: str | None = None,
        effective_status: str | None = None,
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM resources"
        params: tuple[str, ...] = ()
        if resource_type:
            query += " WHERE resource_type = ?"
            params = (resource_type,)
        query += " ORDER BY title"
        with self.connect() as connection:
            rows = [dict(row) for row in connection.execute(query, params)]
        results: list[dict[str, Any]] = []
        for row in rows:
            metadata = json.loads(row["canonical_metadata"])
            row["canonical_metadata"] = metadata
            if topic and topic not in metadata.get("topics", []):
                continue
            if year and not str(metadata.get("published_date", "")).startswith(year):
                continue
            if effective_status and metadata.get("effective_status") != effective_status:
                continue
            results.append(row)
        return results

    def list_official_chunks(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            return [
                dict(row)
                for row in connection.execute(
                    """
                    SELECT c.*, r.title, r.resource_type, r.canonical_metadata
                    FROM chunks c
                    JOIN resources r ON r.resource_id = c.resource_id
                    WHERE r.retrieval_eligibility = 'official'
                    ORDER BY c.resource_id, c.ordinal
                    """
                )
            ]

    def hydrate_chunk(self, chunk_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT c.*, r.title, r.resource_type, r.retrieval_eligibility,
                       r.canonical_metadata
                FROM chunks c
                JOIN resources r ON r.resource_id = c.resource_id
                WHERE c.chunk_id = ?
                """,
                (chunk_id,),
            ).fetchone()
            if row is None:
                return None
            result = dict(row)
            result["canonical_metadata"] = json.loads(result["canonical_metadata"])
            return result

    def list_relations(self, resource_id: str) -> list[dict[str, str]]:
        with self.connect() as connection:
            return [
                {
                    "relation_type": row["relation_type"],
                    "target_ref": row["target_ref"],
                }
                for row in connection.execute(
                    """
                    SELECT relation_type, target_ref
                    FROM resource_relations
                    WHERE source_resource_id = ?
                    ORDER BY relation_type, target_ref
                    """,
                    (resource_id,),
                )
            ]

    def official_fingerprint(self) -> str:
        digest = hashlib.sha256()
        for chunk in self.list_official_chunks():
            digest.update(chunk["chunk_id"].encode("utf-8"))
            digest.update(chunk["text"].encode("utf-8"))
        return digest.hexdigest()
```

- [ ] **Step 4: Run the catalog test**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_catalog.py -q
```

Expected: `1 passed`.

- [ ] **Step 5: Commit the catalog**

```powershell
git add backend/src/ped_agent/catalog.py backend/tests/test_catalog.py
git commit -m "feat: add authoritative resource catalog"
```

### Task 4: Add the content vault and write-free manifest preflight

**Files:**
- Create: `backend/src/ped_agent/vault.py`
- Create: `backend/src/ped_agent/manifest.py`
- Create: `backend/tests/test_manifest_preflight.py`

- [ ] **Step 1: Write failing preflight tests**

```python
# backend/tests/test_manifest_preflight.py
import hashlib
import json
from pathlib import Path

import pytest

from ped_agent.manifest import ManifestPreflightError, load_and_preflight


def write_manifest(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text("\n".join(json.dumps(item) for item in records) + "\n", encoding="utf-8")


def test_preflight_rejects_hash_mismatch_without_creating_storage(tmp_path: Path) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-demo")
    manifest = tmp_path / "manifest.jsonl"
    write_manifest(
        manifest,
        [
            {
                "resource_id": "paper-preflight-2026",
                "resource_type": "literature",
                "title": "Preflight paper",
                "language": "en",
                "source_path": str(source),
                "sha256": "0" * 64,
                "doi": "10.1000/preflight",
                "include": True,
            }
        ],
    )

    with pytest.raises(ManifestPreflightError, match="SHA-256 mismatch"):
        load_and_preflight(manifest)

    assert not (tmp_path / "storage").exists()


def test_preflight_accepts_matching_hash(tmp_path: Path) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-demo")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest = tmp_path / "manifest.jsonl"
    write_manifest(
        manifest,
        [
            {
                "resource_id": "paper-preflight-2026",
                "resource_type": "literature",
                "title": "Preflight paper",
                "language": "en",
                "source_path": str(source),
                "sha256": digest,
                "doi": "10.1000/preflight",
                "include": True,
            }
        ],
    )

    assert load_and_preflight(manifest)[0].resource_id == "paper-preflight-2026"
```

- [ ] **Step 2: Run the tests and verify failure**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_manifest_preflight.py -q
```

Expected: FAIL with an import error for `ped_agent.manifest`.

- [ ] **Step 3: Implement hashing, vault storage, and preflight**

```python
# backend/src/ped_agent/vault.py
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class ContentVault:
    def __init__(self, root: Path) -> None:
        self.root = root

    def put(self, source: Path, expected_sha256: str) -> Path:
        actual = sha256_file(source)
        if actual != expected_sha256:
            raise ValueError(f"SHA-256 mismatch for {source}")
        suffix = source.suffix.lower() or ".bin"
        target = self.root / actual[:2] / f"{actual}{suffix}"
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)
        return target
```

```python
# backend/src/ped_agent/manifest.py
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
```

- [ ] **Step 4: Run the preflight tests**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_manifest_preflight.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Commit vault and preflight support**

```powershell
git add backend/src/ped_agent/vault.py backend/src/ped_agent/manifest.py backend/tests/test_manifest_preflight.py
git commit -m "feat: add governed manifest preflight"
```

### Task 5: Parse PDFs into deterministic page-traceable chunks

**Files:**
- Create: `backend/src/ped_agent/parsing.py`
- Create: `backend/tests/test_parsing.py`

- [ ] **Step 1: Write a failing PDF parsing test**

```python
# backend/tests/test_parsing.py
from pathlib import Path

import fitz

from ped_agent.parsing import parse_pdf


def create_pdf(path: Path) -> None:
    document = fitz.open()
    for page_number in range(1, 4):
        page = document.new_page()
        page.insert_text((72, 36), "Repeated Header")
        page.insert_text((72, 90), f"Page {page_number} pedestrian evidence " + "flow " * 120)
        page.insert_text((72, 760), "Repeated Footer")
    document.save(path)


def test_parser_removes_repeated_edges_and_preserves_page_locator(tmp_path: Path) -> None:
    pdf = tmp_path / "sample.pdf"
    create_pdf(pdf)

    chunks = parse_pdf(
        pdf,
        resource_id="paper-parser-2026",
        version_id="b" * 64,
    )

    assert chunks
    assert all("Repeated Header" not in item.text for item in chunks)
    assert all("Repeated Footer" not in item.text for item in chunks)
    assert chunks[0].locator == "p.1"
    assert max(len(item.text) for item in chunks) <= 1200


def test_parser_extracts_regulation_clause_locator(tmp_path: Path) -> None:
    pdf = tmp_path / "regulation.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "第五条 安全出口附近应避免形成高密度拥堵。")
    document.save(pdf)

    chunks = parse_pdf(
        pdf,
        resource_id="reg-parser-2026",
        version_id="d" * 64,
        detect_clauses=True,
    )

    assert chunks[0].locator == "第五条 / p.1"
    assert chunks[0].section == "第五条"
```

- [ ] **Step 2: Run the test and verify failure**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_parsing.py -q
```

Expected: FAIL with an import error for `ped_agent.parsing`.

- [ ] **Step 3: Implement deterministic PDF cleaning and chunking**

```python
# backend/src/ped_agent/parsing.py
from __future__ import annotations

from collections import Counter
from pathlib import Path

import fitz

from ped_agent.models import CanonicalChunk

PARSER_VERSION = "pedestrian-pdf-v1"
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 120


def _page_lines(document: fitz.Document) -> list[list[str]]:
    return [
        [line.strip() for line in page.get_text("text").splitlines() if line.strip()]
        for page in document
    ]


def _repeated_edge_lines(pages: list[list[str]]) -> set[str]:
    if len(pages) < 2:
        return set()
    counts: Counter[str] = Counter()
    for lines in pages:
        counts.update(set(lines[:2] + lines[-2:]))
    threshold = max(2, (len(pages) + 1) // 2)
    return {line for line, count in counts.items() if count >= threshold}


def _split_text(text: str) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + CHUNK_SIZE)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = end - CHUNK_OVERLAP
    return chunks


def _clause_locator(text: str, page_number: int) -> tuple[str, str | None]:
    import re

    match = re.search(r"第[一二三四五六七八九十百千万0-9.]+条", text)
    if match:
        return f"{match.group(0)} / p.{page_number}", match.group(0)
    return f"p.{page_number}", None


def parse_pdf(
    path: Path,
    *,
    resource_id: str,
    version_id: str,
    detect_clauses: bool = False,
) -> list[CanonicalChunk]:
    document = fitz.open(path)
    if document.needs_pass:
        raise ValueError(f"encrypted PDF is not supported: {path}")
    pages = _page_lines(document)
    repeated = _repeated_edge_lines(pages)
    output: list[CanonicalChunk] = []
    ordinal = 0
    for page_number, lines in enumerate(pages, start=1):
        cleaned = "\n".join(line for line in lines if line not in repeated).strip()
        for text in _split_text(cleaned):
            locator, section = (
                _clause_locator(text, page_number)
                if detect_clauses
                else (f"p.{page_number}", None)
            )
            output.append(
                CanonicalChunk(
                    chunk_id=f"{resource_id}:{version_id[:12]}:{ordinal:05d}",
                    resource_id=resource_id,
                    version_id=version_id,
                    ordinal=ordinal,
                    text=text,
                    page_start=page_number,
                    page_end=page_number,
                    locator=locator,
                    section=section,
                    parser_version=PARSER_VERSION,
                )
            )
            ordinal += 1
    if not output:
        raise ValueError(f"PDF produced no indexable text: {path}")
    return output
```

- [ ] **Step 4: Run the parser test**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_parsing.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Commit the parser**

```powershell
git add backend/src/ped_agent/parsing.py backend/tests/test_parsing.py
git commit -m "feat: add traceable PDF chunking"
```

### Task 6: Orchestrate import and expose local CLI commands

**Files:**
- Create: `backend/src/ped_agent/importer.py`
- Create: `backend/src/ped_agent/cli.py`
- Create: `backend/tests/test_importer.py`

- [ ] **Step 1: Write a failing idempotent import test**

```python
# backend/tests/test_importer.py
import hashlib
import json
from pathlib import Path

import fitz

from ped_agent.catalog import Catalog
from ped_agent.importer import ImportService
from ped_agent.paths import WorkspacePaths


def create_pdf(path: Path) -> str:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Pedestrian bottleneck density evidence.")
    document.save(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_import_is_idempotent_and_stores_official_chunks(tmp_path: Path) -> None:
    paths = WorkspacePaths.from_repo_root(tmp_path)
    paths.ensure_local_dirs()
    source = tmp_path / "paper.pdf"
    digest = create_pdf(source)
    manifest = tmp_path / "manifest.jsonl"
    manifest.write_text(
        json.dumps(
            {
                "resource_id": "paper-import-2026",
                "resource_type": "literature",
                "title": "Import paper",
                "language": "en",
                "source_path": str(source),
                "sha256": digest,
                "doi": "10.1000/import",
                "include": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    service = ImportService(paths)

    first = service.import_manifest(manifest)
    second = service.import_manifest(manifest)

    assert first.imported == 1
    assert second.unchanged == 1
    assert len(Catalog(paths.catalog_path).list_official_chunks()) == 1


def test_import_isolates_one_processing_failure(tmp_path: Path) -> None:
    paths = WorkspacePaths.from_repo_root(tmp_path)
    paths.ensure_local_dirs()
    good = tmp_path / "good.pdf"
    good_hash = create_pdf(good)
    bad = tmp_path / "bad.pdf"
    bad.write_bytes(b"not-a-pdf")
    bad_hash = hashlib.sha256(bad.read_bytes()).hexdigest()
    manifest = tmp_path / "mixed.jsonl"
    records = [
        {
            "resource_id": "paper-good-2026",
            "resource_type": "literature",
            "title": "Good paper",
            "language": "en",
            "source_path": str(good),
            "sha256": good_hash,
            "doi": "10.1000/good",
            "include": True,
        },
        {
            "resource_id": "paper-bad-2026",
            "resource_type": "literature",
            "title": "Bad paper",
            "language": "en",
            "source_path": str(bad),
            "sha256": bad_hash,
            "doi": "10.1000/bad",
            "include": True,
        },
    ]
    manifest.write_text(
        "\n".join(json.dumps(item) for item in records) + "\n",
        encoding="utf-8",
    )

    report = ImportService(paths).import_manifest(manifest)

    assert report.imported == 1
    assert report.failures[0].resource_id == "paper-bad-2026"
    assert Catalog(paths.catalog_path).get_resource("paper-good-2026") is not None
```

- [ ] **Step 2: Run the test and verify failure**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_importer.py -q
```

Expected: FAIL with an import error for `ped_agent.importer`.

- [ ] **Step 3: Implement import orchestration and CLI entry points**

```python
# backend/src/ped_agent/importer.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ped_agent.catalog import Catalog
from ped_agent.manifest import load_and_preflight
from ped_agent.parsing import parse_pdf
from ped_agent.paths import WorkspacePaths
from ped_agent.vault import ContentVault


@dataclass(frozen=True)
class ImportFailure:
    resource_id: str
    reason: str


@dataclass(frozen=True)
class ImportReport:
    imported: int
    unchanged: int
    failures: tuple[ImportFailure, ...]


class ImportService:
    def __init__(self, paths: WorkspacePaths) -> None:
        self.paths = paths
        self.paths.ensure_local_dirs()
        self.catalog = Catalog(paths.catalog_path)
        self.catalog.initialize()
        self.vault = ContentVault(paths.objects_dir)

    def import_manifest(self, manifest_path: Path) -> ImportReport:
        records = load_and_preflight(manifest_path)
        imported = 0
        unchanged = 0
        failures: list[ImportFailure] = []
        for record in records:
            version_id = record.sha256
            existing = self.catalog.get_resource(record.resource_id)
            if existing and existing["canonical_metadata"]["sha256"] == record.sha256:
                unchanged += 1
                continue
            try:
                vault_path = self.vault.put(record.source_path, record.sha256)
                chunks = parse_pdf(
                    vault_path,
                    resource_id=record.resource_id,
                    version_id=version_id,
                    detect_clauses=record.resource_type.value in {"regulation", "standard"},
                )
                self.catalog.upsert_resource(
                    record,
                    version_id=version_id,
                    vault_path=str(vault_path.relative_to(self.paths.library_root)),
                )
                self.catalog.replace_chunks(version_id, chunks)
                imported += 1
            except Exception as exc:
                failures.append(ImportFailure(record.resource_id, str(exc)))
        return ImportReport(
            imported=imported,
            unchanged=unchanged,
            failures=tuple(failures),
        )
```

```python
# backend/src/ped_agent/cli.py
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import typer

from ped_agent.importer import ImportService
from ped_agent.paths import WorkspacePaths

app = typer.Typer(no_args_is_help=True)
library = typer.Typer(no_args_is_help=True)
app.add_typer(library, name="library")


def repo_paths() -> WorkspacePaths:
    return WorkspacePaths.from_repo_root(Path(__file__).resolve().parents[3])


@library.command("import-manifest")
def import_manifest(
    path: Path,
    report_output: Path | None = typer.Option(None, "--report"),
) -> None:
    paths = repo_paths()
    report = ImportService(paths).import_manifest(path)
    payload = json.dumps(asdict(report), ensure_ascii=False, indent=2)
    output = report_output or paths.reports_dir / f"{path.stem}-import.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload, encoding="utf-8")
    typer.echo(payload)
```

- [ ] **Step 4: Run the importer test and CLI help**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_importer.py -q
uv run --project backend ped-agent --help
```

Expected: `2 passed`; CLI help lists the `library` command group.

- [ ] **Step 5: Commit the import pipeline**

```powershell
git add backend/src/ped_agent/importer.py backend/src/ped_agent/cli.py backend/tests/test_importer.py
git commit -m "feat: add local governed import pipeline"
```

### Task 7: Build the bilingual FTS5/BM25 index

**Files:**
- Create: `backend/src/ped_agent/tokenization.py`
- Create: `backend/src/ped_agent/index.py`
- Create: `backend/tests/test_index.py`

- [ ] **Step 1: Write a failing bilingual retrieval test**

```python
# backend/tests/test_index.py
from pathlib import Path

from ped_agent.index import FTSIndex


def test_fts_index_retrieves_chinese_and_english_queries(tmp_path: Path) -> None:
    index = FTSIndex(tmp_path / "fts.sqlite3")
    index.rebuild(
        [
            {
                "chunk_id": "zh-1",
                "resource_id": "reg-1",
                "title": "疏散规范",
                "text": "安全出口附近的人群密度需要受到控制",
                "locator": "第5.2条",
            },
            {
                "chunk_id": "en-1",
                "resource_id": "paper-1",
                "title": "Bottleneck experiment",
                "text": "Pedestrian bottleneck flow decreases under severe congestion",
                "locator": "p.4",
            },
        ],
        source_fingerprint="v1",
    )

    assert index.search("人群密度", limit=3)[0].chunk_id == "zh-1"
    assert index.search("bottleneck congestion", limit=3)[0].chunk_id == "en-1"


def test_failed_rebuild_keeps_last_valid_index(tmp_path: Path) -> None:
    index = FTSIndex(tmp_path / "fts.sqlite3")
    index.rebuild(
        [{"chunk_id": "old", "resource_id": "r1", "title": "density", "text": "density evidence", "locator": "p.1"}],
        source_fingerprint="v1",
    )

    try:
        index.rebuild([{"chunk_id": "broken"}], source_fingerprint="v2")
    except KeyError:
        pass

    assert index.search("density", limit=3)[0].chunk_id == "old"
```

- [ ] **Step 2: Run the test and verify failure**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_index.py -q
```

Expected: FAIL with an import error for `ped_agent.index`.

- [ ] **Step 3: Implement tokenization and the rebuildable index**

```python
# backend/src/ped_agent/tokenization.py
from __future__ import annotations

import re

import jieba


def tokenize_for_search(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    tokens = []
    for token in jieba.cut(normalized):
        cleaned = token.strip()
        if cleaned and re.search(r"[0-9a-z\u4e00-\u9fff]", cleaned):
            tokens.append(cleaned)
    return " ".join(tokens)
```

```python
# backend/src/ped_agent/index.py
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from ped_agent.tokenization import tokenize_for_search


@dataclass(frozen=True)
class IndexHit:
    chunk_id: str
    score: float


class FTSIndex:
    def __init__(self, path: Path) -> None:
        self.path = path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def rebuild(self, chunks: list[dict[str, object]], *, source_fingerprint: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.unlink(missing_ok=True)
        try:
            with sqlite3.connect(temporary) as connection:
                connection.execute("DROP TABLE IF EXISTS documents")
                connection.execute(
                    """
                    CREATE VIRTUAL TABLE documents USING fts5(
                        chunk_id UNINDEXED,
                        resource_id UNINDEXED,
                        title,
                        body,
                        locator UNINDEXED,
                        tokenize='unicode61'
                    )
                    """
                )
                connection.executemany(
                    "INSERT INTO documents VALUES (?, ?, ?, ?, ?)",
                    [
                        (
                            item["chunk_id"],
                            item["resource_id"],
                            tokenize_for_search(str(item["title"])),
                            tokenize_for_search(str(item["text"])),
                            item["locator"],
                        )
                        for item in chunks
                    ],
                )
                connection.execute(
                    "CREATE TABLE index_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
                )
                connection.execute(
                    "INSERT INTO index_metadata VALUES ('source_fingerprint', ?)",
                    (source_fingerprint,),
                )
            temporary.replace(self.path)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise

    def search(self, query: str, *, limit: int = 5) -> list[IndexHit]:
        tokenized = tokenize_for_search(query)
        if not tokenized:
            return []
        match_query = " AND ".join(
            f'"{token.replace(chr(34), chr(34) * 2)}"' for token in tokenized.split()
        )
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT chunk_id, bm25(documents) AS rank
                FROM documents
                WHERE documents MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (match_query, limit),
            ).fetchall()
        return [IndexHit(chunk_id=row["chunk_id"], score=-float(row["rank"])) for row in rows]

    def source_fingerprint(self) -> str:
        if not self.path.exists():
            return ""
        try:
            with self.connect() as connection:
                row = connection.execute(
                    "SELECT value FROM index_metadata WHERE key = 'source_fingerprint'"
                ).fetchone()
        except sqlite3.OperationalError:
            return ""
        return "" if row is None else str(row["value"])
```

- [ ] **Step 4: Run the index test**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_index.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Commit the FTS backend**

```powershell
git add backend/src/ped_agent/tokenization.py backend/src/ped_agent/index.py backend/tests/test_index.py
git commit -m "feat: add bilingual FTS retrieval backend"
```

### Task 8: Hydrate authoritative evidence packages

**Files:**
- Create: `backend/src/ped_agent/retrieval.py`
- Create: `backend/tests/test_retrieval.py`
- Modify: `backend/src/ped_agent/cli.py`

- [ ] **Step 1: Write a failing evidence-hydration test**

```python
# backend/tests/test_retrieval.py
from pathlib import Path

from ped_agent.catalog import Catalog
from ped_agent.index import FTSIndex
from ped_agent.models import CanonicalChunk, ResourceManifest, ResourceType
from ped_agent.retrieval import RetrievalService


def test_retrieval_returns_authoritative_locator_and_metadata(tmp_path: Path) -> None:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    record = ResourceManifest(
        resource_id="reg-exit-2026",
        resource_type=ResourceType.REGULATION,
        title="安全出口规范",
        language="zh-CN",
        source_path=tmp_path / "reg.pdf",
        sha256="c" * 64,
        source_url="https://example.org/reg",
        document_number="GB-DEMO-2026",
        jurisdiction="CN",
        issuing_body="Demo authority",
        effective_status="current",
        published_date="2026-01-01",
        effective_date="2026-07-01",
        legal_level="national_standard",
        include=True,
    )
    catalog.upsert_resource(record, version_id=record.sha256, vault_path="objects/cc/reg.pdf")
    catalog.replace_chunks(
        record.sha256,
        [
            CanonicalChunk(
                chunk_id="reg-exit-2026:c:00000",
                resource_id=record.resource_id,
                version_id=record.sha256,
                ordinal=0,
                text="安全出口附近应避免形成高密度拥堵。",
                page_start=5,
                page_end=5,
                locator="第5.2条 / p.5",
                parser_version="pedestrian-pdf-v1",
            )
        ],
    )
    index = FTSIndex(tmp_path / "fts.sqlite3")
    index.rebuild(
        catalog.list_official_chunks(),
        source_fingerprint=catalog.official_fingerprint(),
    )

    hit = RetrievalService(catalog, index).search("安全出口拥堵", limit=5)[0]

    assert hit.document_number == "GB-DEMO-2026"
    assert hit.locator == "第5.2条 / p.5"
    assert hit.effective_status == "current"
```

- [ ] **Step 2: Run the test and verify failure**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_retrieval.py -q
```

Expected: FAIL with an import error for `ped_agent.retrieval`.

- [ ] **Step 3: Implement retrieval and extend the CLI**

```python
# backend/src/ped_agent/retrieval.py
from __future__ import annotations

from ped_agent.catalog import Catalog
from ped_agent.index import FTSIndex
from ped_agent.models import EvidenceHit


class RetrievalService:
    def __init__(self, catalog: Catalog, index: FTSIndex) -> None:
        self.catalog = catalog
        self.index = index

    def search(self, query: str, *, limit: int = 5) -> list[EvidenceHit]:
        if self.index.source_fingerprint() != self.catalog.official_fingerprint():
            raise IndexStaleError("search index is stale; rebuild it from the authoritative catalog")
        evidence: list[EvidenceHit] = []
        for candidate in self.index.search(query, limit=limit):
            row = self.catalog.hydrate_chunk(candidate.chunk_id)
            if row is None or row["retrieval_eligibility"] != "official":
                continue
            metadata = row["canonical_metadata"]
            evidence.append(
                EvidenceHit(
                    resource_id=row["resource_id"],
                    version_id=row["version_id"],
                    chunk_id=row["chunk_id"],
                    title=row["title"],
                    resource_type=row["resource_type"],
                    text=row["text"],
                    locator=row["locator"],
                    source_url=str(metadata["source_url"]) if metadata.get("source_url") else None,
                    doi=metadata.get("doi"),
                    document_number=metadata.get("document_number"),
                    jurisdiction=metadata.get("jurisdiction"),
                    effective_status=metadata.get("effective_status"),
                    score=candidate.score,
                )
            )
        return evidence


class IndexStaleError(RuntimeError):
    pass
```

Add these commands to `backend/src/ped_agent/cli.py`:

```python
from ped_agent.catalog import Catalog
from ped_agent.index import FTSIndex
from ped_agent.retrieval import RetrievalService


@library.command("build-index")
def build_index() -> None:
    paths = repo_paths()
    catalog = Catalog(paths.catalog_path)
    FTSIndex(paths.index_path).rebuild(
        catalog.list_official_chunks(),
        source_fingerprint=catalog.official_fingerprint(),
    )
    typer.echo("index rebuilt")


@library.command("search")
def search(query: str, limit: int = 5) -> None:
    paths = repo_paths()
    hits = RetrievalService(Catalog(paths.catalog_path), FTSIndex(paths.index_path)).search(
        query, limit=limit
    )
    typer.echo(json.dumps([hit.model_dump(mode="json") for hit in hits], ensure_ascii=False))
```

- [ ] **Step 4: Run retrieval tests and CLI help**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_retrieval.py -q
uv run --project backend ped-agent library --help
```

Expected: `1 passed`; help lists `import-manifest`, `build-index`, and `search`.

- [ ] **Step 5: Commit retrieval evidence packages**

```powershell
git add backend/src/ped_agent/retrieval.py backend/src/ped_agent/cli.py backend/tests/test_retrieval.py
git commit -m "feat: return traceable retrieval evidence"
```

### Task 9: Add Gold Set evaluation without an LLM

**Files:**
- Create: `backend/src/ped_agent/evaluation.py`
- Create: `backend/tests/test_evaluation.py`
- Modify: `backend/src/ped_agent/cli.py`

- [ ] **Step 1: Write failing metric tests**

```python
# backend/tests/test_evaluation.py
import math

import pytest

from ped_agent.evaluation import GoldQuestion, evaluate_rankings


def test_evaluation_computes_recall_mrr_and_locator_hit() -> None:
    questions = [
        GoldQuestion(
            question_id="q1",
            query="出口拥堵",
            expected_resource_ids=["reg-1"],
            expected_locators=["第5.2条"],
        ),
        GoldQuestion(
            question_id="q2",
            query="bottleneck flow",
            expected_resource_ids=["paper-1"],
            expected_locators=["p.4"],
        ),
    ]
    rankings = {
        "q1": [("reg-x", "第1条"), ("reg-1", "第5.2条")],
        "q2": [("paper-1", "p.4")],
    }

    report = evaluate_rankings(questions, rankings, k=5)

    assert report.recall_at_k == 1.0
    assert report.mrr == 0.75
    assert report.locator_hit_rate == 1.0
    assert report.ndcg_at_k == pytest.approx((1 / math.log2(3) + 1.0) / 2)
```

- [ ] **Step 2: Run the test and verify failure**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_evaluation.py -q
```

Expected: FAIL with an import error for `ped_agent.evaluation`.

- [ ] **Step 3: Implement Gold records and metrics**

```python
# backend/src/ped_agent/evaluation.py
from __future__ import annotations

import json
import math
from pathlib import Path

from pydantic import BaseModel, Field


class GoldQuestion(BaseModel):
    question_id: str
    query: str
    expected_resource_ids: list[str] = Field(min_length=1)
    expected_locators: list[str] = Field(default_factory=list)


class EvaluationReport(BaseModel):
    question_count: int
    k: int
    recall_at_k: float
    mrr: float
    ndcg_at_k: float
    locator_hit_rate: float


class CatalogAuditReport(BaseModel):
    resource_count: int
    official_resource_count: int
    official_chunk_count: int
    locator_coverage: float
    duplicate_sha256_count: int


def load_gold(path: Path) -> list[GoldQuestion]:
    return [
        GoldQuestion.model_validate(json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def evaluate_rankings(
    questions: list[GoldQuestion],
    rankings: dict[str, list[tuple[str, str]]],
    *,
    k: int,
) -> EvaluationReport:
    recalls: list[float] = []
    reciprocal_ranks: list[float] = []
    ndcgs: list[float] = []
    locator_hits: list[float] = []
    for question in questions:
        ranked = rankings.get(question.question_id, [])[:k]
        expected_resources = set(question.expected_resource_ids)
        expected_locators = set(question.expected_locators)
        recalls.append(float(any(resource_id in expected_resources for resource_id, _ in ranked)))
        rank = next(
            (index for index, (resource_id, _) in enumerate(ranked, start=1)
             if resource_id in expected_resources),
            None,
        )
        reciprocal_ranks.append(0.0 if rank is None else 1.0 / rank)
        relevance = [int(resource_id in expected_resources) for resource_id, _ in ranked]
        dcg = sum(value / math.log2(index + 1) for index, value in enumerate(relevance, start=1))
        ideal_count = min(len(expected_resources), k)
        ideal_dcg = sum(1.0 / math.log2(index + 1) for index in range(1, ideal_count + 1))
        ndcgs.append(0.0 if ideal_dcg == 0 else dcg / ideal_dcg)
        locator_hits.append(
            float(
                not expected_locators
                or any(
                    expected in actual
                    for _, actual in ranked
                    for expected in expected_locators
                )
            )
        )
    count = len(questions)
    return EvaluationReport(
        question_count=count,
        k=k,
        recall_at_k=sum(recalls) / count,
        mrr=sum(reciprocal_ranks) / count,
        ndcg_at_k=sum(ndcgs) / count,
        locator_hit_rate=sum(locator_hits) / count,
    )


def audit_catalog(catalog) -> CatalogAuditReport:
    resources = catalog.list_resources()
    chunks = catalog.list_official_chunks()
    hashes: list[str] = []
    official = 0
    for resource in resources:
        metadata = resource["canonical_metadata"]
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        hashes.append(metadata["sha256"])
        official += int(resource["retrieval_eligibility"] == "official")
    duplicate_count = len(hashes) - len(set(hashes))
    locator_coverage = (
        0.0 if not chunks else sum(bool(item["locator"]) for item in chunks) / len(chunks)
    )
    return CatalogAuditReport(
        resource_count=len(resources),
        official_resource_count=official,
        official_chunk_count=len(chunks),
        locator_coverage=locator_coverage,
        duplicate_sha256_count=duplicate_count,
    )
```

Add this command to `backend/src/ped_agent/cli.py`:

```python
from ped_agent.evaluation import audit_catalog, evaluate_rankings, load_gold


@app.command("evaluate")
def evaluate(gold: Path, output: Path, k: int = 5) -> None:
    paths = repo_paths()
    service = RetrievalService(Catalog(paths.catalog_path), FTSIndex(paths.index_path))
    questions = load_gold(gold)
    rankings = {
        item.question_id: [
            (hit.resource_id, hit.locator) for hit in service.search(item.query, limit=k)
        ]
        for item in questions
    }
    report = evaluate_rankings(questions, rankings, k=k)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    typer.echo(report.model_dump_json())


@app.command("audit")
def audit(output: Path) -> None:
    report = audit_catalog(Catalog(repo_paths().catalog_path))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    typer.echo(report.model_dump_json())
```

- [ ] **Step 4: Run evaluation tests and Ruff**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_evaluation.py -q
uv run --project backend --group dev ruff check backend/src backend/tests
```

Expected: `1 passed`; Ruff reports `All checks passed!`; CLI exposes `evaluate` and `audit`.

- [ ] **Step 5: Commit evaluation support**

```powershell
git add backend/src/ped_agent/evaluation.py backend/src/ped_agent/cli.py backend/tests/test_evaluation.py
git commit -m "feat: add retrieval gold evaluation"
```

### Task 10: Expose the read-only library API

**Files:**
- Create: `backend/src/ped_agent/api.py`
- Create: `backend/tests/test_api.py`
- Modify: `backend/src/ped_agent/cli.py`

- [ ] **Step 1: Write failing API tests**

```python
# backend/tests/test_api.py
from pathlib import Path

from fastapi.testclient import TestClient

from ped_agent.api import create_app
from ped_agent.catalog import Catalog
from ped_agent.index import FTSIndex


def test_api_is_read_only_and_exposes_library_routes(tmp_path: Path) -> None:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    FTSIndex(tmp_path / "fts.sqlite3").rebuild(
        [], source_fingerprint=catalog.official_fingerprint()
    )
    client = TestClient(create_app(catalog_path=catalog.path, index_path=tmp_path / "fts.sqlite3"))

    assert client.get("/api/library/resources").status_code == 200
    assert client.get("/api/library/search", params={"q": "density"}).status_code == 200
    assert client.post("/api/library/resources").status_code == 405
```

- [ ] **Step 2: Run the test and verify failure**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_api.py -q
```

Expected: FAIL with an import error for `ped_agent.api`.

- [ ] **Step 3: Implement the FastAPI app and local serve command**

```python
# backend/src/ped_agent/api.py
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

from ped_agent.catalog import Catalog
from ped_agent.index import FTSIndex
from ped_agent.retrieval import IndexStaleError, RetrievalService


def create_app(*, catalog_path: Path, index_path: Path) -> FastAPI:
    app = FastAPI(title="Ped-Agent Knowledge API", version="0.1.0")
    catalog = Catalog(catalog_path)
    retrieval = RetrievalService(catalog, FTSIndex(index_path))

    @app.get("/api/library/resources")
    def list_resources(
        resource_type: str | None = None,
        topic: str | None = None,
        year: str | None = None,
        effective_status: str | None = None,
    ) -> list[dict[str, object]]:
        return catalog.list_resources(
            resource_type,
            topic=topic,
            year=year,
            effective_status=effective_status,
        )

    @app.get("/api/library/resources/{resource_id}")
    def get_resource(resource_id: str) -> dict[str, object]:
        result = catalog.get_resource(resource_id)
        if result is None:
            raise HTTPException(status_code=404, detail="resource not found")
        return result

    @app.get("/api/library/search")
    def search(q: str = Query(min_length=1), limit: int = Query(default=10, ge=1, le=50)):
        try:
            return retrieval.search(q, limit=limit)
        except IndexStaleError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    return app
```

Add this to `backend/src/ped_agent/cli.py`:

```python
import uvicorn
from ped_agent.api import create_app


@app.command("serve")
def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    paths = repo_paths()
    uvicorn.run(create_app(catalog_path=paths.catalog_path, index_path=paths.index_path), host=host, port=port)
```

- [ ] **Step 4: Run API tests**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_api.py -q
```

Expected: `1 passed`.

- [ ] **Step 5: Commit the read-only API**

```powershell
git add backend/src/ped_agent/api.py backend/src/ped_agent/cli.py backend/tests/test_api.py
git commit -m "feat: expose read-only knowledge API"
```

### Task 11: Build the unified frontend shell and knowledge-library route

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/env.d.ts`
- Create: `frontend/src/router.ts`
- Create: `frontend/src/api.ts`
- Create: `frontend/src/types.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/views/LibraryView.vue`
- Create: `frontend/tests/App.spec.ts`

- [ ] **Step 1: Write a failing shell test**

```typescript
// frontend/tests/App.spec.ts
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import App from '../src/App.vue'

describe('Ped-Agent shell', () => {
  it('opens the knowledge library and reserves future research areas', () => {
    const wrapper = mount(App, {
      global: { stubs: { RouterView: { template: '<div>Library</div>' } } },
    })

    expect(wrapper.text()).toContain('知识库')
    expect(wrapper.text()).toContain('智能问答')
    expect(wrapper.text()).toContain('轨迹分析')
    expect(wrapper.text()).toContain('安全评估')
    expect(wrapper.text()).toContain('实验支持')
    expect(wrapper.find('[data-route="knowledge"]').classes()).toContain('active')
  })
})
```

- [ ] **Step 2: Create the frontend project and verify the test fails**

```json
// frontend/package.json
{
  "name": "ped-agent-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc --noEmit && vite build",
    "test": "vitest run"
  },
  "dependencies": {
    "vue": "^3.5.18",
    "vue-router": "^4.5.1"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^6.0.1",
    "@vue/test-utils": "^2.4.6",
    "jsdom": "^26.1.0",
    "typescript": "^5.9.2",
    "vite": "^7.1.1",
    "vitest": "^3.2.4",
    "vue-tsc": "^3.0.5"
  }
}
```

Create the remaining configuration exactly as follows:

```typescript
/// <reference types="vitest/config" />
// frontend/vite.config.ts
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue()],
  server: { proxy: { '/api': 'http://127.0.0.1:8000' } },
  test: { environment: 'jsdom' },
})
```

```json
// frontend/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "skipLibCheck": true,
    "lib": ["ES2022", "DOM"],
    "types": ["vitest/globals"]
  },
  "include": ["src/**/*.ts", "src/**/*.vue", "tests/**/*.ts", "vite.config.ts"]
}
```

```html
<!-- frontend/index.html -->
<!doctype html>
<html lang="zh-CN">
  <head><meta charset="UTF-8"><title>Ped-Agent</title></head>
  <body><div id="app"></div><script type="module" src="/src/main.ts"></script></body>
</html>
```

Then run:

```powershell
Set-Location frontend
npm install
npm test
Set-Location ..
```

Expected: FAIL because `src/App.vue` does not exist.

- [ ] **Step 3: Implement the shell, route, API client, and library page**

```typescript
// frontend/src/types.ts
export interface LibraryResource {
  resource_id: string
  resource_type: 'literature' | 'regulation' | 'standard'
  title: string
  language: string
  admission_status: string
  retrieval_eligibility: string
  canonical_metadata: {
    topics?: string[]
    published_date?: string
    document_number?: string
    jurisdiction?: string
    effective_status?: string
    doi?: string
  }
}

export interface EvidenceHit {
  resource_id: string
  chunk_id: string
  title: string
  resource_type: string
  text: string
  locator: string
  score: number
}
```

```typescript
// frontend/src/api.ts
import type { EvidenceHit, LibraryResource } from './types'

const base = '/api/library'

export async function listResources(filters: {
  type?: string
  topic?: string
  year?: string
  effectiveStatus?: string
} = {}): Promise<LibraryResource[]> {
  const params = new URLSearchParams()
  if (filters.type) params.set('resource_type', filters.type)
  if (filters.topic) params.set('topic', filters.topic)
  if (filters.year) params.set('year', filters.year)
  if (filters.effectiveStatus) params.set('effective_status', filters.effectiveStatus)
  const query = params.size ? `?${params}` : ''
  const response = await fetch(`${base}/resources${query}`)
  if (!response.ok) throw new Error(`Failed to load resources: ${response.status}`)
  return response.json()
}

export async function getResource(resourceId: string): Promise<LibraryResource> {
  const response = await fetch(`${base}/resources/${encodeURIComponent(resourceId)}`)
  if (!response.ok) throw new Error(`Failed to load resource: ${response.status}`)
  return response.json()
}

export async function searchEvidence(query: string): Promise<EvidenceHit[]> {
  const response = await fetch(`${base}/search?q=${encodeURIComponent(query)}`)
  if (!response.ok) throw new Error(`Search failed: ${response.status}`)
  return response.json()
}
```

```typescript
// frontend/src/router.ts
import { createRouter, createWebHistory } from 'vue-router'
import LibraryView from './views/LibraryView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/', name: 'knowledge', component: LibraryView }],
})
```

```vue
<!-- frontend/src/App.vue -->
<script setup lang="ts">
import { RouterView } from 'vue-router'

const items = [
  { name: '知识库', active: true },
  { name: '智能问答', active: false },
  { name: '轨迹分析', active: false },
  { name: '安全评估', active: false },
  { name: '实验支持', active: false },
]
</script>

<template>
  <div class="shell">
    <aside>
      <h1>Ped-Agent</h1>
      <div
        v-for="item in items"
        :key="item.name"
        :data-route="item.active ? 'knowledge' : undefined"
        :class="['nav-item', { active: item.active, disabled: !item.active }]"
      >
        {{ item.name }}
        <small>{{ item.active ? '阶段 1' : '后续' }}</small>
      </div>
    </aside>
    <main><RouterView /></main>
  </div>
</template>
```

```vue
<!-- frontend/src/views/LibraryView.vue -->
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getResource, listResources, searchEvidence } from '../api'
import type { EvidenceHit, LibraryResource } from '../types'

const resources = ref<LibraryResource[]>([])
const hits = ref<EvidenceHit[]>([])
const query = ref('')
const type = ref('')
const topic = ref('')
const year = ref('')
const effectiveStatus = ref('')
const selected = ref<LibraryResource | null>(null)
const error = ref('')

async function loadResources() {
  try {
    resources.value = await listResources({
      type: type.value || undefined,
      topic: topic.value || undefined,
      year: year.value || undefined,
      effectiveStatus: effectiveStatus.value || undefined,
    })
  }
  catch (reason) { error.value = String(reason) }
}

onMounted(loadResources)

async function search() {
  error.value = ''
  try { hits.value = query.value.trim() ? await searchEvidence(query.value.trim()) : [] }
  catch (reason) { error.value = String(reason) }
}

async function openResource(resourceId: string) {
  try { selected.value = await getResource(resourceId) }
  catch (reason) { error.value = String(reason) }
}
</script>

<template>
  <section>
    <h2>知识库</h2>
    <div class="filters">
      <select v-model="type" @change="loadResources">
        <option value="">全部类型</option>
        <option value="literature">文献</option>
        <option value="regulation">法规</option>
        <option value="standard">标准</option>
      </select>
      <input v-model="topic" placeholder="主题" @change="loadResources" />
      <input v-model="year" placeholder="年份" @change="loadResources" />
      <select v-model="effectiveStatus" @change="loadResources">
        <option value="">全部效力状态</option>
        <option value="current">当前有效</option>
      </select>
    </div>
    <form @submit.prevent="search">
      <input v-model="query" placeholder="搜索文献、法规、主题、数据集或条款" />
      <button>搜索</button>
    </form>
    <p v-if="error" role="alert">{{ error }}</p>
    <template v-if="hits.length">
      <article v-for="hit in hits" :key="hit.chunk_id">
        <h3>{{ hit.title }}</h3><p>{{ hit.text }}</p><small>{{ hit.locator }}</small>
      </article>
    </template>
    <template v-else>
      <button v-for="item in resources" :key="item.resource_id" @click="openResource(item.resource_id)">
        <strong>{{ item.title }}</strong><small>{{ item.resource_type }}</small>
      </button>
    </template>
    <aside v-if="selected">
      <h3>{{ selected.title }}</h3>
      <p>{{ selected.canonical_metadata.document_number || selected.canonical_metadata.doi }}</p>
      <p>{{ selected.canonical_metadata.effective_status }}</p>
    </aside>
  </section>
</template>
```

```typescript
// frontend/src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router'

createApp(App).use(router).mount('#app')
```

```typescript
/// <reference types="vite/client" />
// frontend/src/env.d.ts
```

- [ ] **Step 4: Run frontend tests and build**

```powershell
Set-Location frontend
npm test
npm run build
Set-Location ..
```

Expected: tests pass and Vite produces `frontend/dist/`.

- [ ] **Step 5: Commit the frontend shell**

```powershell
git add frontend/package.json frontend/package-lock.json frontend/vite.config.ts frontend/tsconfig.json frontend/index.html frontend/src frontend/tests
git commit -m "feat: add unified knowledge library frontend"
```

### Task 12: Collect and validate the real pilot corpus

**Files:**
- Create: `research/sources/pilot_collection_log.csv`
- Create: `research/manifests/pilot_literature.jsonl`
- Create: `research/manifests/pilot_regulations.jsonl`
- Create: `backend/tests/test_pilot_manifests.py`
- Local only: `backend/storage/library/inbox/*.pdf`

- [ ] **Step 1: Write failing pilot-manifest acceptance tests**

```python
# backend/tests/test_pilot_manifests.py
from pathlib import Path

from ped_agent.manifest import load_and_preflight

ROOT = Path(__file__).resolve().parents[2]


def test_pilot_manifest_counts_and_identifiers() -> None:
    literature = load_and_preflight(ROOT / "research/manifests/pilot_literature.jsonl")
    regulations = load_and_preflight(ROOT / "research/manifests/pilot_regulations.jsonl")

    assert len(literature) == 20
    assert len(regulations) == 8
    assert len({item.resource_id for item in literature + regulations}) == 28
    assert sum(bool(item.doi) for item in literature) >= 16
    assert all(item.document_number and item.jurisdiction for item in regulations)
    assert sum(item.jurisdiction != "CN" for item in regulations) == 2
```

- [ ] **Step 2: Run the test and verify the manifests are absent**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_pilot_manifests.py -q
```

Expected: FAIL with `FileNotFoundError` for the pilot manifests.

- [ ] **Step 3: Collect four literature batches with fixed quotas**

Create five verified records in each category, for 20 total:

1. pedestrian-flow fundamentals and fundamental diagrams;
2. controlled experiments and experiment-design methods;
3. trajectory datasets, processing, and metric analysis;
4. mixed flow, evacuation, congestion, and safety assessment.

For every record:

- verify DOI or a stable official URL;
- record venue, year, language, evidence type, topics, datasets, access URL, and legal access status in `pilot_collection_log.csv`;
- obtain a legally accessible PDF and save it under `backend/storage/library/inbox/`;
- compute its exact SHA-256 with `Get-FileHash -Algorithm SHA256`;
- write one `ResourceManifest` JSON object to `pilot_literature.jsonl`;
- store `source_path` as a repository-relative path below `backend/storage/library/inbox/`, never as a user-specific absolute path;
- set `include: true` only after full text opens, page count is plausible, and the title matches the metadata;
- prefer dataset-to-paper evidence over keyword-only discovery when a dataset is involved.

After each five-paper batch run:

```powershell
uv run --project backend ped-agent library import-manifest research/manifests/pilot_literature.jsonl --report backend/storage/library/reports/pilot-literature-import.json
```

Expected after the fourth batch: JSON reports `imported + unchanged = 20` and no preflight error.

- [ ] **Step 4: Collect six Chinese and two international regulation/standard records**

The six Chinese records must cover at least three of these areas: pedestrian facilities, accessibility, building evacuation/fire safety, public-place crowd safety, emergency management. Use official national, ministry, industry, or local-government sources.

The two international comparison records must come from official ISO, NFPA, or equivalent issuing-body pages. If full text cannot be legally stored, replace the candidate with a legally accessible official or author-distributed version; do not admit abstract-only or metadata-only content as full-text RAG evidence.

For every record, verify and record document number, issuing body, jurisdiction, published/effective dates, current status, superseded documents, source URL, file hash, and access date. Save records to `pilot_regulations.jsonl` and source checks to `pilot_collection_log.csv`.

- [ ] **Step 5: Run manifest tests and import the completed pilot**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_pilot_manifests.py -q
uv run --project backend ped-agent library import-manifest research/manifests/pilot_literature.jsonl --report backend/storage/library/reports/pilot-literature-import.json
uv run --project backend ped-agent library import-manifest research/manifests/pilot_regulations.jsonl --report backend/storage/library/reports/pilot-regulations-import.json
uv run --project backend ped-agent library build-index
```

Expected: manifest test passes; total formal resources equal 28; index rebuild completes.

- [ ] **Step 6: Commit verified metadata and collection records, never PDFs**

```powershell
git status --short
git add research/sources/pilot_collection_log.csv research/manifests/pilot_literature.jsonl research/manifests/pilot_regulations.jsonl backend/tests/test_pilot_manifests.py
git commit -m "data: add verified pilot knowledge manifests"
```

Before committing, confirm `git status --short` does not list any file below `backend/storage/library/`.

### Task 13: Build the 30-question Gold Set and enforce pilot thresholds

**Files:**
- Create: `research/experiments/pilot_gold.jsonl`
- Create: `research/experiments/pilot_config.json`
- Create: `backend/tests/test_pilot_acceptance.py`

- [ ] **Step 1: Write the failing pilot threshold test**

```python
# backend/tests/test_pilot_acceptance.py
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_pilot_report_meets_phase_one_thresholds() -> None:
    report = json.loads(
        (ROOT / "research/experiments/pilot_report.json").read_text(encoding="utf-8")
    )

    assert report["question_count"] == 30
    assert report["recall_at_k"] >= 0.80
    assert report["mrr"] >= 0.70
    assert report["locator_hit_rate"] >= 0.75
    audit = json.loads(
        (ROOT / "research/experiments/pilot_audit.json").read_text(encoding="utf-8")
    )
    assert audit["resource_count"] == 28
    assert audit["official_resource_count"] == 28
    assert audit["locator_coverage"] >= 0.90
    assert audit["duplicate_sha256_count"] == 0
```

- [ ] **Step 2: Run the test and verify the report is absent**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_pilot_acceptance.py -q
```

Expected: FAIL with `FileNotFoundError` for `pilot_report.json`.

- [ ] **Step 3: Create the Gold Set with balanced task coverage**

Create exactly 30 questions:

- 8 pedestrian-flow knowledge and metric-definition retrieval questions;
- 8 experiment-design and controlled-observation questions;
- 7 trajectory-data and analysis-method questions;
- 7 regulation, safety, evacuation, or applicability questions.

Every JSONL record must include `question_id`, `query`, at least one `expected_resource_ids` value, and at least one correct `expected_locators` value. A human must open the PDF and verify every locator before the record is admitted.

Create `pilot_config.json` with:

```json
{
  "k": 5,
  "minimum_recall_at_k": 0.8,
  "minimum_mrr": 0.7,
  "minimum_locator_hit_rate": 0.75,
  "expected_question_count": 30
}
```

- [ ] **Step 4: Run evaluation and inspect failure cases**

```powershell
uv run --project backend ped-agent evaluate research/experiments/pilot_gold.jsonl research/experiments/pilot_report.json --k 5
uv run --project backend ped-agent audit research/experiments/pilot_audit.json
```

Expected: a JSON report with 30 questions. If any threshold fails, inspect the missed questions and change only evidence-backed issues in cleaning, chunking, tokenization, metadata, or query wording; do not weaken the threshold or add expected answers after seeing the ranking.

- [ ] **Step 5: Run the pilot acceptance test and commit the Gold Set**

```powershell
uv run --project backend --group dev python -m pytest backend/tests/test_pilot_acceptance.py -q
git add research/experiments/pilot_gold.jsonl research/experiments/pilot_config.json research/experiments/pilot_report.json research/experiments/pilot_audit.json backend/tests/test_pilot_acceptance.py
git commit -m "test: add pilot retrieval benchmark"
```

Expected: `1 passed` and the report meets all three thresholds.

### Task 14: Add complete local validation and project handoff documentation

**Files:**
- Create: `scripts/validate_all.ps1`
- Create: `README.md`
- Create: `docs/architecture.md`
- Create: `docs/memory-solution-study.md`

- [ ] **Step 1: Create the validation script**

```powershell
# scripts/validate_all.ps1
$ErrorActionPreference = 'Stop'

uv sync --project backend --group dev
uv run --project backend --group dev ruff check backend/src backend/tests
uv run --project backend --group dev python -m pytest backend/tests -q

Push-Location frontend
npm ci
npm test
npm run build
Pop-Location

uv run --project backend ped-agent library build-index
uv run --project backend ped-agent evaluate `
  research/experiments/pilot_gold.jsonl `
  research/experiments/pilot_report.json `
  --k 5
uv run --project backend ped-agent audit research/experiments/pilot_audit.json

git diff --check
```

- [ ] **Step 2: Document exact local workflows**

In `README.md`, include copy-ready commands for:

- backend and frontend dependency installation;
- placing private PDFs under `backend/storage/library/inbox/`;
- importing both pilot manifests;
- rebuilding the index;
- running a CLI search;
- starting the API on `127.0.0.1:8000`;
- starting the frontend development server;
- running `scripts/validate_all.ps1`.

In `docs/architecture.md`, restate the authoritative-source rule, rebuildable-index rule, read-only frontend/API boundary, and future shared evidence-package boundary.

In `docs/memory-solution-study.md`, record only the comparison questions for memU, Mem0, Zep, A-MEM, and similar systems: memory types, evidence linkage, approval, conflict/supersession, forgetting, local operation, portability, evaluation, and licensing. Do not choose a backend or define a memory schema in this task.

- [ ] **Step 3: Run the complete validation entry point**

```powershell
powershell -ExecutionPolicy Bypass -File scripts/validate_all.ps1
```

Expected:

- Ruff: `All checks passed!`;
- all backend tests pass;
- all frontend tests pass;
- Vite build succeeds;
- index rebuild succeeds;
- pilot evaluation meets the configured thresholds;
- `git diff --check` produces no output.

- [ ] **Step 4: Verify local/private boundaries**

```powershell
git status --short
git ls-files backend/storage/library
```

Expected: no tracked file under `backend/storage/library`; only source code, manifests, source logs, Gold Set, summary report, docs, and tests are tracked.

- [ ] **Step 5: Commit the validation and handoff documentation**

```powershell
git add scripts/validate_all.ps1 README.md docs/architecture.md docs/memory-solution-study.md
git commit -m "docs: add knowledge foundation runbook"
```

## Final completion check

After Task 14, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/validate_all.ps1
git status --short
git log --oneline --decorate -15
```

The Phase 1 implementation is complete only when:

- all 28 real pilot documents have verified local full text and committed metadata;
- the authoritative catalog and content vault can be rebuilt from the manifests and local originals;
- default retrieval returns only official, currently eligible evidence;
- all 30 Gold Questions have human-verified resource and locator labels;
- Recall@5, MRR, and locator-hit thresholds pass without an LLM;
- the frontend presents the knowledge library inside the unified Ped-Agent shell;
- future navigation is visible but has no implemented QA, trajectory, safety, experiment, or memory behavior;
- the worktree is clean and no private original or rebuildable database/index is tracked by Git.
