# PEARL 6B 剩余工作安排

*6B（E5 评价与总报告）剩余任务的分工、顺序与新会话启动语句；含第 1 期引用标签分化的修复 · status: historical（2026-10-08 终止） · 2026-10-07*

**2026-10-08 终止**：6B 在 T5a 后停止，T5b 及之后的任务不再执行，原因见 [Past/child-parent-Sum](../../Past/child-parent-Sum/README.md)。下文保留为终止时的计划快照。

这是计划，不代表任何一项已经完成。新会话请从这里开始，并以各运行目录的实际产物和 [incidents-and-deviations.md](incidents-and-deviations.md) 为准。

**这是什么实验：** PEARL 切块研究的最后一步。E5 用三种冻结的切块配置（B0 `regex320-overlap48`、C2 `L384-O0`、C3 `L256-O0`，均为 M0、P0、4K）各生成 240 个答案，6B 评价这些答案，并回答 C2、C3 相对 B0 的差异。评审是度量工具，不是研究对象。

## 当前状态

| 项 | 状态与位置 |
| --- | --- |
| 5A／5B／6A | 均已完成。E5 共 720 个答案（3 配置 × 80 意图 × 3 次，deepseek-flash）：[6A 交接](../../outputs/pearl-chunking-dev80-20261006-14/handoff.md) |
| 冻结评价版本 | [evaluation-versions-r01.json](../../outputs/pearl-chunking-dev80-20261006-13/evaluation-versions-r01.json)；裁判调用上限 4,680、技术重试 468 |
| 外部裁判 | ChatGPT（Codex 桌面会话，实际以子代理执行；模型 ID 未暴露）。校准 cgpt-r02 [门禁通过](../../outputs/pearl-chunking-dev80-20261007-16/calibration-gate-cgpt-r02.json)。API 裁判 deepseek-v4-pro 未通过，已停用 |
| 6B 运行目录 | `outputs/pearl-chunking-dev80-20261007-16/`；研究侧记录在其中的 `research/`（身份映射、固定次审抽样、导出记录、分段统计） |
| T1 | **已完成**。依赖与期次见 [research-periods.md](research-periods.md) |
| T3a | **已完成**：第 1 期 1,648 个回答导入并绑定 720 格（[导入记录](../../outputs/pearl-chunking-dev80-20261007-16/research/import-research-primary-1.json)，行数据在 `research/import-research-primary-1/`，只读副本 `research/workpackage-research-primary-1-received/`）；有据性 6,855 个 citation_pairs 标为 superseded。facts-r03 核查证据见 [facts-r03-provenance-r01.json](../../outputs/pearl-chunking-dev80-20261007-16/research/facts-r03-provenance-r01.json)；用户已批准，009 与 034/035/044 的事实性敏感性分析单独报告（[决定记录](../../outputs/pearl-chunking-dev80-20261007-16/research/facts-r03-decision-r01.json)，偏差 D7） |
| T3b | **已完成**：[research-primary-2/](research-primary-2/README.md) 行为 704、事实性 698 包（[导出记录](../../outputs/pearl-chunking-dev80-20261007-16/research/export-research-primary-2.json)、[事实性绑定](../../outputs/pearl-chunking-dev80-20261007-16/research/factuality-bindings-primary-2-r01.json)）；身份映射与次审抽样复现一致；系统提示与 cgpt-r02 逐字一致；说明纳入 F6。第 2 期的导入尚未实现（T5） |
| T3c | **已完成**：F2 片段边界 240 个 context、1,829 个来源块全部严格对齐（0 个对不齐），并经组装记录与来源原文两项独立核验（[审计](../../outputs/pearl-chunking-dev80-20261007-16/research/fragment-boundaries-r03.json)）；r03 格式说明与重做包设计，研究包 704 个只在内存中干跑（[设计记录](../../outputs/pearl-chunking-dev80-20261007-16/research/citation-redo-design-r03.json)，含 F7 草案和对照）；[calibration-citation-r03/](calibration-citation-r03/README.md) 40 包已导出，比对方法在评审前冻结（[比对计划](../../outputs/pearl-chunking-dev80-20261007-16/calibration/calibration-plan-citation-r03.json)、[导出记录](../../outputs/pearl-chunking-dev80-20261007-16/calibration/export-calibration-citation-r03.json)）。偏差 D8。说明见 [citation-redo-r03.md](citation-redo-r03.md)，其中“待决事项”列出单元上限问题，需用户决定 |
| T3d／T3e | **已完成**：40/40 校验有效、引用 36/36、8/8 哨兵，F5 [门禁通过](../../outputs/pearl-chunking-dev80-20261007-16/calibration-gate-citation-r03.json)；[research-citation-r03/](research-citation-r03/README.md) 已导出 704 包、绑定 720 格，身份与次审抽样未变，[导出记录](../../outputs/pearl-chunking-dev80-20261007-16/research/export-research-citation-r03.json)原样冻结 F7；[分段审计](../../outputs/pearl-chunking-dev80-20261007-16/research/lane-audit-calibration-citation-r03-r01.json)及偏差 D9–D10。停止于 T3e，待新会话执行 T4c |
| T4／T4c／T5a | **T4、T4c 已完成；T5a 导入完成，F7 未达标**：[第 2 期导入](../../outputs/pearl-chunking-dev80-20261007-16/research/import-research-primary-2.json)（行为 704、事实性 698 包）与[引用重做导入](../../outputs/pearl-chunking-dev80-20261007-16/research/import-research-citation-r03.json)（704 包，第 1 期 citation_pairs 保留并标为已取代）；[F7 判定](../../outputs/pearl-chunking-dev80-20261007-16/research/lane-audit-citation-r03-r01.json) S2、S3 未达标，偏移来自协调者评审的 citation-0001–0176（[排查](../../outputs/pearl-chunking-dev80-20261007-16/research/f7-investigation-citation-r03-r01.json)）；行为、事实性的分段诊断也有标记（不是门禁）。偏差 D11–D16。**T5b 的前置条件不满足**，补救方案和次审事实性 claims 的选择都待用户决定 |
| T9 | **规格已写**（status: plan）：[scoring-pipeline-spec.md](scoring-pipeline-spec.md)。第 15 节列出 4 项待用户确认的选择；未实现、未运行，写作时未读取研究标签 |
| T2 | **已完成**，有偏差。第 1 期 1,648 个回答格式全部通过；**有据性的引用标签按上下文分化**（D4），其余可用。见 [incidents D3–D6](incidents-and-deviations.md) |
| 工具 | [e6b_workpackage.py](../../experiments/pearl-chunking-dev80-20261005/e6b_workpackage.py)（导出、校验、研究期导入 `import --phase`、事实版本核查 `facts-check`、片段边界 `fragments-audit`、引用重做干跑 `citation-dryrun`）；`e6b_fragments.py`（F2 片段边界）；`e6b_packets.py`（盲化构建，seed 20261005）；`e6b_lane_audit.py`（分段一致性统计，`--f7` 为 F7 验收统计）；`validate_citation_responses.py`（引用重做回答校验）；冻结评分：`experiments/pearl-answer-dev80-20261004/score.py`、`experiments/pearl-layer4-dev80-20261004/` |

## 分工原则

- **ChatGPT**：所有消耗大的工作，包括评审、评分与统计流水线编码、报告初稿。可以使用子代理，但必须遵守下面的 F6。主审、次审、裁决必须相互独立。
- **Claude**：调度、盲化和哈希绑定、门禁、**独立复算核验**、最终审读与交付。凡是进报告的数字，都必须经过 Claude 的独立复算。
- **deepseek-flash**：只能做不涉及判断的文字整理（可选，需授权）。它就是 E5 答案的生成模型，**不得参与任何打标签、裁决、评分或核验**。

## 引用重做的修复方案（F1–F7，用户已同意）

| # | 内容 |
| --- | --- |
| F1 | 登记偏差。**已完成**：incidents D3–D6，分段统计 `research/lane-audit-primary-1-*.json` |
| F2 | 导出端**用程序标出合并来源块中每个片段的文字边界**。context 原文一字不改，只新增字段，写明每个片段在 context 中的 Unicode 起止位置和对应的来源编号。边界由块头区间推算，并逐块核验能否严格对齐；对不齐的块单独标记，不去猜 |
| F3 | 引用重做包包含：query、context、片段边界、raw_answer，以及主审已固定的 claims（claim_id、原文、位置）。**不带** claim 的有据性标签；只输出 `citation_pairs` 和 `citation_extraction_unknown`。claim 层面的有据性保留主审结果 |
| F4 | 冻结的判断规则不动，只补一段“输入格式说明”，讲清片段边界字段怎么读，另存为 r03，并登记为偏差 |
| F5 | 校准复核：用新格式重跑 40 个有据性校准锚点，按原阈值比对引用指标（≥0.95）。**局限**：校准锚点都是单一来源，没有合并块，所以复核只能证明格式说明没有扰动已校准的行为，不能证明合并块处理正确。这一点要在报告中写明 |
| F6 | 执行规则：<br>• 允许子代理，但所有上下文拿到的说明逐字相同；<br>• **协调者不得下发任何判断规则**；<br>• 规则没覆盖的情况，按冻结规则记 unknown 并写明原因，记进 run-notes，由 Claude 统一处理；<br>• 机械修正要留记录；<br>• 已写入的回答不得追加新判断；<br>• 显示包内容时不得删改 |
| F7 | 验收：回收后用 `e6b_lane_audit.py` 按上下文分段统计。标签分布的一致性标准，要在**导出引用重做包时**写进导出记录并冻结，晚于此时不得修改。不达标就逐段排查 |

## 任务清单（按顺序）

| # | 任务 | 执行者 | 依赖 | 交付物 |
| --- | --- | --- | --- | --- |
| T3a | 实现研究期导入，导入第 1 期的 Layer 3、可回答性和有据性（citation_pairs 只保留，标为 superseded，不进入评分），核验绑定；**查明 facts-r03 是否为 5B 冻结的事实版本，向用户汇报** | Claude | T2 | 导入记录；facts-r03 核查结论 |
| T3b | 导出主审第 2 期：行为（D）、事实性（E；claims 取自第 1 期有据性） | Claude | T3a，用户批准 facts-r03 | `research-primary-2/` 与说明 |
| T3c | 引用重做准备：F2 片段边界、F4 格式说明 r03、F5 校准复核包、F6 说明、F7 验收标准 | Claude | T3a | `calibration-citation-r03/`；导出程序；不在此时导出研究重做包 |
| T3d | 校准复核（40 包） | ChatGPT | T3c | responses、run-notes |
| T3e | 导入并比对校准复核；通过后导出 704 个引用重做包，冻结 F7 标准 | Claude | T3d | 门禁记录；`research-citation-r03/` |
| T4 | 主审第 2 期评审 | ChatGPT | T3b | responses、run-notes |
| T4c | 引用重做评审（704 包） | ChatGPT | T3e | responses、run-notes |
| T5a | 导入第 2 期和引用重做，做 F7 检查；列出次审事实性 claims 的选项，等待用户决定 | Claude | T4、T4c | 导入记录、F7 判定 |
| T5b | 按用户决定导出固定次审包（引用用新格式），核对累计单元数 ≤ 4,680 | Claude | T5a，用户决定 | `research-secondary/` |
| T6 | 固定次审评审 | ChatGPT（与主审不同的上下文） | T5b | responses、run-notes |
| T7 | 主审与次审程序比对，导出分歧裁决包 | Claude | T6 | 分歧清单、`research-adjudication/` |
| T8 | 分歧裁决 | ChatGPT | T7 | responses、run-notes |
| T8b | 导入裁决，合成最终标签集，并写明每个标签的来源 | Claude | T8 | 最终标签集清单与 SHA |
| T9 | 评分与统计流水线**规格**：输入、冻结 score.py 的调用、按意图合并 3 次重复、配对 bootstrap（10,000 次，seed 20261005）、对 B0 的差值与 95% 区间、unknown 与失败的分母、成本表；新增：引用的 unknown 上下界，各配置合并块比例作为说明性协变量；事实性去掉 009、034、035、044 后的敏感性分析（76 个意图，单独报告，不替代主结果） | Claude | 可与 T3 起并行 | 规格文档 |
| T10 | 按规格实现流水线并运行 | ChatGPT（Codex，独立编码） | T8b、T9 | 代码与结果 |
| T11 | **独立复算核验**：另写一套程序重算全部分数和统计，与 T10 逐项对比 | Claude | T10 | 核验记录（必须 passed） |
| T12 | 总报告初稿；数字只能引用 T11 核验过的产物 | ChatGPT | T11 | 报告草稿 |
| T13（可选） | 差异案例中文摘要与表格说明润色 | deepseek-flash（需授权） | T11 | 草稿，由 Claude 抽查 |
| T14 | 审读并更正报告；登记协议偏差；更新导航；交付清单与核验 | Claude | T12 | 最终报告、delivery manifest 与 verification |

**并行关系：** T3b 与 T3c 都会修改 `e6b_workpackage.py` 和本目录 README，**不要同时开两个会话**，先做哪个都可以。T4 与 T3c–T4c 可以并行。T9 可以随时单独进行。

## 报告必须包含的未决项与偏差

- E2：C3 的重叠选择 pending；E4：M0/M1 pending（最终冻结用 M0）；B0 与 C3 的局部恢复 pending；补审后仍剩的 unknown。
- 6B：
  - 裁判身份两次变更（Agent 角色 → API → ChatGPT）；
  - r02 澄清是看到失败后补写的；
  - 裁判模型身份无法验证；
  - 多子代理执行（D3）；
  - 引用标签分化与重做，包括 r03 格式说明、F5 的局限（D4）；
  - 事后修正（D5）与显示重排（D6）；
  - 事实版本不在 5B 冻结范围内，沿用历史 facts-r03，并附 009、034/035/044 的事实性敏感性分析（D7）；
  - `human_verified=false`。

## 新会话启动语句

**通用规则：**
- 每条语句只执行一个任务，完成后汇报并停止。
- Claude 任务都“不评审、不打标签、不调用模型 API、不覆盖已有产物”。
- ChatGPT 的每一轮都必须开**新的 ChatGPT 会话**：协调者本身也是一个上下文，不能跨轮复用。主审、次审、裁决不能是同一个会话。
- 目录名以前一个 Claude 任务实际导出并在汇报中给出的为准。
- T3a、T3b、T3c、T9 已完成，T3a、T3b 的语句从略。
- **每条语句前都写了前置条件。执行前先核对：所需目录和文件必须已存在，本任务要导出的目录必须尚不存在。不满足就不要开始。**

### T3c（Claude）：引用重做准备

**前置条件：** 已存在 `outputs/pearl-chunking-dev80-20261007-16/research/import-research-primary-1.json`；`paper/pearl-6b-judge-workpackage/calibration-citation-r03/` **尚不存在**；没有其他 Claude 会话在修改 `e6b_workpackage.py`。注意：T4 已经开始时，不得改动 `research-primary-2/` 和 `validate_responses.py`。不满足就不要开始，先回到前一个任务。

> 请先阅读 paper/pearl-6b-judge-workpackage/6b-work-plan.md（重点 F2–F7）、README.md、incidents-and-deviations.md（重点 D4），以及 outputs/pearl-chunking-dev80-20261007-16/research/import-research-primary-1.json。只执行计划中的 T3c，为引用重做做准备：
> 1. F2：程序推算合并来源块中每个片段在 context 中的 Unicode 边界，逐块核验能否严格对齐，统计对不齐的块；context 原文不改。
> 2. F3、F4：设计引用重做包（claims 取自第 1 期导入的有据性 claims，不带 claim 标签）和 r03 输入格式说明，冻结的判断规则不改。
> 3. F5：导出 40 个有据性校准锚点的新格式复核包 calibration-citation-r03/，写明比对方法：只看引用指标，阈值不变。
> 4. F6：写给 ChatGPT 的说明。
> 5. F7：起草分段一致性验收标准，写明统计量、阈值和不达标时的处理。
>
> 704 个研究重做包要等 F5 通过后，在 T3e 中导出。登记 r03 偏差。不评审、不打标签、不调用模型 API。完成后汇报并停止。

### T3d（ChatGPT，新会话）：校准复核

**前置条件：** `paper/pearl-6b-judge-workpackage/calibration-citation-r03/README.md` 已存在（由 T3c 导出），并且 `responses/` 为空。不满足就不要开始，先回到前一个任务。

> 请阅读 paper/pearl-6b-judge-workpackage/calibration-citation-r03/README.md，并严格按其中的说明完成评审。可以使用子代理，但所有子代理必须使用同一份说明，协调者不得自行补充或解释任何判断规则；遇到规则没有覆盖的情况，按说明记录，不要自行裁定。只读写该目录，以及说明中允许的根目录文件。

### T3e（Claude）：校准复核门禁与研究重做包导出

**前置条件：** `calibration-citation-r03/responses/` 中回答数等于包数，`run-notes.md` 已存在；`paper/pearl-6b-judge-workpackage/research-citation-r03/` **尚不存在**。不满足就不要开始，先回到前一个任务。

> 请先阅读 paper/pearl-6b-judge-workpackage/6b-work-plan.md（重点 F5–F7）、incidents-and-deviations.md、citation-redo-r03.md、calibration-citation-r03/README.md 与 run-notes.md，以及 T3c 的导出记录 outputs/pearl-chunking-dev80-20261007-16/calibration/export-calibration-citation-r03.json 与比对计划 calibration-plan-citation-r03.json。只执行计划中的 T3e：
> 1. 校验并导入 calibration-citation-r03 的回答，按 T3c 写定的方法和原阈值用程序比对，写门禁记录。阈值不得因结果调整。
> 2. 如果未通过：写 blocked 记录，汇报原因并停止，不导出研究包。
> 3. 如果通过：导出 704 个研究引用重做包 research-citation-r03/，身份映射必须复现一致。在导出记录中**冻结 F7 验收标准**，写好给 ChatGPT 的说明（纳入 F6）。
>
> 同时用 e6b_lane_audit.py 检查复核回答的上下文一致性，并读 run-notes，按 D3–D6 的口径登记新偏差。不评审、不打标签、不调用模型 API。完成后汇报并停止。

### T4（ChatGPT，新会话）：主审第 2 期

**前置条件：** `paper/pearl-6b-judge-workpackage/research-primary-2/README.md` 已存在，两个任务的 `responses/` 为空或只有本轮已写的回答。当前可以开始。不满足就不要开始，先回到前一个任务。

> 请阅读 paper/pearl-6b-judge-workpackage/research-primary-2/README.md，并严格按其中的说明完成评审。行为（behavior/）与事实性（factuality/）必须由互不接触对方目录的上下文完成。可以使用子代理，但所有子代理必须使用同一份说明，协调者不得自行补充或解释任何判断规则；遇到规则没有覆盖的情况，按说明记录，不要自行裁定。

### T4c（ChatGPT，新会话，不要与 T4 共用会话）：引用重做

**前置条件：** `paper/pearl-6b-judge-workpackage/research-citation-r03/README.md` 已存在（由 T3e 在校准复核通过后导出）；T3e 的门禁记录状态为 passed。不满足就不要开始，先回到前一个任务。

> 请阅读 paper/pearl-6b-judge-workpackage/research-citation-r03/README.md，并严格按其中的说明完成评审。可以使用子代理，但所有子代理必须使用同一份说明，协调者不得自行补充或解释任何判断规则；遇到规则没有覆盖的情况，按说明记录，不要自行裁定。在 run-notes 中逐一写明每个上下文（子代理）负责的包范围。

### T5a（Claude）：导入第 2 期与引用重做

**前置条件：** T4 和 T4c 都已完成：`research-primary-2/` 两个任务和 `research-citation-r03/` 的回答数等于包数，各有 `run-notes.md`；T3e 导出记录中已冻结 F7 标准。不满足就不要开始，先回到前一个任务。

> 请先阅读 paper/pearl-6b-judge-workpackage/6b-work-plan.md、incidents-and-deviations.md、research-primary-2/ 与 research-citation-r03/ 的 README 和各 run-notes，以及 outputs/pearl-chunking-dev80-20261007-16/research/ 下的导出记录、事实性绑定和 T3e 冻结的 F7 标准。只执行计划中的 T5 的导入部分：
> 1. 实现并运行 research-primary-2 和 research-citation-r03 的导入：校验、哈希核对、绑定回 cell（事实性按 factuality-bindings；引用重做取代第 1 期 citation_pairs，原数据保留）、定位偏移、记录裁判身份。
> 2. 按 run-notes 中的上下文范围，用 e6b_lane_audit.py 对行为、事实性、引用逐段统计，并按**已冻结的 F7 标准**判定。不达标时写明并停止，不得调整标准。
> 3. 读 run-notes，登记新偏差。
> 4. 列出次审事实性使用哪组 claims 的选项（主审选定的 claims，或次审有据性重新抽取的 claims），说明各自对独立性和可比性的影响，给出建议，等待用户决定。
>
> 不评审、不改任何标签、不调用模型 API。完成后汇报并停止。

### T5b（Claude）：导出固定次审

**前置条件：** `outputs/pearl-chunking-dev80-20261007-16/research/` 下已有 T5a 的导入记录，F7 判定为通过；用户已给出次审事实性 claims 的决定；`paper/pearl-6b-judge-workpackage/research-secondary/` **尚不存在**。不满足就不要开始，先回到前一个任务。

> 请先阅读 paper/pearl-6b-judge-workpackage/6b-work-plan.md、research-periods.md、incidents-and-deviations.md、T5a 的导入与 F7 记录，以及 outputs/pearl-chunking-dev80-20261007-16/research/secondary-sample-r01.json。按用户对次审事实性 claims 的决定，只执行计划中 T5 的导出部分：按冻结抽样导出固定次审包 research-secondary/，包括 Layer 3、可回答性、有据性（claims）、引用（r03 新格式）、行为、事实性。次审包与主审包的内容必须一致，只是交给新的上下文评审；身份映射与抽样必须复现一致。写给 ChatGPT 的说明（纳入 F6，并要求不得打开任何主审目录）。在导出记录中写明各任务的单元数，并核对累计单元数不超过冻结上限 4,680。不评审、不打标签、不调用模型 API。完成后汇报并停止。

### T6（ChatGPT，新会话，不得是任何主审会话）：固定次审

**前置条件：** `paper/pearl-6b-judge-workpackage/research-secondary/README.md` 已存在（由 T5b 导出），`responses/` 为空。不满足就不要开始，先回到前一个任务。

> 请阅读 paper/pearl-6b-judge-workpackage/research-secondary/README.md，并严格按其中的说明完成评审。不要打开 research-primary-1、research-primary-2、research-citation-r03 或任何校准目录。可以使用子代理，但所有子代理必须使用同一份说明，协调者不得自行补充或解释任何判断规则；遇到规则没有覆盖的情况，按说明记录，不要自行裁定。

### T7（Claude）：主审与次审比对，导出分歧裁决

**前置条件：** `research-secondary/` 的回答数等于包数，`run-notes.md` 已存在；`paper/pearl-6b-judge-workpackage/research-adjudication/` **尚不存在**。不满足就不要开始，先回到前一个任务。

> 请先阅读 paper/pearl-6b-judge-workpackage/6b-work-plan.md、incidents-and-deviations.md、research-secondary/ 的 README 与 run-notes，outputs/pearl-chunking-dev80-20261006-13/evaluation-versions-r01.json（裁决单元上限：L3 72、L4 288），以及历史 Layer 3/4 协议中关于次审一致性与裁决的规定。只执行计划中的 T7：
> 1. 导入次审回答并做分段一致性检查。
> 2. 按冻结规则用程序比对主审与次审，输出各任务的一致率和分歧清单。
> 3. 导出分歧裁决包 research-adjudication/：裁决者看到包内容和两份匿名判断，不知道哪份是主审。写给 ChatGPT 的说明（纳入 F6）。
>
> 如果分歧单元超过冻结上限，或者冻结规则没有明确的分歧定义，先汇报并停止，不得自行选择。不评审、不打标签、不调用模型 API。完成后汇报并停止。

### T8（ChatGPT，新会话，不得是任何主审或次审会话）：分歧裁决

**前置条件：** `paper/pearl-6b-judge-workpackage/research-adjudication/README.md` 已存在（由 T7 导出），`responses/` 为空。不满足就不要开始，先回到前一个任务。

> 请阅读 paper/pearl-6b-judge-workpackage/research-adjudication/README.md，并严格按其中的说明完成裁决。不要打开该目录以外的任何评审目录。可以使用子代理，但所有子代理必须使用同一份说明，协调者不得自行补充或解释任何判断规则；遇到规则没有覆盖的情况，按说明记录，不要自行裁定。

### T8b（Claude）：导入裁决，形成最终标签集

**前置条件：** `research-adjudication/` 的回答数等于包数，`run-notes.md` 已存在；最终标签集清单尚未生成。不满足就不要开始，先回到前一个任务。

> 请先阅读 paper/pearl-6b-judge-workpackage/6b-work-plan.md、incidents-and-deviations.md、research-adjudication/ 的 README 与 run-notes，以及 T7 的比对记录。导入裁决回答，校验并绑定，按冻结规则把主审、次审、裁决合成为最终标签集，并写明每个最终标签的来源（主审、次审一致或裁决）。生成最终标签集的清单与 SHA，作为 T10、T11 的唯一输入。登记新偏差。不评审、不改任何标签、不调用模型 API。完成后汇报并停止。

### T9（Claude，已完成）：统计规格

**前置条件：** **已完成**：`paper/pearl-6b-judge-workpackage/scoring-pipeline-spec.md` 已写。不需要再执行；第 15 节列出的 4 项选择需要用户确认。不满足就不要开始，先回到前一个任务。

> 请先阅读 paper/pearl-6b-judge-workpackage/6b-work-plan.md、research-periods.md、incidents-and-deviations.md，outputs/pearl-chunking-dev80-20261006-13/evaluation-versions-r01.json，outputs/pearl-chunking-dev80-20261007-16/research/facts-r03-decision-r01.json，以及 experiments/pearl-answer-dev80-20261004/score.py、experiments/pearl-layer4-dev80-20261004/protocol.md 与 score.py。只执行计划中的 T9：写评分与统计流水线的规格文档（status: plan），内容按计划 T9 一栏列出的各项。另外写明输入文件格式，以及 T11 独立复算时逐项比对的容差。只写规格，不实现、不运行、不读取任何研究标签。完成后汇报并停止。

### T10（ChatGPT，新的 Codex 编码会话）：实现并运行流水线

**前置条件：** T8b 的最终标签集清单已存在；`scoring-pipeline-spec.md` 第 15 节的 4 项选择**用户已确认**，并已写回规格。不满足就不要开始，先回到前一个任务。

> 请阅读 T9 的规格文档（路径见 paper/pearl-6b-judge-workpackage/6b-work-plan.md 的 T9 交付物）和 T8b 的最终标签集清单。严格按规格实现评分与统计流水线，并在新的运行目录中运行，输出逐意图得分、对 B0 的差值与 95% 区间、敏感性分析、成本表和图。冻结的 score.py 只能调用，不得修改；不得修改任何标签或输入；随机种子按规格。在运行目录写 run-notes：环境、命令、开始与结束时间、输入 SHA、遇到的问题。规格不清楚的地方记录下来，并按最保守的做法处理，不要自行扩展口径。

### T11（Claude）：独立复算核验

**前置条件：** T10 的运行目录、结果和 run-notes 已存在；**执行 T11 的会话在写完自己的程序之前不得打开 T10 的代码**。不满足就不要开始，先回到前一个任务。

> 请先阅读 T9 的规格文档、T8b 的最终标签集清单，以及 paper/pearl-6b-judge-workpackage/6b-work-plan.md。只执行计划中的 T11：**在打开 T10 的代码之前**，按规格另写一套独立程序，从最终标签集重算全部分数、统计与敏感性分析；写完并运行后，再与 T10 的结果按规格容差逐项比对，写核验记录（passed/failed，附逐项差异）。不一致时定位原因，并说明是哪一方的问题，不得修改任何一方的结果去凑数。不调用模型 API。完成后汇报并停止。

### T12（ChatGPT，新会话）：报告初稿

**前置条件：** T11 的核验记录已存在，状态为 passed。不满足就不要开始，先回到前一个任务。

> 请阅读 paper/pearl-6b-judge-workpackage/6b-work-plan.md（重点“报告必须包含的未决项与偏差”）、incidents-and-deviations.md、T9 规格，以及 T11 核验通过的结果和核验记录。写 PEARL 切块研究 E5/6B 的总报告初稿，包括：
> - 5 个 RQ 的回答、推荐配置、适用范围；
> - 遗留项与全部偏差；
> - 差异案例；
> - 事实性的敏感性分析单独成节。
>
> 报告中的每个数字都只能引用 T11 核验过的产物，并注明来源文件；不得引用未核验的数字，也不得自行计算新数字。写成新文件，不修改任何已有产物。

### T13（可选，需用户授权 deepseek-flash）

**前置条件：** T12 报告初稿已存在；用户已明确授权使用 deepseek-flash。不满足就不要开始，先回到前一个任务。

> 只有在用户明确授权后执行：用 deepseek-flash 为 T12 初稿中的差异案例起草中文摘要和表格说明，写成单独的草稿文件；由 Claude 逐条抽查是否忠于原文并记录。deepseek-flash 不得接触任何标签、评分或裁决。

### T14（Claude）：终审与交付

**前置条件：** T12 报告初稿已存在（如果执行了 T13，其草稿与抽查记录也已存在）。不满足就不要开始，先回到前一个任务。

> 请先阅读 paper/pearl-6b-judge-workpackage/6b-work-plan.md、incidents-and-deviations.md、T11 核验记录和 T12 报告初稿（以及 T13 草稿，如果有）。只执行计划中的 T14：
> 1. 逐条核对报告中的数字与 T11 核验产物，并更正。
> 2. 补全并核对协议偏差清单。
> 3. 更新导航（工作包 README、paper/README.md、实验 README、docs/README.md 如有需要）。
> 4. 生成交付清单与核验记录（文件、SHA、数量）。
>
> 不调用模型 API，不覆盖已有产物。完成后汇报并停止。
