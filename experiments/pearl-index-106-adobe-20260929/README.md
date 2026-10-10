# PEARL 106 篇 Adobe 语料索引构建

*统一英文 child 资产、FTS 与 BGE-M3/Chroma 的独立构建实验 · status: current · 2026-09-29*

本实验执行已确认的 [106 篇 Adobe-only 语料选择](../../paper/pearl-framework/datasets/retrieval-corpus/README.md)，为后续 PEARL R1–R4 生成共同检索资产，不读取旧题集、旧索引、排名或评分。两篇仅有 PyMuPDF 解析的文献不纳入；主库以只读方式访问，输出目录必须尚不存在。

## 输入与执行计划

1. 将来源清单按原文 SHA-256 与 Catalog 活动 Adobe 版本逐一核对，核验原文及规范文档哈希。
2. 导出 `parent-child-v1` 的实际 child 文本、ID、来源、页及 locator，保存不可变快照。保留既有分块，不混入 parent 文本，不重新解析。
3. 用 `EnglishLexicalAnalyzer` 建立只索引 child 正文的 FTS5。查询使用相同分析器及 OR 词项，并列分数按 chunk ID 排序。
4. 核验本地 BGE-M3 权重和 tokenizer，固定 CUDA/FP16、batch=8、max_length=1024、seed=20260929；生成归一化 dense 向量，保存向量矩阵及 Chroma 索引。
5. 逐条核对两索引与快照的成员／内容一致性、向量维度与范数、截断情况及冒烟检索，记录输入、配置、模型、代码和产物哈希。

## 实现与对照边界

R1 使用 SQLite FTS5 BM25（k1=1.2、b=0.75），只使用 body 列。其 IDF 为 `max(ln((N-df+0.5)/(df+0.5)), 1e-6)`，与旧 108 篇纯 PyMuPDF 试标的 `ln(1+(N-df+0.5)/(df+0.5))` 不同。两者是不同实验配置，不能把旧分数当成此次重跑结果。标题和章节保留作追溯元数据，不加权参与检索。

R2 只启用 BGE-M3 dense 通道。保存归一化向量，供后续精确余弦检索及稳定并列排序；Chroma 的近似检索冒烟不等于已完成正式 R2 评价。R3 复用两通道排名，R4 还需独立验证重排模型。此次不生成 CEGR 成绩、不修改语义 Gold、不扩建或读取封存评估题。

## 运行与验证

从仓库根目录运行；输出目录必须不存在：

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python experiments/pearl-index-106-adobe-20260929/build.py --output-dir outputs/pearl-index-106-adobe-20260929-01
```

实现见 [build.py](build.py)，针对性测试见 [test_build.py](test_build.py)。上面的目录已完成运行，复现时必须改用另一个尚不存在的输出目录。

## 实际完成结果

| 项目 | 已验证结果 |
| --- | --- |
| 来源 | 106 篇，全部 `adobe-pdf-extract-v1`，来源及规范文档哈希核对通过 |
| 共同 child 库 | 6,433 条，FTS／Chroma／快照成员及文本一致 |
| Parent | 2,830 条，仅保存追溯快照，不进入两套检索索引或 embedding 输入 |
| 词法索引 | EnglishLexicalAnalyzer，FTS5 正文检索，唯一词项 OR，并列按 chunk ID |
| Dense | 本地 BGE-M3，RTX 3080 CUDA/FP16 实际执行，6,433 × 1,024 归一化向量 |
| 模型输入 | tokenizer 实测最长 665 tokens；0 条超过 1,024，保存实际 input IDs／mask |
| 构建耗时 | 快照约 3.89 秒，FTS 约 1.18 秒，dense 阶段约 244.26 秒，总计约 250.39 秒；不是在线查询延迟 |
| 验证 | 14 项针对性测试通过；构建进程退出后另开进程，逐条核对 FTS 内容及 Chroma 全部元数据、文本、向量和逻辑内容哈希 |
| 冒烟 | 固定通用查询 `pedestrian bottleneck flow`；重开后 ANN 与精确余弦 Top-10 重合 10/10，仅为单查询技术检查，不代表总体 ANN 召回或语义效果 |

本地输出目录为 [outputs/pearl-index-106-adobe-20260929-01](../../outputs/pearl-index-106-adobe-20260929-01/)。主要产物：

| 文件 | 用途 |
| --- | --- |
| [build_manifest.json](../../outputs/pearl-index-106-adobe-20260929-01/build_manifest.json) | 配置、模型 revision／实际权重与 tokenizer 哈希、依赖、代码与产物哈希、设备和耗时 |
| [verification.json](../../outputs/pearl-index-106-adobe-20260929-01/verification.json) | 独立进程重开后的最终验收记录 |
| `sources.jsonl`、`child_chunks.jsonl`、`parent_chunks.jsonl` | 输入身份与实际文本快照 |
| `fts.sqlite3` | 英文正文 FTS 索引；后续使用本实验 `sparse_query` 保持并列规则 |
| `dense_vectors.npy`、`dense_ids.json` | 一一对应的归一化向量与 ID，支持精确余弦对照 |
| `chroma/` | 独立持久化向量索引，collection 为 `pearl_106_adobe_bge_m3` |
| `model_inputs.jsonl`、`token_lengths.jsonl`、`truncated_child_ids.json` | 实际输入视图、长度与截断审计 |
| `smoke.json`、`smoke_query_vector.npy` | 未计分的通用查询冒烟 |

Chroma HNSW 的随机种子未由当前配置接口暴露，因此不宣称 ANN 位级复现；精确余弦检索可使用已冻结的向量矩阵和 ID 并列规则。Chroma 物理文件可能随关闭而改变，清单采用排序后的文本／元数据／float32 向量逻辑内容 SHA-256，并已在独立进程中复核。

脚本由子 Agent `build_adobe_indexes` 实现，`review_index_plan` 只读审查，主 Agent 执行真实 GPU 构建与最终重开验收。原 Catalog 只读访问，旧索引及试标结果不被本实验覆盖；语料、语义 Gold 和 PEARL 指标没有因建库改变。

## 8 题 Adobe-only 开发对照

以[新语料绑定 Gold](../../paper/pearl-framework/datasets/retrieval-pilot/pearl-retrieval-dev-pilot-8-adobe106-gold.json)为输入，`compare_pilot.py` 在上述冻结 child 库上执行了 R1–R3。输出目录为 `outputs/pearl-retrieval-dev-pilot-8-adobe106-20260929-01/`，`run_manifest.json` 保存输入和输出哈希、模型和方法配置；`rankings.jsonl` 保存每题每组 Top-100 的实际 child 文本；`rrf_union.jsonl` 保存合并前两通道各 Top-100 后的完整 union；另有真实 query 向量、输入 token、分阶段耗时及不含方法、排名和分数的审查池。该原始运行登记 R4 未执行；随后本地模型下载并核验完成，R4 在独立目录 `outputs/pearl-retrieval-dev-pilot-8-adobe106-r4-20260929-01/` 补跑，原始记录未修改。

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python experiments/pearl-index-106-adobe-20260929/compare_pilot.py --output-dir outputs/<new-unique-name>
```

两组子 Agent 分别盲化审查了 001–004 和 005–008。原始统一支持映射为输出目录中的 `pearl-retrieval-dev-pilot-8-adobe106-support-map-pearl-retrieval-dev-pilot-8-adobe106-20260929-01.json`，覆盖 R1–R3 前 20 联集的 266 条 intent-child 候选关系，计分范围内无未决项；原 Gold 的语义要求未放宽。`score_pilot.py` 用该映射计算原始 `preliminary-scores.json`。R4 新进入前 20 的 36 条关系由两组子 Agent 再次盲审，合并成[四方法统一映射](../../outputs/pearl-retrieval-dev-pilot-8-adobe106-r4-20260929-01/pearl-retrieval-dev-pilot-8-adobe106-support-map-pearl-retrieval-dev-pilot-8-adobe106-r4-20260929-01.json)并统一重算；R1–R3 汇总值与原始成绩逐项相同。

**8 题开发初步对照**（每格依次为 CEGR／BestGroupCov／CompleteMRR；不能代表 80 题开发集或 200 题封存评估集）：

R1–R3 的逐题证据位置、候选截断与指标差异见[原分析](r1-r3-pilot-analysis-2026-09-29.md)；R4 的模型核验、逐题排序变化与四方法统一重算见[补跑分析](r4-pilot-analysis-2026-09-29.md)。

| K | R1 正文 FTS BM25 | R2 BGE-M3 精确余弦 | R3 RRF k=60 | R4 |
| ---: | --- | --- | --- | --- |
| 1 | 0.125 / 0.1875 / 0.125 | 0.125 / 0.1875 / 0.125 | 0.250 / 0.3125 / 0.250 | 0.250 / 0.3125 / 0.250 |
| 5 | 0.375 / 0.500 / 0.250 | 0.375 / 0.500 / 0.1979 | 0.375 / 0.500 / 0.2917 | 0.375 / 0.500 / 0.2813 |
| 10 | 0.500 / 0.625 / 0.2625 | 0.375 / 0.500 / 0.1979 | 0.375 / 0.5625 / 0.2917 | 0.500 / 0.625 / 0.2938 |
| 20 | 0.625 / 0.6875 / 0.2699 | 0.500 / 0.625 / 0.2042 | 0.625 / 0.750 / 0.3066 | 0.750 / 0.8125 / 0.3121 |

本次 R1、R2、R3 的 Top-100 每题都完整保存。Shi Table 2 的均龄题在 Adobe child 中需要数值行与“Mean age (years)”表头共同出现，不能把单个数值 child 当完整支持。Li 的速度比较还需 running 条件；Pouw 的来源补充池命中不回填未检回的 Top-K。8 题样本仅用于流程和开发分析，不作显著性或优劣推广。`preliminary-scores.json` SHA-256：`4f6bfc6b94071e1f8a4b0284466d4622524cd54056df08c0820f8ef6fb544db7`；统一支持映射 SHA-256：`29e869d55361f9045ffab5ab3dd9e43f4ac2ea6c74c6e3c89d90f451cb19c57c`。

R4 本地模型 revision、权重哈希、CUDA/FP16 配置、800 个零截断输入及每题完整 Top-100 见[补跑清单](../../outputs/pearl-retrieval-dev-pilot-8-adobe106-r4-20260929-01/run_manifest.json)。新统一评分 SHA-256 为 `8b4e29ab5618aac881abb9765779234b217f4f4927ad6682e530758b907bc52d`；R4 @10 完整证据为 4/8，相比 R3 的 3/8 多 1 题，但 001 题从第 1 位后移至第 11 位。补跑及复现边界见[分析记录](r4-pilot-analysis-2026-09-29.md)。

评分复现（以现有封存输出为输入；新输出文件名必须不存在）：

```powershell
.\.venv\Scripts\python experiments/pearl-index-106-adobe-20260929/score_pilot.py combine --directory outputs/pearl-retrieval-dev-pilot-8-adobe106-20260929-01 --output outputs/<new-support-map>.json
.\.venv\Scripts\python experiments/pearl-index-106-adobe-20260929/score_pilot.py score --directory outputs/pearl-retrieval-dev-pilot-8-adobe106-20260929-01 --mapping outputs/<new-support-map>.json --output outputs/<new-preliminary-scores>.json
```

## 后续步骤

[80 题开发 Gold 与 200 题封存评估 Gold](../pearl-dataset-80-200-20261003/README.md)已建成；[完整 80 题 R1–R4 开发实验](../pearl-retrieval-dev80-20261003/README.md)已复用本目录算法，在同一冻结 Adobe-only 索引上完成三遍真实运行、独立实际 child 盲审、统一评分与开发分析。原 8 题试标的脚本、支持映射和结果保持可复现，不与新 80 题分析合并为额外样本。下一步复核开发难例与配置并登记正式冻结版本；200 题未运行且不参与调参，不从旧知识库 Gold v5 搬运题目。
