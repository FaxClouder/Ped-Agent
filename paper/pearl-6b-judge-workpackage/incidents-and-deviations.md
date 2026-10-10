# PEARL 6B 失误与协议偏差记录

*6B（E5 评价）从 API 裁判转为 ChatGPT 代理过程中，研究主审第 1、2 期、引用重做准备（T3c）与回收（T3e、T5a）的失误、偏差与处理 · status: current · 2026-10-08*

本记录如实列出 Claude 会话自身的失误和协议设计缺陷，以及每一项的影响和处理。冻结阈值始终没有改动；所有被取代的产物都保留，没有覆盖。

## 时间线

| UTC（2026-10-07） | 事件 |
| --- | --- |
| 05:20 | 6A 收尾通过后，任务链立即用**旧模板**（Agent 子代理评审）启动 6B a1 |
| 05:22 | 用户已改用 API 裁判；a1 被终止，6B 以 a2 重启（裁判 deepseek-v4-pro） |
| 05:38–05:42 | v4-pro 校准未通过，6B a2 判为 blocked；DeepSeek 余额也不够研究评审（[run](../../outputs/pearl-chunking-dev80-20261006-15/handoff.md)） |
| 之后 | 用户决定由 ChatGPT 代理评审，导出本工作包 |
| 06:05–06:13 | ChatGPT 完成校准 cgpt-r01（200 包，单线程） |
| 导入后 | cgpt-r01 未通过，原因只有一个：behavior 字段 `unsupported_completion`。用户决定出 r02 澄清条款，200 包全部重做 |
| 06:28–06:54 | ChatGPT 在新对话中完成 cgpt-r02；导入后**全部指标 1.0、哨兵全过，校准通过**（[门禁](../../outputs/pearl-chunking-dev80-20261007-16/calibration-gate-cgpt-r02.json)）。r01 回答经核对未被改动 |
| 07:28 | T1：导出研究主审第 1 期（Layer 3 704、可回答性 240、有据性 704），冻结身份映射与固定次审抽样 |
| 07:37–17:31 | T2：ChatGPT 完成第 1 期。三个任务均由同一个 Codex 协调者派出的子代理执行；有据性先后用了约 23 个子代理上下文，分 A/B/C 三线并行 |
| 之后 | Claude 只读核验：文件完整、输入未改；发现有据性的**引用标签按上下文分化**（D4）。用户决定重做引用部分，见 [6b-work-plan.md](6b-work-plan.md) |

## 失误（Claude 会话）

| # | 失误 | 影响 | 处理 |
| --- | --- | --- | --- |
| 1 | 改变 6B 评审方式时没有先暂停任务链。6A 收尾只用了 5 分钟，链在模板改好之前就用旧方案启动了 6B a1 | a1 运行约 2 分钟，做了 23 次只读操作；没有启动子代理，没有评审，没有产物，没有付费调用 | 终止 a1，用新模板以 a2 重启。**教训：修改下一阶段的方案之前，先停链** |
| 2 | 首次汇报 v4-pro 校准结果时，把历史 Agent 的成绩（AC 40/40）误当成阈值 | 汇报内容有误，结论没有受影响（仍是未通过） | 随后在汇报中更正：L3 阈值是 AC、claim ≥ 0.90，加 5 个哨兵 |
| 3 | 工作包首次导出时，字段名用了 `expected_identity_*`，容易被误认为 expected 标签 | 交给裁判之前就发现了 | 只改字段名后重新导出；包内确认没有 expected 标签 |
| 4 | 导入 cgpt-r01 后，冻结的 `compare()` 因缺少 `calibration-plan-cgpt-r01.json` 而中断 | 回答已经导入，比对报告没写出来；没有数据损坏 | 补写计划记录（标注为导入时写成，阈值和比对规则逐字照抄 API 计划 r01），只重跑比对 |

## 协议设计缺陷与偏差

| # | 内容 | 处理与登记 |
| --- | --- | --- |
| D1 | 5B 冻结的评价身份是“Agent 审查角色”。用户先改为 API 裁判 deepseek-v4-pro（成本原因），后又改为 ChatGPT 代理 | 登记为裁判身份偏差。与历史 Layer 3/4 比较时必须注明。模型身份按用户和 run-notes 记录：sol6.1 未经确认，`human_verified=false` |
| D2 | 量表 “unsupported_completion 另列，含限定词仍无支持补齐不能算受限回答” 没有说明“补齐”只针对 context 的缺口。两个裁判在 contradicted 锚点（context 完整、回答与之矛盾）上都给出 true，与 expected、历史 Agent 裁判的 false 不一致：v4-pro 错 cal-24–30，cgpt-r01 错 cal-23–30。这是 cgpt-r01 唯一的失败原因：behavior 32/40 与哨兵 cal-23 | 按 Layer 4 协议“失败修订 prompt/rubric 另存 r02，保留 r01 并重校准全部相关锚点”，写了 [澄清条款 r02](../../experiments/pearl-chunking-dev80-20261005/e6b-behavior-addendum-r02.md)，只附在 behavior 规则末尾。用户决定 200 包全部重做（cgpt-r02，独立新对话）。**这条澄清是在看到失败和 expected 的规律之后写的，属于事后修订，单独登记**；研究阶段沿用 r02 |

## 研究主审第 1 期（T2）的偏差

核验证据：三份分段统计 `outputs/pearl-chunking-dev80-20261007-16/research/lane-audit-primary-1-{grounding,layer3,answerability}-r01.json`，由 `experiments/pearl-chunking-dev80-20261005/e6b_lane_audit.py` 只读生成。三个任务的回答 704/240/704 全部通过格式校验；packets、系统提示、manifest 的哈希与导出记录一致。

| # | 内容 | 影响 | 处理 |
| --- | --- | --- | --- |
| D3 | **执行方式**：没有按说明“每个任务一个新对话”，而是在一个 ChatGPT（Codex）会话里由协调者派出子代理：Layer 3 `/root/judge_layer3`、可回答性 `/root/judge_answerability` 各一个，有据性约 23 个（`judge_grounding` 及 cont2–7、lane a2–a3/b1–b3/c2–c3、resume a4–a8/b4/b6/b7/c4），A/B/C 三线并行。子代理自报只读自己任务的范围，协调者只转发进度。模型与推理强度全部 unknown；有据性 C2 自报产品为 “Codex API assistant”，A4 自报 “GPT-6 family” | 任务之间仍然隔离；同一任务内多上下文接力，是 D4 的前提 | 如实登记；今后的说明明确允许子代理，但规定说明逐字相同、协调者不得下发规则（见计划 F6） |
| D4 | **有据性的引用标签按上下文分化**。E5 的 4K context 会把同一来源的相邻片段合并成一个来源块，块头列出多个片段，回答只引用其中一个。冻结规则没有覆盖这种情况。B3 把边界问题上报给协调者（约 11:48 UTC），协调者在 15:42 UTC 给 A8 下发口头规则：“包内没有明确绑定时，引用记 unknown”，只对之后的包生效。各上下文的引用 unknown 比例：main 0.01、A 0.01、A8 澄清前 0.04、A8 澄清后 0.28、B1–B3 0.00–0.01、**B4 0.62、B6 0.53、B7 0.71**、C 0.00；unsupported 也不一致（main 0.22、C3 0.34，其余 0.01–0.15）。例：grounding-0030 与 grounding-0421 的 context、claims 和引用片段完全相同，前者 supported，后者 unknown。claim 层面的有据性各段 0.92–0.98，比较稳定；Layer 3、可回答性在各压缩分段之间也稳定 | 合并块比例因配置不同：B0 0.87、C2 0.77、C3 0.55。引用口径会**按配置不同地**影响引用指标，直接干扰切块对比。第 1 期的 citation_pairs 不可用于报告 | 用户决定：保留 Layer 3、可回答性、claim 层面的有据性；**704 包的引用部分在统一条件下重做**（导出端用程序标出片段边界，规则只加输入格式说明，并做校准复核）。原 citation_pairs 保留，标记为“已取代” |
| D5 | **回答写入后又修改**：依据用户授权（“修正吧”“进行修正”“允许修正”“授权进行修正，后续出现类似问题直接进行修正，不需要再请求了。但需要留下每次修正的记录”），做了机械修正：L3 0312–0314 条件键 `k1→scope`；有据性多处 claim_id、source_id、source_label、citation_occurrence。其中 B1 对 0368、0378 的 18 个 source_id 修改**发生在授权到达之前，且没有备份**（原值可由去掉末尾括号恢复）。0273–0275、0455 是**事后追加的新引用判断**，不是机械修正 | 机械修正不改变标签；追加的判断只涉及引用，会随 D4 的重做一并取代 | 如实登记；修正记录保存在各 run-notes 中 |
| D6 | **评审看到的是重排过的输入**：Layer 3 从 answer-0057 起，显示时去掉了参考引文的元数据，并对相同引文去重；可回答性显示时重排了来源头，省略了 SHA 字段。另有多次显示截断，各上下文报告都已重新完整读取 | 语义字段都完整显示了，预计影响很小 | 登记；今后的说明要求不得对包内容做删改式显示 |
| D7 | **事实版本不在 5B 冻结范围内**：5B 的 `evaluation-versions-r01.json` 没有冻结任何事实文件。6B 沿用历史 Layer 4 冻结并用于评分的 facts-r03（SHA `cf00cb9d…`），它的哈希在第 1 期导出时、早于任何研究标签就已记录，第 1 期可回答性包的必要结论也取自它。文件状态字段仍是 `source_built_pending_independent_review`（文件不可改写），独立复审已按同一 SHA 接受，但复审者不完全盲，也没有通读全部 149 个片段 | 事实性的真值来源不是 5B 冻结的版本；意图 009（隔离例外）和 034/035/044（单位与记号问题未解决）的事实存在已知瑕疵 | 用户决定（T3a 后）：批准 facts-r03，并把这 4 个意图（36 格）去掉后的事实性结果作为敏感性分析单独报告，主结果仍用 80 个意图。子集在任何事实性标签产生之前固定：[决定记录](../../outputs/pearl-chunking-dev80-20261007-16/research/facts-r03-decision-r01.json)、[核查证据](../../outputs/pearl-chunking-dev80-20261007-16/research/facts-r03-provenance-r01.json) |

## 引用重做准备（T3c）的偏差

| # | 内容 | 影响 | 处理 |
| --- | --- | --- | --- |
| D8 | **引用重做改用 r03 输入格式。** 冻结的判断规则（cgpt-r02 有据性系统提示中的 judge prompt、rubric、引用归属补充 r02、本次任务）逐字不变，程序按 SHA 核对；只把末尾的 harness 输出格式换成“输入格式说明 r03”和只输出引用的格式。包内新增程序推算的 `source_fragments`（240 个 context 的 1,829 个来源块全部严格对齐，并经组装记录和来源原文两项独立核验），`claims_candidates` 换成主审固定的 claims（不带标签），`instruction` 换成 r03 说明。引用改由新的上下文在 claims 固定的条件下单独判断，不再与 claim 层面的有据性同时判断。F7 草案在 T3c 内改过一次：固定上限 U ≤ 0.10 在交错分段的阴性对照上误报，换成置换校准的 S3；改动时还没有任何重做标签 | 引用指标来自与第 1 期不同的格式和流程，与历史 Layer 4 的引用结果不能直接比较。F5 校准锚点都是单块、单来源，复核只能说明新格式没有扰动已校准的引用行为，不能证明合并块的处理正确 | 登记为偏差；报告必须写明 r03 格式、claims 固定和 F5 的局限。细节见 [citation-redo-r03.md](citation-redo-r03.md)；F5 比对方法在评审前冻结（`calibration-plan-citation-r03.json`）；F7 标准在 T3e 导出研究包时冻结 |

## 记录位置

- cgpt-r01 比对与门禁：[calibration-comparison-cgpt-r01.json](../../outputs/pearl-chunking-dev80-20261007-16/calibration/calibration-comparison-cgpt-r01.json)、[calibration-gate-cgpt-r01.json](../../outputs/pearl-chunking-dev80-20261007-16/calibration-gate-cgpt-r01.json)
- v4-pro 校准：[calibration-gate-r01.json](../../outputs/pearl-chunking-dev80-20261006-15/calibration-gate-r01.json)
- 链事件：[chain-log.jsonl](../../outputs/pearl-chunking-chain-20261006/chain-log.jsonl)
- 第 1 期分段统计：`outputs/pearl-chunking-dev80-20261007-16/research/lane-audit-primary-1-*.json`；评审原始记录：`research-primary-1/*/run-notes.md`
- 引用重做准备（D8）：`outputs/pearl-chunking-dev80-20261007-16/research/fragment-boundaries-r03.json`、`citation-redo-design-r03.json`；`outputs/pearl-chunking-dev80-20261007-16/calibration/calibration-plan-citation-r03.json`、`export-calibration-citation-r03.json`

## 引用校准复核回收（T3e）的执行登记

| # | D3–D6 口径与证据 | 影响与处理 |
| --- | --- | --- |
| D9 | **执行方式及读取范围（D3）**：T3d 使用 4 个上下文，三子代理各负责 cal-01–10、11–20、21–30，协调者负责 31–40；继承完整历史。run-notes 披露此前目标目录不存在的尝试中读取了范围外的 using-superpowers/SKILL.md 和 MEMORY.md，历史摘要包含旧校准范围、JSON 与验证流程；未打开旧回答。模型具体版本与推理强度 unknown，实际开始时间部分 unknown。 | 范围外读取及其历史继承是协议偏差，不能宣称完全没有历史上下文暴露。未报告判断规则往来、未覆盖情况、机械修正、写后判断修改、删改显示、截断或压缩续做（D4–D6 无新增此类事件）。按 run-notes 如实登记，不修改任何回答；这些过程陈述来自自报，并非独立执行轨迹审计。 |
| D10 | **上下文分布诊断（D4）**：e6b_lane_audit.audit/f7 按上述四段运行，S1 p=0.0001、S2 p=1.0、S3 不适用。每段引用标签计数与冻结 expected 的同范围标签计数完全一致，程序比对零失败。 | 校准锚点按类别排列，并非研究盲化随机顺序；分布差异与预设锚点构成一致，不能单凭 S1 诊断上下文口径漂移。此处保留 not_met 诊断原值，不把只对研究回收冻结的 F7 追加为 F5 门禁；F5 仍按 T3c 冻结方法通过，阈值未变。CLI 的 merged_share 依赖研究身份映射，校准不适用，因此直接调用同文件 audit/f7，不改算法。 |

T3e：40/40 有效，引用 36/36，8/8 哨兵通过，citation_schema 与定位失败均为 0，非引用输入指标与 cgpt-r02 完全一致；已导入只读副本并导出 704 个研究引用重做包，绑定 720 格，身份映射与固定次审抽样 verified_unchanged。F7 原样冻结，F6 写入研究 README。F5 不验证合并块处理；不调用模型 API、不产生或修改标签，human_verified=false。未处理单元上限待决事项，停止于 T3e。

证据：[T3d run-notes](calibration-citation-r03/run-notes.md)、[F5 门禁](../../outputs/pearl-chunking-dev80-20261007-16/calibration-gate-citation-r03.json)、[分段审计](../../outputs/pearl-chunking-dev80-20261007-16/research/lane-audit-calibration-citation-r03-r01.json)、[研究导出记录（F7 冻结）](../../outputs/pearl-chunking-dev80-20261007-16/research/export-research-citation-r03.json)、[研究说明（F6）](research-citation-r03/README.md)。

## 第 2 期与引用重做回收（T5a）的登记

核验证据：导入记录 [import-research-primary-2.json](../../outputs/pearl-chunking-dev80-20261007-16/research/import-research-primary-2.json)、[import-research-citation-r03.json](../../outputs/pearl-chunking-dev80-20261007-16/research/import-research-citation-r03.json)；F7 判定 [lane-audit-citation-r03-r01.json](../../outputs/pearl-chunking-dev80-20261007-16/research/lane-audit-citation-r03-r01.json) 与逐段排查 [f7-investigation-citation-r03-r01.json](../../outputs/pearl-chunking-dev80-20261007-16/research/f7-investigation-citation-r03-r01.json)；行为、事实性分段诊断 `lane-audit-primary-2-{behavior,factuality}-r01.json`。三个任务的包、manifest、系统提示、冻结绑定与校验器哈希均与导出记录一致，回答全部通过校验；引用定位失败 0。

| # | D3–D6 口径与证据 | 影响与处理 |
| --- | --- | --- |
| D11 | **执行方式与读取范围（D3）**。第 2 期共 7 个上下文：协调者 `/root` 加 6 个评审上下文（行为 `behavior_review` 1–211、`behavior_front_continued` 212–224、`behavior_front_0225` 225–352、`behavior_review/behavior_tail` 353–704；事实性 `factuality_review` 0001–0600 的 595 包、`factuality_tail` 0601–0704 的 103 包），派发时 fork_turns=none。引用重做 4 个上下文，各 176 包，连续且不重叠：`/root` 0001–0176 由**协调者本人评审**，其余三段由子代理评审。范围外读取：第 2 期协调者读了仓库 README、AGENTS、docs/project-architecture、docs/README、EVALUATION-STANDARD、MEMORY.md 与两份 skill；`behavior_review`、`factuality_review` 读了 using-superpowers/SKILL.md，并按关键词检索 MEMORY.md 中的校准与工作包摘要；`behavior_front_0225` 读了 SKILL.md；`behavior_tail` 未单独列明（unknown）。引用重做协调者读了仓库 README、AGENTS、project-architecture、SKILL.md，并检索 MEMORY.md；`review_0353_0528` 读了 SKILL.md 并检索 MEMORY.md；`review_0177_0352` 读了 SKILL.md；`review_0529_0704` 无范围外读取。上下文压缩：behavior_tail 9 次，引用重做 `/root` 8 次，其余三段各 7 次，另有多次显示截断后重读。模型自报 GPT-6 系列，精确型号与推理强度 unknown | 任务之间仍然隔离，没有报告跨任务读取或判断往来；协调者在两轮中都没有下发判断规则。引用 README 的 F6 第 2 条写明协调者“只负责派发、转达进度和汇总”，但同一 README 的验收一节又要求写明“每个上下文（包括协调者）”的范围，两处不一致；协调者评审的那一段正是 F7 偏移的来源（D14）。如实登记，回答一律不改 |
| D12 | **已写入回答被覆盖，且没有备份（D5）**。`behavior-0209`–`0211` 最初由 `behavior_front_continued` 写入（07:12:04Z）；协调者收尾时再次按模板派发全范围，`behavior_review` 从自己的旧续做边界继续，于 08:07:03–08:07:48Z 重写了这三个文件。原内容没有备份，标签是否变化 unknown。协调者发现后中断了该上下文，没有自行裁定 | 违反 F6 第 4、5 条。导入使用现有文件，把这三个 ID 归入 `behavior_review`，导入行带 `execution_event` 标记。`behavior-0211` 在固定次审抽样中，次审会独立再判一次。不恢复，不重判 |
| D13 | **引用重做的写后修改（D5）**，均有修改前全文备份：0396 的 source_id 缩写（`B6F1`）与非枚举拼写 `partially_supported`→`partial`，起因是压缩摘要中的缩写被续写进文件；0527 的 citation_occurrence 重新编号；0061–0064 字段名 `citation_extraction_unknown_reason`→`reason`；0211、0216 的引用括号与出现序号、0275 的出现序号（协调者按子代理报告修正）；0596–0643 共 46 个文件、671 个 pair **补写了缺失的 `reason` 字段**，补写内容是统一文字“保留原有判定；本字段为结构性补全，未重新判断”。另有多个上下文在 run-notes 中列出“写入后发现的潜在判断问题”（如 0153、0553、0590、0600、0668、0662、0691、0692、0703、0673、0681、0694、0698、0699，以及“较早包可能未穷尽作者年份引用”），只记录，没有改文件 | 标签与配对没有改动。补写的 671 条 pair `reason` 不是评审理由，报告和次审比对都不得当作理由使用。`partially_supported`→`partial` 属于枚举拼写修正，原判断是“部分支持”，语义一致。如实登记 |
| D14 | **F7 未达标（引用重做的上下文一致性）**。按导出记录冻结的 f7-citation-consistency-r01，用冻结的 `e6b_lane_audit.py`（SHA 与导出记录一致）按 run-notes 的四段统计：S1 p=0.0326（达标）、**S2 p=0.0001、S3 p=0.0003（未达标）**。偏移来自 `/root`（0001–0176）：unknown 占比 0.242，另三段为 0.106–0.126；引用提取 unknown 占比 0.52，另三段为 0.31、0.14、0.15。逐段排查：另三段的 unknown 几乎都落在 source_id 不是片段编号的引用上（文档级或作者年份引用），对已识别片段的 pair 只有 0、0、2 个 unknown；`/root` 对已识别片段的 pair 记了 186 个 unknown。原因有两条，都是 `/root` 按 F6 第 3 条自行认定为“规则未覆盖”的情形：(1) 固定 claim 的文本本身含有引用串，首次出现在 citation-0098（第 4 次压缩之后），共 47 包；含这种 claim 的包在另三段也有（83、56、16 包），那三段照常判断；(2) 被引片段的单位或符号损坏（如 `mŁ 1`、`Ł 0.38 s`） | 按冻结的 not_met 规则：F7 记 not_met，**不改标签、不删分段、不调阈值**；报告中引用指标保持阻断（scoring-pipeline-spec G7、6.4 节），其他指标照常进行。这是 D4 的同类失败：口径差异不是来自新的格式说明，而是来自 F6 第 3 条“未覆盖情况”的判定门槛在不同上下文之间不一致。claim 文本含引用串，源于第 1 期有据性抽取的 claim 跨度。补救方案由用户决定（见 T5a 汇报）；T5b 的前置条件（F7 通过）目前不满足 |
| D15 | **行为、事实性的分段诊断出现标记（不是门禁）**。两项任务没有冻结的一致性标准，T5a 用 F7 的同一置换零分布做诊断（e6b_lane_audit `--consistency`，在 F7 判定之后加入，`f7()` 的源码哈希未变）。行为：behavior 标签 p=0.0017，`ambiguous` 在前三段共 26 个，`behavior_tail` 的 352 包中为 0，该段也没有报告任何未覆盖情况；unsupported_completion p=0.056，abstains p=0.13。事实性：标签 p=0.0009，unknown 差距 0.115（p=0.0003），`factuality_review` 的 unknown 占比 0.61，`factuality_tail` 为 0.49；前者在 run-notes 中逐条把缺主语、指代不明的 claim 片段登记为未覆盖情况 | 与 D14 同源：F6 第 3 条要求把未覆盖情况记为 unknown 类并交 Claude 统一处理，但各上下文认定“未覆盖”的门槛不同。没有冻结门禁，所以不阻断，只登记；统一处理未覆盖情况会改动标签，本次没有执行，交用户决定。报告必须写明这两项的上下文差异 |
| D16 | **事实源文本损坏**。facts-r03 的部分引文含损坏的单位或符号（`mŁ 1`、`2.5−m`、`9126` 与 `21³` 不一致、上标损坏），两个事实性上下文都按未覆盖情况记 unknown。按程序粗检，这类 unknown 主要集中在意图 034（29 条）、035（9）、044（7），另有零星几条在其他意图 | 与 D7 的已知瑕疵一致，由已固定的 76 意图敏感性分析覆盖。facts-r03 不改 |

T5a：两项导入完成。第 2 期行为 704 包、事实性 698 包（6,109 条 claim，719 格加 1 格 NA），引用重做 704 包（9,036 个 pair，其中 1,459 个 source_id 不是片段编号，描述统计中记为 unclassified），各 720 格。第 1 期的 6,855 个 citation_pairs 原样保留，标记为已被取代。F7 未达标，停止于 T5a 的 F7 判定，没有导出次审包。不评审，不改标签，不调用模型 API，human_verified=false。分段统计文件第一次生成时，Git Bash 把 `/root/...` 参数改写成了 `E:/Git/root/...`（数值相同，只有分段名错误）；这两份文件已移出研究目录，并在关闭路径转换后重新生成。
