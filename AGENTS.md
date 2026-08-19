# Ped-Agent contribution guide

_Repository-wide rules for agents and contributors · current research-engineering boundary_

---

## 📍 Start here

Read documents in this order before changing the repository:

1. [`README.md`](README.md) for the project purpose and validation command
2. [`AGENTS.md`](AGENTS.md) for contribution boundaries and safety rules
3. [`docs/project-architecture.md`](docs/project-architecture.md) for the current module map
4. The README of the module being changed
5. [`docs/README.md`](docs/README.md) to locate the small set of maintained documents

The repository is a **research engineering project**, not a Web product or a long-running service.

## 🧭 Current boundaries

The three research capabilities are:

- **Knowledge and evidence** — `Knowledge-Base/` and `memPed/knowledge/`
- **Detection, tracking, and flow analysis** — `Video-Analysis/`
- **Evidence orchestration and research QA** — `Agent/`

`Contracts/` is shared infrastructure for stable data contracts. It is not a fourth product
capability. Cross-module experiments belong in `experiments/`; paper assets belong in `paper/`;
local results belong in `outputs/`.

Do not reintroduce FastAPI, Vue, SSE, task queues, session databases, or product-level
observability unless a new architecture decision explicitly changes this boundary.

## 🔗 Source-of-truth rules

- Current behavior is determined by code plus the relevant module README and
  [`docs/project-architecture.md`](docs/project-architecture.md).
- [`docs/project-architecture.md`](docs/project-architecture.md) defines the current dependency
  direction and research constraints.
- `docs/data-analysis-module-design.md` and `docs/vision-module-design.md` describe target depth;
  they are not proof that every planned capability is implemented.
- If code and a design document disagree, describe the discrepancy and update the current
  document before copying the old design into new code.

## 🧪 Change and validation rules

- Keep each change focused on one module or one stable contract.
- Preserve input hashes, model and algorithm versions, configuration, random seeds, and result
  provenance for experiments.
- For numerical algorithms, add or retain a fixed example or reference output.
- Set `PYTHONPATH` to all four `src` directories when running the repository test suite:

  ```powershell
  $env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
  .\.venv\Scripts\python -m pytest Contracts/tests Agent/tests Knowledge-Base/tests Video-Analysis/tests -q
  ```

- Run a narrower module test first, then the full suite when the change crosses a contract.
- Do not claim real OCR, embedding, reranker, GPU, or video-model validation unless the required
  assets and models were actually available and executed.

## 🔒 Data and security rules

- `memPed/` contains research data, indexes, records, and reports; do not put business code there.
- `outputs/` contains local experiment results and must remain reproducible and separately named.
- Do not commit API keys, cookies, restricted source files, databases, vector indexes, model
  weights, or large generated artifacts.
- Model configuration belongs in Git; model weights stay local and their SHA-256 belongs in the
  corresponding manifest/configuration.
- Do not overwrite an existing research output without explicit authorization.

## ✍️ Documentation rules

- Every new document has one H1 title, a short italic context line, and a clear status:
  `current`, `target`, `historical`, or `plan`.
- Update [`docs/README.md`](docs/README.md) when adding or removing a maintained document.
- Prefer tables for document inventories and Mermaid for architecture or process relationships.
- Keep current guidance separate from design proposals and plans; do not silently present a plan
  as implemented behavior.
- Use repository-relative links and verify that links resolve before finishing.
