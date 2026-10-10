# 实验验证准备情况与评测进展报告

> **status: historical** · 2026-10-07 审计标注：本文是写作当日的快照，其中“当前”“完成”等表述只指当时状态。当前 RAG 状态见 [RAG 资产与一致性审计](rag-asset-audit-2026-10-07.md)。

_状态：historical（原为 current）· 2026-09-24 · 104资源语料 V1 索引与 Gold v5 开发集评测_

## 执行摘要

**✅ 实验验证准备完成**，可进行以下工作：
- 开发集（20 intents）重复评测和方法对比
- 失效案例深入分析
- parent-child-v2 切块策略对比（需构建新索引）
- Reranker 性能评测（需集成）

**⚠️ 测试集（100 intents）已封存但未评测**，按实验设计在配置最终确定后一次性评测。

**🔧 关键发现**：
1. BM25 对中文查询结构性失效（0% Recall），稠密向量是唯一有效路径
2. BGE-M3 英文 Recall@5 = 100%，中文 = 95%，语言不对称明显
3. 索引现独立存储在 `outputs/` 目录，不在 `memPed/knowledge/` 下

---

## 1. 语料与数据库状态

### 1.1 Catalog

| 项目 | 状态 | 详情 |
|------|------|------|
| **位置** | ✅ | `memPed/knowledge/knowledge.sqlite3` (34MB) |
| **资源数** | ✅ | 104 篇文献，全部 `official` 检索资格 |
| **Chunks** | ✅ | 9,112 条，policy_version = `parent-child-v1` |
| **Tokenizer** | ✅ | `regex-token-v1`（V1策略），V2候选未激活 |
| **语料快照** | ✅ | `memPed/knowledge/literature/records/core_manifest.jsonl` |
| **SHA-256校验** | ✅ | Catalog 记录每个资源的原文哈希 |

### 1.2 派生文档

```
memPed/knowledge/derived/<resource-id>/<sha256>/
├── canonical.json           # 规范化文档结构
├── elements/                # 解析元素
└── adobe/                   # Adobe PDF Extract 原始资产（如使用）
```

**解析器**：默认 Adobe PDF Extract v1，可选 PyMuPDF v2

---

## 2. 检索索引状态

### 2.1 索引位置变更 🔧

**新策略**：实验索引独立命名，保存在 `outputs/` 目录
- **格式**：`outputs/knowledge-index-<corpus>-<version>-<date>-<seq>/`
- **当前 V1**：`outputs/knowledge-index-104-v1-20260924-01/`
- **原因**：多版本并存、实验可复现性、避免与权威数据混淆

**不再使用** `memPed/knowledge/fts.sqlite3` 或 `memPed/knowledge/indexes/`

### 2.2 V1 索引详情

#### FTS5/BM25 索引

```
outputs/knowledge-index-104-v1-20260924-01/fts.sqlite3
```

| 配置项 | 值 |
|--------|-----|
| **大小** | 19MB |
| **分词器** | jieba (JiebaLexicalAnalyzer) |
| **tokenize** | unicode61 |
| **字段** | title, heading, body (均已分词) |
| **Policy** | parent-child-v1 |
| **Chunks** | 9,112 条 child chunks |

#### BGE-M3 稠密向量索引

```
outputs/knowledge-index-104-v1-20260924-01/chroma/
```

| 配置项 | 值 |
|--------|-----|
| **向量维度** | 1024 |
| **模型** | BGE-M3 (BAAI/bge-m3) |
| **权重位置** | `memPed/knowledge/models/bge-m3/` |
| **存储** | Chroma persistent client |
| **设备** | CUDA/FP16 |
| **Chunks** | 9,112 条 child chunks |

#### 索引指纹记录

```json
// outputs/knowledge-index-104-v1-20260924-01/build_report.json
{
  "catalog_fingerprint": "d4a05aa6c6ea72436bc318f71edc74a81f666372be4c4d364988461ffad82535",
  "lexical_analyzer_fingerprint": "<jieba-fingerprint>",
  "embedding_fingerprint": "<bge-m3-fingerprint>",
  "policy_version": "parent-child-v1",
  "tokenizer_fingerprint": "regex-token-v1"
}
```

---

## 3. Gold Questions 状态

### 3.1 活跃评测集：v5 (2026-09-23 rebuild)

**位置**：`memPed/knowledge/gold/2026-09-23-rebuild/`

#### 数据文件

| 文件 | 内容 | 规模 |
|------|------|------|
| `questions_full_candidate_v5.jsonl` | 全部查询变体 | 280 queries |
| `evidence_planned_candidate_v5.jsonl` | 可回答意图证据标注 | 120 intents |
| `unanswerable_questions_candidate_v5.jsonl` | 拒答查询 | 40 queries (20 intents) |
| `full_candidate_manifest_v5.json` | 版本清单、哈希、门禁 | metadata |

#### 意图划分

```
总计：140 独立意图
├── 120 可回答意图
│   ├── 20 development intents（已评测）
│   └── 100 test intents（封存，未评测）
└── 20 拒答意图（未评测）
```

每个可回答意图包含：
- 1 个英文查询变体
- 1 个中文查询变体
- 页级证据定位（PDF SHA-256 + page index）
- AND/OR 证据组（12 个测试意图需对比两篇论文）

#### 证据标注特点

```json
{
  "evidence_groups": [
    {
      "alternatives": [  // OR within group
        {
          "resource_id": "lit-10-1007-s11069-022-05208-y",
          "source_pdf_sha256": "0a7abbf...",
          "locator": {"page_index": 0, "element_id": null},
          "locator_granularity": "pdf_page"
        }
      ],
      "group_id": "g1"
    }
  ]  // AND across groups
}
```

- **证据组间 AND**：必须在每个组中找到至少一个替代来源
- **组内 OR**：任一替代来源命中即满足该组
- **元素级定位**：当前 `element_id` 多为 null，需进一步精化

### 3.2 审查与验证状态

| 审查类型 | 状态 | 详情 |
|----------|------|------|
| **AI 词法/短语审查** | ✅ | 120 题×104 文献，检索替代来源 |
| **BGE-M3 语义审查** | ✅ | 360 个 top-100 候选，无新来源被接受 |
| **技术验证** | ✅ | SHA-256、页码、中英配对、开发/测试无泄漏 |
| **独立复核** | ✅ | u021 拒答题隧道范围澄清 |
| **元素级定位** | ⚠️ | 待完善（当前页级） |
| **语料治理** | ⚠️ | 最终确认待完成 |
| **人工验证** | ❌ | `human_verified=false`，AI 审查不建立专家标签 |

### 3.3 历史 Gold Questions

| 文件 | 状态 | 说明 |
|------|------|------|
| `pilot_gold.jsonl` | 历史 | 31题，资源ID与当前104资源不匹配 |
| `core_gold.jsonl` | 历史 | 空文件 |

**不再用于当前评测**，已被 v5 重构替代。

---

## 4. 开发集评测结果

### 4.1 评测配置

**执行路径**：`experiments/benchmark-gold-20260923/evaluate_dev.py`

| 参数 | 值 |
|------|-----|
| **问题数** | 20 intents (40 中英变体) |
| **索引** | `outputs/knowledge-index-104-v1-20260924-01/` |
| **k** | 5 (Top-5 distinct resources) |
| **Recall limit** | 40 child chunks |
| **RRF k** | 60 |
| **方法** | BM25, BGE-M3, RRF fusion |

**输出目录**：`outputs/gold-v5-dev-exploratory-20260924-01/`
- `summary.json` - 聚合指标、指纹、配对差异
- `per_query.jsonl` - 每题排名详情
- `runner_provenance.json` - 运行元数据

### 4.2 核心指标（Recall@5）

#### 按方法和语言

| 方法 | 英文 Recall@5 | 中文 Recall@5 | 中英差异 |
|------|---------------|---------------|----------|
| **BM25** | 0.95 | **0.00** 🚨 | -0.95 |
| **BGE-M3** | **1.00** | 0.95 | -0.05 |
| **RRF** | **1.00** | 0.95 | -0.05 |

#### 完整指标矩阵

**BM25/英文**：
```
Resource Hit@5:          0.95
Resource Recall@5:       0.95
Complete Evidence@5:     0.95
Exact Locator Recall@5:  0.95
Complete Locator@5:      0.95
MRR:                     0.95
nDCG@5:                  0.95
```

**BM25/中文**：
```
所有指标:                 0.00  🚨 结构性失效
```

**BGE-M3/英文**：
```
Resource Hit@5:          1.00
Resource Recall@5:       1.00
Complete Evidence@5:     1.00
Exact Locator Recall@5:  1.00
Complete Locator@5:      1.00
MRR:                     0.9625
nDCG@5:                  0.9715
```

**BGE-M3/中文**：
```
Resource Hit@5:          0.95
Resource Recall@5:       0.95
Complete Evidence@5:     0.95
Exact Locator Recall@5:  0.95
Complete Locator@5:      0.95
MRR:                     0.7892
nDCG@5:                  0.8290
```

**RRF/英文**：
```
Resource Hit@5:          1.00
MRR:                     0.9417
nDCG@5:                  0.9565
```

**RRF/中文**：
```
Resource Hit@5:          0.95
MRR:                     0.7392
nDCG@5:                  0.7921
```

### 4.3 失效案例

#### BM25 中文失效（21 queries）

```
所有20个中文开发题+1个英文题（rgq-136-en）全失败
```

**原因分析**：
- 语料：104篇**英文 PDF**
- Gold：**中文问题**
- BM25：词法精确匹配，无跨语言能力
- jieba 分词对英文文本无效

**结论**：BM25 在当前语料-题集组合下对中文查询结构性不可用。

#### BGE-M3/RRF 失效（1 query）

```
rgq-052-zh（两种方法均失败）
```

需深入分析该题的证据定位和检索结果。

### 4.4 语言不对称总结

| 维度 | 发现 |
|------|------|
| **BM25** | 英文可用（95%），中文完全失效（0%） |
| **BGE-M3** | 跨语言支持，但中文 MRR 低 0.17，nDCG 低 0.14 |
| **RRF** | 继承 BGE-M3 表现，BM25 对中文无贡献 |
| **结论** | 稠密向量是中文检索的**唯一承重路径** |

---

## 5. 评测框架

### 5.1 评分器：gold_v2

**模块**：`ped_knowledge.evaluation.gold_v2`

**核心函数**：
```python
score_answerable(evidence, ranking, k=5) -> dict[str, float]
score_refusal(expected_absent, ranking) -> dict[str, float]
summarize_paired(en_scores, zh_scores) -> dict[str, float]
```

**支持特性**：
- ✅ AND/OR 证据组语义
- ✅ 页级+元素级精确定位
- ✅ 中英配对差异计算
- ✅ 拒答标签验证
- ✅ 版本化证据记录

**与 legacy 的区别**：
- Legacy `GoldQuestion` 不支持证据组或拒答
- 两者的指标数值**不可直接对比**

### 5.2 指标定义

| 指标 | 定义 |
|------|------|
| **Resource Hit@k** | 至少一个期望资源在 top-k 中 |
| **Resource Recall@k** | 所有必需证据组均被命中 |
| **Complete Evidence@k** | 等同 Resource Recall@k |
| **Exact Locator Group Recall@k** | 页码+元素ID 精确匹配的证据组比例 |
| **Complete Locator@k** | 所有证据组的定位器均精确命中 |
| **MRR** | Mean Reciprocal Rank |
| **nDCG@k** | Normalized Discounted Cumulative Gain |

**证据组计数规则**：
- 组内替代来源（OR）不会增加分母
- 只统计必需的证据组数（AND）

---

## 6. 实验可执行性清单

### 6.1 ✅ 立即可执行（基于现有索引）

| 实验 | 命令 | 输出 |
|------|------|------|
| **重跑开发集** | `evaluate_dev.py --candidate-version v5 --output-dir outputs/gold-v5-dev-exploratory-YYYYMMDD-02` | 验证可复现性 |
| **分析 BM25 失效** | 读取 `per_query.jsonl`，检查分词和召回 | 诊断中文查询处理 |
| **分析 rgq-052-zh** | 同上，深入检查唯一 BGE-M3 失效案例 | 证据定位问题？ |
| **中英排名对比** | 基于 `per_query.jsonl` 计算排名相关性 | 量化语言差异 |

### 6.2 ⚠️ 需构建新索引

| 实验 | 依赖 | 估计工作量 |
|------|------|-----------|
| **parent-child-v2 对比** | 构建 v2 策略索引 | 中等（需重新 chunk + 索引） |
| **词法分析器 v1** | 固定领域词表，构建新 FTS | 中等 |
| **Reranker 评测** | FlagEmbedding Cross-Encoder 集成 | 中等（API 集成 + 评测） |

### 6.3 ❌ 封存前禁止

| 项目 | 原因 |
|------|------|
| **测试集评测（100题）** | 按设计一次性评测，配置最终确定后执行 |
| **拒答集评测（20题）** | 与测试集同步封存和评测 |

---

## 7. 待完成工作

### 7.1 高优先级

1. **元素级定位精化**
   - 当前：页级（`element_id: null`）
   - 目标：表格、图、段落级精确定位
   - 影响：Exact Locator 指标的可靠性

2. **语料治理最终确认**
   - 104 资源的 admission status 复核
   - 配额 (quotas.yaml) 与实际一致性验证
   - Topic/tier/year 元数据完整性

3. **rgq-052-zh 失效分析**
   - 唯一在 BGE-M3/RRF 下均失败的中文题
   - 证据标注问题？查询表述问题？

### 7.2 中优先级

4. **测试集配置封存**
   - 确认最终检索配置（是否启用 reranker）
   - 冻结测试题集和证据标注
   - 记录封存指纹和时间戳

5. **V2 策略索引构建**
   - parent-child-v2 chunk policy
   - BGE-M3 tokenizer 精确计数
   - 词法分析器 v1（固定词表）

6. **Reranker 集成**
   - FlagEmbedding Cross-Encoder 适配器
   - 延迟和成本测量
   - 排名增益评估

### 7.3 低优先级（研究性）

7. **语义替代来源完整性**
   - 当前 BGE-M3 top-100 bounded search 已完成
   - 更广泛的搜索策略（其他模型、外部语料）

8. **跨页证据处理**
   - v5 发现 2 个跨页证据案例
   - 评测框架是否正确处理？

9. **数值冲突解决**
   - v5 发现 1 个源内 58%/59% 冲突
   - 是否影响答案生成？

---

## 8. 文档同步更新

### 8.1 已修正的文档错误

| 文件 | 修正内容 |
|------|----------|
| `memPed/README.md` | 索引位置从 `knowledge/` 更新为 `outputs/` |
| `Knowledge-Base/README.md` | 同步索引位置、Gold v5 状态、开发集评测结果 |
| `experiments/benchmark-gold-20260923/README.md` | 补充当前状态：索引已构建、开发集已评测、测试集封存 |

### 8.2 文档仍需补充

- `memPed/knowledge/collection_standard.md` - 索引构建说明
- `docs/project-architecture.md` - 评测流程架构图
- 评测指标详细定义文档（当前分散在代码注释中）

---

## 9. 关键文件清单

### 9.1 权威数据

```
memPed/knowledge/
├── knowledge.sqlite3                        # Catalog (34MB, 104资源, 9112 chunks)
├── literature/files/<sha256>.pdf            # 原文 Vault
├── literature/records/core_manifest.jsonl   # 导入清单
├── derived/<resource-id>/<sha>/             # 派生文档
├── models/bge-m3/                           # BGE-M3 权重
└── gold/2026-09-23-rebuild/                 # Gold v5 候选
    ├── questions_full_candidate_v5.jsonl
    ├── evidence_planned_candidate_v5.jsonl
    ├── unanswerable_questions_candidate_v5.jsonl
    └── full_candidate_manifest_v5.json
```

### 9.2 实验索引

```
outputs/knowledge-index-104-v1-20260924-01/
├── fts.sqlite3              # BM25 索引 (19MB)
├── chroma/                  # BGE-M3 索引
│   └── chroma.sqlite3
├── build_report.json        # 索引指纹
└── runner_provenance.json   # 构建元数据
```

### 9.3 评测输出

```
outputs/gold-v5-dev-exploratory-20260924-01/
├── summary.json             # 聚合指标、指纹、配对差异
└── per_query.jsonl          # 每题排名（resource + chunk）
```

### 9.4 代码入口

```
Knowledge-Base/src/ped_knowledge/
├── evaluation/
│   ├── __init__.py          # Legacy GoldQuestion 评测
│   └── gold_v2.py           # 新评分器（证据组、拒答、配对）
├── indexing/__init__.py     # FTSIndex, ChromaVectorIndex
├── retrieval/__init__.py    # HybridRetriever, RetrievalService
└── storage/__init__.py      # Catalog

experiments/benchmark-gold-20260923/
├── evaluate_dev.py          # 开发集评测主脚本
├── find_semantic_alternatives.py  # 语义替代来源发现
└── validate_candidate_v3.py       # 技术验证脚本
```

---

## 10. 下一步建议

### 优先执行

1. **分析失效案例**
   ```bash
   python -c "
   import json
   with open('outputs/gold-v5-dev-exploratory-20260924-01/per_query.jsonl') as f:
       for line in f:
           item = json.loads(line)
           if item['question_id'] == 'rgq-052-zh':
               print(json.dumps(item, indent=2, ensure_ascii=False))
   "
   ```

2. **验证可复现性** - 重跑开发集，比对指纹和指标

3. **规划 V2 索引实验** - 确定资源需求和时间表

### 按需执行

- 如需论文数据：提取开发集指标到 LaTeX 表格
- 如需深入诊断：分析 BM25 的 jieba 分词结果
- 如需对比基线：构建 naive dense-only 索引（无 BM25）

---

## 附录：快速参考命令

### 重跑开发集

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python -u experiments/benchmark-gold-20260923/evaluate_dev.py `
  --candidate-version v5 `
  --output-dir outputs/gold-v5-dev-exploratory-$(Get-Date -Format yyyyMMdd)-02
```

### 验证索引指纹

```python
from ped_knowledge.indexing import FTSIndex
fts = FTSIndex(Path("outputs/knowledge-index-104-v1-20260924-01/fts.sqlite3"))
print(f"Policy: {fts.policy_version()}")
print(f"Tokenizer: {fts.tokenizer_fingerprint()}")
print(f"Analyzer: {fts.lexical_analyzer_fingerprint()}")
```

### 查看失效题

```bash
jq -r 'select(.bge_m3.resource_recall_at_5 == 0) | .question_id' \
  outputs/gold-v5-dev-exploratory-20260924-01/per_query.jsonl
```

---

**报告生成时间**：2026-09-24\
**Catalog 指纹**：`d4a05aa6c6ea72436bc318f71edc74a81f666372be4c4d364988461ffad82535`\
**代码版本**：`d739b75bc2beb3963acc279a0b59b3304b00a857`\
**索引版本**：V1 (104-paper, 2026-09-24-01)\
**Gold 版本**：v5 (2026-09-23-rebuild)
