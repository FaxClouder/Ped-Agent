# 索引构建报告

**日期**: 2026-09-24  
**会话**: Index building for knowledge base  
**状态**: ✓ 完成（验证性构建）

## 概览

本报告记录了一次验证性索引构建，用于确认索引构建流程和工具的可用性。

**注意**: 正式的实验索引位于 `outputs/knowledge-index-104-v1-20260924-01/`（2026-09-24 14:21 构建），
已用于 Gold v5 开发集评测。本报告记录的验证索引（2026-09-24 18:05 构建）已删除，因其路径不符合
实验规范且元数据不完整。

## 正式实验索引

**位置**: `outputs/knowledge-index-104-v1-20260924-01/`  
**构建时间**: 2026-09-24 14:21  
**代码版本**: d739b75bc2beb3963acc279a0b59b3304b00a857

### FTS5/BM25 词法索引

**文件**: `fts.sqlite3` (19 MB)

**配置**:
- 词法分析器: jieba-lexical-v1
- 词法指纹: `75333cf88223b51dc36eb9a45aa60cb54955bbac486403929f7ad6c2ef34db2d`
- 领域词表: `Knowledge-Base/config/retrieval/pedestrian_terms.txt`
- 停用词: `Knowledge-Base/config/retrieval/stopwords_zh_en.txt`
- 查询操作符: OR（任意词命中即召回）

**统计**:
- 索引文档: 6,336 个 child chunks
- 切块策略: parent-child-v1
- 源指纹: d4a05aa6c6ea72436bc318f71edc74a81f666372be4c4d364988461ffad82535
- 清单指纹: d500dd379826fa8fb3f145bfb1320fd5aba801b70cd3a72f8c649b33661724d0

**Gold v5 dev 评测结果**（k=5，20 个意图/40 个变体）:
```
英文查询: resource_hit@5=0.95, MRR=0.95, nDCG@5=0.95
中文查询: resource_hit@5=0.00, MRR=0.00, nDCG@5=0.00（结构性失效）
配对差值: -0.95 跨所有指标
```

### BGE-M3 稠密向量索引

**目录**: `chroma/`

**配置**:
- 模型: BAAI/bge-m3
- 模型版本: 5617a9f61b028005a4858fdac845db406aefb181
- 模型权重 SHA-256: b5e0ce3470abf5ef3831aa1bd5553b486803e83251590ab7ff35a117cf6aad38
- 设备: CUDA (NVIDIA GeForce RTX 3080)
- 精度: FP16
- 维度: 1024
- 最大长度: 1024 tokens
- 归一化: True

**统计**:
- 索引向量: 6,336 条
- 切块策略: parent-child-v1
- Catalog指纹: d4a05aa6c6ea72436bc318f71edc74a81f666372be4c4d364988461ffad82535
- Embedding指纹: f292f358b907bf3686f2d899e0d67a25b936777a74ae1138b727e33c48356715

**Gold v5 dev 评测结果**（k=5）:
```
英文查询: resource_hit@5=1.00, MRR=0.963, nDCG@5=0.972
中文查询: resource_hit@5=0.95, MRR=0.789, nDCG@5=0.829
配对差值: -0.05 (hit), -0.173 (MRR), -0.143 (nDCG)
```

### RRF 融合结果

**RRF k=60**（Gold v5 dev，k=5）:
```
英文查询: resource_hit@5=1.00, MRR=0.942, nDCG@5=0.957
中文查询: resource_hit@5=0.95, MRR=0.739, nDCG@5=0.792
```

**观察**:
- RRF 融合在当前配置下**无正收益**
- 英文: MRR 从 0.963 降至 0.942（−0.021）
- 中文: MRR 从 0.789 降至 0.739（−0.050）
- 原因: BM25 中文零信号稀释了 BGE-M3 的稠密排序

## 构建流程

### 依赖安装

本次构建时 `jieba`、`chromadb`、`FlagEmbedding==1.4.2` 在 `.venv` 中已满足，无需安装。

索引实际是在 **torch 2.14.0+cu130**（仓库 BGE-M3 文档指定的版本）下构建的。不要安装
`torch==2.4.0+cu121`：它与本环境的 NumPy 2.5.3 不兼容，导入 torch 会因
`_ARRAY_API not found` 失败。版本和安装源见
[`config/embeddings/bge-m3/README.md`](config/embeddings/bge-m3/README.md)。

### 索引构建

```bash
PYTHONPATH="Contracts/src:Knowledge-Base/src:Agent/src:Video-Analysis/src" \
  .venv/Scripts/python.exe Knowledge-Base/build_indexes.py
```

选项:
- `--policy-version parent-child-v1`: 指定切块策略（默认）
- `--skip-fts`: 跳过FTS5/BM25索引
- `--skip-dense`: 跳过BGE-M3稠密索引

### 索引验证

```bash
PYTHONPATH="Contracts/src:Knowledge-Base/src" \
  .venv/Scripts/python.exe Knowledge-Base/verify_indexes.py
```

## 技术细节

### FTS5索引结构

- 使用 SQLite FTS5 虚拟表
- 分词器: unicode61（FTS5内置）
- 索引字段: title, heading, body（均经过jieba分词）
- 未索引字段: chunk_id, resource_id, version_id, locator
- BM25参数: 标题权重=3.0, 正文权重=1.5
- 元数据表: 记录 source/lexical_analyzer/policy/tokenizer 指纹

### Chroma索引结构

- 后端: Chroma PersistentClient
- Collection: ped_agent_official_evidence
- 向量维度: 1024
- 距离度量: L2 (Chroma默认，负距离作为相似度分数)
- 元数据: catalog/embedding/policy/tokenizer/lexical_analyzer 指纹

### 指纹验证

两种索引都实现了指纹校验机制：
- **source_fingerprint**: catalog中official chunks的内容哈希
- **lexical_analyzer_fingerprint**: 词表+停用词+版本的哈希
- **tokenizer_fingerprint**: 切块tokenizer的标识
- **embedding_fingerprint**: 模型名+base_url+维度的哈希

读取索引时会验证lexical_analyzer_fingerprint匹配，防止使用错误的分词器查询。

## 已知问题

### 1. BM25中文召回失效

**现象**: 中文查询返回0结果，英文查询正常

**原因分析**:
- 语料以英文为主（104篇文献，绝大部分英文）
- jieba分词后的中文tokens在FTS5索引中几乎没有匹配
- Gold评测题目全为中文，形成语言不对称

**影响**: 
- BM25无法作为中文检索的有效通道
- RRF融合时BM25贡献为空，完全依赖BGE-M3

**缓解方案**:
1. 短期：依赖BGE-M3稠密检索（已验证有效）
2. 中期：增加中文文献或中英对照摘要
3. 长期：实现跨语言查询扩展或翻译增强

### 2. 当前 .venv 中的 torch 已被降级（待修复）

**现象**: 索引构建完成后，一条后台 `uv pip install --reinstall "torch==2.4.0+cu121"`
卸载了 torch 2.14.0+cu130 并装上 2.4.0+cu121。该版本与环境中的 NumPy 2.5.3
不兼容，`import torch` 会报 `Failed to initialize NumPy: _ARRAY_API not found`。

**影响**:
- 已构建的两个索引不受影响（构建发生在降级之前，用的是 2.14.0+cu130）
- 但当前环境**无法**再加载 BGE-M3，稠密检索查询和重建都会失败

**修复**: 重新安装文档指定版本
```powershell
uv pip install --python .venv\Scripts\python.exe --reinstall `
  "torch==2.14.0+cu130" --index-url https://mirrors.aliyun.com/pytorch-wheels/cu130/
```
修复后用 `import torch; torch.cuda.is_available()` 确认无 NumPy 警告。

### 3. 活动索引版本管理

**当前状态**: 索引指纹已记录，但缺少自动化的过期检测

**建议**:
- 在retrieval pipeline启动时验证索引指纹
- catalog更新后自动标记索引为过期
- 提供索引重建通知或自动触发

## 后续工作

### 评测准备

- [ ] 使用新索引运行Gold评测基线
- [ ] 记录BM25/BGE-M3/RRF的召回率和精确率
- [ ] 验证中文查询在BGE-M3上的有效性
- [ ] 对比parent-child-v1和v2切块策略（v2待构建）

### 索引优化

- [ ] 实验BM25参数调优（标题/正文权重）
- [ ] 测试不同的jieba词表配置
- [ ] 探索查询预处理（同义词扩展、术语识别）
- [ ] 评估重排序（Reranker）的增益

### 工具完善

- [ ] 添加索引增量更新支持
- [ ] 实现索引统计和诊断工具
- [ ] 提供索引比对和A/B测试框架
- [ ] 文档化索引管理最佳实践

## 文件清单

新增文件:
- `Knowledge-Base/build_indexes.py` - 索引构建脚本
- `Knowledge-Base/verify_indexes.py` - 索引验证脚本
- `Knowledge-Base/INDEX_BUILD_REPORT.md` - 本报告

生成的索引（不提交Git）:
- `memPed/knowledge/indexes/fts-parent-child-v1.sqlite3`
- `memPed/knowledge/indexes/bge-m3-1024/`

## 参考

- [Knowledge-Base README](README.md) - RAG研究链路说明
- [BGE-M3 配置](config/embeddings/bge-m3/README.md) - 模型下载和CUDA配置
- [词法配置](config/retrieval/lexical-v1.yaml) - jieba分词器配置
- Memory: `rag-eval-language-asymmetry.md` - BM25失效根因分析
