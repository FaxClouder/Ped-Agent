# 环境配置执行指南

_手动执行步骤 · 使用 UV_

---

## 🚀 执行步骤

请在 PowerShell 中依次执行以下命令：

### 步骤 1: 进入项目目录
```powershell
cd E:\F_Workspace\F-Agent-Paper
```

### 步骤 2: 创建虚拟环境
```powershell
uv venv --python 3.12
```
**预期输出**: `Using Python 3.12.x interpreter at: ...`

---

### 步骤 3: 激活虚拟环境
```powershell
.\.venv\Scripts\Activate.ps1
```
**预期输出**: 命令提示符前出现 `(.venv)`

---

### 步骤 4: 安装核心依赖（逐个安装）
```powershell
# ChromaDB
uv pip install chromadb==0.5.23

# Transformers
uv pip install transformers==4.46.3

# Sentence Transformers
uv pip install sentence-transformers==3.3.1

# PDF 解析
uv pip install pypdf==5.1.0

# 测试框架
uv pip install pytest==8.3.4

# 数据处理
uv pip install numpy pandas tqdm
```

---

### 步骤 5: 安装 PyTorch

#### CUDA 13.0 版本（项目标准）
```powershell
uv pip install "torch==2.14.0+cu130" "torchvision==0.29.0+cu130" --index-url https://download.pytorch.org/whl/cu130
```

---

### 步骤 6: 验证安装
```powershell
# 验证所有依赖
python -c "import chromadb; print(f'ChromaDB: {chromadb.__version__}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
python -c "from sentence_transformers import SentenceTransformer; print('Sentence Transformers: OK')"
```

**预期输出**:
```
ChromaDB: 0.5.23
Transformers: 4.46.3
PyTorch: 2.14.0+cu130
CUDA Available: True
Sentence Transformers: OK
```

---

### 步骤 7: 设置 PYTHONPATH
```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
```

---

### 步骤 8: 测试环境
```powershell
# 运行简单测试
python -m pytest Knowledge-Base/tests/test_module_boundary.py -v
```

---

## ✅ 成功标志

所有步骤完成后，您应该看到：
- ✅ 虚拟环境已激活（提示符有 `.venv`）
- ✅ 所有包版本正确
- ✅ CUDA 状态显示（True 或 False）
- ✅ 测试通过

---

## ⚠️ 如果遇到错误

### 错误 1: uv 命令未找到
**解决**:
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

### 错误 2: 网络超时
**解决**: 使用国内镜像
```powershell
uv pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <package-name>
```

### 错误 3: 权限拒绝
**解决**: 以管理员身份运行 PowerShell

---

## 📋 完整一键命令（复制粘贴）

如果您想一次性执行，可以复制以下内容到 PowerShell：

```powershell
# 进入项目目录
cd E:\F_Workspace\F-Agent-Paper

# 创建虚拟环境
uv venv --python 3.12

# 激活环境
.\.venv\Scripts\Activate.ps1

# 安装所有依赖
uv pip install chromadb==0.5.23 transformers==4.46.3 sentence-transformers==3.3.1 pypdf==5.1.0 pytest==8.3.4 numpy pandas tqdm

# 安装 PyTorch (CUDA)
uv pip install "torch==2.14.0+cu130" "torchvision==0.29.0+cu130" --index-url https://download.pytorch.org/whl/cu130

# 验证
python -c "import chromadb; import transformers; import torch; print('✅ 所有依赖已安装')"
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# 设置 PYTHONPATH
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"

Write-Host "✅ 环境配置完成！" -ForegroundColor Green
```

---

## 📞 完成后请告诉我

执行完成后，请告诉我：
1. 是否所有包都安装成功？
2. CUDA 是否可用？
3. 测试是否通过？

我会帮您进行下一步的系统测试！

---

**预计总时间**: 5-10 分钟
