# 环境检查报告

> **status: historical** · 2026-10-07 审计标注：本文是写作当日的快照，其中“当前”“完成”等表述只指当时状态。当前 RAG 状态见 [RAG 资产与一致性审计](rag-asset-audit-2026-10-07.md)。

## BGE-M3 模型 ✅ 已完成

**模型路径**: `memPed/knowledge/models/bge-m3/`
**总大小**: 7.1 GB

**关键文件**:
- ✅ `pytorch_model.bin` (2.2 GB) - 主模型权重
- ✅ `config.json` - 模型配置
- ✅ `tokenizer.json` (17 MB) - 分词器
- ✅ `sentencepiece.bpe.model` (4.9 MB) - SentencePiece 模型
- ✅ `colbert_linear.pt` (2.1 MB) - ColBERT 线性层
- ✅ `sparse_linear.pt` (3.5 KB) - 稀疏检索层
- ✅ `1_Pooling/` - Pooling 层配置
- ✅ `onnx/` - ONNX 格式（可选）

**状态**: ✅ **完整下载，可以使用**

---

## PyTorch + CUDA ⚠️ 需要确认

**当前状态**: PyTorch 模块未找到

**可能原因**:
1. PyTorch 安装在不同的 Python 环境
2. 需要重新安装
3. 环境变量问题

**需要安装的命令**:
```bash
pip install torch==2.14.0+cu130 torchvision==0.29.0+cu130 \
    --index-url https://download.pytorch.org/whl/cu130
```

或者使用项目配置的源：
```bash
pip install torch==2.14.0+cu130 \
    --index-url https://mirrors.aliyun.com/pytorch-wheels/cu130/
```

---

## 结论

- ✅ **BGE-M3 模型已完整下载** (7.1 GB)
- ⚠️ **PyTorch 需要检查安装状态**

建议：先确认 PyTorch 安装，然后就可以运行向量索引构建了！
