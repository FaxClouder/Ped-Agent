# Cloud development preparation

*Lightweight source publication boundary and setup notes · status: current · 2026-10-08*

The `codex/cloud-dev-prep-20261008` branch targets `FaxClouder/Ped-Agent` (GitHub repository ID
`1284945987`). It preserves the eleven local commits after remote main
`f3b4621ef5c46e27d9db351dd1c930500464261d` and adds reviewed source snapshots without changing
research results or rewriting history. Publication was prepared in a separate temporary repository
because the original checkout had moved to `feat/frontend`.

## Included source and local boundaries

The snapshot includes Knowledge-Base source, retrieval configuration, tests and literature metadata;
Agent-Harness execution source and tests; root dependency configuration and `uv.lock`; evaluation
standards/registry and maintained architecture, module and research documentation. Agent source and
baseline tests are preserved from the existing local commits.

Real Gold, complete evaluation inputs, incoming PDFs, model weights, indexes, databases, experiment
outputs and full response packages remain local. Experimental scripts and their run-specific inputs,
local setup scripts, report build dependencies, and frontend work are outside this publication.
Existing research documents retain their original status and provenance; their local data and result
links are not a promise that those assets are available in the cloud checkout. Five reference PDFs
already present in local history are preserved as ordinary Git files; this branch does not add new PDFs.

The [evaluation standard](../experiments/EVALUATION-STANDARD.md) governs access to real question sets.
Synthetic module tests do not authorize running the sealed evaluation set.

## Lightweight Linux setup

The root lock describes the existing Windows Python 3.12/CUDA environment and pins Windows PyTorch
wheel URLs. Preserve it for that environment; use module installation for Linux source development:

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ./Contracts -e ./Agent -e ./Agent-Harness -e ./Knowledge-Base pytest pytest-asyncio
export PYTHONPATH="Contracts/src:Agent/src:Agent-Harness/src:Knowledge-Base/src"
python -m pytest Contracts/tests Agent/tests Agent-Harness/tests Knowledge-Base/tests -q
```

This setup covers source/module tests. Video tests need their declared dependencies; real dense
retrieval, reranking, OCR and video inference require separately provisioned assets and validation.
Do not download large models merely to prepare a lightweight development environment.

## Use the branch

Select `codex/cloud-dev-prep-20261008` in the existing Ped-Agent cloud environment when starting a
later authorized task. Do not replace its repository with the separately named F-Agent-Paper
repository. No saved environment settings, remote main, or pull requests are changed by this preparation.

## Preparation validation

The isolated snapshot passed 221 tests across Contracts, Agent, Agent-Harness, Knowledge-Base and
Video-Analysis using the existing local Python environment. The manifest preflight test required
an explicit 2026-07-29 reference date for its fixed 2026-07-01 fixture; production freshness rules
were not changed. After formatting, all 23 governance-manifest tests passed again. Candidate
secret-pattern scans and staged diff checks found no unresolved findings. These checks do not
validate real OCR, embedding, reranker, GPU/video inference or a fresh Linux dependency installation.
