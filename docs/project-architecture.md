# Ped-Agent current project architecture

_Current architecture and maturity map · authoritative overview for the modular research project_

---

## 📋 Project position

Ped-Agent is a modular research engineering repository for pedestrian-flow studies. Its current
goal is to make knowledge retrieval, video/trajectory analysis, and evidence-based research QA
independently testable and reproducible. It is not currently organized as a Web product or a
long-running service.

## 🧩 Module map

```mermaid
flowchart LR
    accTitle: Current module map
    accDescr: Contracts defines shared data structures. Knowledge Base, Video Analysis, and Agent depend on those contracts and can be combined through experiments.

    contracts["Contracts\nshared data"]
    knowledge["Knowledge-Base\nknowledge and evidence"]
    video["Video-Analysis\ndetection and flow analysis"]
    agent["Agent\nevidence orchestration and QA"]
    experiments["experiments\nreproducible studies"]
    data[("memPed\nresearch data")]

    knowledge --> contracts
    video --> contracts
    agent --> contracts
    knowledge --> data
    video --> data
    knowledge -. "evidence" .-> agent
    experiments --> knowledge
    experiments --> video
    experiments --> agent

    classDef shared fill:#f3f4f6,stroke:#6b7280,stroke-width:2px,color:#1f2937
    classDef module fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f
    classDef data fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d
    classDef experiment fill:#ffedd5,stroke:#ea580c,stroke-width:2px,color:#7c2d12

    class contracts shared
    class knowledge,video,agent module
    class data data
    class experiments experiment
```

## 🧭 Engineering principles

- Facts belong to `Knowledge-Base`; calculations belong to `Video-Analysis`; orchestration and
  explanation belong to `Agent`.
- Modules communicate through `Contracts`, not through each other's internal storage or code.
- Research data, configuration, model versions, input hashes, random seeds, and provenance stay
  visible in experiments.
- Product concerns such as FastAPI, Vue, SSE, task queues, sessions, and long-running services are
  outside the current scope.

## 📚 Module responsibilities

| Area | Authoritative code/docs | Main responsibility | Does not own |
| --- | --- | --- | --- |
| Shared contracts | `Contracts/`, `Contracts/README.md` | Evidence, answer, and trajectory data shapes | Algorithms, storage, HTTP |
| Knowledge and evidence | `Knowledge-Base/`, `Knowledge-Base/README.md` | Technical preflight, parsing, chunking, indexing, retrieval, rerank, evaluation | Final answer generation, video inference |
| Detection and flow analysis | `Video-Analysis/`, `Video-Analysis/README.md` | Detection, tracking, calibration, trajectories, density/speed/flow/OD analysis | Document admission, natural-language QA |
| Evidence orchestration and QA | `Agent/`, `Agent/README.md` | Evidence graph, citation rules, model adapters, research answers | FastAPI, SSE, sessions, task queues |
| Reproducible studies | `experiments/`, `experiments/README.md` | Inputs, hypotheses, versions, seeds, commands, metrics, outputs | Core reusable module implementation |

## 💾 Data boundaries

[`memPed/README.md`](../memPed/README.md) is the data-root guide. In short:

- `memPed/knowledge/` stores governed literature/regulation assets, catalogs, derived documents,
  indexes, and reports
- `memPed/conversations/` stores conversation artifacts when a research workflow needs them
- `memPed/methods/` stores method candidates and approved methods
- `outputs/` stores local experiment outputs; it is not the source of truth for code or methods
- `paper/` stores manuscript sources and build artifacts

## 📊 Current maturity language

Use these labels consistently:

| Label | Meaning |
| --- | --- |
| `current` | Implemented repository behavior or active engineering rule |
| `target` | Intended research depth; implementation may be partial |
| `historical` | Retained for design traceability; not an instruction for current code |
| `plan` | Step-by-step proposal or implementation record |

The module READMEs describe the current boundaries. The larger design documents describe desired
depth and should be checked against code and tests before being treated as implemented capability.

## 🧭 Extension rule

New cross-module behavior starts as an experiment. Only move it into a public module API after its
data contract, reproducibility requirements, and tests are stable. If a future change needs a
Web/API integration layer, record that as a new architecture decision instead of reviving the
archived product-integration tree implicitly.
