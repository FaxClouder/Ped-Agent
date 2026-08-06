# Ped-Agent

Ped-Agent is a local-first, evidence-bound research agent for pedestrian-flow research.

The project has three foundation modules:

1. **知识与证据底座** — governed literature, regulations, and formal evidence, with
   Catalog, Vault, FTS5, Chroma, and retrieval evaluation.
2. **检测追踪与流动分析** — video or trajectory processing, tracking, density, speed,
   flow, OD, and future Flow Evidence.
3. **LLM 问答与会话** — conversations, deterministic evidence orchestration, structured
   generation, citation validation, semantic verification, and SSE.

Literature QA, trajectory analysis, scenario diagnosis, safety assessment, and experiment
support are applications that combine these modules, not independent foundations. See the
[approved three-module architecture specification](docs/superpowers/specs/2026-08-06-ped-agent-three-module-architecture-design.md)
for the canonical boundaries.

Contributors should also read the
[active and legacy code map](docs/legacy-scaffold.md) before changing entrypoints,
configuration, retrieval, or Agent routing.

The repository preserves two Python distributions:

- `ped-agent-core` / `ped_agent`: shared contracts, policies, evidence graph, analysis,
  vision interfaces, and domain models
- `ped-agent-server` / `ped_agent_server`: FastAPI, SQLite, retrieval, model,
  external-search, observability, and CLI adapters

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

The running `ped_agent_server` treats the repository-root `.env` file and process environment
as its only authoritative configuration sources. Configuration changes require a restart, and
embedding changes require `ped-agent agent rebuild-vector-index`; the legacy YAML files under
`config/` are not server runtime inputs.

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

The tracked governance records live under `research/`. They define the controlled
pedestrian-flow and evacuation taxonomy, pilot/core quotas, JCI and CAS partition
requirements, citation thresholds, screening records, and import-ready manifests.

PDFs, parsed text, SQLite catalogs, and search indexes remain local under
`backend/storage/library/` and must not be committed to GitHub. See
`research/README.md` for the exact tracked/local boundary.

Validate a complete literature or regulation manifest before importing it:

```powershell
uv run --project backend ped-agent library validate-manifest `
  research/manifests/literature/pilot.jsonl `
  --phase pilot
```

The validation enforces formal publication status, verified JCI/CAS metrics,
age-adjusted citation impact, quality tiers, exception limits, and topic quotas.

After importing five literature items or two regulations per batch, rebuild the index
and run the Gold Question acceptance gate:

```powershell
uv run --project backend ped-agent evaluate `
  research/experiments/pilot_gold.jsonl `
  backend/storage/library/reports/pilot-evaluation.json `
  --config research/experiments/pilot_config.json
```
