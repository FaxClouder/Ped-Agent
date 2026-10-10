# PEARL 6B 评分与统计流水线规格

*6B T9 产物：E5 三配置 720 个答案的评分、意图级合并、配对 bootstrap、分母与成本表的实现规格；供 T10 独立编码、T11 独立复算 · status: plan · 2026-10-07*

本文是**规格**，不是实现，也不代表任何分数已经算出。写作时没有读取任何研究标签（第 1 期导入行、各期 responses、分段统计的标签分布都未打开）；只读了冻结代码、冻结版本记录、E5 生成记录与 E4 记录的字段结构。冻结规则与本文冲突时，以冻结规则为准，并把冲突登记为偏差。

## 1. 范围与不做的事

| 项 | 规定 |
| --- | --- |
| 被评对象 | E5：B0 `B0-regex320-overlap48-M0`、C2 `C2-L384-O0-M0`、C3 `C3-L256-O0-M0`（P0、4K）× 80 意图 × 3 次重复 = 720 格 |
| 主比较 | 每个配置对 B0 的差：C2−B0、C3−B0。不做 C2−C3 推断（可在描述表中并列，不给区间） |
| 统计单位 | 意图。先在意图内合并 3 次重复，再跨意图汇总（[evaluation-versions-r01.json](../../outputs/pearl-chunking-dev80-20261006-13/evaluation-versions-r01.json) `statistics.unit`） |
| 不做 | 不打标签、不改标签、不补判断、不调用模型；不做事后显著性检验；不用 unknown 过滤后的点估计替代上下界；不把开发集结果写成独立确认结果 |
| 实现者 | T10（ChatGPT/Codex 独立编码）。T11 由 Claude 另写一套程序复算，二者逐项比对 |

## 2. 前置门禁（任一不满足即中止，不写任何结果文件）

| # | 检查 | 依据 |
| --- | --- | --- |
| G1 | `experiments/pearl-answer-dev80-20261004/score.py` SHA = `6b975f26…1a5f`；`experiments/pearl-layer4-dev80-20261004/score.py` SHA = `60ea13fe…b0a0` | evaluation-versions `layer3/layer4.score_py_sha256`（2026-10-07 已核对一致） |
| G2 | evaluation-versions-r01.json 本身、参考 `reference-freeze-r01.json`（`52127942…3c1e`）、facts-r03（`cf00cb9d…`，以决定记录中的完整 SHA 为准）均与冻结值一致 | evaluation-versions；[facts-r03 决定记录](../../outputs/pearl-chunking-dev80-20261007-16/research/facts-r03-decision-r01.json) |
| G3 | 6A 交付清单无漂移；720 条 generation 记录全部 `record_kind=real`；`e5-cells-r01.jsonl` SHA = 6A 清单值 | [6A 交接](../../outputs/pearl-chunking-dev80-20261006-14/handoff.md) |
| G4 | 身份映射 `research-identity-map-r01.json`、次审抽样 `secondary-sample-r01.json`、事实性绑定 `factuality-bindings-primary-2-r01.json` 与各导出/导入记录中登记的 SHA 一致 | [research-periods.md](research-periods.md) |
| G5 | 各期导入记录存在且行文件 SHA 不变：research-primary-1、research-primary-2、引用重做 r03、固定次审、分歧裁决（T3a、T5、T7 之后的导入） | 6b-work-plan T3a–T8 |
| G6 | 选定标签记录（T7/T8 之后）存在：每个评价单元列出 primary／secondary／adjudication 的路径与 SHA 以及 `selected` 角色 | 见第 4 节 |
| G7 | 引用重做的 F7 验收记录为 passed | 6b-work-plan F7。**F7 未通过时只阻断引用指标**（第 6.4 节标为 `blocked`），其余指标照常计算 |
| G8 | 输出目录不存在（排他创建） | AGENTS：不覆盖已有研究输出 |

## 3. 输入

| 输入 | 路径 | 用途 |
| --- | --- | --- |
| 冻结参考 | `outputs/pearl-answer-dev80-20261004-01/reference-freeze-r01.json` `rows` | Layer 3 `score_cell` 的 reference；`stratum` 取自这里（4 层：`single_source`、`numeric_table`、`within_paper_multi`、`cross_paper`，各 20） |
| E5 上下文 | `outputs/pearl-chunking-dev80-20261006-14/e5-cells-r01.jsonl`（240 行） | 合并块协变量；`context_id` 用于连接 L2 |
| E5 答案记录 | `outputs/pearl-chunking-dev80-20261006-14/generation/*.json`（720） | `generation_status`、`response_sha256`；绑定核对 |
| L2 充分性 | `outputs/pearl-chunking-dev80-20261006-13/score-details-e4-r12.jsonl`（SHA `e1ad82ed…7e63`，5B 交付清单已登记） | 连接规则：`context_id` 等于 E5 上下文的 `context_id`，且 `stage=final`、`panel_id=fixed_budget_main`、`strategy=P0`、`budget=4096`；每个（配置，意图）必须恰好 1 行，取 `sufficient`（yes/no/unknown）。3 次重复共用同一 L2 值 |
| 身份映射 | `outputs/pearl-chunking-dev80-20261007-16/research/research-identity-map-r01.json` | blind_id → cells；cell → 配置、意图、重复编号 |
| 选定标签 | T7/T8 之后的选定记录（文件名由 T7 定） | 每个单元唯一的选定回答 |
| 事实性绑定 | `research/factuality-bindings-primary-2-r01.json`（及次审期的对应记录） | 事实性包 → cells；精确重复包绑定到多格；无 claims 的格记 NA |
| facts-r03 决定记录 | `research/facts-r03-decision-r01.json` | 敏感性分析的排除意图（第 8 节） |
| 成本来源 | `outputs/pearl-chunking-dev80-20261006-14/generation-summary-r01.json`、`generation-ledger-r01.jsonl`；各期导出/导入记录与 run-notes | 第 9 节 |

所有输入在运行开始时计算 SHA-256，写入 `inputs-r01.json`（路径、SHA、角色）；运行结束前再算一次，前后不一致即中止。

## 4. 每格的选定判断

流水线**不选择**标签，只读取 T7/T8 冻结的选定记录并核对：

- 每个任务、每个单元恰有一个 `selected`，其路径属于该单元的 primary／secondary／adjudication 之一，文件 SHA 与记录一致。
- 一致性检查按 T7 导出记录中冻结的选定规则执行（例如“主次一致取主审、不一致取裁决、未抽中取主审”，以 T7 记录为准）；检查不通过即中止并列出单元，由 Claude 处理。
- 盲化单元经身份映射展开到 cells。可回答性一个单元对应同一（配置，意图）的 3 格；精确重复包对应其绑定的全部格。
- 有据性 claims 与事实性 claims 的 `claim_id` 集合必须完全相同（按格比较）；不同即中止。次审事实性用哪一组 claims 由 T5 决定，本规格只要求选定的两侧一致。
- 第 1 期的 `citation_pairs`（标记 superseded）**不得读取**；引用只取引用重做 r03 的选定回答。

## 5. 调用冻结评分代码

两份冻结 `score.py` 按路径导入（`importlib`），导入前先过 G1。原文件不改、不复制改写。

### 5.1 Layer 3

逐格调用 `score_cell(reference, cell)`，其中：

```text
reference = reference-freeze-r01 中该意图的行（原样）
cell = {intent_id, arm: <配置 ID>, generation_status: <generation 记录值>, record_kind: 'real',
        l2_sufficient: <第 3 节连接的 L2 值>, decision: <选定 Layer 3 回答的 decision 对象>}
```

**禁止调用** `score_bundle`、`exact_mcnemar`／`holm` 的组合流程：`score_bundle` 写死了 `ARMS`（A0/A1）、`PAIRS` 与 seed 20261004，不适用于 E5。允许按配置调用 `summarize(rows)`，产出逐格合并的描述性汇总（四态、数值诊断、积分适用 N），标为 `cell_pooled`。

### 5.2 Layer 4

不调用 `score()`：它按（intent_id, arm）查旧 Layer 3 行，E5 每个（配置，意图）有 3 格，键会冲突。改为逐格按 `score()` 第 72–78 行的同一方式组装行，唯一差别是 `old_strict` 按 `cell_id` 取本次 E5 的 Layer 3 `strict`：

| 行字段 | 来源 |
| --- | --- |
| `cell_id`、`intent_id`、`arm`（配置 ID）、`stratum` | 身份映射；参考 |
| `answerability` | 选定可回答性回答的 `answerability` |
| `behavior`、`abstain` | 选定行为回答的 `behavior`、`abstains_from_unsupported_completion` |
| `reason` | 选定行为回答的 `refusal_reason`：字符串原样；`{label: …}` 取 label；`null`/`None`/`na`/`NA`/空串记 `na`（同冻结 `normalize_behavior` 与历史 `assemble_d400_r01.py`） |
| `claims[*].grounding.label` | 选定有据性回答各 claim 的 `label` |
| `claims[*].factuality.label` | 选定事实性回答中同 `claim_id` 的 `label`；无 claims 的格 `claims=[]` |
| `extraction_unknown` | 选定有据性回答 |
| `citation_pairs`、`citation_extraction_unknown` | 选定引用重做 r03 回答（不是第 1 期） |
| `old_strict` | 本次 E5 Layer 3 的 `strict`（字段名为兼容冻结 `summarize` 保留） |

然后调用 `claim_metrics`、`citation_metrics`（`extraction_unknown` 为真时 recall 置 `[None, None]`，同 `score()` 第 77 行），按配置调用冻结 `summarize(rows)` 得到逐格合并的宏／微平均、`reliability_metrics`、`behavior_counts`、`joint_counts`，标为 `cell_pooled`。行为字段与历史 `validate_behavior_decision` 的一致性规则（如 `full_answer` 必须 `abstain=false`、`reason=na`）只做**检查与报告**，违反时中止并列出单元，不改标签。

## 6. 意图级合并与指标

### 6.1 合并规则（新增代码，T11 独立复算）

每个指标在每格给出区间 `[lo, hi]`（确定值时 lo=hi），或 NA。

1. 意图值：对该（配置，意图）的 3 格，lo、hi 分别取**非 NA 格**的算术平均；3 格全 NA 则该意图该指标 NA。同时记录参与平均的格数 `k∈{1,2,3}`。
2. 配置值：80 个意图中非 NA 意图值的算术平均（lo、hi 分别平均），并报告非 NA 意图数。
3. 配对差（X−B0）：只在两侧意图值都非 NA 的**固定共同集合**上计算。下界 = lo_X − hi_B0，上界 = hi_X − lo_B0（冻结口径：减对侧端点，不做下减下）。点估计为共同集合上意图差的平均。

### 6.2 各指标的格级区间

| 指标 | 格级 lo / hi | NA |
| --- | --- | --- |
| AC | `ac`，None → 0 / 1 | 不出现（参考 80/80 resolved） |
| Strict | `strict=='yes'` / `strict!='no'` | — |
| Claim Coverage | `coverage_lower` / `coverage_upper` | — |
| Integration | `integration=='yes'` / `integration!='no'` | `integration=='na'`（意图不适用，三个配置相同） |
| Faithfulness、广义未支持、context 冲突 | `claim_metrics` 的两个端点 | claims 为 0 或 `extraction_unknown` |
| Factuality | `claim_metrics.factuality` | 同上 |
| 引用 Precision / Recall | `citation_metrics` 的两个端点 | 无 pairs（precision）；claims 为 0 或抽取 unknown（recall） |

主终点：Layer 3 为 Strict 与 AC；Layer 4 为意图宏平均 Faithfulness（Layer 4 协议“主指标题宏平均 Faithfulness”）。其余为辅助描述指标。

### 6.3 可靠性（拒绝补全）

`reliability_metrics` 是逐格汇总的混淆表比值，无法先在意图内平均。按配置报告冻结函数给出的 TP/FP/FN/TN、可行界与 `may_be_na`，作**描述**，不给 bootstrap 区间（与历史 Layer 4 “Citation/Rejection 只作带分母的描述”一致）。可回答性 unknown 与 `abstain` 为 None 的格不进确定表，报告覆盖率。

### 6.4 引用的 unknown 上下界（新增）

引用口径曾按上下文分化（D4），所以引用必须同时给出两层界，不能只报已解析部分：

| 层 | lo | hi |
| --- | --- | --- |
| A：pair 级 unknown（冻结） | `citation_metrics` 原样：supported / 全部 pairs | (supported+unknown) / 全部 pairs；recall 同理 |
| B：格级抽取 unknown（新增，补充） | 在 A 的基础上，`citation_extraction_unknown=true` 的格不再记 NA，precision、recall 记 0 | 同格记 1 |

- B 只把“抽取 unknown”纳入，真正的 NA（无 pairs 的 precision、纯拒答零 claims 的 recall）仍为 NA。
- 每配置报告：pairs 总数、unknown pairs 数与比例、`invalid`、`outside-context`、抽取 unknown 格数；F2 标记为“边界不能严格对齐”的来源块中的 pairs 数（按 r03 包的边界字段识别；识别不了记 `unclassified` 并计数）。
- 差值按 6.1 的对侧端点规则给出两层的上下界与 bootstrap 区间，标为**辅助、描述性**。若区间只因 unknown 跨过 0，结论写“未定”，不写“无差异”。

## 7. 配对 bootstrap

| 项 | 规定 |
| --- | --- |
| 次数、种子 | 10,000；`numpy.random.default_rng(20261005)` |
| 分层 | 按 `stratum` 分层，层名按字典序；层内意图按 `intent_id` 字典序编号 |
| 抽样矩阵 | 依层序，每层 `rng.choice(n_s, size=(10000, n_s), replace=True)` 得层内位置，映射为该层的全局意图下标后沿轴 1 拼接，得到 10000×80 的下标矩阵。**整次运行只生成这一次**，所有指标、两个配对、两层界都共用同一矩阵（各配置共享抽样） |
| 每次的统计量 | 对一行抽样，取共同集合内意图差的平均（重复抽中的意图按次数计）；该行未抽中任何共同意图时跳过，并记录跳过次数 |
| 区间 | 对有效行的均值取 `numpy.quantile(values, [0.025, 0.975], method='linear')`；lo、hi 端点各自独立 bootstrap |
| 适用指标 | 6.2 表中全部意图级指标；可靠性除外 |
| 多重比较 | 两个配对、多个指标的区间均不做多重校正；报告中写明是描述性 95% 区间 |
| McNemar | evaluation-versions 规定“exact，只用于没有 unknown 的二元面板”。意图级 Strict 是 3 次重复的平均（0、1/3、2/3、1），不是二元面板，所以主分析**不做** McNemar，结果中记 `mcnemar: not_applicable` 及原因 |

区间只覆盖意图抽样的不确定性；单次生成随机性（已由 3 次重复部分平均）、评审不确定性、来源聚类不在其中，报告必须写明。

## 8. 事实性敏感性分析（76 个意图）

- 排除集合从 facts-r03 决定记录 `sensitivity_analysis.intents` 读取，并断言恰为 `pearl-dev-009`、`pearl-dev-034`、`pearl-dev-035`、`pearl-dev-044`，`cells_affected=36`（4 × 3 配置 × 3 重复）。
- 只重做**事实性**：Factuality 意图宏平均界、已解析准确率 T/(T+F)、解析覆盖率 (T+F)/N、对 B0 的差与区间。其他指标不做敏感性版本。
- bootstrap 在 76 意图面板上**重新生成**抽样矩阵：同一种子 20261005、同一算法，层大小按剩余意图重算。
- 结果单独成文件、单独成表，与 80 意图主结果并列，标注“敏感性分析，不替代主结果”。
- 已知范围限制（报告照写，不扩展分析）：可回答性与行为包中的必要结论也取自 facts-r03，用户决定只对事实性做敏感性分析。

## 9. 合并块比例（说明性协变量）

只读 context，不读任何标签，可在评审完成前独立计算。

- 解析：对 E5 每个 context，用与 `e6b_lane_audit.py` 相同的正则 `^\[Source (\[\[.*?\]\])\]`（多行）取每个来源块头，JSON 解析后元组数 > 1 记为合并块。
- 单位：唯一（配置，意图）context，每配置 80 个（不按 3 次重复加权）。
- 输出：每配置的块总数、合并块数、块加权比例；意图级比例的均值；每意图 X 与 B0 的比例差。D4 记录的值（B0 0.87、C2 0.77、C3 0.55）出自分段统计，按本口径重算后如有差异须说明原因。
- 用法：在引用表旁并列；按“被引来源块是否合并”拆分引用标签分布（按 r03 边界字段识别，识别不了记 `unclassified`）。**不做回归、不做调整、不做检验**：合并块比例本身由切块配置决定，与配置完全混杂，只能说明引用差异可能的来源。

## 10. unknown、NA 与失败的分母

每个配置 × 指标都报告下表各列，任何结果表都不能只给比率：

| 列 | 含义 |
| --- | --- |
| `cells_planned` / `intents_planned` | 240 / 80（主分母，不删困难项） |
| `generation_failed` | 6A 为 0；仍按 `score_cell` 规则处理：Strict=no、AC=0，单列为运行失败 |
| `evaluation_missing` | 选定判断缺失的单元。**默认中止**；若用户事后决定保留，按 unknown 处理（lo=0、hi=1）、留在分母并单列，登记偏差 |
| `unknown_cells` | 该指标格级区间宽度 > 0 的格数 |
| `na_cells` / `na_intents` | NA 的格数与意图数（意图 NA = 3 格全 NA） |
| `k_distribution` | 意图值由 1、2、3 格平均的意图数 |
| `common_N` | 每个配对的共同意图数，以及两侧各自 NA 数 |
| `extraction_unknown` / `citation_extraction_unknown` | 格数 |
| `bootstrap_skipped_draws` | 第 7 节跳过的抽样行数 |

## 11. 成本表

| 部分 | 内容 | 来源 |
| --- | --- | --- |
| 生成（按配置） | 格数、returned、provider 调用、技术重试、prompt／completion tokens（含缓存命中与未命中）、单次时延均值与最大值、`finish_reason` | `generation-summary-r01.json`、`generation-ledger-r01.jsonl` 重算并核对一致 |
| 生成费用 | 只报 off-peak～peak 估计区间（0.457～0.915 USD 的来源与口径照抄 6A），写明不是账单 | 6A 交接 |
| 上下文规模（按配置） | 请求 UTF-8 字节均值与最大值、来源块数、合并块数 | `e5-cells-r01.jsonl` |
| 评审单元 | 按期次 × 任务列包数与绑定格数：主审、引用重做、次审、裁决；精确重复复用数；合计与冻结上限 4,680 的比较；技术重试与上限 468 的比较（按 run-notes 记录，没有记录就写 unknown） | 各期导出与导入记录 |
| 评审用量与费用 | ChatGPT 不返回 usage，记 `null`，不推测 | — |
| 已作废的评审 | 校准 cgpt-r01（200 包）、第 1 期引用部分（704 包内的引用）、API 校准 v4-pro 单列，不计入研究结果但计入实际消耗 | 导入记录、incidents |

## 12. 输出

T10 写入 `outputs/pearl-chunking-dev80-20261007-16/scoring/`（排他创建，修订号 r01），代码放 `experiments/pearl-chunking-dev80-20261005/e6b_score.py`，测试放 `test_e6b_score.py`。

| 文件 | 内容 |
| --- | --- |
| `inputs-r01.json` | 第 3 节全部输入的路径、SHA、角色；G1–G8 结果；代码 SHA；Python 与 NumPy 版本 |
| `rows-layer3-r01.jsonl` / `rows-layer4-r01.jsonl` | 每格一行（720 行）：`score_cell` 输出／第 5.2 节行与冻结函数输出，附选定回答路径与 SHA |
| `intent-panel-r01.jsonl` | 每（配置，意图）一行：各指标的 lo、hi、`k` 或 NA |
| `summary-r01.json` | 配置级意图宏平均、`cell_pooled` 冻结汇总、第 10 节分母表、可靠性描述 |
| `bootstrap-r01.json` | 每配对 × 指标 × 端点：点估计、95% 区间、`common_N`、跳过次数；`seed`、`iterations`、`quantile_method`、`stratified`、抽样矩阵 SHA（矩阵按 int32 C 顺序的字节计算） |
| `sensitivity-factuality-76-r01.json` | 第 8 节 |
| `covariate-merged-blocks-r01.json` | 第 9 节 |
| `cost-r01.json` | 第 11 节 |
| `command-r01.json` 与 stdout/stderr | 运行回执 |

浮点结果原样保存（`allow_nan=False`，NA 写 `null`），不在结果文件中四舍五入。

## 13. 固定算例（T10 必须做成测试，T11 必须复现）

**冻结函数的协议算例**（来自 Layer 4 协议，确认导入的是冻结实现）：N5（S2/P1/U1/C0/X1）Faithfulness 与广义未支持均为 [0.4, 0.6]；N0 为 NA；三 pairs 两 supported 一 invalid，precision = 2/3；TP2/FP1/FN1/TN2 时 P = R = F1 = 2/3，False Answer = 误拒 = 1/3。

**意图级合并与对侧端点**（新增代码）：

| 情形 | 输入 | 期望 |
| --- | --- | --- |
| Strict | X 三格 yes／unknown／no；B0 三格 yes／yes／no | X = [1/3, 2/3]；B0 = [2/3, 2/3]；差 = [1/3−2/3, 2/3−2/3] = [−1/3, 0] |
| 含 NA 的平均 | X 三格 Faithfulness [0.4, 0.6]、NA、[1, 1] | 意图值 [0.7, 0.8]，k = 2 |
| 全 NA | 三格均无 claims | 意图 NA，不进共同集合 |
| 引用 B 层 | 一格 `citation_extraction_unknown=true`，其余两格 precision [0.5, 0.5] | A 层意图值 [0.5, 0.5]（k=2）；B 层 [(0+0.5+0.5)/3, (1+0.5+0.5)/3] = [1/3, 2/3]（k=3） |

**bootstrap**：用 2 层 × 3 意图 × 3 配置的合成面板，固定种子 20261005、100 次，T10 把抽样矩阵 SHA 与区间写进测试期望值；T11 用独立代码按第 7 节算法重算，必须逐位一致。

## 14. T11 独立复算的接口要求

- T11 不得 import `e6b_score.py`，也不得调用两份冻结 `score.py` 的函数（Layer 4 协议：摘要与行级复算不得调用同一评分实现）；格级指标、意图合并、bootstrap、分母、协变量、成本全部另写。
- 比对：计数与 NA 位置逐项完全相同；浮点绝对差 ≤ 1e-12；抽样矩阵 SHA 相同。任何一项不符即 `failed`，不得调参使其通过。
- 篡改检验：在临时副本中分别改一个标签、一个 claim 位置、一个输入 SHA、一个结果数值，复算必须检出。
- 只有 T11 记为 passed 的数字可以进入 T12 报告。

## 15. 需要用户确认的选择

以下是本规格自行作出的选择，括号内为默认做法；T10 开始前如有不同意见请改本节：

1. 主分析不做 McNemar（默认：不做，记 `not_applicable`）。理由见第 7 节。
2. 可靠性只作描述，不给 bootstrap 区间（默认：按历史 Layer 4 做法）。
3. 引用差值给 bootstrap 区间但标为辅助、描述性（默认：给）。
4. 评审单元缺失时中止（默认：中止，由用户决定是否按 unknown 保留）。
