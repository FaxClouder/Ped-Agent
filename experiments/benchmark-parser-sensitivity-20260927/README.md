# PDF 解析器敏感性实验（P2）

_PyMuPDF 与 Adobe PDF Extract 在同一语料、切块、检索与题集下的配对对照 · status: current_

## 研究问题

在相同 PDF、切块策略（`parent-child-v1`）、tokenizer、embedding、检索参数和开发集题目下，
PyMuPDF 与 Adobe PDF Extract 的解析差异是否会改变**可用证据**、**页级定位**和**检索效果**？

判断不依据解析出的元素数或表格数。数量差异只作描述，结论以阅读顺序核对、证据文本可定位性
和逐题检索指标为准。

## 结论摘要

| 问题 | 回答 |
| --- | --- |
| 解析器选择是否影响当前核心 RAG 指标（资源级证据召回）？ | **基本不影响。** 20 意图开发集上 `complete_evidence@5` 的配对差异为 0.00（BM25/英文、RRF/英文）到 −0.05（中文，1 题翻转），符号检验 p=1.0。 |
| 是否影响页级定位？ | **小幅下降。** `complete_locator@5` 配对差异 −0.05 ~ −0.075，2~3 题翻转，p≥0.25。 |
| 是否影响**证据文本**可定位性？ | **一致下降，且方向单一。** `complete_text_locator@5` 配对差异 −0.15 ~ −0.20；全部 5 个不一致意图都是 Adobe 优于 PyMuPDF，0 个反向；p=0.0625（5 个不一致对的精确符号检验最小可达值）。 |
| MRR / nDCG@5 | **噪声主导，无方向性。** 例如 `pymupdf_dev_targets/rrf` 的 MRR 为 +0.085（7 改善 / 2 变差，p=0.18）；`pymupdf_all/bge_m3` 中文 MRR +0.036（4/4，p=1.0）。不构成解析器优劣证据。 |

核心判断：**解析器选择不改变"找到哪篇文献"，但改变"能否在该文献的正确页上定位到证据原文"。**
资源级指标（论文当前主要汇报的口径）对解析器不敏感；页级与文本级证据定位对解析器敏感。

## 语料现状（实验前核对）

当前 Catalog 的 104 个活动版本**混用两种解析来源**：102 篇 `adobe-pdf-extract-v1`，
2 篇 `pymupdf-structured-v2`（`lit-10-1016-j-trc-2024-104762`、`lit-10-1016-j-trc-2024-104763`；
2026-09-24 Adobe 多次 `ConnectionError`/`SSLError` 后改用本地解析，见
[`core-adobe-import-status-2026-09-24.md`](../../memPed/knowledge/reports/core-adobe-import-status-2026-09-24.md)）。
因此 V1/V2 索引与 P0–P1 结果**不能**当作解析器对照：它们都建立在这一混合语料上。本实验新建隔离索引。

102 篇的 Adobe 原始响应 ZIP 已存于 `memPed/knowledge/derived/<resource-id>/<sha>/adobe/extract.zip`。
本实验**复用这些已保存的真实响应，未发起任何新的 Adobe 调用**，因此没有新的 PDF 上传。

## 配对样本（仅开发集）

20 个开发意图的证据涉及 12 篇 PDF。11 篇构成配对样本（有已保存 Adobe 响应），覆盖：

| 案例类型 | 文献 |
| --- | --- |
| 扫描页 + 内嵌 OCR 文本层 | `lit-10-1103-physreve-51-4282`（1995 PRE，5 页全部 `is_scanned=true`） |
| 双栏正文 | `lit-10-1016-j-ssci-2020-104760` p12、`lit-10-1016-j-tbs-2020-10-007` |
| 无框统计表格 | `lit-10-1016-j-ssci-2020-105121` Table 3、`lit-10-1016-j-ssci-2023-106243` Table 4 |
| 跨页双证据组 + 页间重复文本 | `rgq-122`（p5 表格 + p9 附录，两页含同一句 58%/38%） |
| 公式页（P1 已知定位困难） | `lit-10-1016-j-trc-2018-03-027` p4–6（`rgq-015` 仍为 `agent_disputed`） |
| 数学符号密集正文 | `b3-14` p13 |

`lit-10-1016-j-trc-2024-104763`（`rgq-108`）**无 Adobe 输出**：Adobe 导入历史性失败，且
`rights_status=pending`（[`manifest_readiness_2026-09-23.csv`](../../memPed/knowledge/literature/records/manifest_readiness_2026-09-23.csv)
104 篇全部 pending），未确认上传授权，故不上传。该篇在所有实验臂中解析器恒定，已在
`summary.json` 的 `parser_constant_dev_resources` 标记。

**只使用开发集。** 100 个 sealed test intent 与 20 个拒答 intent 未被读取、未用于选样或调参。

### 跨解析器核对基准：原 PDF 页码 + 证据原文

不同解析器生成的 `element_id` 不可比较（两者都是内容哈希，输入不同必然不同）。
本实验以**原 PDF 页码 + 从原文逐字摘录的锚点文本**作为核对基准，定义在
[`evidence_anchors_dev.json`](evidence_anchors_dev.json)（38 个锚点，全部经原 PDF 文本层验证命中标注页；
表格与扫描页另经渲染页图核对）。归一化为 NFKC + casefold + 仅保留 ASCII 字母数字与 `.%`，
使连字符换行、ligature、数学字体和空白差异不影响匹配。列表型锚点要求各部分在**同一文本片段内共现**
（用于表格行列关系，如 `["logistic regression models predicting risk behaviors","3.43","1.28","9.21"]`）。

## 步骤 1：解析质量对照

复用 `ped_knowledge.parsing.compare.write_comparison`，输入为已保存的 Adobe ZIP：

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python experiments/benchmark-parser-sensitivity-20260927/parse_review.py --output-dir outputs/parser-sensitivity-p2-parse-新编号
```

产物：`outputs/parser-sensitivity-p2-parse-20260927-01/`。`compare/<resource>/` 为两种
CanonicalDocument 的逐元素文本、表格与原始 Adobe 响应；`anchor_locatability.csv` 和
`group_locatability.csv` 记录每个锚点在元素/child/parent 中的可定位情况。
11 篇的 Adobe 重解析结果与 Catalog 中已保存的 `document.json` **逐字节一致**
（`adobe_reparse_equals_catalog_document=true`），即对照材料与活动语料同源。

### 逐篇人工/agent 核对结论

完整核对表见 [`parse_review_agent_dev.json`](parse_review_agent_dev.json)（12 篇 × 6 个维度，
`human_verified=false`，标签来源为本会话 agent 核对）。判定分布：

| 维度 | same | adobe_better | not_applicable |
| --- | ---: | ---: | ---: |
| 阅读顺序 | 8 | 3 | 1 |
| 文字缺失/重复 | 6 | 5 | 1 |
| 表格行列关系 | 2 | 5 | 5 |
| 页码 | 11 | 0 | 1 |
| 关键数值与单位 | 4 | 1 | 7 |
| Gold 证据可定位 | 8 | 3 | 1 |

**没有任何维度判为 `pymupdf_better`。** 关键机制：

1. **PyMuPDF 标题过度识别 → 父块碎片化。** 字号启发式把大量正文判为 heading
   （`apm-2019` 140 vs Adobe 19；`trb-2020` 183 vs 36；`physreve` 59 vs 6；`pone` 83 vs 25）。
   `parent-child-v1` 在每个 heading 处切新父块，导致 PyMuPDF 父块数量远多、长度远短
   （`apm-2019`：138 父块 / 中位 38 token，Adobe：21 父块 / 中位 304 token）。
   这是解析器影响切块的主要路径，也是全语料 child chunk 数 10,564 vs 6,336 的来源。
2. **双栏阅读顺序交错。** `get_text(sort=True)` 按垂直位置排序，在双栏页交错左右栏：
   `ssci-2020-104760` p12 的右栏编号条目被插入左栏段落之间。
3. **右栏 References 提前终止解析 → 真实内容丢失。** `tbs-2020-10-007` p11 的右栏
   "References" 块排序早于左栏下半部，PyMuPDF 在此停止收录，**整个 "5. Conclusion" 三段丢失**；
   Adobe 保留。该页不是 Gold 页，但属实质缺失。
4. **无框表格行列关系丢失。** `find_tables` 未识别 `ssci-105121` Table 3 与
   `ssci-2023` Table 4：单元格变成逐行独立段落，列头（`Model 2: Filming`）与数值
   （`3.43`）落在不同元素，仅凭文本无法判定 3.43 属于哪个模型。Adobe 保留
   `['Odds ratio','1.89','3.43*','0.17*']` 行结构。同时 PyMuPDF 在有框表格上**重复**
   输出文本（块文本 + `find_tables`，`s41598` p13 重复小数 32 个 vs Adobe 5 个）。
5. **参考文献误入索引。** PyMuPDF 未识别非独立块的 References 标题（`s41598`、`ssci-2023`），
   索引了约 29 / 24 条文献条目；Adobe 在 11 篇配对样本上全部在 References 处停止。
6. **Adobe 对扫描页重做 OCR 并修正文本层错误。** `physreve-51-4282`：
   `reQecting`→`reflecting`、`coinpared`→`compared`、`trafj%c`→`traffic`。
   因此"文本层覆盖率"指标在扫描 PDF 上**系统性偏向 PyMuPDF**（该指标以 PDF 内嵌文本层为基准，
   而 PyMuPDF 正是读取该层），不能解读为 Adobe 丢字。
7. **页码一致。** 12 篇的全部 Gold 锚点都被两种解析器定位在标注的原 PDF 页上，
   `page_numbers` 维度 11 same / 1 n.a.，无页码偏移。

## 步骤 2：下游隔离检索对照

三个实验臂，**只改变解析器**，其余全部固定（104 篇同一语料、`parent-child-v1`、
`regex-token-v1`、基础 jieba 分析器、BGE-M3 1024 维 fp16/CUDA、`recall_limit=40`、
`k=5` 去重资源、`rrf_k=60`、同一 40 条开发集查询）：

| 臂 | 解析来源 | child chunks |
| --- | --- | ---: |
| `catalog_mixed` | 102 Adobe + 2 PyMuPDF（等同当前 Catalog） | 6,336 |
| `pymupdf_all` | 104 篇全部 PyMuPDF | 10,564 |
| `pymupdf_dev_targets` | 11 篇开发集证据文献换 PyMuPDF，其余保持 Catalog 解析 | 6,751 |

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python -u experiments/benchmark-parser-sensitivity-20260927/retrieval_eval.py --output-dir outputs/parser-sensitivity-p2-retrieval-新编号
.\.venv\Scripts\python experiments/benchmark-parser-sensitivity-20260927/synthesize.py --parse-dir outputs/parser-sensitivity-p2-parse-20260927-01 --retrieval-dir outputs/parser-sensitivity-p2-retrieval-20260927-01 --output-dir outputs/parser-sensitivity-p2-synthesis-新编号
```

（已执行的运行是在本实验目录内调用的，`summary.json` 的 `command` 字段因此记录了相对路径
`../../outputs/...`；目录内容与从仓库根运行一致。）

**基线有效性**：`catalog_mixed` 臂重建的 chunk 指纹为
`d4a05aa6c6ea72436bc318f71edc74a81f666372be4c4d364988461ffad82535`，与
`outputs/knowledge-index-104-v1-20260924-01/build_report.json` 的 `catalog_fingerprint`
完全一致，即该臂逐字符复现了 V1 Catalog 的 6,336 个 child chunk。

**向量可比性**：每条唯一文本只 embedding 一次（16,160 条，77.7 s），三臂共享的 chunk 与
全部查询得到逐位相同的向量，排除了模型抖动被误读为解析器差异。

### 指标定义（新增文本级定位）

现有 `gold_v2` 的 `complete_locator@5` 只要求"命中资源的某个 chunk 页范围覆盖标注页"。
由于 PyMuPDF 的父块更碎、页跨度不同，页范围覆盖会**高估**定位质量。本实验增加三个
解析器中立的文本级指标（定义在 `retrieval_eval.text_locator_metrics`）：

- `complete_text_locator@5`：每个证据组都有一个 child **同时**覆盖标注页且包含**全部**必需锚点。
- `complete_split_text_locator@5`：放宽为每个锚点各自落在某个 Gold 页 child（允许跨 child 拼装）。
- `complete_parent_text_locator@5`：在父上下文文本中检查（Agent 实际读到的窗口）。

### 汇总指标（20 意图，按语言分列）

| 臂 / 方法 | 语言 | 证据@5 | 页定位@5 | 文本定位@5 | 父块文本定位@5 | MRR | nDCG@5 | 命中页 chunk 平均页跨度 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| catalog_mixed / RRF | en | 1.00 | 1.00 | **1.00** | 1.00 | 0.942 | 0.957 | 1.38 |
| pymupdf_all / RRF | en | 1.00 | 0.95 | **0.85** | 0.85 | 1.000 | 1.000 | 1.71 |
| pymupdf_dev_targets / RRF | en | 1.00 | 0.95 | **0.85** | 0.85 | 0.975 | 0.982 | 1.71 |
| catalog_mixed / RRF | zh | 0.95 | 0.95 | **0.90** | 0.95 | 0.739 | 0.792 | 1.50 |
| pymupdf_all / RRF | zh | 0.90 | 0.90 | **0.75** | 0.75 | 0.767 | 0.801 | 1.86 |
| pymupdf_dev_targets / RRF | zh | 0.95 | 0.90 | **0.75** | 0.75 | 0.875 | 0.895 | 1.81 |
| catalog_mixed / BGE-M3 | en | 1.00 | 1.00 | 1.00 | 1.00 | 0.963 | 0.972 | 1.43 |
| pymupdf_all / BGE-M3 | en | 1.00 | 0.90 | 0.80 | 0.80 | 0.950 | 0.963 | 1.69 |
| catalog_mixed / BM25 | en | 0.95 | 0.95 | 0.95 | 0.95 | 0.950 | 0.950 | 1.45 |
| pymupdf_all / BM25 | en | 0.95 | 0.95 | 0.80 | 0.85 | 0.888 | 0.903 | 1.71 |
| 任一臂 / BM25 | zh | 0.00 | 0.00 | 0.00 | 0.00 | 0.000 | 0.000 | — |

完整 18 组见 `summary.json` 的 `metrics_by_arm_method_language`。

BM25 中文在三臂全部为 0：语料全英文而查询为中文，jieba 切出的中文词在英文倒排索引中无命中。
这是 **P0/P1 已记录的语言不对称**，与解析器无关，也说明 BM25 中文一路无法用于解析器对照。

### 配对统计（意图为单位）

`paired_tests.csv` 给出每个臂 × 方法 × 指标 × 语言的配对差值、意图级 bootstrap 95% 区间
（`bootstrap_seed=20260927`，10,000 次重抽）和不一致对的精确符号检验。中英合并行的要点：

| 臂 / 方法 | 指标 | 配对差值 | bootstrap 95% | 改善/变差 | 符号检验 p |
| --- | --- | ---: | --- | ---: | ---: |
| pymupdf_all / RRF | complete_evidence@5 | −0.025 | [−0.075, 0.000] | 0 / 1 | 1.000 |
| pymupdf_all / RRF | complete_locator@5 | −0.050 | [−0.125, 0.000] | 0 / 2 | 0.500 |
| pymupdf_all / RRF | **complete_text_locator@5** | **−0.150** | [−0.300, −0.025] | **0 / 4** | 0.125 |
| pymupdf_all / BGE-M3 | **complete_text_locator@5** | **−0.175** | [−0.325, −0.050] | **0 / 5** | 0.0625 |
| pymupdf_all / BGE-M3 | **complete_parent_text_locator@5** | **−0.200** | [−0.375, −0.050] | **0 / 5** | 0.0625 |
| pymupdf_dev_targets / RRF | MRR | +0.085 | [+0.008, +0.167] | 7 / 2 | 0.180 |
| pymupdf_all / BGE-M3 | MRR | +0.012 | [−0.081, +0.105] | 4 / 4 | 1.000 |

文本定位的 bootstrap 区间不含 0，且**所有不一致意图方向一致（0 改善 / 4~5 变差）**；
p=0.0625 是 5 个不一致对时精确符号检验能达到的最小值，即样本量本身限制了显著性，
不是效应方向存在争议。资源级证据召回与 MRR/nDCG 的区间跨 0，符号检验 p≥0.18，无方向性结论。

### 逐题失败案例与机制

`outputs/parser-sensitivity-p2-synthesis-20260927-01/failure_cases.md` 列出 44 / 120 个
（题×方法）行发生变化。文本定位翻转的意图分两类机制——这一区分来自**与检索无关的**
解析级共现检查（`group_locatability.csv`）：

**A 类：真实解析缺陷**（PyMuPDF 在 Gold 页的任何 child 中都无法共现必需文本）

| 意图 | 机制 |
| --- | --- |
| `rgq-139` | `ssci-105121` Table 3 无框：PyMuPDF 下表题元素与 `3.43/(1.28–9.21)` 数值元素分离，任何 child 与 parent 都不共现（`(False,False,False)`）。Adobe 全部共现。 |
| `rgq-122` g2 | `ssci-2023` p9 附录：PyMuPDF 把 `Q1: What was your psychological state...` 判为 heading 从而切开父块，问题文本与其 58%/38% 答案落入不同父块。p9 与 p5 含同一句 58%/38%，故该锚点必须靠问题文本区分页面。 |
| `rgq-136` | `ssci-104760` p12 双栏交错：两个锚点在同一 1.3k 字符段落内，但 PyMuPDF 的 child 窗口把它们切开（`all_required_in_one_gold_child=False`，parent 仍共现 `True`）。 |

**B 类：排名竞争效应**（文本在 PyMuPDF 下可共现，但 Gold 页 chunk 未进入召回窗口）

| 意图 | 机制 |
| --- | --- |
| `rgq-052` | 基线中 Gold 页 chunk 本就排在第 35 位（top-40 边缘）；PyMuPDF 臂该资源 chunk 数增加，竞争加剧后掉出 top-40。资源名次仍为 1、证据@5 仍为 1。 |
| `rgq-005` | 中文查询下 Gold 资源名次由 4 掉到 20/15，跌出 k=5 窗口（扫描件 PyMuPDF 侧保留 OCR 错字，影响稠密表征）。 |
| `rgq-025` | BM25/英文：共现成立，仅排名变化导致 Gold 页 chunk 未进召回窗口。 |

值得单独记录的口径问题：`rgq-052-en`（BGE-M3）在 `pymupdf_all` 下 `complete_evidence@5=1`、
资源名次=1，但 `complete_locator@5=0`、文本定位=0。**资源级指标显示"成功"，而该资源被召回的
chunk 并不覆盖证据页。** 这说明只汇报资源级召回会高估证据可用性。

### 运行限制与失败案例（实验本身）

- **稠密检索存在跑间抖动。** 与 2026-09-24 保存的 V1 开发集运行对比：BM25 的 top-40
  chunk 列表 40/40 完全一致；BGE-M3 仅 9/40、RRF 10/40 完全一致，但**三种方法的 40/40
  逐题指标全部一致**。另用一次独立预运行与本次记录运行对比，`pymupdf_all` 有 1/40 题
  （`rgq-067-zh`）的页定位与文本定位翻转，top-5 资源相同——Gold 页 chunk 在 top-40 边缘进出。
  据此，20 意图比率的跑间不确定度约 ±0.05。上表中 −0.15 ~ −0.20 的文本定位差异大于该噪声，
  而 −0.025 ~ −0.05 的证据/页定位差异与噪声同量级，**不应据后者断言方向**。
- **Cross-Encoder 未运行**：无固定版本的本地 reranker 权重。
- **Adobe 未新调用**：`rights_status` 全部 `pending`，仅复用已保存响应；`rgq-108` 对应文献无
  Adobe 输出，保留可执行方案（凭据 + 授权确认后运行 `parse_review.py` 即可纳入配对）。
- **未采集逐题延迟**：本实验只比较解析器，未重复 P1 的延迟与上下文成本测量。
- **解析耗时**（供成本参考，`parse_log.csv`）：104 篇 PyMuPDF 本地解析合计 365.8 s；
  Catalog 侧合计 18.6 s，但那是**复用已保存 ZIP 的重解析**（主要是 JSON 解码），
  **不代表 Adobe API 调用成本**。2026-09-24 的真实 Adobe 调用共 104 篇，首轮 7 篇失败、
  需多轮重试，最终 2 篇始终失败，是有外部依赖、网络失败率和云端上传的操作。
  因此本实验的耗时数字不能用于"Adobe 比 PyMuPDF 快"这类结论。

## 统计与适用范围限制

- 样本为 **20 个开发意图 / 12 篇 PDF**，其中 11 篇构成解析器配对。**不是 104 篇全语料的系统结论。**
  `pymupdf_all` 臂虽重建了全部 104 篇的索引，但评测题目仍只覆盖这 12 篇的证据；其余 92 篇
  只作为干扰项影响排名竞争。
- 标签来源为 `outputs/stage2-agent-adjudicated-20260927-03/`（agent 复核），
  `human_verified=false`；`rgq-015` 与 `rgq-122` 仍带争议说明。**不称为正式 Gold。**
- 中英问法按一个 intent 统计；40 条查询不是 40 个独立样本。
- 结论**不**激活新的默认解析策略，不修改 Catalog、V1/V2 索引与 P0–P1 结果。

## 证据等级声明

| 结论 | 依据 |
| --- | --- |
| 两种 CanonicalDocument 的逐篇差异、阅读顺序、表格行列、锚点可定位性 | **真实解析运行**（PyMuPDF 本地执行 + 已保存的真实 Adobe 响应重解析，与 Catalog 逐字节一致） |
| 三臂 FTS5/BM25 与 BGE-M3 索引、逐题检索指标 | **真实模型运行**（BGE-M3 本地权重、CUDA/fp16、RTX 3080，权重哈希与 V1 一致） |
| `catalog_mixed` 复现 V1 Catalog chunk | **真实计算**（指纹与 V1 build report 一致） |
| 逐篇核对表的 6 维判定 | **agent 静态核对**（读取两种解析输出 + 原 PDF 文本层 + 渲染页图），`human_verified=false` |
| Adobe 在 `rgq-108` 文献上的表现 | **未运行**，无法评估 |
| Adobe API 调用成本与失败率 | 引用 2026-09-24 导入报告，本实验**未新调用** |
| 104 篇全语料的解析器收益 | **未验证**，仅 12 篇证据文献参与评测 |

## 产物

| 目录 | 内容 |
| --- | --- |
| `outputs/parser-sensitivity-p2-parse-20260927-01/` | 逐篇对照材料、锚点/证据组可定位性、页级字符统计、`gold_page_tables.json`、人工核对表模板 |
| `outputs/parser-sensitivity-p2-retrieval-20260927-01/` | 三臂隔离索引（FTS + Chroma + child chunks）、逐题排名、配对检验、解析日志 |
| `outputs/parser-sensitivity-p2-synthesis-20260927-01/` | 逐篇解析差异表、逐题检索差异表、失败案例 |

每个 `summary.json` 记录输入哈希、配置、代码版本（Git HEAD + 逐文件 SHA-256，因工作树有未提交
改动，单凭 HEAD 不足以标识代码）、解析器/模型版本与运行命令。

## 测试

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python -m pytest experiments/benchmark-parser-sensitivity-20260927 Knowledge-Base/tests -q
```

本实验只新增实验目录代码，未修改共享契约或模块默认行为。
