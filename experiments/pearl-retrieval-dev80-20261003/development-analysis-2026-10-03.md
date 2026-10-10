# PEARL Layer 1：80 题开发对照，Agent 复核初步结果

*106 篇 Adobe-only 英文来源上的 R1–R4 完整开发运行 · status: current · agent_reviewed_preliminary · 2026-10-03*

本次已完成 80 题四方法真实运行、实际 child 内容盲审、统一评分、开发统计与独立复算。R1／R2／R3／R4 的 CEGR@10 为 47／48／51／58 题；R4 相比 R3 多完成 7 题，但同时有 3 题从完整退为不完整。三个预设比较的 Holm 调整 p 均大于 0.05，来源聚类敏感性区间也跨越零；结果用于开发诊断，不作正式优劣结论。200 题独立评估仍封存且未运行。

## 固定输入与实际执行

run ID：`pearl-retrieval-dev80-20261003-01`。开发四层各 20 题；来源 Gold、问题、答案、条件和组结构未改，原 8 道试标题原样保留。共享 106 篇来源、6,433 个 child、2,830 个追溯 parent；parent 不进入检索或计分。开发出题来源 32 篇与评估 74 篇互斥，但 106 篇共同参与搜索，属于固定语料实验。

| 方法 | 本次执行口径 |
| --- | --- |
| R1 | 英文正文 `sparse_query`，NFKC／lowercase／alphanumeric OR；SQLite FTS5 BM25，k1=1.2、b=0.75；标题与 heading 为空、无标题加权 |
| R2 | BGE-M3 本地固定资产；真实 CUDA/FP16 编码 query，归一化 1,024 维；已存文档向量 float32 精确点积，不用 ANN 代替 |
| R3 | R1／R2 各 Top-100，等权 RRF k=60；保存最多 200 的 union 后取 Top-100 |
| R4 | 固定 R3 Top-100 的 ID 与完整正文；BAAI/bge-reranker-v2-m3，revision `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`；batch=4，query_max_length=768，max_length=1024 |

R1 实际 SQLite 3.45.3 的 IDF 为 `max(ln((N-df+0.5)/(df+0.5)), 1e-6)`；6 篇等长固定算例的高频／低频词实测分别为 1e-6 与 ln(1.8)，见 [实现探针](../../outputs/pearl-retrieval-dev80-20261003-01/sqlite-bm25-implementation-probe.json)。BM25 常量与负 rank 约定见 [SQLite 官方说明](https://www.sqlite.org/fts5.html#the_bm25_function)。

所有并列按 chunk ID 升序；seed=20260929。RTX 3080、一次一个 query、模型和索引缓存；5 道不同开发 query 完整预热，之后相同固定随机顺序运行 3 遍。首遍唯一用于评分，后两遍只作时延／确定性核验。三遍排名 ID、分数和 query 向量文件字节完全一致，最大分数差 0；没有执行失败或合法空结果，首遍 320 个单元各返回 100 个 child。

三遍 240 个 timed query 与 24,000 个 R4 query-child 对全部核验实际 torch forward token 输入，截断数为 0；预热另存且同样核验。dense query 最长 64 tokens，首遍 R4 最长 628 tokens。R3／R4 的 80×100 个候选 ID、正文与正文 SHA 一致。模型加载约 90.156 秒，离线建库属于既有冻结资产，不计入在线时延。

## 实际 child 盲审与评分边界

八个独立批次、两次独立裁决调用均以 `fork_turns=none` 创建，不携带方法、排名、分数或父任务执行历史。正文包随机排列，并剥离检索线索；每题逐项检查对象、实验范围、条件、数值、单位、表头与最小联合 child 路径。辅助脚本仅编排阅读与校验结构，不能产生语义标签。原文／parent 补证不回填 Layer 1。审员调用配置为继承配置，无模型 override；未猜测未暴露的模型身份。原批次决定、修订稿和复裁稿均保留。

最终选定版本覆盖 3,116 个必审 intent-child 关系；共 3557 个关系充分审定，12397 个补充关系保持 unresolved。补充池为四方法 D100 联集与全部 Gold 来源 child 的并集，后者不带排名。K≤20 的计分支持无未决项；补充关系是按题计数，同一 child 在不同题中重复出现不代表独立样本。

选定版本见 [80 份最终文件选择](../../outputs/pearl-retrieval-dev80-20261003-01/review/selected-review-files.json) 与 [审员及修订 provenance](../../outputs/pearl-retrieval-dev80-20261003-01/review/reviewer-provenance.json)。009／018 修正重复 constituent ID；076 仅修正年份备注；034、079、080 采用另一审员的独立复裁。支持 map 重读所选原审查文件并做全文一致性校验，不仅检查哈希清单；每条路径逐字摘录覆盖全部组成 child。

同一 atom 内路径为 OR，路径内 child 为 AND；requirement 的 bundle 内 atom 为 AND、bundle 间为 OR；完整组内 requirement 为 AND、组间为 OR。重复返回位置不能压缩排名；空 Gold 拒绝。BestGroupCov 取单个最佳组的满足比例，不跨组拼接；CompleteMRR 对首个完整组完成的原始排名求倒数，未完成记 0。未审定深层内容不记无支持。题集实际替代完整组为 0，既定 16 道期望未达；8 道替代 bundle 与多条 child 路径不充当替代完整组。

## 统一主表

以下区间是 10,000 次固定四层权重 0.25 的配对 intent bootstrap 95% 边际区间；seed=20260929，quantile 使用 NumPy linear。它们不是 Holm 调整区间，也未把三遍运行当成三倍样本。来源相关性敏感性另表。

| 方法 | CEGR@10 | intent 区间 | BestGroupCov@10（区间） | CompleteMRR@10（区间） |
| --- | --- | --- | --- | --- |
| R1 | 47/80 = 58.75% | [51.25%, 66.25%] | 0.7125 [0.6500, 0.7750] | 0.4011 [0.3353, 0.4683] |
| R2 | 48/80 = 60.00% | [51.25%, 68.75%] | 0.7250 [0.6500, 0.7937] | 0.3781 [0.3080, 0.4486] |
| R3 | 51/80 = 63.75% | [56.25%, 71.25%] | 0.7562 [0.6875, 0.8187] | 0.4192 [0.3531, 0.4870] |
| R4 | 58/80 = 72.50% | [65.00%, 80.00%] | 0.8313 [0.7750, 0.8813] | 0.5224 [0.4621, 0.5799] |

全部 K 如下，每格依次为 CEGR／BestGroupCov／CompleteMRR；四方法均 N=80。

| K | R1 | R2 | R3 | R4 |
| ---: | --- | --- | --- | --- |
| 1 | 0.3125 / 0.3937 / 0.3125 | 0.2750 / 0.3500 / 0.2750 | 0.3250 / 0.4375 / 0.3250 | 0.4250 / 0.5375 / 0.4250 |
| 5 | 0.5250 / 0.6438 / 0.3921 | 0.5000 / 0.6125 / 0.3650 | 0.5500 / 0.6625 / 0.4071 | 0.6375 / 0.7438 / 0.5108 |
| 10 | 0.5875 / 0.7125 / 0.4011 | 0.6000 / 0.7250 / 0.3781 | 0.6375 / 0.7562 / 0.4192 | 0.7250 / 0.8313 / 0.5224 |
| 20 | 0.6875 / 0.8000 / 0.4079 | 0.7250 / 0.8187 / 0.3856 | 0.7375 / 0.8375 / 0.4258 | 0.8250 / 0.8938 / 0.5295 |

## 分层与逐题完成

每层 N=20。每格为完整题数／20，BestGroupCov，CompleteMRR（均 @10）。完整逐题要求、缺失 atom、已满足组合与原始完成位置见 [评分明细](../../outputs/pearl-retrieval-dev80-20261003-01/score-details.json)；320 行矩阵见 [CSV](../../outputs/pearl-retrieval-dev80-20261003-01/scores.csv)。

| 主层 | R1 | R2 | R3 | R4 |
| --- | --- | --- | --- | --- |
| 单来源 | 20/20, 1.0000, 0.7767 | 18/20, 0.9000, 0.6917 | 19/20, 0.9500, 0.8017 | 19/20, 0.9500, 0.9250 |
| 数值／表格 | 16/20, 0.8000, 0.5988 | 16/20, 0.8000, 0.5560 | 17/20, 0.8500, 0.5976 | 19/20, 0.9500, 0.7675 |
| 同篇多证据 | 11/20, 0.7250, 0.2288 | 11/20, 0.7250, 0.2456 | 12/20, 0.7750, 0.2600 | 15/20, 0.8750, 0.3521 |
| 跨论文 | 0/20, 0.3250, 0.0000 | 3/20, 0.4750, 0.0193 | 3/20, 0.4500, 0.0174 | 5/20, 0.5500, 0.0451 |

本轮跨论文题的完整组完成仍较少：R1 0/20、R4 5/20；单来源题则 R1 20/20、R4 19/20。这说明净增益在不同层并不相同，不能用整体均值推断每题都有改善。资源与页诊断如下，均是“至少一个”Gold 来源／页命中，不能替代完整组。

| 方法 | AnySourceHit@10 | AnyPageHit@10 | CEGR@10 |
| --- | --- | --- | --- |
| R1 | 80/80 | 73/80 | 47/80 |
| R2 | 80/80 | 77/80 | 48/80 |
| R3 | 80/80 | 77/80 | 51/80 |
| R4 | 79/80 | 77/80 | 58/80 |

## 预设比较与来源依赖

胜／负以 CEGR@10 从 0→1／1→0 定义，其余为平；p 是双侧精确 McNemar，三个预设比较统一 Holm。差的区间仍是未作多重校正的配对 bootstrap 边际区间。

| 比较 | 胜／负／平 | 净差（百分点） | intent 差区间（百分点） | 精确 p | Holm p |
| --- | --- | ---: | --- | ---: | ---: |
| R2-R1 | 6/5/69 | +1.25 | [-6.25, 8.75] | 1.000000 | 1.000000 |
| R3-R2 | 4/1/75 | +3.75 | [-1.25, 8.78] | 0.375000 | 0.750000 |
| R4-R3 | 10/3/67 | +8.75 | [0.00, 17.50] | 0.092285 | 0.276855 |

R3−R1 是额外描述：6 胜／2 负／72 平，净增 5.00 个百分点，intent 差区间 [-1.25, 12.50]；不加入三个预设检验家族。R4−R3 的 intent 差区间从约 0 起，数值尾差不能当成严格正界，且 Holm p=0.276855。BestGroupCov 与 CompleteMRR 的配对差和逐层差在 [机器可复算开发统计](../../outputs/pearl-retrieval-dev80-20261003-01/development-analysis.json) 中完整保存，用于解释主指标。

32 个 Gold 来源产生 100 个 source-intent 关联，单来源最多复用 7 题，HHI=0.0364。按“任一共享 Gold 来源”连边并保留跨层传递关系，共 12 个连通分量，大小为 33、8、8、5、4、4、4、3、3、3、3、2。最大分量占 41.25%，80 行不能视为 80 个互不依赖的原文研究。

整分量重采样仍按原 N_h/N=0.25 加权，10,000 次均可估计。本次满足实现登记的报告门槛（≥10 分量、最大分量<40题、缺层抽样≤5%），但只有 12 个分量且一个很大，所以仅作敏感性诊断；该门槛不是有限样本覆盖率保证，不能由它声称精确独立证据。图使用冻结 Gold 来源；题族、主题和额外等价支持带来的相关性仍可能未完全建模。

| 预设差 | Gold 来源分量敏感性 95% 区间（百分点） |
| --- | --- |
| R2-R1 | [-8.66, 7.85] |
| R3-R2 | [-1.79, 16.02] |
| R4-R3 | [-8.44, 19.93] |

三个来源敏感性差区间均跨零；不把开发 McNemar、intent bootstrap 或次指标作为正式独立评估结论。

## 失败、处理缺失与未知深度

CEGR@10 不完整单元共 116/320：89 个已知在该方法 Top-100 中有充分路径，因此可标 R_TOPK；27 个未取得足够证据作更具体归因，保持 UNRESOLVED。R4 的 3 个 R_RERANK_LOSS（pilot-001、070、071）同时属于排序诊断，标签有重叠，不相加当互斥总数。逐题缺失 requirement、atom、候选阶段与接受／拒绝理由见 [逐题失败诊断](../../outputs/pearl-retrieval-dev80-20261003-01/per-intent-failures.json)。

| 阶段 | 本轮可以确认的观察 | 不能据此推出的结论 |
| --- | --- | --- |
| 解析 | dev034 PDF 的 inverse-metre 进入 canonical 已变为 `mŁ 1`，实际 child 延续损坏；属于局部 P_PARSE 观察 | 不是该题唯一根因，也不代表所有解析内容不可用 |
| canonical→child | dev034 的图像类型元素仍含 reciprocal-of-meter 说明和密度公式，68 个同源实际 child 全部包含在包内，却没有该元素正文；当前切块代码排除 IMAGE，与缺失一致 | 历史 catalog 构建代码哈希未完全锁定，不将当前代码一致性当唯一历史因果；未做新切块实验 |
| 索引 | 成员、正文、向量 ID 与冻结哈希核验通过；没有观察到这些身份不一致 | 不能把上游信息丢失称为索引丢失 |
| 候选生成 | 已保存 R1／R2 Top-100 和来源补充池的正向充分路径 | 深层候选未全审，不能将未知当 R_CANDIDATE_UNOBSERVED 或声称全库无证据 |
| 融合截断 | union 与 R3 Top-100 的顺序／集合绑定核验通过 | 本轮没有满足完整核验条件的已证实融合截断负例；不能据此宣称融合截断没有损失 |
| 排序 | 89 个 R_TOPK 已有真实充分路径；3 个 R4 @10 完整性损失可定位 | 未审定深层的更早完成只能给已知路径的上界，不能报精确首次排名 |

dev034 四方法 @1／5／10／20 均未完整，原 Gold 与分母不改。独立 child 裁决先冻结，再做 PDF 页图／canonical 追溯，追溯材料不计支持。详细证据见 [处理审计](../../outputs/pearl-retrieval-dev80-20261003-01/review/adjudications/dev034-processing-audit.json) 和 [完整同源 child／元素选择追溯](../../outputs/pearl-retrieval-dev80-20261003-01/review/adjudications/dev034-child-selection-followup.json)。dev035 的损坏正文未被修复回填，实际结论 child 仍提供可接受路径；R1／R2／R3 在第 7 位完成，R4 在第 6 位完成，说明已知损坏不自动导致该题不完整。

D100 的“存在已知充分路径”是正向下界：R1 70 题、R2 71 题、R3/R4 共享候选池 76 题；其余分别 10、9、4 题是未决，不能记全深度失败。四方法 Top-100 中未充分审定的关系数分别为 5,369、5,389、4,750、4,750；这些是按题／方法计数，不能相加为唯一 child 数。所有 80 题的 R3/R4 D100 支持都未完成全深度审定，故没有执行覆盖不变性比较。结构上的候选身份一致不替代这一内容核验。

## 实际时延与输入视图

三遍合计 240 个 query 时序观测，5 次预热不计；不是独立的 240 道统计题。下面方法总时延保留 runner 的审计扣除估计口径：R2=编码＋精确搜索，R3=顺序 R1＋R2＋融合，R4=R3＋重排＋排序；它们不是并行产品端到端 SLA。

| 方法 | 审计扣除估计 p50（ms） | p95（ms） |
| --- | ---: | ---: |
| R1 | 40.994 | 61.727 |
| R2 | 38.417 | 54.424 |
| R3 | 80.088 | 107.375 |
| R4 | 1059.731 | 1218.556 |

| 原始带核验开销观测／阶段 | p50（ms） | p95（ms） |
| --- | ---: | ---: |
| query 编码 gross | 34.516 | 49.498 |
| dense 精确搜索 | 4.157 | 5.875 |
| RRF 融合 | 0.131 | 0.196 |
| R4 重排 gross | 985.962 | 1116.745 |
| R4 显式输入核验 | 142.111 | 213.091 |
| 完整 instrumented pipeline | 1217.777 | 1431.837 |

gross 使用 CUDA 同步，含实际运行时 forward hook；调整值扣除显式输入核验、验证与已测 hook CPU 时段，无法重建完全无 instrumentation 的干净延迟，故只能称估计。FlagEmbedding 的适应性 batch 探针仍在实际推理中保留。各遍 p50／p95、gross／adjusted 定义和全部阶段原始时间见 [query timings](../../outputs/pearl-retrieval-dev80-20261003-01/query_timings.jsonl) 与 [run manifest](../../outputs/pearl-retrieval-dev80-20261003-01/run_manifest.json)。没有截断降级、替换模型或选择最快一遍。

## 复算、资产与后续边界

60 项专项测试通过，覆盖新实验与复用的 Adobe 统一索引算法；未跨共享契约，不声称完整仓库所有测试均执行。运行后冻结输入 244 项哈希一致；269 个运行产物哈希通过；独立重开所选审查原文件的 80 项全文绑定通过。评分器新加载原始排名／map 重算一致，另一个不导入评分函数的布尔公式实现核对 1,280 个 K 前缀、48 个总体指标一致。200 个封存文件（评估 Gold、清单和198个质控文件）仅以 byte hash／只读属性核验，未解析评估内容。

| 交付物 | 入口 |
| --- | --- |
| 执行及四方法参数 | [run_manifest.json](../../outputs/pearl-retrieval-dev80-20261003-01/run_manifest.json) |
| 盲审包清单 | [review/packet-manifest.json](../../outputs/pearl-retrieval-dev80-20261003-01/review/packet-manifest.json) |
| 共同实际 child 支持 map | [pearl-retrieval-dev-80-adobe106-support-map-pearl-retrieval-dev80-20261003-01.json](../../outputs/pearl-retrieval-dev80-20261003-01/pearl-retrieval-dev-80-adobe106-support-map-pearl-retrieval-dev80-20261003-01.json) |
| 首遍原始 Top-100 | [rankings.jsonl](../../outputs/pearl-retrieval-dev80-20261003-01/rankings.jsonl) |
| 320 行评分矩阵 | [scores.csv](../../outputs/pearl-retrieval-dev80-20261003-01/scores.csv) |
| 逐题组合评分 | [score-details.json](../../outputs/pearl-retrieval-dev80-20261003-01/score-details.json) |
| 统计、来源依赖、时延 | [development-analysis.json](../../outputs/pearl-retrieval-dev80-20261003-01/development-analysis.json) |
| 逐题失败与未知范围 | [per-intent-failures.json](../../outputs/pearl-retrieval-dev80-20261003-01/per-intent-failures.json) |
| 独立公式／封存验证 | [verification.json](../../outputs/pearl-retrieval-dev80-20261003-01/verification.json) |
| 独立评分器重载验证 | [score-recompute-verification.json](../../outputs/pearl-retrieval-dev80-20261003-01/score-recompute-verification.json) |
| 专项测试原始输出 | [test-verification.json](../../outputs/pearl-retrieval-dev80-20261003-01/test-verification.json) |
| 冻结资产运行后哈希 | [frozen-input-post-run-verification.json](../../outputs/pearl-retrieval-dev80-20261003-01/frozen-input-post-run-verification.json) |

关键绑定：

| 输入／输出 | SHA-256 |
| --- | --- |
| Gold | `4b118700b2ec810dd57d342ab3d5447b7d313c11aea73535dff160bfaba2d56c` |
| child library | `d07712d6d3c2ee1904cfa0ad95d4136090cbc1e2943be2bd676e18fbd48fee3a` |
| 统一 map | `b79f1d80a7d9246d6ba64911f60cc2fc919ad0a10f66f4b9722b2effdd63b9e1` |
| 评分 | `a6b23167a6b0981a287322d1770cc4034d8c7cb7f83135b4c7faab7b34cb918e` |

原 `run_manifest` 故意保持检索完成时的 `retrieval_complete_support_review_pending` checkpoint，避免改变映射已绑定的哈希；全链完成状态由另存的 delivery manifest 表达。完整重跑使用新目录，盲审决定不能由脚本自动生成；现有排名的映射／计分／分析复算命令见 [实验 README](README.md)。运行源码和后处理源码分别有本地快照，结果依赖原冻结资产可用及其哈希一致。

下一阶段进入开发难例与配置复核：优先检查 dev012 的摘要／正文范围、dev030 的阈值方向差异、pilot006 的 max／min 表述、dev050 的参与者称谓，以及 034 的处理缺失和 079／080 的语义边界。人工审查可后置，用于难例与必要调优，不是本次运行的门槛。若改语义 Gold 或映射，保留旧版本，并对全部方法一致另存重算；若改参数／模型，则在独立新 run 中重新执行受影响开发比较。

决定是否保留现行方法后，再登记正式使用的协议、语料、Gold、模型 revision／SHA、方法与评分代码冻结版本。补足深层内容核验是进一步 D100 归因与覆盖不变性分析的前提。200 题的检索、盲审和正式报告本次均未开始；不自动进入评估，也未执行解析、切块、模型替换、调参搜索或 Agentic 实验。
