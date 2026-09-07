# BGE-M3 本地配置

_Knowledge-Base 的本地向量模型配置与复现命令 · status: current_

## 固定路径

- 参数配置：`Knowledge-Base/config/embeddings/bge-m3/model.yaml`
- 模型权重：`memPed/knowledge/models/bge-m3/`
- 后续索引：`memPed/knowledge/indexes/bge-m3-1024/`

模型权重和向量索引属于本地研究数据，不提交 Git。以下命令均从仓库根目录执行。

## 安装依赖

```powershell
uv pip install --python .venv\Scripts\python.exe "FlagEmbedding==1.4.2"
uv pip install --python .venv\Scripts\python.exe --reinstall `
  "torch==2.14.0+cu130" --index-url https://download.pytorch.org/whl/cu130
```

第二条命令安装 CUDA 13.0 的 Windows PyTorch wheel；默认 PyPI 的 `torch` wheel 为 CPU
版本，不能使用本机 RTX 3080。

## 下载模型

```powershell
New-Item -ItemType Directory -Force -Path `
  'memPed/knowledge/models/bge-m3', `
  'memPed/knowledge/indexes/bge-m3-1024' | Out-Null

.\.venv\Scripts\python.exe -c "from huggingface_hub import snapshot_download; print(snapshot_download(repo_id='BAAI/bge-m3', local_dir='memPed/knowledge/models/bge-m3'))"
```

## CUDA 冒烟验证

```powershell
.\.venv\Scripts\python.exe -c "import numpy as np; import torch; from FlagEmbedding import BGEM3FlagModel; m=BGEM3FlagModel('memPed/knowledge/models/bge-m3', devices='cuda:0', use_fp16=True); out=m.encode(['行人通过瓶颈时的流动特征','Pedestrian motion through a bottleneck'], batch_size=8, max_length=1024, return_dense=True, return_sparse=False, return_colbert_vecs=False); v=np.asarray(out['dense_vecs']); print({'shape': list(v.shape), 'dtype': str(v.dtype), 'gpu': torch.cuda.get_device_name(0)}); assert v.shape==(2,1024)"
```

预期输出包含 `shape: [2, 1024]` 和 `NVIDIA GeForce RTX 3080`。本配置不构建正式
Chroma 索引。
