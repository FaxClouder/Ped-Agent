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

The repository exposes two Python package boundaries and one server distribution:

- `ped-agent-core` / `ped_agent`: shared contracts, policies, evidence graph, compatibility
  imports, and domain models
- `Video-Analysis/` / `ped_video_analysis`: detector manifests, model-weight location,
  detection/tracking, calibration, trajectory processing, flow analysis, and public APIs
- `ped-agent-server` / `ped_agent_server`: FastAPI, SQLite, retrieval, model,
  external-search, observability, and CLI adapters

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

## Quality-Governed Knowledge Corpus

The repository now manages knowledge, conversation memory, and reviewed method memory under
the data-only [`memPed/`](memPed/README.md) root. Literature and regulations keep separate
files and governance records, while sharing the local Catalog and retrieval indexes.

Tracked quality rules, screening records, manifests, Gold Questions, and approved methods
remain reproducible in Git. PDFs, SQLite databases, conversations, candidate methods, reports,
and search indexes remain local through `.gitignore`.

Validate a complete literature or regulation manifest before importing it:

```powershell
uv run --project backend ped-agent library validate-manifest `
  memPed/knowledge/literature/records/pilot_manifest.jsonl `
  --phase pilot
```

The validation enforces formal publication status, verified JCI/CAS metrics,
age-adjusted citation impact, quality tiers, exception limits, and topic quotas.

After importing five literature items or two regulations per batch, rebuild the index
and run the Gold Question acceptance gate:

```powershell
uv run --project backend ped-agent evaluate `
  memPed/knowledge/pilot_gold.jsonl `
  memPed/knowledge/reports/pilot-evaluation.json `
  --config memPed/knowledge/pilot_config.json
```
