# Knowledge-Base

_知识与证据科研模块的当前边界与本地配置入口 · status: current_

知识与证据科研模块，围绕行人流与疏散交通文献研究 RAG：PDF 解析、层次化切块、
BM25 与 BGE-M3 检索、RRF 融合、可选重排，以及面向 Agent 的可定位证据输出。

## RAG 研究链路

`PDF → CanonicalDocument → parent/child chunks → FTS5/BM25 + BGE-M3/Chroma → RRF → 可选 Rerank → EvidenceItem → Gold 评测`。
对照实验固定语料与题集，分别比较切块策略、词法分析器、稀疏/稠密检索、融合和重排；
记录模型权重、tokenizer、索引与代码版本。Agent 的答案生成和引用质量在下游单独评价。

| 环节 | 当前实现或配置 | 实验关注点 |
| --- | --- | --- |
| 解析 | Adobe PDF Extract；可显式选择 PyMuPDF | 阅读顺序、表格和证据页定位 |
| 切块 | `parent-child-v1` 默认；`v2` 候选 | 长度、边界、父上下文与召回 |
| 词法检索 | `EnglishLexicalAnalyzer`（`english-lexical-v1`）+ FTS5/BM25 | 英文术语、数值与精确标识符 |
| 稠密检索 | BGE-M3、1024 维、Chroma 配置 | 语义召回与跨语言差异 |
| 融合/重排 | RRF；可选 FlagEmbedding Cross-Encoder 适配器 | 排名增益、延迟和降级情况 |

## 边界

- 只依赖 `ped_contracts` 的共享证据契约，不依赖 Agent 或产品后端。
- `governance/` 保存离线语料统计和旧精选规则；不参与在线检索门禁。准备表
  [`manifest_readiness_2026-09-23.csv`](../memPed/knowledge/literature/records/manifest_readiness_2026-09-23.csv)
  是历史输入快照，不代替当前语料与索引指纹。
- `IngestionManifest.include=true` 激活后产生 `approved/official` 检索状态；该状态
  只表示检索资格，不代表证据质量。实验质量通过逐题指标和来源定位报告。
- 正式数据、数据库、模型权重写入 `memPed/knowledge/`；实验索引与评测报告写入 `outputs/`；均不提交 Git。
- Embedding、OCR 和 Rerank 通过协议或实验适配器提供。

完整的数据目录、权威资产与可重建资产边界见 [`../memPed/README.md`](../memPed/README.md)。当前模块提供 Python API 和测试，但没有稳定的 `ped-agent library` 命令行入口。

## 目录

```text
Knowledge-Base/
├── src/ped_knowledge/
│   ├── contracts/
│   ├── governance/
│   ├── ingestion/
│   ├── parsing/
│   ├── chunking/
│   ├── tokenization/
│   ├── storage/
│   ├── indexing/
│   ├── retrieval/
│   ├── reranking/
│   └── evaluation/
├── config/
│   ├── embeddings/
│   └── retrieval/
└── tests/
```

## RAG 分词与切块状态

| 能力 | 当前基线 | V2 候选 |
|---|---|---|
| Chunk policy | `parent-child-v1`，兼容原正则计数 | `parent-child-v2`，BGE-M3 tokenizer 计数 |
| 边界 | 固定 token 窗口 | 元素、段落、双语句子、超长原子单元 token 回退 |
| Child 预算 | target 320、max 450、overlap 48 | 同一预算，强制 `token_count <= 450` |
| 发布状态 | 默认行为 | candidate，尚未替换当前基线 |

V2 策略保存在
[`config/retrieval/chunking-v2.yaml`](config/retrieval/chunking-v2.yaml)。

词法检索只使用英文分析器 `EnglishLexicalAnalyzer`（NFKC、小写、`[a-z]+|[0-9]+`，不去停用词、不做词干），
配置见 [`config/retrieval/lexical-english-v1.yaml`](config/retrieval/lexical-english-v1.yaml)；`FTSIndex`
未传入分析器时默认使用它，查询 OR 召回并校验分析器指纹。2026-10-07 起 jieba 分析器、中英领域词表和停用词已从
代码、配置和依赖中移除；用 jieba 构建的旧 FTS 索引因指纹不匹配会被拒绝读取。Chunk 记录包含 tokenizer
指纹、token 数、父文本字符偏移和 `hard_split` 标记。Catalog 按 `policy_version` 并存 V1/V2，
索引构建记录 policy、tokenizer、词法分析器、模型和实验来源指纹，读取时拒绝不匹配的候选。

## PEARL 当前评价与历史 Gold

当前评价框架为 [PEARL Layer 1](../paper/pearl-framework/layer-1-retrieval/README.md)。本轮固定 106 篇 Adobe-only 英文文献、6,433 个 child，使用 [80 题开发 Gold 与 200 题封存评估 Gold](../experiments/pearl-dataset-80-200-20261003/README.md)（规范位置 `memPed/knowledge/gold/pearl-adobe106/`，使用规则见 [评测规范](../experiments/EVALUATION-STANDARD.md)）。[80 题四方法开发实验](../experiments/pearl-retrieval-dev80-20261003/README.md)单独记录真实运行、实际 child 盲审、统一计分及开发分析；200 题不用于开发；200 题独立评价见[阶段 D 分析](../experiments/pearl-retrieval-eval200-20261003/evaluation-analysis-2026-10-03.md)，切片策略研究见[切片实验入口](../experiments/pearl-chunking-dev80-20261005/README.md)，全部 RAG 产物分类见 [RAG 资产与一致性审计](../docs/rag-asset-audit-2026-10-07.md)。下列 Gold v5、Stage 和旧索引记录属于 historical，不进入 PEARL 的题集、基线、分母或评分。

**历史评测集**：`memPed/knowledge/gold/2026-09-23-rebuild/` v5 版本
- **280 query variants**：120 可回答 + 20 拒答意图，各含中英双语问法
- **划分**：20 development / 100 test (sealed) / 20 refusal
- **证据标注**：页级定位，AND/OR 证据组，PDF SHA-256 映射
- **AI 审查**：120 题×104 文献词法/语义替代来源检索，360 个 BGE-M3 top-100 候选已复核
- **开发集评测**：已完成（`failed/outputs-void-scores/gold-v5-dev-exploratory-20260924-01/`，旧评分口径已作废），BM25/BGE-M3/RRF
- **Stage 1 离线重分析（已作废）**：脚本保存在 [`failed/stage1-analysis/`](../failed/stage1-analysis/)，旧资源召回口径不属于 PEARL child 内容支持评价。
- **Stage 2 答案标注与复核**：见 [`experiments/stage2-annotation`](../experiments/stage2-annotation/README.md)，20 个开发意图、40 条双语查询；原始 v1 参考答案保持空值。2026-09-27 独立子 agent 完成 20 题 PDF 复核，新版包的 20 题均可用于开发集研究，其中 18 题有 agent 候选答案、2 题带争议说明。全部 `human_verified=false`；人工 Gold 审查不是当前研究门槛。
- **2026-09-26 独立候选对照**：V2 的 104 篇独立 FTS/BGE-M3 索引见 `outputs/knowledge-index-104-v2-candidate-20260926-02/`（7,884 个 child chunks）；固定词表的 V1 chunks 独立 FTS 见 `outputs/knowledge-index-104-v1-lexical-candidate-20260926-01/`。开发集逐题合成保存在 `failed/outputs-void-scores/gold-v5-dev-p1-synthesis-20260926-03/`（2026-09-29 迁出，旧评分口径已作废）。V2 中文 Dense/RRF 完整证据@5 为 17/20，V1 为 19/20；固定词表候选未改善开发集汇总。标签仍未获领域人工核验，V2 不作为默认或已发布基线。Cross-Encoder 因无固定本地权重未运行。

**历史问题集**：`pilot_gold.jsonl`（31题）和 `core_gold.jsonl` 的资源 ID 与当前 104 资源 Catalog 不匹配，已被 v5 重构替代。

**历史评分实现**：`ped_knowledge.evaluation.gold_v2` 提供旧证据组评分、精确定位、中英配对差异和拒答标签验证。PEARL 的实际 child 支持组合、CEGR、BestGroupCov 和 CompleteMRR 使用独立实验评分入口，不继承旧评分结果。

## BGE-M3 本地配置与索引位置

BGE-M3 的固定参数和复现命令见 [`config/embeddings/bge-m3/README.md`](config/embeddings/bge-m3/README.md)。
- **模型权重**：`memPed/knowledge/models/bge-m3/` ✅
- **实验索引**：`outputs/knowledge-index-<corpus>-<version>-<date>-<seq>/chroma/` ✅
  - PEARL 当前冻结索引：`outputs/pearl-index-106-adobe-20260929-01/`（106 篇 Adobe-only、6,433 child）
  - 旧 V1 历史索引记录：`outputs/knowledge-index-104-v1-20260924-01/`，不进入 PEARL
  - 向量维度 1024，CUDA/FP16

实验索引独立命名并保存在 `outputs/` 目录，不在 `memPed/knowledge/indexes/` 下常驻，以支持多版本索引并存和实验可复现性。两者均不提交 Git。

通用建库与核验脚本：`python Knowledge-Base/build_indexes.py --output-dir outputs/knowledge-index-<corpus>-<version>-<date>-<seq>`，`python Knowledge-Base/verify_indexes.py --index-dir <同一目录>`。输出目录必须不存在，脚本不会覆盖已有索引。

## PDF 默认解析：Adobe PDF Extract

`ImportService(paths)` 默认使用 `adobe-pdf-extract-v1`，通过 Adobe API 解析 PDF。SDK `pdfservices-sdk==4.2.0` 是模块依赖。正式导入会将所选 PDF 上传到 Adobe 云端，因此只导入允许上传的文献。需要完全本地解析时，显式使用 `ImportService(paths, parser_backend="pymupdf")`，对应 `pymupdf-structured-v2`。Adobe 调用失败会使该文献导入失败，不会自动改用 PyMuPDF。

PyMuPDF 解析报告中的 `manual_review_pages` 是空文本页告警；实验报告统计其数量及
对证据定位的影响。

本地凭据有两种配置方式：设置 `PDF_SERVICES_CLIENT_ID` 和 `PDF_SERVICES_CLIENT_SECRET` 环境变量，或将 Adobe 下载包中的 `pdfservices-api-credentials.json` 放在 `Knowledge-Base/local/`。该目录被 Git 忽略，凭据不应提交。缺少凭据时默认导入会报错；可显式选择 `parser_backend="pymupdf"` 运行本地解析。

先做独立对照，避免改变已有 Catalog、索引或派生产物：

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python -m ped_knowledge.parsing.compare "路径\文献.pdf" --output "outputs\adobe-compare-唯一名称" --resource-id paper-id
```

输出目录必须不存在。`comparison.json` 记录原文与 Adobe 响应 SHA-256、解析器版本及元素/图表数量；`*-elements.txt`、`*-tables.json` 用于定位阅读顺序与表格差异，`adobe-extract.zip` 保留原始响应。命令不修改 Catalog 或索引；数量差异不能单独代表解析准确率。

正式导入时，Adobe 原始 ZIP 和图表附件存入 `memPed/knowledge/derived/<resource-id>/<sha>/adobe/`；Catalog 记录解析器版本和派生文件哈希。已有相同 SHA-256 活动版本的文献会按既有规则跳过。PEARL 语料的 106 篇 Adobe 解析结果见 [106 篇 Adobe-only 索引实验](../experiments/pearl-index-106-adobe-20260929/README.md)，与 PyMuPDF 的配对对照见 [解析器敏感性实验](../experiments/benchmark-parser-sensitivity-20260927/README.md)；解析效果只以这些独立实验报告为准。
