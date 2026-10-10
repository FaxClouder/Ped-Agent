# 安装缺失的依赖
# 使用方式: .\install-missing-deps.ps1

Write-Host "开始安装缺失的依赖..." -ForegroundColor Cyan

# 确保在项目目录
Set-Location E:\F_Workspace\F-Agent-Paper

# 激活虚拟环境
Write-Host "`n激活虚拟环境..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# 安装缺失的包
Write-Host "`n安装 Transformers..." -ForegroundColor Yellow
python -m pip install transformers==4.46.3

Write-Host "`n安装 Sentence Transformers..." -ForegroundColor Yellow
python -m pip install sentence-transformers==3.3.1

Write-Host "`n安装 PyPDF..." -ForegroundColor Yellow
python -m pip install pypdf==5.1.0

Write-Host "`n安装 Pytest..." -ForegroundColor Yellow
python -m pip install pytest==8.3.4

Write-Host "`n安装 PyTorch (CUDA 版本)..." -ForegroundColor Yellow
uv pip install "torch==2.14.0+cu130" "torchvision==0.29.0+cu130" --index-url https://download.pytorch.org/whl/cu130

# 验证安装
Write-Host "`n======================================" -ForegroundColor Green
Write-Host "验证安装结果..." -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

Write-Host "`n检查 Transformers..." -ForegroundColor Cyan
python -c "import transformers; print('Transformers:', transformers.__version__)"

Write-Host "检查 Sentence Transformers..." -ForegroundColor Cyan
python -c "from sentence_transformers import SentenceTransformer; print('Sentence Transformers: OK')"

Write-Host "检查 PyPDF..." -ForegroundColor Cyan
python -c "import pypdf; print('PyPDF:', pypdf.__version__)"

Write-Host "检查 Pytest..." -ForegroundColor Cyan
python -c "import pytest; print('Pytest:', pytest.__version__)"

Write-Host "检查 PyTorch..." -ForegroundColor Cyan
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA Available:', torch.cuda.is_available())"

Write-Host "检查 ChromaDB..." -ForegroundColor Cyan
python -c "import chromadb; print('ChromaDB:', chromadb.__version__)"

Write-Host "`n======================================" -ForegroundColor Green
Write-Host "所有依赖安装完成!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
