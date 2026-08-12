# Ped-Agent

Ped-Agent is a local-first, evidence-bound research agent for pedestrian-flow research.

The project has three foundation modules:

1. **知识与证据底座** — governed literature, regulations, and formal evidence, with
   Catalog, Vault, FTS5, Chroma, and retrieval evaluation.
2. **检测追踪与流动分析** — video or trajectory processing, detection, tracking,
   calibration, review, density, speed, flow, and OD analysis.
3. **LLM 问答与会话** — conversations, deterministic evidence orchestration, structured
   generation, citation validation, semantic verification, and SSE.

Literature QA, trajectory analysis, scenario diagnosis, safety assessment, and experiment
support are applications that combine these modules, not independent foundations. See the
[approved three-module architecture specification](docs/superpowers/specs/2026-08-06-ped-agent-three-module-architecture-design.md)
for the canonical boundaries.

Contributors should also read the
[active and legacy code map](docs/legacy-scaffold.md) before changing entrypoints,
configuration, retrieval, or Agent routing.

The repository exposes three program packages and one server distribution:

- `ped-agent-core` / `ped_agent`: shared contracts, policies, evidence graph, compatibility
  imports, and domain models
- `Knowledge-Base/` / `ped_knowledge`: technical ingestion, structured parsing,
  parent-child Chunking, Catalog/Vault, sparse and dense indexing, hybrid retrieval,
  optional Cross-Encoder Rerank, and Gold evaluation
- `Video-Analysis/` / `ped_video_analysis`: detector manifests, model-weight location,
  detection/tracking, calibration, trajectory processing, flow analysis, and public APIs
- `ped-agent-server` / `ped_agent_server`: FastAPI, CLI, configuration, Run lifecycle,
  model/external-service providers, observability, and cross-module adapters

The knowledge program now lives at `Knowledge-Base/src/ped_knowledge/`, parallel to
`Video-Analysis/`. The former server knowledge modules remain as compatibility exports, while
the active API, CLI, and EvidenceGraph runtime assemble `ped_knowledge` directly. `memPed/`
remains data-only. See the
[knowledge and evidence module design](docs/modules/knowledge-and-evidence.md).

The current detection-and-flow delivery includes an end-to-end mixed-flow trajectory
workbench with immutable pixel/world artifacts, review patches, calibration quality gates,
Plotly exploration, and publication figures.

## Quick Start

```powershell
Copy-Item .env.example .env
uv sync --project backend
uv run --project backend ped-agent agent doctor
uv run --project backend ped-agent library build-index
uv run --project backend ped-agent agent rebuild-vector-index
uv run --project backend ped-agent serve
```

Optional extras:

```bash
pip install -e ".[rag]"
pip install -e ".[vision]"
```

For the local server with Ultralytics, ByteTrack, OpenCV-contrib, PedPy and Parquet support:

```powershell
uv sync --project backend --extra vision --group dev
uv run --project backend ped-agent serve
```

Open `http://127.0.0.1:8000/vision` through the Vue development server, or use the
`/api/vision/*` resources directly. Detector YAML files live under
`Video-Analysis/src/ped_video_analysis/configs/detectors/`, while local model weights belong in
`Video-Analysis/models/weights/`; no model training or bundled weights are provided. Runtime
tasks and artifacts are stored under `Video-Analysis/runtime/`. Annotated result videos are
intentionally never generated. See
[`Video-Analysis/README.md`](Video-Analysis/README.md) and
[`docs/vision-trajectory-workbench.md`](docs/vision-trajectory-workbench.md).

The repository-root `.env` file and process environment are the only authoritative persisted
configuration sources for `ped_agent_server` and repository scripts. All project variables use the
`PED_AGENT_*__*` namespace; unscoped legacy key aliases are no longer accepted. Configuration
changes require a restart, and embedding changes require
`ped-agent agent rebuild-vector-index`.

Dense retrieval defaults to local `BAAI/bge-m3` embeddings on CUDA with FP16. Model files are
downloaded lazily into Git-ignored `backend/storage/models/embeddings/`; Chroma data remains under
`memPed/knowledge/vectors/`. The runtime fails clearly when CUDA is unavailable instead of silently
using the CPU. An explicit CPU fallback requires both
`PED_AGENT_EMBEDDING__DEVICE=cpu` and `PED_AGENT_EMBEDDING__USE_FP16=false`. The
`openai_compatible` embedding protocol remains available for remote services.

The first-version answer runtime uses `deepseek-v4-flash`, with `deepseek-v4-pro` for semantic
verification. DeepSeek structured output is requested through LangChain `json_mode`. Every run
performs deterministic local-evidence preflight before any DeepSeek chat call and, only when
needed, at most one external-search pass. Once usable evidence exists, Flash rewrites the query
for refined local retrieval before drafting. Zero usable evidence produces a deterministic
`insufficient_evidence` answer without calling Flash or Pro, although vector retrieval may still
call the configured Embedding service.

LangSmith is optional, off by default, restricted to the `redacted` content policy, and
non-blocking after startup configuration succeeds: tracing or feedback delivery failures do not
change the local Run result. The local Run UUID is also the LangSmith root Trace UUID. When
enabled, traces may contain the current query, verified final answer, evidence identity,
candidate metadata, and metrics. They exclude conversation history, evidence quotes, abstracts,
drafts, raw model payloads, and secrets; traced URLs have credentials, query strings, and
fragments removed. See [`docs/agent-architecture.md`](docs/agent-architecture.md) for the full
API, SSE, privacy boundary, and answer chain.

## Knowledge Corpus and Ingestion

The repository manages knowledge, conversation memory, and reviewed method memory under the
data-only [`memPed/`](memPed/README.md) root. Literature and regulations keep separate files and
records, while sharing the local Catalog and retrieval indexes.

Documents entering the ingestion flow are assumed to have been selected before upload. Runtime
admission performs technical checks only: file integrity, PDF readability, SHA-256,
duplicate/version identity, minimum metadata, and parseability. Existing quality rules and
screening records remain tracked as upstream and compatibility assets. The former strict
`ResourceManifest` validation remains available only through the legacy/offline governance path;
the active low-level importer uses `ped_knowledge.ingestion.IngestionManifest`, while the CLI
requires an approved PRISMA selection freeze and bound Manifest Release for literature.

PDFs, SQLite databases, conversations, candidate methods, reports, and search indexes remain local
through `.gitignore`. Gold Questions gate retrieval/index configuration releases, not individual
document admission.

Initialize and complete a governed review, freeze the selection, release the Manifest, then run
technical preflight and formal import:

```powershell
uv run --project backend ped-agent research init <review_id>
uv run --project backend ped-agent research freeze-selection <review_id> --approved-by <name>
uv run --project backend ped-agent research release-manifest <review_id> `
  memPed/knowledge/literature/records/import_manifest.jsonl --approved-by <name>

uv run --project backend ped-agent library preflight `
  memPed/knowledge/literature/records/import_manifest.jsonl

uv run --project backend ped-agent library import-manifest `
  memPed/knowledge/literature/records/import_manifest.jsonl `
  --release memPed/knowledge/literature/reviews/<review_id>/08-manifest/manifest_release.json
```

`--technical-only` is reserved for controlled low-level import smoke tests and is not formal
literature admission. Regulation and standard Manifests currently remain outside the PRISMA
Release requirement and must be imported separately from literature.

`library validate-manifest` remains an optional offline audit command for the historical
JCI/CAS/citation and corpus-quota rules; it is not called by runtime import.

After an import batch, rebuild the indexes and run the Hybrid + optional Rerank Gold gate.
Use `--pipeline fts` only for the compatibility baseline:

```powershell
uv run --project backend ped-agent library build-index
uv run --project backend ped-agent agent rebuild-vector-index

uv run --project backend ped-agent evaluate `
  memPed/knowledge/pilot_gold.jsonl `
  memPed/knowledge/reports/pilot-evaluation.json `
  --config memPed/knowledge/pilot_config.json `
  --pipeline hybrid
```
