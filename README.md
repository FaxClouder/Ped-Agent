# Ped-Agent

Ped-Agent is a local-first, evidence-bound research agent for pedestrian-flow literature,
regulations, experiments, scenario analysis, and optional video-to-trajectory extraction.

The repository now contains two Python distributions:

- `ped-agent-core` / `ped_agent`: graph, schemas, policies and protocols
- `ped-agent-server` / `ped_agent_server`: FastAPI, SQLite, retrieval, model and search adapters
- Vue 3 knowledge-library and verified evidence-QA workspaces
- Deterministic LangGraph with FTS5 + Chroma retrieval, conditional external search,
  citation rules, semantic verification and one revision
- Pydantic data models for literature, scenario, and trajectory data
- Module boundaries for RAG, analysis, experiment evaluation, vision plugins, and evals
- Pytest smoke tests for the scaffold
- LangSmith runtime configuration wiring for local or traced runs

## Quick Start

```powershell
Copy-Item .env.example .env
uv sync --project backend
uv run --project backend ped-agent agent doctor
uv run --project backend ped-agent serve
```

Optional extras:

```bash
pip install -e ".[rag]"
pip install -e ".[vision]"
```

The Agent runtime reads only `.env` / process environment. Configuration changes require a
restart, and embedding changes require `ped-agent agent rebuild-vector-index`. LangSmith is
off unless `PED_AGENT_LANGSMITH__ENABLED=true`. See
[`docs/agent-architecture.md`](docs/agent-architecture.md) for the full API, SSE and answer chain.

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
