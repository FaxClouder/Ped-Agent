# PyTorch CUDA Unification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the CPU-only PyTorch runtime with the repository-standard CUDA 13.0 build and verify real RTX 3080 execution.

**Architecture:** The workspace root owns the exact Torch and TorchVision versions and maps both packages to the official cu130 index. Active setup entry points repeat the same exact versions, while `uv.lock` records the resolved CUDA wheels and `uv sync` installs them into `.venv`.

**Tech Stack:** Python 3.12, uv 0.11.7, PyTorch 2.14.0+cu130, TorchVision 0.29.0+cu130, PowerShell, pytest

## Global Constraints

- Use `torch==2.14.0+cu130` and `torchvision==0.29.0+cu130` from `https://download.pytorch.org/whl/cu130`.
- Do not install TorchAudio because the project does not use it and no matching 2.14.0 cu130 Windows wheel exists.
- Preserve all unrelated working-tree changes and local research assets.
- Do not rewrite historical design records.
- Validate on the installed NVIDIA GeForce RTX 3080 with an actual CUDA matrix multiplication.

---

### Task 1: Make the CUDA dependency declaration reproducible

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`

**Interfaces:**
- Consumes: Python 3.12 on Windows and the official PyTorch cu130 package index.
- Produces: A workspace lock in which Torch and TorchVision resolve from the cu130 index.

- [ ] **Step 1: Reproduce the current source mismatch**

Run:

```powershell
.\.venv\Scripts\python.exe -c "import torch; print(torch.__version__, torch.version.cuda)"
rg -n 'source = \{ registry = "https://pypi.org/simple" \}' uv.lock
```

Expected before the change: Python prints `2.14.0+cpu None`, and the Torch lock entry uses PyPI.

- [ ] **Step 2: Declare the exact CUDA dependencies and index**

Set the root project dependencies and uv source mapping to:

```toml
dependencies = [
  "torch==2.14.0+cu130",
  "torchvision==0.29.0+cu130",
]

[[tool.uv.index]]
name = "pytorch-cu130"
url = "https://download.pytorch.org/whl/cu130"
explicit = true

[tool.uv.sources]
torch = { index = "pytorch-cu130" }
torchvision = { index = "pytorch-cu130" }
```

- [ ] **Step 3: Re-resolve the lock file**

Run:

```powershell
uv lock
```

Expected: exit code 0 and Torch/TorchVision package sources under the cu130 PyTorch registry.

- [ ] **Step 4: Verify the lock source and versions**

Run:

```powershell
uv tree --locked | Select-String -Pattern 'torch|torchvision'
rg -n '2\.14\.0\+cu130|0\.29\.0\+cu130|download\.pytorch\.org/whl/cu130' uv.lock
```

Expected: the tree contains Torch 2.14.0+cu130 and TorchVision 0.29.0+cu130; the lock contains cu130 URLs.

### Task 2: Align active Windows setup entry points

**Files:**
- Modify: `setup-environment.ps1`
- Modify: `setup-environment-quick.ps1`
- Modify: `install-missing-deps.ps1`
- Modify: `QUICK-SETUP.md`
- Modify: `SETUP-INSTRUCTIONS.md`
- Modify: `docs/uv-environment-status.md`

**Interfaces:**
- Consumes: The exact versions and index declared by Task 1.
- Produces: Setup commands that install the same CUDA packages without TorchAudio or CPU fallback commands.

- [ ] **Step 1: Locate active inconsistent install commands**

Run:

```powershell
rg -n 'cu121|cu124|torchaudio|uv pip install torch|pip install torch' setup-environment.ps1 setup-environment-quick.ps1 install-missing-deps.ps1 QUICK-SETUP.md SETUP-INSTRUCTIONS.md docs/uv-environment-status.md
```

Expected before the change: matches include cu121, TorchAudio, and unqualified CPU fallback commands.

- [ ] **Step 2: Replace each active install command with the unified command**

Use this command in every active setup path:

```powershell
uv pip install "torch==2.14.0+cu130" "torchvision==0.29.0+cu130" --index-url https://download.pytorch.org/whl/cu130
```

Remove TorchAudio and unqualified `torch torchvision` fallback commands. Keep explanatory text aligned with CUDA 13.0 and the RTX 3080 driver requirement.

- [ ] **Step 3: Verify no active mismatch remains**

Run:

```powershell
rg -n 'cu121|cu124|torchaudio|uv pip install torch torchvision|pip install torch torchvision' setup-environment.ps1 setup-environment-quick.ps1 install-missing-deps.ps1 QUICK-SETUP.md SETUP-INSTRUCTIONS.md docs/uv-environment-status.md
```

Expected: no matches.

### Task 3: Install and execute on the GPU

**Files:**
- Modify locally: `.venv/`
- Test: `Video-Analysis/tests/`
- Test: `Contracts/tests/`, `Agent/tests/`, `Knowledge-Base/tests/`, `Video-Analysis/tests/`

**Interfaces:**
- Consumes: The locked cu130 dependencies from Task 1.
- Produces: A local environment that executes PyTorch kernels on the RTX 3080.

- [ ] **Step 1: Synchronize the virtual environment**

Run:

```powershell
uv sync --all-groups
```

Expected: exit code 0 and CPU-only Torch is replaced by cu130 Torch.

- [ ] **Step 2: Verify package metadata and real CUDA execution**

Run:

```powershell
.\.venv\Scripts\python.exe -c "import torch, torchvision; assert torch.__version__ == '2.14.0+cu130'; assert torchvision.__version__ == '0.29.0+cu130'; assert torch.version.cuda == '13.0'; assert torch.cuda.is_available(); assert torch.cuda.get_device_name(0) == 'NVIDIA GeForce RTX 3080'; a=torch.randn((1024,1024),device='cuda'); b=a@a; torch.cuda.synchronize(); print({'torch':torch.__version__,'torchvision':torchvision.__version__,'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0),'result':float(b[0,0])})"
```

Expected: exit code 0 and a result dictionary identifying CUDA 13.0 and the RTX 3080.

- [ ] **Step 3: Run the narrow video-analysis test suite**

Run:

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python.exe -m pytest Video-Analysis/tests -q
```

Expected: exit code 0 with no failed tests.

- [ ] **Step 4: Run the complete repository test suite**

Run:

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python.exe -m pytest Contracts/tests Agent/tests Knowledge-Base/tests Video-Analysis/tests -q
```

Expected: exit code 0 with no failed tests.

- [ ] **Step 5: Review only task-related changes before committing**

Run:

```powershell
git diff --check
git diff -- pyproject.toml setup-environment.ps1 setup-environment-quick.ps1 install-missing-deps.ps1 QUICK-SETUP.md SETUP-INSTRUCTIONS.md docs/uv-environment-status.md uv.lock
```

Expected: no whitespace errors and only the CUDA unification changes described above.
