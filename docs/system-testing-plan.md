# Ped-Agent 知识库系统测试方案

> **status: historical** · 2026-10-07 审计标注：本文是写作当日的快照，其中“当前”“完成”等表述只指当时状态。当前 RAG 状态见 [RAG 资产与一致性审计](rag-asset-audit-2026-10-07.md)。

_基于 34 篇文献的完整测试流程 · created: 2026-09-09_

---

## 🎯 测试目标

验证从文献导入到检索评测的完整知识处理链路，确保：
1. ✅ 文献能够成功导入到 Catalog
2. ✅ PDF 能够正确解析和分块
3. ✅ BGE-M3 向量索引正常工作
4. ✅ 检索系统能够返回相关结果
5. ✅ Gold Questions 评测达到预期指标

---

## 📋 测试环节与流程

### 环节 1: 准备阶段（Preparation）
**目标**: 准备导入 Manifest 和配置文件

#### 输入
- 34 篇 PDF 文件（`memPed/knowledge/pilot-batch-1-candidates/pdfs/`）
- 评分结果（`scoring-results.csv`）
- 文献元数据（标题、作者、期刊、年份、DOI）

#### 操作
1. 生成 IngestionManifest
   - 扫描所有 PDF 文件
   - 计算 SHA-256 哈希
   - 提取元数据
   - 分配 resource_id（如 `lit-001`, `lit-002`...）

2. 验证文件完整性
   - PDF 可读性检查
   - 文件大小验证
   - 去重检查

#### 输出
- `manifest.json` - 导入清单
- `preflight_report.md` - 预检报告

**预期结果**: 34 篇文献全部通过预检

---

### 环节 2: 导入阶段（Ingestion）
**目标**: 将文献导入到知识库 Catalog

#### 操作
1. **文件存储**
   - 复制 PDF 到 Vault：`memPed/knowledge/literature/files/`
   - 按 SHA-256 命名存储

2. **元数据入库**
   - 写入 `knowledge.sqlite3` Catalog
   - 记录：resource_id, title, authors, journal, year, doi, sha256
   - 记录主题标签（primary_topic）

3. **版本管理**
   - 记录导入时间戳
   - 记录导入批次（batch_id）

#### 输出
- `knowledge.sqlite3` - 权威 Catalog 数据库
- `literature/files/*.pdf` - 原文 Vault
- `import_log.jsonl` - 导入日志

**预期结果**:
- 34 条记录成功写入 Catalog
- 34 个 PDF 文件存储到 Vault
- 无重复、无错误

---

### 环节 3: 解析与分块阶段（Parsing & Chunking）
**目标**: 解析 PDF 并生成可检索的文本块

#### 操作
1. **PDF 解析**
   - 提取全文文本
   - 识别页码
   - 保留结构信息（章节、段落）

2. **Parent-Child Chunking**
   - Parent Chunk: 大块（~1500 tokens）
   - Child Chunk: 小块（~512 tokens）
   - 保持语义完整性

3. **元数据附加**
   - 每个 Chunk 记录：
     - resource_id
     - page_number
     - chunk_id
     - parent_chunk_id（如果是 child）

#### 输出
- `derived/<resource-id>/<sha>/text.json` - 解析后的全文
- `derived/<resource-id>/<sha>/chunks.json` - 分块结果
- Catalog 中的 chunks 表记录

**预期结果**:
- 34 篇文献成功解析
- 生成约 2000-3000 个 chunks（平均 ~60-90 chunks/篇）
- 页码信息完整

---

### 环节 4: 向量化阶段（Embedding）
**目标**: 使用 BGE-M3 生成向量并建立索引

#### 操作
1. **加载 BGE-M3 模型**
   - 从 `memPed/knowledge/models/bge-m3/` 加载
   - 设备: CUDA/FP16
   - 维度: 1024

2. **批量向量化**
   - 对所有 chunks 生成 embedding
   - 批处理（batch_size=32）

3. **构建 Chroma 索引**
   - 存储路径: `memPed/knowledge/indexes/bge-m3-1024/`
   - 包含元数据（resource_id, page, chunk_id）

#### 输出
- `indexes/bge-m3-1024/` - Chroma 向量索引
- `embedding_stats.json` - 向量化统计

**预期结果**:
- ~2000-3000 个向量成功索引
- 索引大小: ~10-20 MB
- 查询响应时间 < 100ms

---

### 环节 5: FTS5 全文索引阶段（Full-Text Search）
**目标**: 构建 SQLite FTS5 索引用于关键词检索

#### 操作
1. **创建 FTS5 表**
   - 索引字段: title, authors, abstract, full_text

2. **填充索引**
   - 从 Catalog 读取文本
   - 写入 FTS5 表

#### 输出
- `fts.sqlite3` - 全文检索索引

**预期结果**:
- 34 篇文献的全文可搜索
- 支持中英文混合检索

---

### 环节 6: 检索测试阶段（Retrieval Testing）
**目标**: 验证检索系统功能

#### 操作
1. **向量检索测试**
   - 输入查询: "What is the fundamental diagram?"
   - Top-K: 5
   - 返回相关 chunks

2. **混合检索测试**
   - 向量检索 + FTS5
   - 结果融合（如 RRF）

3. **页码定位测试**
   - 验证返回结果包含准确页码
   - 可追溯到原文

#### 测试用例（示例）
```json
[
  {
    "query": "What is the fundamental diagram of pedestrian flow?",
    "expected_topics": ["fundamental_diagram", "flow_capacity"],
    "expected_resources": ["lit-001", "lit-002"]
  },
  {
    "query": "How does crowd density affect evacuation time?",
    "expected_topics": ["evacuation", "density"],
    "expected_resources": ["lit-015", "lit-020"]
  }
]
```

#### 输出
- `retrieval_test_results.json` - 检索测试结果
- 每个查询的 Top-5 结果
- 相关性分数

**预期结果**:
- 查询响应时间 < 200ms
- Top-5 结果包含相关文献
- 页码信息准确

---

### 环节 7: Gold Questions 评测阶段（Evaluation）
**目标**: 使用标准问题集评估检索质量

#### 输入
- `pilot_gold.jsonl` - Gold Questions（30 个问题）
- `pilot_config.json` - 评测配置

#### 操作
1. **执行批量检索**
   - 对每个 Gold Question 执行检索
   - 记录 Top-K 结果（K=5, 10）

2. **计算评测指标**
   - **Recall@5**: 前 5 个结果中包含相关文档的比例
   - **MRR (Mean Reciprocal Rank)**: 第一个相关结果的平均倒数排名
   - **页码命中率**: 返回结果页码准确性

3. **生成评测报告**
   - 整体指标
   - 按主题分类的指标
   - 失败案例分析

#### Gold Questions 示例
```jsonl
{"question_id": "gq-001", "query": "什么是行人流基本图？", "relevant_docs": ["lit-001", "lit-006"], "relevant_pages": [[5, 6], [10, 12]]}
{"question_id": "gq-002", "query": "瓶颈对行人流量的影响", "relevant_docs": ["lit-003", "lit-012"], "relevant_pages": [[8], [15, 16]]}
{"question_id": "gq-003", "query": "Love Parade 踩踏事故的主要原因", "relevant_docs": ["lit-025"], "relevant_pages": [[3, 4, 5]]}
```

#### 输出
- `pilot_evaluation_report.json` - 详细评测结果
- `pilot_evaluation_summary.md` - 可读性报告
- `failed_queries.jsonl` - 失败案例

**预期结果**（Pilot 阶段目标）:
- **Recall@5**: ≥ 0.80（80%）
- **MRR**: ≥ 0.70
- **页码命中率**: ≥ 0.75

---

## 📊 完整测试输出

### 文件输出清单

```
memPed/knowledge/
├── literature/
│   ├── files/              # 34 个 PDF（按 SHA-256）
│   └── records/
│       └── manifest.json   # 导入清单
├── derived/
│   ├── lit-001/
│   │   └── <sha>/
│   │       ├── text.json
│   │       └── chunks.json
│   ├── lit-002/
│   └── ...                 # 34 个资源
├── indexes/
│   └── bge-m3-1024/        # Chroma 向量索引
├── models/
│   └── bge-m3/             # BGE-M3 模型权重
├── reports/
│   ├── preflight_report.md
│   ├── import_log.jsonl
│   ├── embedding_stats.json
│   ├── retrieval_test_results.json
│   ├── pilot_evaluation_report.json
│   └── pilot_evaluation_summary.md
├── knowledge.sqlite3       # Catalog 数据库
├── fts.sqlite3            # 全文索引
├── pilot_gold.jsonl       # Gold Questions
└── pilot_config.json      # 评测配置
```

---

## 📈 成功标准

### ✅ 技术指标
| 指标 | 目标 | 说明 |
|------|------|------|
| 导入成功率 | 100% | 34/34 文献成功导入 |
| 解析成功率 | ≥ 95% | ≥ 32/34 文献成功解析 |
| 向量化成功率 | 100% | 所有 chunks 成功索引 |
| 查询响应时间 | < 200ms | 95 分位数 |
| 索引大小 | < 100 MB | Chroma + FTS5 总大小 |

### ✅ 检索质量指标
| 指标 | Pilot 目标 | Core 目标 |
|------|-----------|-----------|
| Recall@5 | ≥ 0.80 | ≥ 0.85 |
| MRR | ≥ 0.70 | ≥ 0.75 |
| 页码命中率 | ≥ 0.75 | ≥ 0.80 |

---

## 🚀 测试执行方式

### 方式 1: Python 测试脚本
```powershell
# 设置环境变量
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"

# 执行完整测试链
.\.venv\Scripts\python -m pytest Knowledge-Base/tests/test_full_pipeline.py -v

# 或分步执行
.\.venv\Scripts\python -m pytest Knowledge-Base/tests/test_ingestion.py -v
.\.venv\Scripts\python -m pytest Knowledge-Base/tests/test_retrieval.py -v
.\.venv\Scripts\python -m pytest Knowledge-Base/tests/test_evaluation.py -v
```

### 方式 2: 手动执行（如果测试脚本未就绪）
1. 生成 Manifest
2. 运行导入
3. 触发解析
4. 构建索引
5. 执行评测

---

## ⚠️ 潜在问题与解决方案

### 问题 1: BGE-M3 模型未下载
**解决**:
```python
from ped_knowledge.embeddings import download_bge_m3
download_bge_m3(target_dir="memPed/knowledge/models/bge-m3")
```

### 问题 2: CUDA 不可用
**解决**: 降级到 CPU 模式（会变慢）
```python
device = "cpu"  # 在配置中设置
```

### 问题 3: PDF 解析失败
**原因**: 扫描版 PDF、加密 PDF
**解决**: 跳过问题文件，记录到报告

### 问题 4: 内存不足
**原因**: 34 篇文献同时处理
**解决**: 分批处理（batch_size=5-10）

---

## 📝 测试后续步骤

### 如果测试通过
1. ✅ 确认系统就绪
2. ✅ 补充到 40 篇（批次 4）
3. ✅ 扩展到 Core 阶段（120 篇）
4. ✅ 开始实际问答实验

### 如果测试未通过
1. ⚠️ 分析失败原因
2. ⚠️ 调整配置参数
3. ⚠️ 优化分块策略
4. ⚠️ 重新评测

---

## 📅 预估时间

| 环节 | 预估时间 |
|------|---------|
| Manifest 生成 | 2-5 分钟 |
| 导入 | 5-10 分钟 |
| 解析与分块 | 10-20 分钟 |
| 向量化（CUDA） | 10-15 分钟 |
| 向量化（CPU） | 30-60 分钟 |
| 构建索引 | 5-10 分钟 |
| 检索测试 | 2-5 分钟 |
| Gold Questions 评测 | 5-10 分钟 |
| **总计（CUDA）** | **~40-75 分钟** |
| **总计（CPU）** | **~70-125 分钟** |

---

**准备好开始测试了吗？**
