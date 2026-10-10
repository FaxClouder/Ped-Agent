# 环境配置执行步骤

## 📋 执行清单

### 第 1 步：打开 PowerShell
- 在开始菜单搜索 "PowerShell"
- 以普通用户身份打开即可（无需管理员）

---

### 第 2 步：复制粘贴以下命令
```powershell
# 1. 进入项目目录
cd E:\F_Workspace\F-Agent-Paper

# 2. 创建虚拟环境
uv venv --python 3.12

# 3. 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 4. 安装核心依赖
uv pip install chromadb==0.5.23 transformers==4.46.3 sentence-transformers==3.3.1 pypdf==5.1.0 pytest==8.3.4 numpy pandas tqdm

# 5. 安装 PyTorch (CUDA 13.0 版本)
uv pip install "torch==2.14.0+cu130" "torchvision==0.29.0+cu130" --index-url https://download.pytorch.org/whl/cu130

# 6. 验证安装
python -c "import chromadb; print('ChromaDB: OK')"
python -c "import transformers; print('Transformers: OK')"
python -c "import torch; print(f'PyTorch: OK'); print(f'CUDA: {torch.cuda.is_available()}')"

# 7. 设置环境变量
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"

# 8. 完成提示
Write-Host "`n✅ 环境配置完成！" -ForegroundColor Green
```

---

### 第 3 步：等待安装完成
- 预计时间：5-10 分钟
- 会看到很多下载进度条

---

### 第 4 步：检查结果
应该看到：
```
ChromaDB: OK
Transformers: OK
PyTorch: OK
CUDA: True (或 False)

✅ 环境配置完成！
```

---

## ⚠️ 注意事项

1. **如果提示 "无法加载文件 .venv\Scripts\Activate.ps1"**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
   然后重新执行第 3 步

2. **如果网络很慢**
   在每个 `uv pip install` 前加上：
   ```powershell
   -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

3. **如果无 GPU（CUDA: False）**
   这是正常的，使用 CPU 模式即可

---

## 📞 完成后告诉我

1. 是否看到 "✅ 环境配置完成！"？
2. CUDA 显示 True 还是 False？
3. 有任何错误提示吗？

我会帮您继续下一步的系统测试！

---

**预计总时间：5-10 分钟**
