# P2 实验交付清单

_2026-09-27/28 完成，status: current_

## 产物目录

### 1. 解析对照（步骤 1）

**`outputs/parser-sensitivity-p2-parse-20260927-01/`** (81 MB)

- `summary.json` — 输入哈希、配置、代码版本、解析器/模型版本、运行命令
- `resource_stats.csv` — 104 篇逐篇 child/parent 数量、页跨度、文本层覆盖率、解析耗时
- `page_stats.csv` — 逐页字符统计
- `anchor_locatability.csv` — 38 个锚点在元素级的可定位情况（两种解析器）
- `group_locatability.csv` — 40 个证据组（20 意图 × 最多 2 组）在 child/parent 级的共现情况
- `gold_page_tables.json` — Gold 页上检测到的表格（`find_tables` vs Adobe）
- `manual_review_checklist_template.csv` — 人工核对表模板（未填充，实际判定在 `parse_review_agent_dev.json`）
- `compare/<resource>/` — 11 篇配对样本的逐元素对照：
  - `adobe-document.json` / `pymupdf-document.json` — 两种 CanonicalDocument
  - `adobe-elements.txt` / `pymupdf-elements.txt` — 逐元素文本（1 行 1 元素）
  - `adobe-extract.zip` — 已保存的真实 Adobe 响应（复用，未新调用）

### 2. 检索对照（步骤 2）

**`outputs/parser-sensitivity-p2-retrieval-20260927-01/`** (422 MB，主要是 3 个 Chroma 索引)

- `summary.json` — 输入哈希、三臂配置、检索参数、embedding 指纹、运行命令；内嵌：
  - `metrics_by_arm_method_language` — 18 组汇总指标
  - `reproduction_vs_saved_v1_dev_run` — 与 2026-09-24 V1 运行的对比
  - `unique_text_vector_cache` — 16,160 条唯一文本的缓存向量（三臂共享，消除模型抖动）
- `per_query.jsonl` — 120 行（40 查询 × 3 臂），逐题排名、指标与文本定位
- `paired_tests.csv` — 配对统计（128 行：2 臂 × 3 方法 × 7 指标 × 3 语言维度）
- `parse_log.csv` — 104 篇解析耗时（PyMuPDF 365.8 s，Adobe 重解析 18.6 s）
- `indexes/<arm>/` — 三个隔离索引（`catalog_mixed` / `pymupdf_all` / `pymupdf_dev_targets`）：
  - `fts.sqlite3` — FTS5 BM25 索引
  - `chroma/` — BGE-M3 向量索引（Chroma 持久化目录）
  - `child_chunks.jsonl` — child chunks（6,336 / 10,564 / 6,751 行）

### 3. 综合汇总（步骤 3）

**`outputs/parser-sensitivity-p2-synthesis-20260927-01/`** (84 KB)

- `summary.json` — 变化题数、判定分布、headline 指标、输入哈希
- `per_pdf_parse_diff.csv` — 12 篇逐篇解析差异（元素数、chunk 数、判定标签）
- `per_query_retrieval_diff.csv` — 120 行逐题三臂指标对比（标记 `changed` 行）
- `failure_cases.md` — 44 / 120 个变化行的中文失败案例表格

## 实验脚本与输入

**`experiments/benchmark-parser-sensitivity-20260927/`**

| 文件 | 说明 |
| --- | --- |
| `README.md` | 完整实验说明（研究问题、结论、方法、限制、证据等级） |
| `parse_review_agent_dev.json` | 12 篇 × 6 维度的解析质量核对表（agent 标签，`human_verified=false`） |
| `evidence_anchors_dev.json` | 38 个锚点（20 意图的证据文本，经原 PDF 验证） |
| `parse_review.py` | 步骤 1 入口：解析对照 |
| `retrieval_eval.py` | 步骤 2 入口：三臂隔离检索 |
| `synthesize.py` | 步骤 3 入口：综合两步产物 |
| `p2_common.py` | 共享工具（chunk 指纹、配对检验、锚点归一化） |
| `test_p2.py` | 7 个单元测试（全部通过） |
| `DELIVERABLES.md` | 本文件 |

## 复现命令

```powershell
# 环境
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"

# 步骤 1：解析对照（输入：已保存 Adobe ZIP + 原 PDF）
.\.venv\Scripts\python experiments/benchmark-parser-sensitivity-20260927/parse_review.py `
  --output-dir outputs/parser-sensitivity-p2-parse-20260927-01

# 步骤 2：检索对照（输入：步骤 1 的解析日志 + 40 条开发集查询）
.\.venv\Scripts\python -u experiments/benchmark-parser-sensitivity-20260927/retrieval_eval.py `
  --output-dir outputs/parser-sensitivity-p2-retrieval-20260927-01

# 步骤 3：综合汇总（输入：步骤 1+2 的产物 + 核对表）
.\.venv\Scripts\python experiments/benchmark-parser-sensitivity-20260927/synthesize.py `
  --parse-dir outputs/parser-sensitivity-p2-parse-20260927-01 `
  --retrieval-dir outputs/parser-sensitivity-p2-retrieval-20260927-01 `
  --output-dir outputs/parser-sensitivity-p2-synthesis-20260927-01

# 测试
.\.venv\Scripts\python -m pytest experiments/benchmark-parser-sensitivity-20260927/test_p2.py -v
```

## 核心结论（摘自 README.md）

| 问题 | 回答 |
| --- | --- |
| 解析器选择是否影响资源级证据召回？ | **基本不影响**（配对差异 0.00 ~ −0.05，p=1.0） |
| 是否影响页级定位？ | **小幅下降**（−0.05 ~ −0.075，p≥0.25） |
| 是否影响证据文本可定位性？ | **一致下降且方向单一**（−0.15 ~ −0.20，全部 5 个不一致意图都是 Adobe 优于 PyMuPDF，p=0.0625） |
| MRR / nDCG@5 | **噪声主导，无方向性**（区间跨 0，p≥0.18） |

**判断：解析器选择不改变"找到哪篇文献"，但改变"能否在该文献的正确页上定位到证据原文"。**

## 证据等级

- ✅ **真实运行**：PyMuPDF 本地解析 + 已保存的真实 Adobe 响应重解析 + BGE-M3 本地权重
- ✅ **真实计算**：`catalog_mixed` 臂的 chunk 指纹与 V1 build report 逐字节一致
- ⚠️ **agent 静态核对**：12 篇 × 6 维判定，`human_verified=false`
- ❌ **未运行**：`rgq-108` 文献无 Adobe 输出（授权待确认）
- ❌ **未验证**：104 篇全语料收益（仅 12 篇证据文献参与评测）

## 未激活的改动

本实验**不**修改或覆盖：

- 当前 Catalog（仍保持 102 Adobe + 2 PyMuPDF 混合）
- V1/V2 索引与 P0–P1 结果
- 任何模块的默认解析策略
- Knowledge-Base 的共享契约（实验代码只新增，未改动既有接口）

## 归档说明

- 三个 `outputs/parser-sensitivity-p2-*/` 目录已完整生成，总计约 503 MB
- 每个 `summary.json` 记录输入哈希与代码版本（Git HEAD + 逐文件 SHA-256）
- 实验目录代码（`experiments/benchmark-parser-sensitivity-20260927/`）已纳入版本控制
- 中间临时文件（`/tmp/p2/`、`C:\Users\11315\AppData\Local\Temp\p2\`）可删除
- Chroma 索引（约 380 MB）可压缩归档；`summary.json` 的向量缓存（68 MB）重建需约 78 s
