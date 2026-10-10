# UV 快速环境配置（精简版）
# 适合已经熟悉 UV 的用户

# 创建虚拟环境
uv venv --python 3.12

# 激活环境
.\.venv\Scripts\Activate.ps1

# 安装依赖（使用 uv pip）
uv pip install chromadb==0.5.23
uv pip install transformers==4.46.3
uv pip install sentence-transformers==3.3.1
uv pip install pypdf==5.1.0
uv pip install pytest==8.3.4
uv pip install numpy pandas tqdm

# 安装 PyTorch (CUDA 13.0)
uv pip install "torch==2.14.0+cu130" "torchvision==0.29.0+cu130" --index-url https://download.pytorch.org/whl/cu130

# 验证安装
python -c "import chromadb; import transformers; import torch; print('✅ 所有依赖已安装')"
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
