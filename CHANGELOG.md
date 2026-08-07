# Changelog

All notable changes to Ped-Agent will be documented in this file.

The project follows semantic versioning while it matures:

- Patch: bug fixes and internal maintenance
- Minor: backward-compatible feature additions
- Major: breaking API or workflow changes

## Unreleased

- Added the independent `Knowledge-Base/` / `ped_knowledge` package with technical
  preflight, structured Canonical Documents, deterministic parent-child Chunking,
  active-version Catalog semantics, rebuildable FTS/Chroma indexes, RRF, optional
  Cross-Encoder Rerank, and end-to-end Gold release gates
- Migrated the active API, CLI, and EvidenceGraph retrieval assembly to `ped_knowledge`;
  former server knowledge modules remain compatibility exports and the historical
  academic-quality validation remains an offline audit path
- Extracted detection, tracking, calibration, trajectory processing, and flow-analysis code
  into `Video-Analysis/`, with module-owned detector YAML, weight/runtime directories, a
  `ped_video_analysis` public API, and compatibility aliases for the former imports
- Added the data-only `memPed/` root for governed knowledge, session-partitioned
  conversations, and human-reviewed method memory
- Migrated knowledge governance assets and local knowledge runtime paths from
  `research/` and `backend/storage/library/` into `memPed/knowledge/`
- Migrated the default conversation and vector-index paths into `memPed/`
- Adopted the three-module project boundary:
  知识与证据底座、检测追踪与流动分析、LLM 问答与会话
- Classified literature QA, trajectory analysis, scenario diagnosis, safety assessment,
  and experiment support as applications built from the foundation modules
- Documented the authoritative runtime and retained legacy scaffold paths
- Consolidated runtime and repository-script configuration on the root `.env`, removed the
  legacy YAML configuration directory, and retired unscoped API-key aliases

## 0.1.0 - 2026-06-30

- Added Phase 1 project scaffold.
- Added configuration, model, Agent routing, RAG, analysis, experiment, vision, and eval module boundaries.
- Added initial tests and CI workflow.
- Wired LangSmith runtime environment configuration into the CLI entrypoint.
- Added the documented environment template and strengthened Phase 1 unit coverage.
