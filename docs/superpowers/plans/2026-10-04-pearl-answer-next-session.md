# PEARL Layer 3 Answer 下一会话执行说明

*Evidence交付后的答案生成、参考复核与正确性评价 · status: plan · 2026-10-04；本文未执行Layer 3实验*

> **For agentic workers:** 使用 `executing-plans` 按阶段执行；实现任务可使用 `subagent-driven-development`。独立参考构建、校准裁决及答案语义评分必须使用 `fork_turns=none` 的独立Agent。每阶段保存验证证据、报告后继续，不等待人工审批。用户明确的新指示优先；本计划不授权自动commit、push、merge或清理工作区。

**Goal:** 在冻结的80题开发集和Layer 2上下文上，完成一个固定生成器的真实答案评价，交付中文分析，区分上游证据不足与证据齐备后的生成错误。

**Architecture:** 生成侧只消费查询与固定实际正文，评估侧独立保管参考答案、claims、rubric及充分性标签。先验证参考与评分入口、校准语义评审，再做20题诊断及完整80题；各阶段以新版本产物记录，不重跑Retrieval或改写Evidence。

前序实际交付入口：[Evidence中文分析](../../../experiments/pearl-evidence-dev80-20261004/evidence-analysis-2026-10-04.md)、[冻结Evidence协议](../../../experiments/pearl-evidence-dev80-20261004/protocol.md)、[Evidence交付清单](../../../outputs/pearl-evidence-dev80-20261004-01/delivery-manifest-r01.json)。

**Tech Stack:** 现有Windows/PowerShell、仓库`.venv`、Agent模型配置与`DirectModelGateway`、Python实验脚本、独立Agent语义审查与不共享评分核心的程序复算。本说明中的新脚本/CLI均为下一会话待实现项目，不是已有命令或已通过结果。

## 1. 当前是否可以开始

**可以开始Layer 3的实施与评估准备，真实批量生成须先完成模型预检、参考答案复核和judge校准。** 不需要先补齐Layer 2旧总体设计中的所有扩展策略，也不要求人工审查。完成规定验证的Agent评估按[现行标准](../../research-review-standard.md)作为正式项目内容。

| 前置项 | 当前核验事实 | 下一会话行动 |
| --- | --- | --- |
| Layer 2输入 | A–D完成；80题×4组320上下文，398实际盲包，1,280步骤绑定 | 消费冻结保存正文，禁止重新组装替代原输入 |
| Evidence结果 | child 4K/8K CGC为63/64，parent 4K/8K为62/71，分母各80；unknown=0 | 用于评估侧分层归因，不注入生成prompt |
| 研究基准 | r02中有`reference_answer`、requirements、atoms和允许证据组 | 有字段不等于Layer 3参考/rubric已独立验收；另存答案参考版本 |
| Agent生成入口 | `Agent/src/ped_research_agent/config.py`、`model_gateway.py`已有配置及直接生成适配 | 复用直接调用，避免运行会重新取证/改稿的整个EvidenceGraph |
| 模型可用性 | 本会话只读加载本地`.env`与环境后，`load_settings()`返回ValueError；未发现有效answer配置，未发网络请求 | 只检查配置是否存在；无可用凭证时先完成离线工作，真实生成前请用户配置模型，不能虚构答案实验 |
| Layer 3文档/实现 | [README](../../../paper/pearl-framework/layer-3-answer/README.md)与[design](../../../paper/pearl-framework/layer-3-answer/design.md)有边界设计；目录仅这两份文档，metrics/rubrics/运行实验尚未实现 | 落地本轮最小协议和实验入口，不能照抄旧计划称已实现 |

编写本说明前，Evidence交付清单中的734个文件核验：除维护入口`docs/README.md`的当前内容已不同于其交付快照外，其余733个绑定文件均一致。导航文档是可维护入口；原manifest保留当时SHA，不追改。下一会话须区分已披露的导航变更与冻结科学输入/输出漂移，不能忽略后者。

## 2. 启动阅读与全局边界

按仓库要求读：根README → AGENTS → project-architecture → Agent/README → docs/README，再读本计划、Layer 3设计、Evidence协议/分析/交付清单。以当前代码及本轮冻结协议确认行为，旧目标设计不是实现证明。

- 工作目录：`E:\F_Workspace\F-Agent-Paper`。先检查dirty状态，保留用户及其他任务修改。
- 只做Layer 3开发评价；不新跑200题Evidence/Answer、不新增题集、不调优Retrieval或Evidence策略。
- 不执行Layer 4 Faithfulness/Factuality/拒答决策评测、Layer 5 Agentic或新视频模型实验。
- 保存claim与citation原始信息便于未来层使用；引用存在性不替代答案正确性。
- 不将Gold答案、requirements、claims、rubric、参考引文、L2支持标签或旧评分放入被测生成请求；被测输入仅查询、原实际context及统一生成指令。
- 不改变历史Gold、排名、上下文、评审、评分或manifest。新答案参考、oracle context、校准、生成、评分都另存版本。
- 只选一个本地有效、用户允许的生成模型，固定提示/语言/参数完成五臂；不在看到成绩后换模型或选最佳答案。
- 模型配置的代码默认字符串不能证明模型可用。真实调用需返回成功且身份/配置可记录；密钥不打印、不写入manifest或Git。
- 正式Agent验收与开发用途分别说明：本轮80题不是新独立测试集，20题是其子集，不声称100题。

## 3. 冻结输入和复用接口

| 输入/接口 | 路径 | 使用边界 |
| --- | --- | --- |
| Evidence交付清单 | `outputs/pearl-evidence-dev80-20261004-01/delivery-manifest-r01.json` | SHA `021e20fc45909237a514a8356e65dbfaaf0e8054bcbdc7b0ed694134b656d8dc`；保护科学文件，导航快照差异另列 |
| 保存最终context | `outputs/pearl-evidence-dev80-20261004-01/stage80/contexts.jsonl` | SHA `2463a197f1bd2250eadaf09c4bc3667e3e5d022ca4bd0495303efc660177b49a`；只读取final字符串，禁止使用未预算中间视图给生成器补证 |
| L2逐题裁决 | `outputs/pearl-evidence-dev80-20261004-01/stage80/scores-r01.json` | SHA `136840ddd2ad6665733077bef4a321fa74c65fec18d98ee23f1f9e953ed81be5`；按intent/configuration接入充分性标签，仅评估侧 |
| Evidence输入清单 | `outputs/pearl-evidence-dev80-20261004-01/stage80/input-manifest.json` | 追溯查询、child/parent、tokenizer、旧资产及r02精确身份；不选择“最新”文件 |
| r02开发Gold | `outputs/pearl-retrieval-dev80-gold-r02-20261003-01/gold-r02.json` | SHA `7f64ac4559fbf604c0d4d6aca81e23685f1dcbf009853ee3c8637dc368ad29f5`；参考构建/评分侧读取，生成侧隔离 |
| 20题诊断名单 | `outputs/pearl-evidence-dev80-20261004-01/stage20/selection.json` | 沿用四类各5的名单，禁止按新答案效果挑题 |
| 正式验收依据 | `docs/research-review-standard.md` | Agent实际评价及规定验证即可验收，不新增人工门槛 |
| 配置加载 | `Agent/src/ped_research_agent/config.py::load_settings` | 只读取配置；检查SecretStr是否存在，禁止输出完整settings或异常中的凭证 |
| 模型适配器 | `Agent/src/ped_research_agent/model_gateway.py::DirectModelGateway.from_settings / generate` | 固定输入的直接调用，保留原始答案；不调用EvidenceGraph的检索/搜索/修订流程 |
| 模型输出契约 | `Contracts/src/ped_contracts/evidence.py::ModelOutput` | 当前保留content和model；usage/finish_reason等未暴露字段不能编造 |

复用现有SDK/网关；需要补充provider usage或finish_reason时优先在实验适配器记录实际响应，不无端重构业务模块或稳定契约。不能获得的字段保存null和不可获取原因。

## 4. 实验矩阵与生成协议

### 五个条件

| 条件 | 生成正文 | 作用 |
| --- | --- | --- |
| A0-4096 | Evidence C0-4096最终正文 | child 4K对照 |
| A0-8192 | Evidence C0-8192最终正文 | child 8K对照 |
| A1-4096 | Evidence C1-4096最终正文 | parent 4K对照 |
| A1-8192 | Evidence C1-8192最终正文 | parent 8K候选 |
| Aref-8192 | 独立构建且复核完整支持允许组的原文参考context | 完整证据条件下的诊断对照，不是实际检索成绩 |

每臂目标80个intent，四个实际context臂必须覆盖全部80；计划最多400个逻辑生成单元，20题诊断最多100个。相同intent、完整请求、非秘密模型配置和选择规则完全相同，才可显式绑定复用同一次实际生成；不能将400逻辑单元说成400次provider请求。阶段C已完成的精确请求可复用于D，另存复用清单；变更提示或模型后必须另开版本并重跑受影响单元。

**Aref是评估侧构造的oracle条件**：可用r02允许组与定位从同版冻结child/parent原文选择连续片段，但不得把参考答案或人工改写结论充作context。保存源ID、定位、原文字节区间、顺序、拼接格式、SHA和token，保留标题、条件、单位与必要周边语句。由未见实际context策略/成绩的独立Agent只读其实际完整正文验证充分性。不能从A1的支持标签自动复制。

Aref以8,192个冻结BGE计量token为统一预算。无法在该预算内构成且验证完整组时，标记`oracle_unresolved`并保存原因，禁止悄悄用16K/整篇全文或删除该题。Aref仅对已核定的eligible intents真实运行并报告N；与A1-8192只比较相同eligible子集，四个实际臂总体仍为N=80。若所有80题均核定，则五臂合计400个逻辑单元；否则明确实际分母和计划缺口，不能声称80个完整参考context已完成。

### 固定生成请求

以下指令作为本轮基础模板，阶段A仅因真实API格式/语言冲突做一次明确修订并冻结；看到答案后不得改写：

```text
Answer the research question in English using only the supplied context.
State the requested findings and retain the relevant experimental conditions,
numerical values and units. For comparisons, explicitly explain the relationship
between the findings rather than listing unrelated facts. Use the supplied
source labels for citations where possible. Do not invent missing evidence.
If the context does not establish part of the answer, state that limitation.

Question:
{query}

Context:
{exact_saved_context}
```

仅替换两个字段；记录完整请求SHA，不只记录context。源标签与系统/用户消息封装在A固定。正文被模型当作资料而非新增系统指令。各臂同一英语答案语言、同一输出上限（默认2,048生成token）、temperature=0（仅provider支持时）、seed=20261004（仅provider支持时）；不支持的参数记录实际行为，不能声称确定性或强行发送。验证provider窗口容纳完整输入+指令+输出预留；BGE计量不是provider窗口或计费token的等价证明。

每单元主结果为第一份成功返回的原始答案，不追加基于评分的改写/重试。SDK隐藏重试设0，由实验层最多三次可见技术尝试（初次+两次），只重试连接/限流/超时等技术失败，记录每次参数、错误类别、时延、response ID和可获取usage；不因答错而重试。拒答与部分答案原样保存，不当技术错误。技术失败也必须占据expected cell并单列，不能只报成功请求。

当前网关若不暴露结束原因，保存`finish_reason=null`；不能据长度臆测未截断。真实预检检查响应元数据可用性，并在成本/限制中说明。本轮一遍主生成不评估模型随机性；后续多遍另立协议，不挑best-of-N。

## 5. 答案参考、指标和统计口径

### 参考侧必须新增的冻结记录

每个intent单独记录：原query/Gold SHA、引用源/版本、参考答案、必要atomic claims与允许claim groups、关键结论targets、实验条件/范围、数值目标/单位/容差依据、整合关系要求、质量/争议、独立构建与复核记录。不自动把`reference_answer`或requirement claim视为已完成Layer 3复核；原文有冲突时保存多种合法解释或unknown，禁止强选一个有利答案。

参考构建与复核分别用独立`fork_turns=none` Agent：构建者只见query、必要需求和冻结来源原文，不见被测答案、策略/排名/成绩；复核者见候选参考、原文与规则，逐项核验语义及数值。答案与条件均有可追溯引文才可冻结；旧答案可在独立构建后作差异诊断，不覆盖旧Gold。参考freeze必须早于任何真实被测答案。

### 主要与辅助指标

| 指标 | 本轮固定含义与分母 |
| --- | --- |
| Answer Correctness（主要） | 每题0/0.5/1或unknown：1为预先冻结的关键结论及必要条件全部正确且关系正确、无实质矛盾；0.5为部分关键结论正确但结论不完整，且无实质矛盾；0为没有正确关键结论、实质方向/数值/关系矛盾，或有可回答参考却完全拒答。总体映射0–1后按intent宏平均，不同题型不拼接不同量纲 |
| Strict Answer Success（配对检验主终点） | AC=1记yes，AC=0/0.5记no，未裁决为unknown；N包含所有预定intent。它是完整正确答案比例，不与AC均值混称“准确率” |
| Claim Coverage | 正确给出的必要claims在一个最佳允许组内的比例；组内AND/组间OR，不拼不同替代组。correct计下界，correct+unknown计上界；missing/incorrect为0。正确性对照答案参考，不对照本次context支持 |
| Integration Success | 仅预先指定的同篇多证据/跨篇题适用（目标40题；实际参考记录逐题固定适用性）。须正确呈现指定来源/条件和所要求的比较、组合或机制关系；单纯列举不足。保留yes/no/unknown并报告适用N，不把单源/数值N/A当失败 |
| 数值诊断 | 在冻结数值目标上报告单位换算后的绝对/相对误差、可解析N、缺失N、错误单位N和unknown N；MAE按同量纲目标分开，不能跨m/s、人数、百分比求全局MAE。参考0时相对误差N/A |
| L2×L3四态 | 用保存的L2充分性与Strict Success配对计n11/n10/n01/n00及unknown；充分·错答是L3新增失败，不足·错答是上游传播。新增失败率=n10/(n11+n10)，充分子集Strict Success=n11/(n11+n10)，暴露子集N；总体结果仍报所有80 |
| 不足·答对 | 只记观察到的正确但来源机制未判明案例；不能据此称已合法补证、参数知识作用或L2错误。Layer 4尚未执行，不计算Faithfulness也不改L2标签 |
| 成本/运行质量 | 完整请求/答案SHA、输入/输出长度、BGE计量token、可获取provider usage和费用、单次时延、可见技术尝试、错误/拒答/结束原因。未暴露费用/用量为null，不用context noise代替答案质量 |

AC关键结论targets和必要claims有不同职责：前者决定题目结论正确性，后者记录解释覆盖；必须在参考freeze时逐题写出，而非看答案后临时拆分。若某题两个指标本来等价，如实说明，不人为改变target制造差异。纯形式措辞不扣分，同义改写需实际语义裁决。额外表述只有与题目参考实质矛盾才影响本轮AC，不扩展成Layer 4全域事实审查。

**数值规则：** 单位归一化（如120 cm/s与1.2 m/s）和百分比/百分点差别先冻结；正确数值缺必要条件/单位不能自动满分。容差来自明确原文近似范围、已复核精度依据或题目定义；不能默认“误差5%”或从答案拟合。浮点计算epsilon只处理计算误差，不是科学容差。无可支持容差的离散目标按冻结规范值/合法范围判断；有原文冲突且未裁决的目标保留unknown。

**未知/技术失败：** unknown在AC及Strict中报上下界，全部80题为主分母，同时报reference-resolved和response-returned子集N，不能删除困难项。有已核定可回答参考但三次技术尝试均失败的cell，端到端Strict记no/AC=0并标`generation_failed`；不得伪造语义评分，把它单列为运行失败而非读错证据。参考本身未裁决时语义分数unknown。四态分解另列运行失败与语义错答，不将两者统称读错。

### 预设比较

四个实际臂按intent配对：A1-4096−A0-4096、A1-8192−A0-8192、A0-8192−A0-4096、A1-8192−A1-4096；第五项Aref-8192−A1-8192只在相同oracle-eligible子集配对。五项Strict终点采用resolved pairs上的双侧exact McNemar+Holm（五项族；无适用oracle比较则该项p按1纳入，报告未可检验），并同时报告全分母unknown差界、增益、损失、resolved/unknown pairs与N。

AC均值、Claim Coverage、Integration作为描述性辅助，不再临时增加显著性检验。四类分层、以intent为单位、各臂共享抽样的配对bootstrap 10,000次，seed=20261004，95%线性分位数；必须在任何真实生成/校准评分汇总前冻结公式、比较族与代码版本。oracle子集使用其实际分层数量。来源相关性、参考/评审不确定性及单次生成随机性未由此区间覆盖，开发成绩不包装成独立确认结果。

## 6. 拟新增文件与职责

执行日期变化时调整新目录日期并记录；输出目录已存在则用新序号，绝不覆盖。以下是拟新增资产，不是当前已实现CLI。

| 文件 | 下一会话实现职责 |
| --- | --- |
| `experiments/pearl-answer-dev80-20261004/README.md` | 实际运行命令与范围，不写未执行通过 |
| 同目录`protocol.md`、`rubrics.md` | 指标、五臂、三值/技术失败、数值/整合锚点、统计和模型身份冻结 |
| 同目录`prepare.py` | SHA保护、query/context生成隔离包、参考包与选定版本导入、精确oracle映射 |
| 同目录`generate.py` | 单固定模型真实直接调用、raw逐次记录、不可覆盖保存与精确复用 |
| 同目录`review.py` | 答案judge盲包、实际校准/裁决记录导入与选择；不生成参考标签 |
| 同目录`score.py` | 三指标、Strict、数值、四态、分题型、配对和区间 |
| 同目录`verify.py` | 不调用score核心的独立重算及保存产物/provenance核验 |
| 同目录`test_prepare.py`、`test_generate.py`、`test_score.py`、`test_verify.py` | 下述固定合成例与失败门禁 |
| 同目录`answer-analysis-2026-10-04.md` | 最终中文分析；若日期改变相应调整 |
| `outputs/pearl-answer-dev80-20261004-01/` | 新输入/参考/oracle/校准/生成/审查/评分/独立复算/成本/交付manifest |

避免在`memPed/`写业务代码。无需搭Web服务、数据库或新Agent运行平台。优先实验内适配；跨稳定契约变更须说明必要性并跑全仓测试。

## 7. 分阶段执行

### 阶段A：输入盘点、参考与协议冻结

- [ ] 按阅读顺序确认代码及dirty状态；保存最小复用清单，不重新设计已有模型网关。
- [ ] 对冻结科学输入/原输出核SHA；单独保存`docs/README.md`导航快照差异，不放宽Gold/context/评分保护。
- [ ] 固定80题和原20题名单；检查intent/configuration唯一性，320最终字符串和L2支持标签精确对应。
- [ ] 检查本地model配置，SecretStr仅报告存在/缺失；记录非秘密协议、requested model、参数、超时/重试、上下文窗口依据。缺凭证时继续离线参考/入口工作，但不得真实生成，最终向用户明确缺失项。
- [ ] 独立构建/复核80题答案参考、atomic claims、关键targets、数值规范与整合规则；保留差异、裁决和unknown，freeze新版本，不覆盖r02。
- [ ] 构建并独立实际阅读Aref原文，验证预算与完整组，保存eligible/unknown清单。其构造使用Gold定位必须显式标oracle，不能声称是新检索算法。
- [ ] 冻结本说明第4–5节落地协议、生成prompt、rubric、judge prompt、配置、五项检验族和未知口径；生成包与评估包路径/字段隔离。

**阶段交付：** 输入manifest、复用盘点、参考/oracle核验、模型配置存在性记录和冻结协议。报告后继续B；缺模型凭证不阻断离线准备。

### 阶段B：合成入口验证、judge校准与真实模型预检

- [ ] TDD：先实现第8节固定算例的失败测试，再实现最小入口，保存实际红绿结果；仅合成query/context/answer，不消耗80题调试脚本。
- [ ] 保存并复读测试输入、答案、评分、SHA、样本分母；拒绝Gold/参考字段进入生成包、重复cell、缺失cell、改动prompt/model/context、跨版本复用和已有输出覆盖。
- [ ] 独立构造40个评分锚点（四类各10，含正确、部分、错误、限定/单位/关系陷阱），分别由两个独立Agent按原文/rubric裁决；未裁决锚点不得当确定真值。
- [ ] 冻结校准期望后，实际judge盲评这些答案：只提供query、匿名答案、冻结参考/rubric，不提供期望分数、生成策略、模型、L2标签或实际context成绩；保存逐条实际判断及依据。
- [ ] 校准门槛：已裁决40锚点上的AC等级exact agreement及必要claim标签micro agreement均≥90%，单独报告四题型；单位错误、比较方向反转、缺范围条件、缺整合、替代组错误拼接五类哨兵均须判对。门槛是本轮操作验收标准，不宣称已测得或通用研究定律。分歧独立裁决，若修改rubric/judge另存版本并重跑全部校准，不降低门槛迁就结果。
- [ ] 有有效模型配置时，使用单条非研究样本做真实连接/身份/输出预检，保存实际响应及元数据；不把mock或继承聊天Agent当配置固定的被测生成器。失败保留实际原因，禁止伪造成功。未配置时明确请求配置，在此之前不启动依赖真实模型的C/D。

**阶段交付：** 合成落盘验证、定向测试、40锚点和实际judge一致性/裁决、模型真实预检。通过后继续C，不等待人工批准。

### 阶段C：20题真实开发诊断

- [ ] 使用原20题名单；同一个冻结生成模型在四实际臂及eligible oracle臂产生原始答案，计划最多100个逻辑cell。每次都记录完整请求、config、模型、响应/技术失败、时间和可获取usage。
- [ ] 答案judge使用独立`fork_turns=none`角色，只见query/答案/冻结参考/rubric；没有methods/ranks/L2支持/旧评判。不能只用字符串相似度评估机制、比较或跨源整合。
- [ ] 全部实际答案完成AC、必要claim标签、适用整合裁决；未知有具体歧义依据，未阅读不计unknown。保存原判断、独立分歧裁决及明确所选版本。
- [ ] 独立重算逐题、题型、三指标、Strict、数值分组误差、四态/技术失败、配对与bootstrap；检查保存文件及输出漏项。
- [ ] 诊断错误仅修正明确实现/序列化/计分问题；另存版本，重跑受影响配置。不得根据答错问题改prompt、改模型、调context或参考使答案更容易得分。

**阶段交付：** 20题中文诊断、真实生成/裁决/独立复算和当前入口。入口通过后继续D；20题是开发子集，允许精确复用，不单列成独立测试集。

### 阶段D：完整80题正式Agent开发评价与交付

- [ ] 固定最终规则完成320个实际context逻辑cell，以及全部eligible oracle cell；精确复用C记录要有完整请求/config/响应SHA，其他cell真实生成。报告期望/成功/技术失败/未知/复用数量。
- [ ] 完成全部实际答案的独立盲评、所选审查和数值抽取；组装标签不能复制为答案正确标签，答案正确不能倒改L2充分性。
- [ ] 独立评分实现复算总体、四题型、适用整合、数值同量纲统计、四态、五项配对/多重比较/区间及运行失败分母；保留所有unknown上下界。
- [ ] 分析四臂的预算/展开变化是否传递到答案质量；用oracle同intent子集区分完整证据条件仍错与实际context不足。不足·答对仅标待未来Layer 4研究的机制未判明案例。
- [ ] 报告provider数据可获取性、实际时延、token/费用/技术尝试、拒答及输出截断；不以“Noise 94%”断言答案性能损失或改写旧指标。
- [ ] 保存代码/config快照、输入/输出/审查/provenance、实际命令/返回码、独立复算、旧科学资产未改SHA及中文分析；更新维护导航，导航的允许修改另列，不追改旧manifest。
- [ ] 写清正式Agent评估、开发集用途、model/judge局限、oracle eligible N和未知；若参考或模型仍阻塞则明确已完成/未完成，不伪称完整真实80题。

**完成标准：** 四实际臂全部80题有可追溯实际结果或真实技术失败记录；eligible oracle全部有实际结果；所有评分/未知及独立复算齐备；保存参考/校准/统计/成本/旧资产保护/中文分析。交付后停止Layer 3，不自动继续Layer 4或新200题评价。

## 8. 固定算例与验证要求

这些是下一会话必须落地的测试规格，不是当前已存在函数或测试通过记录。

| 固定输入 | 预期行为 |
| --- | --- |
| allowed group=[c1,c2]；c1正确、c2缺失 | Claim Coverage=0.5；完整组不能判成功 |
| 两替代组[c1,c2]和[c3,c4]；仅c1/c4正确 | 最佳组覆盖0.5；不能拼成完整组 |
| 同上但c3/c4都正确 | 完整替代组成功，不强制覆盖两组全部claims |
| 参考1.2 m/s；答案120 cm/s，条件正确 | 同单位目标一致；误差0，不能因不同字符串扣分 |
| 参考通行能力增加；答案说降低并正确列其他claims | 核心方向实质矛盾，AC=0；其余正确claims仍可计Coverage |
| 参考限定中学生与老年人；答案只说任意年龄混合 | 缺必要实验条件，不能AC=1 |
| 跨篇双方结论正确但没写参考要求的关系 | Claim Coverage可高；Integration不成功 |
| claim存在未裁决语义歧义 | 保留unknown，主分母不删，报告上下界 |
| 可回答参考下完全拒答/技术尝试均失败 | 单列refusal/generation_failed；端到端Strict=no，两者不能混作同类语义错答 |
| 没有实际响应，只保存mock内容 | 可以合成测试，不能接受为真实生成记录 |
| 缺一个预定intent×arm或重复ID | 样本完整性门禁失败；明确失败cell不同于缺失cell |
| 选定答案、prompt、参考、context或config变更 | provenance/跨manifest门禁失败，不静默复用 |

先跑实验定向测试；只有跨稳定契约才跑全仓。下一会话从仓库根使用现有验证环境：

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
$env:PYTHONIOENCODING = "utf-8"
# 下列实验目录必须在下一会话实际实现后才可运行；这里没有声称通过。
.\.venv\Scripts\python -m pytest experiments/pearl-answer-dev80-20261004 -q
# 若更改跨模块稳定契约，再执行：
.\.venv\Scripts\python -m pytest Contracts/tests Agent/tests Knowledge-Base/tests Video-Analysis/tests -q
```

README只写实际存在的CLI和实测返回码；不要把本说明的待实现文件表转换成“已完成能力”。

## 9. 新会话启动消息

```text
工作目录：E:\F_Workspace\F-Agent-Paper
请读取 docs/superpowers/plans/2026-10-04-pearl-answer-next-session.md，按阶段A–D执行Layer 3 Answer开发实验并交付中文分析。
Retrieval和本轮Evidence均已完成，不重复执行、不调优、不覆盖Gold/排名/上下文/旧输出。
按现行研究标准，完成规定验证的Agent评估就是正式内容，本任务不要求人工审查。
先核验Evidence输入、复核冻结答案参考/rubric、校准独立judge及检查真实生成模型配置；缺API凭证时先推进离线准备，再明确需要的配置，不伪造真实生成。
使用一个固定生成器，沿用child/parent×4K/8K四个实际上下文，并构建独立复核的8K完整参考context对照；生成侧只见查询和正文，不见Gold答案、rubric或充分性标签。
先完成20题开发诊断，再交付完整80题的答案正确性、claim覆盖、整合、数值诊断、L2×L3归因、配对统计、真实成本和独立复算。
各阶段完成后报告并继续；本轮不新跑200题，不执行Layer 4/5，不自动commit/push/merge或清理工作区。完成Layer 3后汇报并停止。
```
