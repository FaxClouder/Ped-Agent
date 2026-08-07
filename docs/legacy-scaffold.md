# Ped-Agent Active and Legacy Code Map

_Current runtime boundary for contributors · 2026-08-06_

---

## 📋 Active runtime

| Responsibility | Authoritative path |
| --- | --- |
| CLI and server startup | `ped_agent_server.cli` |
| HTTP and SSE | `ped_agent_server.api` |
| Verified answer graph | `ped_agent.agent.evidence_graph.EvidenceGraph` |
| Runtime configuration | repository `.env` and `PED_AGENT_*__*` variables |
| Server and cross-module adapters | `backend/src/ped_agent_server/` — spans API/SSE, Run lifecycle, retrieval, model, external search, and observability adapters |
| memPed data root | `memPed/` — governed knowledge, conversation, and reviewed-method data assets |
| Video analysis module | `Video-Analysis/` and `ped_video_analysis` — detector configuration, weights, vision algorithms, flow analysis, and public Python APIs |
| Answer workspace | `frontend/src/views/AnswerView.vue` |

## ⚠️ Legacy scaffold

| Path | Boundary |
| --- | --- |
| `src/ped_agent/main.py` | Early compatibility CLI; reads the root `.env`, but is not the server entrypoint |
| `src/ped_agent/agent/graph.py` | Generic routing prototype |
| `src/ped_agent/agent/nodes.py` | Early application nodes with scaffold responses |
| `src/ped_agent/agent/tools.py` | Unconnected tool stubs |
| `src/ped_agent/knowledge/` | Early RAG and source-adapter scaffold |
| `src/ped_agent/analysis/` | Compatibility import aliases for `ped_video_analysis.analysis` |
| `src/ped_agent/vision/` | Compatibility import aliases for `ped_video_analysis.vision` |
| `scripts/evaluate_agent.py` | Old routing-graph smoke path |

## 🔗 Shared code that remains active

- `src/ped_agent/agent/contracts.py`
- `src/ped_agent/agent/policy.py`
- `src/ped_agent/models/`
- `Video-Analysis/src/ped_video_analysis/analysis/`
- `Video-Analysis/src/ped_video_analysis/vision/`

The shared paths are active foundations or contracts even when their product integration is incomplete.
