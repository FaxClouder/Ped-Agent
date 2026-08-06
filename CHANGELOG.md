# Changelog

All notable changes to Ped-Agent will be documented in this file.

The project follows semantic versioning while it matures:

- Patch: bug fixes and internal maintenance
- Minor: backward-compatible feature additions
- Major: breaking API or workflow changes

## Unreleased

- Adopted the three-module project boundary:
  知识与证据底座、检测追踪与流动分析、LLM 问答与会话
- Classified literature QA, trajectory analysis, scenario diagnosis, safety assessment,
  and experiment support as applications built from the foundation modules
- Documented the authoritative runtime and retained legacy scaffold paths

## 0.1.0 - 2026-06-30

- Added Phase 1 project scaffold.
- Added configuration, model, Agent routing, RAG, analysis, experiment, vision, and eval module boundaries.
- Added initial tests and CI workflow.
- Wired LangSmith runtime environment configuration into the CLI entrypoint.
- Added the documented environment template and strengthened Phase 1 unit coverage.
