# Ped-Agent

Ped-Agent is an agentic toolkit for pedestrian-flow literature QA, experiment-plan
evaluation, structured scenario analysis, and optional video-to-trajectory extraction.

This repository contains the Phase 1 foundation:

- Python package layout under `src/ped_agent`
- YAML configuration system with environment-variable interpolation
- Lightweight LLM factory and LangGraph-compatible routing graph
- Pydantic data models for literature, scenario, and trajectory data
- Module boundaries for RAG, analysis, experiment evaluation, vision plugins, and evals
- Pytest smoke tests for the scaffold
- LangSmith runtime configuration wiring for local or traced runs

## Quick Start

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev]"
pytest
ped-agent "How should I evaluate a pedestrian evacuation experiment?"
```

Optional extras:

```bash
pip install -e ".[rag]"
pip install -e ".[vision]"
```

Copy `config/.env.example` to `.env` and fill API keys when enabling real model,
LangSmith, RAG, or vision backends. Set `langsmith.enabled=true` in configuration
when you want CLI runs to publish traces.

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
