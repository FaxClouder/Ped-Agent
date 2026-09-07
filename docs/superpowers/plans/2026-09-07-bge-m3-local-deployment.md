# BGE-M3 Local Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Configure and verify a local CUDA/FP16 BGE-M3 installation for the Knowledge-Base module without building a production vector index.

**Architecture:** Store tracked runtime settings and instructions under `Knowledge-Base/config/embeddings/bge-m3/`, while storing downloaded weights and future Chroma data under `memPed/knowledge/`. Install the locked FlagEmbedding stack into the existing `.venv`, then run one real bilingual embedding smoke check on the RTX 3080.

**Tech Stack:** Python 3.12, uv, PyTorch, Transformers, FlagEmbedding, BAAI/bge-m3, CUDA

## Global Constraints

- Do not add a service process, HTTP API, MCP server, approval workflow, or broad test suite.
- Do not build or overwrite a formal Chroma index in this plan.
- Keep model weights and indexes under `memPed/knowledge/`; do not commit them.
- Keep model settings and reproduction instructions under `Knowledge-Base/config/embeddings/bge-m3/`.
- Use CUDA, FP16, 1024-dimensional dense embeddings, batch size 8, and maximum input length 1024.

---

### Task 1: Create the independent BGE-M3 configuration area

**Files:**
- Create: `Knowledge-Base/config/embeddings/bge-m3/model.yaml`
- Create: `Knowledge-Base/config/embeddings/bge-m3/README.md`
- Modify: `Knowledge-Base/README.md`

**Interfaces:**
- Consumes: Repository-root-relative paths defined by the approved design.
- Produces: A fixed local configuration and exact operator commands for installation, download, and smoke verification.

- [ ] **Step 1: Create the model configuration**

```yaml
model_id: BAAI/bge-m3
model_path: memPed/knowledge/models/bge-m3
index_path: memPed/knowledge/indexes/bge-m3-1024
device: cuda
use_fp16: true
dimensions: 1024
batch_size: 8
max_length: 1024
normalize_embeddings: true
```

- [ ] **Step 2: Create the operator README**

Create a current-status README with four sections: fixed paths, dependency installation,
model download, and CUDA smoke verification. Copy the exact PowerShell commands from Tasks 2
and 3 so the deployment can be repeated from the repository root.

- [ ] **Step 3: Link the configuration area from the Knowledge-Base README**

Add a `BGE-M3 本地配置` section linking to `config/embeddings/bge-m3/README.md` and state that
weights live under `memPed/knowledge/models/bge-m3/` while future indexes live under
`memPed/knowledge/indexes/bge-m3-1024/`.

- [ ] **Step 4: Validate the configuration files**

Run:

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; import yaml; p=Path('Knowledge-Base/config/embeddings/bge-m3/model.yaml'); c=yaml.safe_load(p.read_text(encoding='utf-8')); assert c['model_id']=='BAAI/bge-m3'; assert c['dimensions']==1024; assert c['device']=='cuda'; print(c)"
```

Expected: the parsed configuration is printed without an assertion failure.

### Task 2: Install the local embedding dependencies

**Files:**
- Modify: `Knowledge-Base/pyproject.toml`

**Interfaces:**
- Consumes: Existing `.venv` and the workspace's uv dependency resolution.
- Produces: Importable `torch`, `transformers`, `sentence_transformers`, and `FlagEmbedding` packages.

- [ ] **Step 1: Declare the embedding extra**

Add the following optional dependency while preserving the existing rerank extra:

```toml
embedding = ["FlagEmbedding>=1.4,<2"]
```

- [ ] **Step 2: Install the resolved dependency stack without pruning other workspace packages**

Run:

```powershell
uv pip install --python .venv\Scripts\python.exe "FlagEmbedding==1.4.2"
```

Expected: FlagEmbedding and its PyTorch/Transformers dependencies install successfully.

- [ ] **Step 3: Verify imports and CUDA availability**

Run:

```powershell
.\.venv\Scripts\python.exe -c "import torch, transformers, sentence_transformers, FlagEmbedding; print('torch', torch.__version__); print('cuda', torch.cuda.is_available()); print('gpu', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none'); assert torch.cuda.is_available()"
```

Expected: `cuda True` and `NVIDIA GeForce RTX 3080`.

### Task 3: Download and verify BGE-M3

**Files:**
- Create locally: `memPed/knowledge/models/bge-m3/`
- Reserve locally: `memPed/knowledge/indexes/bge-m3-1024/`

**Interfaces:**
- Consumes: Hugging Face model id `BAAI/bge-m3` and the installed FlagEmbedding runtime.
- Produces: Local model files and one successful `N × 1024` bilingual dense embedding result.

- [ ] **Step 1: Create the local deployment directories**

Run:

```powershell
New-Item -ItemType Directory -Force -Path 'memPed/knowledge/models/bge-m3','memPed/knowledge/indexes/bge-m3-1024' | Out-Null
```

- [ ] **Step 2: Download the required model snapshot into the configured path**

Run:

```powershell
.\.venv\Scripts\python.exe -c "from huggingface_hub import snapshot_download; print(snapshot_download(repo_id='BAAI/bge-m3', local_dir='memPed/knowledge/models/bge-m3'))"
```

Expected: the absolute or repository-relative local model directory is printed after download completion.

- [ ] **Step 3: Run the real CUDA/FP16 bilingual smoke check**

Run:

```powershell
.\.venv\Scripts\python.exe -c "import numpy as np; import torch; from FlagEmbedding import BGEM3FlagModel; m=BGEM3FlagModel('memPed/knowledge/models/bge-m3', devices='cuda:0', use_fp16=True); out=m.encode(['行人通过瓶颈时的流动特征','Pedestrian motion through a bottleneck'], batch_size=8, max_length=1024, return_dense=True, return_sparse=False, return_colbert_vecs=False); v=np.asarray(out['dense_vecs']); print({'shape': list(v.shape), 'dtype': str(v.dtype), 'gpu': torch.cuda.get_device_name(0)}); assert v.shape==(2,1024)"
```

Expected: `shape` is `[2, 1024]` and `gpu` is `NVIDIA GeForce RTX 3080`.

- [ ] **Step 4: Record installed versions and downloaded size in the final handoff**

Run:

```powershell
.\.venv\Scripts\python.exe -c "import torch, transformers, sentence_transformers, FlagEmbedding; print(torch.__version__, transformers.__version__, sentence_transformers.__version__, FlagEmbedding.__version__)"
Get-ChildItem -LiteralPath 'memPed/knowledge/models/bge-m3' -Recurse -File | Measure-Object -Property Length -Sum
```

Expected: package versions and a nonzero model byte count are printed.

### Task 4: Verify documentation and preserve unrelated data

**Files:**
- Verify: `Knowledge-Base/config/embeddings/bge-m3/README.md`
- Verify: `Knowledge-Base/README.md`
- Verify: `docs/README.md`

**Interfaces:**
- Consumes: Completed local deployment and its actual commands.
- Produces: Accurate documentation and a focused change set that excludes downloaded weights, indexes, and unrelated candidate-literature records.

- [ ] **Step 1: Check documentation links and whitespace**

Run:

```powershell
git diff --check
Test-Path -LiteralPath 'Knowledge-Base/config/embeddings/bge-m3/model.yaml'
Test-Path -LiteralPath 'memPed/knowledge/models/bge-m3/config.json'
```

Expected: no diff errors and both path checks return `True`.

- [ ] **Step 2: Inspect the focused change set**

Run:

```powershell
git status --short
git diff -- Knowledge-Base/pyproject.toml Knowledge-Base/README.md Knowledge-Base/config/embeddings/bge-m3 docs/superpowers/plans/2026-09-07-bge-m3-local-deployment.md
```

Expected: downloaded weights and index contents are not staged; the existing candidate-literature JSONL files remain untouched.
