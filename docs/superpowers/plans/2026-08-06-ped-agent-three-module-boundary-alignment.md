# Ped-Agent Three-Module Boundary Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the approved three-module architecture visible, test-enforced, and consistent across the repository without moving packages, changing research data, or expanding unfinished product capabilities.

**Architecture:** Keep the current `ped_agent` and `ped_agent_server` package split intact. Use the approved design specification as the canonical boundary source, add lightweight documentation contract tests, mark historical and legacy paths explicitly, and update the Vue shell so the three foundation modules are visually separate from derived research applications.

**Tech Stack:** Python 3.12, Pytest, Markdown, Vue 3, TypeScript, Vitest, CSS, Git

---

## Scope and file map

This plan implements shared architecture and repository-boundary alignment only. The three functional subsystems remain independent follow-on projects.

### Files created

| File | Responsibility |
| --- | --- |
| `backend/tests/test_three_module_architecture.py` | Enforce canonical module names, spec links, document status banners, and the legacy map |
| `docs/legacy-scaffold.md` | Explain active, shared, legacy, and future code paths |

### Files modified

| File | Responsibility |
| --- | --- |
| `README.md` | Present the three-module architecture and source-of-truth links |
| `docs/rag-architecture.md` | Mark the broad RAG proposal as historical reference |
| `docs/data-analysis-module-design.md` | Mark the analysis document as a target-module design |
| `docs/experiment-evaluation-module-design.md` | Reclassify experiment evaluation as a derived application |
| `docs/vision-module-design.md` | Reclassify vision under detection and flow analysis |
| `src/ped_agent/main.py` | Identify the old scaffold CLI without changing behavior |
| `src/ped_agent/agent/graph.py` | Identify the generic routing graph as a legacy scaffold |
| `backend/tests/test_package_boundary.py` | Protect the active and legacy runtime boundary |
| `frontend/src/App.vue` | Separate foundation modules from research applications |
| `frontend/src/styles.css` | Style module and application navigation groups |
| `frontend/tests/App.spec.ts` | Verify the new information architecture |
| `CHANGELOG.md` | Record the architecture alignment |

### Explicitly out of scope

- No changes to `research/sources/`, `research/screening/`, `research/manifests/`, or local PDFs
- No screening, metric verification, Manifest generation, import, or index rebuild
- No directory moves or package renames
- No new `FlowEvidence` runtime type
- No real model, external-search, Embedding, or LangSmith smoke test
- No implementation of safety assessment, experiment support, or video-processing UI

## Task 1: Make the README declare the canonical architecture

**Files:**
- Create: `backend/tests/test_three_module_architecture.py`
- Modify: `README.md:1-17`
- Reference: `docs/superpowers/specs/2026-08-06-ped-agent-three-module-architecture-design.md`

- [ ] **Step 1: Write the failing README architecture tests**

Create `backend/tests/test_three_module_architecture.py`:

```python
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
SPEC = ROOT / "docs/superpowers/specs/2026-08-06-ped-agent-three-module-architecture-design.md"

MODULE_NAMES = (
    "知识与证据底座",
    "检测追踪与流动分析",
    "LLM 问答与会话",
)


def test_approved_three_module_spec_exists() -> None:
    assert SPEC.is_file()
    text = SPEC.read_text(encoding="utf-8")
    for module_name in MODULE_NAMES:
        assert module_name in text


def test_readme_declares_three_module_architecture() -> None:
    text = README.read_text(encoding="utf-8")
    for module_name in MODULE_NAMES:
        assert module_name in text
    assert "2026-08-06-ped-agent-three-module-architecture-design.md" in text
```

- [ ] **Step 2: Run the test and verify the README case fails**

Run from the repository root:

```powershell
uv run --project backend --no-sync pytest backend/tests/test_three_module_architecture.py -q -p no:cacheprovider
```

Expected: the spec test passes; the README test fails because the old feature list does not contain the three approved names.

- [ ] **Step 3: Replace the README introduction**

Keep the existing quick-start and operational sections. Replace the introductory feature list with:

```markdown
Ped-Agent is a local-first, evidence-bound research agent for pedestrian-flow research.
The project is organized around three foundation modules:

1. **知识与证据底座** — governed literature, regulations, formal evidence, Catalog,
   Vault, FTS5, Chroma, and retrieval evaluation
2. **检测追踪与流动分析** — video or trajectory processing, tracking, density,
   speed, flow, OD, and future Flow Evidence
3. **LLM 问答与会话** — conversations, deterministic evidence orchestration,
   structured generation, citation validation, semantic verification, and SSE

Research applications such as literature QA, trajectory analysis, scenario diagnosis,
safety assessment, and experiment support are combinations of these modules rather than
independent foundations.

See the approved
[three-module architecture design](docs/superpowers/specs/2026-08-06-ped-agent-three-module-architecture-design.md)
for responsibilities, maturity, storage boundaries, and delivery order.

The repository contains two Python distributions:

- `ped-agent-core` / `ped_agent`: shared contracts, policies, evidence graph, analysis,
  vision interfaces, and domain models
- `ped-agent-server` / `ped_agent_server`: FastAPI, SQLite, retrieval, model,
  external-search, observability, and CLI adapters
```

- [ ] **Step 4: Run the test and verify it passes**

Run:

```powershell
uv run --project backend --no-sync pytest backend/tests/test_three_module_architecture.py -q -p no:cacheprovider
```

Expected: `2 passed`.

- [ ] **Step 5: Commit**

```powershell
git add README.md backend/tests/test_three_module_architecture.py
git commit -m "docs: declare three-module project architecture"
```

## Task 2: Mark historical and target design documents

**Files:**
- Modify: `backend/tests/test_three_module_architecture.py`
- Modify: `docs/rag-architecture.md:1-3`
- Modify: `docs/data-analysis-module-design.md:1-3`
- Modify: `docs/experiment-evaluation-module-design.md:1-3`
- Modify: `docs/vision-module-design.md:1-3`

- [ ] **Step 1: Add failing status-banner tests**

Append:

```python
HISTORICAL_DOCUMENTS = {
    "docs/rag-architecture.md": "historical reference",
    "docs/data-analysis-module-design.md": "target module design",
    "docs/experiment-evaluation-module-design.md": "derived application design",
    "docs/vision-module-design.md": "target module design",
}


def test_broad_design_documents_declare_their_current_status() -> None:
    for relative_path, expected_status in HISTORICAL_DOCUMENTS.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        header = "\n".join(text.splitlines()[:8]).lower()
        assert expected_status in header, relative_path
        assert "2026-08-06-ped-agent-three-module-architecture-design.md" in header
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run:

```powershell
uv run --project backend --no-sync pytest backend/tests/test_three_module_architecture.py::test_broad_design_documents_declare_their_current_status -q -p no:cacheprovider
```

Expected: FAIL because the four documents lack the new status banners.

- [ ] **Step 3: Add the banners**

Insert immediately below each H1.

`docs/rag-architecture.md`:

```markdown
> **Status: historical reference.** This document preserves the broad RAG research proposal.
> Canonical module boundary:
> [Ped-Agent 三模块总体架构设计](superpowers/specs/2026-08-06-ped-agent-three-module-architecture-design.md).
```

`docs/data-analysis-module-design.md`:

```markdown
> **Status: target module design.** This document describes intended analysis depth;
> current code remains an engineering foundation under “检测追踪与流动分析”.
> Canonical module boundary:
> [Ped-Agent 三模块总体架构设计](superpowers/specs/2026-08-06-ped-agent-three-module-architecture-design.md).
```

`docs/experiment-evaluation-module-design.md`:

```markdown
> **Status: derived application design.** Experiment support combines
> “知识与证据底座” and “LLM 问答与会话”; it is not a fourth foundation module.
> Canonical module boundary:
> [Ped-Agent 三模块总体架构设计](superpowers/specs/2026-08-06-ped-agent-three-module-architecture-design.md).
```

`docs/vision-module-design.md`:

```markdown
> **Status: target module design.** Vision belongs to “检测追踪与流动分析”
> and is not a standalone product line.
> Canonical module boundary:
> [Ped-Agent 三模块总体架构设计](superpowers/specs/2026-08-06-ped-agent-three-module-architecture-design.md).
```

- [ ] **Step 4: Run the architecture tests**

Run:

```powershell
uv run --project backend --no-sync pytest backend/tests/test_three_module_architecture.py -q -p no:cacheprovider
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```powershell
git add backend/tests/test_three_module_architecture.py docs/rag-architecture.md docs/data-analysis-module-design.md docs/experiment-evaluation-module-design.md docs/vision-module-design.md
git commit -m "docs: classify historical and target module designs"
```

## Task 3: Mark the legacy scaffold runtime in code

**Files:**
- Modify: `backend/tests/test_package_boundary.py`
- Modify: `src/ped_agent/main.py:1`
- Modify: `src/ped_agent/agent/graph.py:1`

- [ ] **Step 1: Add failing module-docstring tests**

Replace `backend/tests/test_package_boundary.py` with:

```python
from __future__ import annotations

import ast
from pathlib import Path

import ped_agent
import ped_agent_server
import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_core_and_server_are_distinct_python_packages() -> None:
    core_path = Path(ped_agent.__file__).resolve()
    server_path = Path(ped_agent_server.__file__).resolve()

    assert core_path != server_path
    assert core_path.parts[-2] == "ped_agent"
    assert server_path.parts[-2] == "ped_agent_server"


@pytest.mark.parametrize(
    "relative_path",
    ["src/ped_agent/main.py", "src/ped_agent/agent/graph.py"],
)
def test_legacy_modules_name_the_authoritative_runtime(relative_path: str) -> None:
    source = (ROOT / relative_path).read_text(encoding="utf-8")
    docstring = ast.get_docstring(ast.parse(source)) or ""

    assert "Legacy" in docstring
    assert "ped_agent_server" in docstring
    assert "EvidenceGraph" in docstring
```

- [ ] **Step 2: Run the tests and verify the new cases fail**

Run:

```powershell
uv run --project backend --no-sync pytest backend/tests/test_package_boundary.py -q -p no:cacheprovider
```

Expected: the package-distinction test passes and both legacy-docstring cases fail.

- [ ] **Step 3: Add a non-behavioral marker to the old CLI**

Insert before `from __future__ import annotations` in `src/ped_agent/main.py`:

```python
"""Legacy Phase 1 scaffold CLI.

The authoritative application CLI and server runtime live in ped_agent_server.
Verified answers are executed by EvidenceGraph through the server Run lifecycle.
This module remains only for scaffold compatibility and unit tests.
"""
```

- [ ] **Step 4: Add a non-behavioral marker to the generic graph**

Insert before `from __future__ import annotations` in `src/ped_agent/agent/graph.py`:

```python
"""Legacy generic routing scaffold.

The authoritative application runtime lives in ped_agent_server and uses EvidenceGraph.
This graph remains as an early routing prototype for compatibility tests and reference.
"""
```

Do not emit warnings or change runtime behavior.

- [ ] **Step 5: Run boundary and routing tests**

Run:

```powershell
uv run --project backend --no-sync pytest backend/tests/test_package_boundary.py -q -p no:cacheprovider
uv run --no-sync pytest tests/unit/test_agent_routing.py -q -p no:cacheprovider
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```powershell
git add backend/tests/test_package_boundary.py src/ped_agent/main.py src/ped_agent/agent/graph.py
git commit -m "docs: mark legacy scaffold runtime boundaries"
```

## Task 4: Add an active-versus-legacy code map

**Files:**
- Modify: `backend/tests/test_three_module_architecture.py`
- Create: `docs/legacy-scaffold.md`
- Modify: `README.md`

- [ ] **Step 1: Add a failing legacy-map test**

Append:

```python
LEGACY_MAP = ROOT / "docs/legacy-scaffold.md"


def test_readme_links_an_explicit_legacy_code_map() -> None:
    assert LEGACY_MAP.is_file()
    legacy_text = LEGACY_MAP.read_text(encoding="utf-8")
    readme_text = README.read_text(encoding="utf-8")

    assert "ped_agent_server.cli" in legacy_text
    assert "EvidenceGraph" in legacy_text
    assert "src/ped_agent/main.py" in legacy_text
    assert "src/ped_agent/agent/graph.py" in legacy_text
    assert "docs/legacy-scaffold.md" in readme_text
```

- [ ] **Step 2: Run the test and verify it fails**

Run:

```powershell
uv run --project backend --no-sync pytest backend/tests/test_three_module_architecture.py::test_readme_links_an_explicit_legacy_code_map -q -p no:cacheprovider
```

Expected: FAIL because `docs/legacy-scaffold.md` does not exist.

- [ ] **Step 3: Create the legacy map**

Create `docs/legacy-scaffold.md`:

```markdown
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
| Knowledge runtime | `backend/src/ped_agent_server/` and `backend/storage/library/` |
| Answer workspace | `frontend/src/views/AnswerView.vue` |

## ⚠️ Legacy scaffold

| Path | Boundary |
| --- | --- |
| `src/ped_agent/main.py` | Early OmegaConf CLI; not the server entrypoint |
| `src/ped_agent/agent/graph.py` | Generic routing prototype |
| `src/ped_agent/agent/nodes.py` | Early application nodes with scaffold responses |
| `src/ped_agent/agent/tools.py` | Unconnected tool stubs |
| `src/ped_agent/knowledge/` | Early RAG and source-adapter scaffold |
| `config/*.yaml` | Legacy configuration; not server runtime input |
| `scripts/evaluate_agent.py` | Old routing-graph smoke path |

## 🔗 Shared code that remains active

- `src/ped_agent/agent/contracts.py`
- `src/ped_agent/agent/policy.py`
- `src/ped_agent/models/`
- `src/ped_agent/analysis/`
- `src/ped_agent/vision/`

The shared paths are active foundations or contracts even when their product integration is incomplete.
```

- [ ] **Step 4: Link it from the README**

Add after the architecture-spec link:

```markdown
Contributors should also read the
[active and legacy code map](docs/legacy-scaffold.md) before changing entrypoints,
configuration, retrieval, or Agent routing.
```

- [ ] **Step 5: Run the architecture tests**

Run:

```powershell
uv run --project backend --no-sync pytest backend/tests/test_three_module_architecture.py -q -p no:cacheprovider
```

Expected: `4 passed`.

- [ ] **Step 6: Commit**

```powershell
git add README.md docs/legacy-scaffold.md backend/tests/test_three_module_architecture.py
git commit -m "docs: map active and legacy project paths"
```

## Task 5: Align Vue navigation with modules and applications

**Files:**
- Modify: `frontend/tests/App.spec.ts`
- Modify: `frontend/src/App.vue:1-43`
- Modify: `frontend/src/styles.css:125-164`

- [ ] **Step 1: Write failing navigation expectations**

Replace the first test in `frontend/tests/App.spec.ts`:

```typescript
it('separates foundation modules from derived research applications', async () => {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div>Library</div>' } },
      { path: '/qa', component: { template: '<div>Answer</div>' } },
    ],
  })
  await router.push('/')
  await router.isReady()
  const wrapper = mount(App, {
    global: { plugins: [router] },
  })

  const modules = wrapper.get('[aria-label="基础模块"]')
  const applications = wrapper.get('[aria-label="研究应用"]')

  expect(modules.findAll('[data-module]')).toHaveLength(3)
  expect(modules.text()).toContain('知识与证据底座')
  expect(modules.text()).toContain('检测追踪与流动分析')
  expect(modules.text()).toContain('LLM 问答与会话')
  expect(applications.text()).toContain('场景诊断')
  expect(applications.text()).toContain('安全评估')
  expect(applications.text()).toContain('实验支持')
  expect(wrapper.find('[data-route="knowledge"]').classes()).toContain('active')
  expect(wrapper.find('[data-route="answer"]').attributes('href')).toBe('/qa')
})
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run from `frontend/`:

```powershell
npm.cmd test -- tests/App.spec.ts
```

Expected: FAIL because the shell has one five-item list and no navigation groups.

- [ ] **Step 3: Define the navigation data**

Replace `const navigation` in `frontend/src/App.vue`:

```typescript
const moduleNavigation = [
  {
    index: '01',
    key: 'knowledge',
    name: '知识与证据底座',
    description: '文献、法规、正式证据与检索',
    route: '/',
    routeName: 'knowledge',
    stage: '建设中',
  },
  {
    index: '02',
    key: 'analysis',
    name: '检测追踪与流动分析',
    description: '视频、轨迹、指标与 Flow Evidence',
    stage: '工程骨架',
  },
  {
    index: '03',
    key: 'answer',
    name: 'LLM 问答与会话',
    description: '证据编排、验证回答与会话',
    route: '/qa',
    routeName: 'answer',
    stage: '可用',
  },
]

const researchApplications = [
  { name: '场景诊断', description: '组合正式证据与 Flow Evidence' },
  { name: '安全评估', description: '风险指标与规范符合性' },
  { name: '实验支持', description: '方案、数据与指标设计' },
]
```

- [ ] **Step 4: Replace the navigation template**

Replace the existing `<nav>` block:

```vue
<nav class="primary-nav" aria-label="Ped-Agent 功能导航">
  <section class="nav-group" aria-label="基础模块">
    <p class="nav-group-title">基础模块</p>
    <RouterLink
      v-for="item in moduleNavigation"
      :key="item.key"
      :to="item.route || '#'"
      :data-module="item.key"
      :data-route="item.routeName"
      :class="['nav-item', { disabled: !item.route }]"
      active-class="active"
      :aria-disabled="!item.route"
      :tabindex="item.route ? 0 : -1"
      @click="!item.route && $event.preventDefault()"
    >
      <span class="nav-index">{{ item.index }}</span>
      <span class="nav-copy">
        <strong>{{ item.name }}</strong>
        <small>{{ item.description }}</small>
      </span>
      <span class="nav-stage">{{ item.stage }}</span>
    </RouterLink>
  </section>

  <section class="nav-group application-group" aria-label="研究应用">
    <p class="nav-group-title">研究应用</p>
    <div
      v-for="item in researchApplications"
      :key="item.name"
      class="nav-item application-item disabled"
      data-application
      aria-disabled="true"
    >
      <span class="nav-index">—</span>
      <span class="nav-copy">
        <strong>{{ item.name }}</strong>
        <small>{{ item.description }}</small>
      </span>
      <span class="nav-stage">后续</span>
    </div>
  </section>
</nav>
```

- [ ] **Step 5: Add grouping styles**

Add after `.primary-nav`:

```css
.nav-group {
  display: grid;
  gap: 6px;
}

.nav-group + .nav-group {
  margin-top: 22px;
}

.nav-group-title {
  margin: 0 10px 4px;
  color: rgb(247 244 237 / 46%);
  font-family: "Cascadia Mono", Consolas, monospace;
  font-size: 0.66rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.application-item {
  min-height: 58px;
}
```

- [ ] **Step 6: Run the frontend test and build**

Run from `frontend/`:

```powershell
npm.cmd test -- tests/App.spec.ts
npm.cmd run build
```

Expected: `2 passed` and the Vite production build exits with code 0.

- [ ] **Step 7: Commit**

```powershell
git add frontend/src/App.vue frontend/src/styles.css frontend/tests/App.spec.ts
git commit -m "feat: align navigation with three-module architecture"
```

## Task 6: Record the alignment and run the full regression gate

**Files:**
- Modify: `backend/tests/test_three_module_architecture.py`
- Modify: `CHANGELOG.md:1-8`
- Verify: all test suites

- [ ] **Step 1: Add a failing changelog test**

Append:

```python
def test_changelog_records_three_module_alignment() -> None:
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## Unreleased" in text
    for module_name in MODULE_NAMES:
        assert module_name in text
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run:

```powershell
uv run --project backend --no-sync pytest backend/tests/test_three_module_architecture.py::test_changelog_records_three_module_alignment -q -p no:cacheprovider
```

Expected: FAIL because the changelog lacks an Unreleased section.

- [ ] **Step 3: Add the changelog entry**

Insert above `## 0.1.0`:

```markdown
## Unreleased

- Adopted the three-module project boundary:
  知识与证据底座、检测追踪与流动分析、LLM 问答与会话
- Classified literature QA, trajectory analysis, scenario diagnosis, safety assessment,
  and experiment support as applications built from the foundation modules
- Documented the authoritative runtime and retained legacy scaffold paths
```

- [ ] **Step 4: Commit the changelog**

```powershell
git add CHANGELOG.md backend/tests/test_three_module_architecture.py
git commit -m "docs: record three-module architecture alignment"
```

- [ ] **Step 5: Confirm unrelated work remains untouched**

Run:

```powershell
git status --short
```

Expected remaining unrelated paths:

```text
 M research/sources/literature/candidates.csv
 M research/sources/literature/search_log.csv
?? docs/assets/
```

Do not stage or modify those paths.

- [ ] **Step 6: Run core tests**

Run from the repository root:

```powershell
uv run --no-sync pytest tests -q -p no:cacheprovider
```

Expected: all core tests pass.

- [ ] **Step 7: Run backend tests**

Run from `backend/`:

```powershell
uv run --no-sync pytest -q -p no:cacheprovider --basetemp '..\.pytest-three-module-alignment'
```

Expected: all backend tests, including the architecture contracts, pass.

- [ ] **Step 8: Run frontend tests and build**

Run from `frontend/`:

```powershell
npm.cmd test
npm.cmd run build
```

Expected: all frontend tests pass and the production build succeeds.

- [ ] **Step 9: Check formatting and final scope**

Run:

```powershell
git diff --check
git status --short --branch
```

Expected:

- No whitespace errors
- The alignment commits are present
- The pre-existing candidate CSV and `docs/assets/` changes remain uncommitted

## Follow-on subprojects

Do not append these independent workstreams to this alignment plan. Each requires its own approved specification and implementation plan.

### Knowledge and evidence foundation

Preserve this governed order:

1. Candidate discovery
2. Screening
3. Quality and metric evaluation
4. Legal full-text confirmation
5. Manifest construction
6. Import
7. Index rebuild
8. Gold evaluation

No stage starts automatically because the preceding stage completed.

### Detection tracking and flow analysis

Create a separate vertical-slice specification covering:

1. One public trajectory dataset
2. Canonical trajectory normalization
3. Density, speed, flow, and OD validation
4. A versioned `FlowEvidence` contract
5. Reproducible reports and visualizations
6. Video extraction only after the trajectory path passes acceptance

### LLM question answering and conversation

Create a separate integration specification covering:

1. Formal local corpus acceptance
2. Real-provider smoke tests
3. Flow Evidence retrieval and citation
4. Conversation and domain-memory boundary enforcement
5. Scenario diagnosis as the first combined application

## Completion criteria

The boundary-alignment implementation is complete when:

- README, historical documents, legacy paths, frontend navigation, and changelog use the same three module names
- The approved architecture specification remains the canonical source
- Automated tests fail if required architecture labels or status banners disappear
- The active `ped_agent_server + EvidenceGraph` runtime is clearly distinguished from the legacy scaffold
- The frontend shows three foundation modules separately from derived applications
- Core, backend, and frontend regression gates pass
- Existing candidate records, search logs, and untracked framework images remain untouched
