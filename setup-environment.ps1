# UV 环境配置脚本
# 使用 uv 快速创建和管理 Python 环境

Write-Host "=== Ped-Agent 环境配置（使用 UV）===" -ForegroundColor Cyan
Write-Host ""

# 检查 uv 是否安装
Write-Host "检查 uv 安装状态..." -ForegroundColor Yellow
try {
    $uvVersion = uv --version
    Write-Host "✅ UV 已安装: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ UV 未安装，请先安装 UV" -ForegroundColor Red
    Write-Host ""
    Write-Host "安装方法:" -ForegroundColor Yellow
    Write-Host "  PowerShell: irm https://astral.sh/uv/install.ps1 | iex" -ForegroundColor White
    Write-Host "  或访问: https://github.com/astral-sh/uv" -ForegroundColor White
    exit 1
}

Write-Host ""

# 切换到项目目录
$projectRoot = "E:\F_Workspace\F-Agent-Paper"
Set-Location $projectRoot
Write-Host "📁 项目目录: $projectRoot" -ForegroundColor Cyan
Write-Host ""

# 检查是否已有虚拟环境
if (Test-Path ".venv") {
    Write-Host "⚠️  检测到现有 .venv 目录" -ForegroundColor Yellow
    $response = Read-Host "是否删除并重新创建? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "删除旧环境..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force .venv
        Write-Host "✅ 已删除" -ForegroundColor Green
    } else {
        Write-Host "保留现有环境，跳过创建步骤" -ForegroundColor Yellow
        $skipCreate = $true
    }
}

Write-Host ""

# 创建虚拟环境
if (-not $skipCreate) {
    Write-Host "步骤 1: 创建虚拟环境" -ForegroundColor Cyan
    Write-Host "执行: uv venv --python 3.12" -ForegroundColor Gray
    uv venv --python 3.12

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 虚拟环境创建成功" -ForegroundColor Green
    } else {
        Write-Host "❌ 虚拟环境创建失败" -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

# 激活虚拟环境
Write-Host "步骤 2: 激活虚拟环境" -ForegroundColor Cyan
Write-Host "执行: .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
& .\.venv\Scripts\Activate.ps1

if ($?) {
    Write-Host "✅ 虚拟环境已激活" -ForegroundColor Green
} else {
    Write-Host "❌ 虚拟环境激活失败" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 安装核心依赖
Write-Host "步骤 3: 安装核心依赖" -ForegroundColor Cyan
Write-Host ""

$packages = @(
    "chromadb==0.5.23",
    "transformers==4.46.3",
    "sentence-transformers==3.3.1",
    "pypdf==5.1.0",
    "pytest==8.3.4",
    "numpy",
    "pandas",
    "tqdm"
)

foreach ($package in $packages) {
    Write-Host "  安装: $package" -ForegroundColor Gray
    uv pip install $package
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ⚠️  安装 $package 时出错，继续..." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "✅ 核心依赖安装完成" -ForegroundColor Green
Write-Host ""

# 安装 PyTorch（CUDA 版本）
Write-Host "步骤 4: 安装 PyTorch (CUDA 支持)" -ForegroundColor Cyan
Write-Host ""

Write-Host "  安装 PyTorch 2.14.0 (CUDA 13.0)..." -ForegroundColor Gray
uv pip install "torch==2.14.0+cu130" "torchvision==0.29.0+cu130" --index-url https://download.pytorch.org/whl/cu130

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PyTorch (CUDA 13.0) 安装完成" -ForegroundColor Green
} else {
    Write-Host "❌ PyTorch CUDA 版本安装失败" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 验证安装
Write-Host "步骤 5: 验证安装" -ForegroundColor Cyan
Write-Host ""

# 检查 ChromaDB
Write-Host "  检查 ChromaDB..." -ForegroundColor Gray
python -c "import chromadb; print(f'    ✅ ChromaDB: {chromadb.__version__}')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "    ❌ ChromaDB 不可用" -ForegroundColor Red
}

# 检查 Transformers
Write-Host "  检查 Transformers..." -ForegroundColor Gray
python -c "import transformers; print(f'    ✅ Transformers: {transformers.__version__}')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "    ❌ Transformers 不可用" -ForegroundColor Red
}

# 检查 PyTorch
Write-Host "  检查 PyTorch..." -ForegroundColor Gray
python -c "import torch; print(f'    ✅ PyTorch: {torch.__version__}'); print(f'    ✅ CUDA Available: {torch.cuda.is_available()}')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "    ❌ PyTorch 不可用" -ForegroundColor Red
}

# 检查 Sentence Transformers
Write-Host "  检查 Sentence Transformers..." -ForegroundColor Gray
python -c "from sentence_transformers import SentenceTransformer; print('    ✅ Sentence Transformers: OK')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "    ❌ Sentence Transformers 不可用" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== 环境配置完成 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步:" -ForegroundColor Yellow
Write-Host "  1. 确保虚拟环境已激活: .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  2. 设置 PYTHONPATH:" -ForegroundColor White
Write-Host '     $env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"' -ForegroundColor Gray
Write-Host "  3. 运行测试: python -m pytest Knowledge-Base/tests/ -v" -ForegroundColor White
Write-Host ""
