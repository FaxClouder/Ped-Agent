# PEARL 6B 引用重做 r03

*T3c 产物：引用重做的片段边界（F2）、重做包与 r03 格式说明（F3、F4）、校准复核方法（F5）、执行规则（F6）、F7 验收标准草案 · status: current · 2026-10-08*

本文记录 T3c 实际完成的内容。标为“草案”或“T3e”的部分还没有冻结或执行。偏差登记见 [incidents D8](incidents-and-deviations.md)，任务顺序见 [6b-work-plan.md](6b-work-plan.md)。

## 产物

| 产物 | 位置 | 说明 |
| --- | --- | --- |
| F2 片段边界审计（冻结） | [fragment-boundaries-r03.json](../../outputs/pearl-chunking-dev80-20261007-16/research/fragment-boundaries-r03.json) | 240 个 E5 context 与 40 个校准锚点 |
| 重做设计与研究包干跑、F7 草案 | [citation-redo-design-r03.json](../../outputs/pearl-chunking-dev80-20261007-16/research/citation-redo-design-r03.json) | 只在内存中构建 704 包，没有导出 |
| F5 比对方法（评审前冻结） | [calibration-plan-citation-r03.json](../../outputs/pearl-chunking-dev80-20261007-16/calibration/calibration-plan-citation-r03.json) | 方法、阈值、门禁条件 |
| T3c 导出记录 | [export-calibration-citation-r03.json](../../outputs/pearl-chunking-dev80-20261007-16/calibration/export-calibration-citation-r03.json) | 各文件 SHA |
| 校准复核包 | [calibration-citation-r03/](calibration-citation-r03/README.md) | 40 包，待 T3d 评审 |
| r03 输入格式说明 | [e6b-citation-input-format-r03.md](../../experiments/pearl-chunking-dev80-20261005/e6b-citation-input-format-r03.md) | 附在冻结规则之后 |
| 校验器 | [validate_citation_responses.py](validate_citation_responses.py) | 只查格式；原 `validate_responses.py` 未改动 |
| 程序 | [e6b_fragments.py](../../experiments/pearl-chunking-dev80-20261005/e6b_fragments.py)、[e6b_workpackage.py](../../experiments/pearl-chunking-dev80-20261005/e6b_workpackage.py)（`fragments-audit`、`citation-dryrun`、`export/import --phase calibration-citation-r03`、`export --phase research-citation-r03`）、[e6b_lane_audit.py](../../experiments/pearl-chunking-dev80-20261005/e6b_lane_audit.py)（`--f7`） | |

## F2：片段边界

E5 context 按 source-assembly-r01 序列化：每个来源块是 `[Source [[doc_id,source_version,element_id,start,end],...]]` 加换行和正文，块之间空一行。块内各片段依次是 `element_text[start:end]`；后一片段接着同一 element 的上一个 end 时不加分隔，否则加 `\n\n`。所以只看块头区间，就能算出每个片段在 context 中的位置。

程序 `e6b_fragments.derive` 只用块头推算。一个块只有同时满足以下条件才标 `exact`：块头是合法的五元组列表；推算出的正文恰好结束在下一个块头之前（或 context 末尾）；每个分隔符都确实是空行。不满足的块标 `unaligned`，片段位置为 null，不作推测。另有两项独立核验，都不参与推算：

- 与冻结的组装记录（E3 `contexts-*-P0-4096-fixed_budget_main.jsonl` 的 `final.units`）对照块头、片段位置和正文；
- 与冻结的来源视图（`source-views-prepared.json`）逐片段对照原文。

| 配置 | context | 来源块 | 合并块 | 合并比例 | 片段 | 对不齐的块 |
| --- | --- | --- | --- | --- | --- | --- |
| B0 | 80 | 492 | 430 | 0.874 | 1,991 | 0 |
| C2 | 80 | 510 | 392 | 0.769 | 1,993 | 0 |
| C3 | 80 | 827 | 455 | 0.550 | 1,889 | 0 |
| 合计 | 240 | 1,829 | 1,277 | | 5,873 | **0** |

两项独立核验都是 240/240 通过。三个上下文文件的 SHA 与 5B 冻结记录（`final-config-freeze-r01.json`、`e5-call-plan-r01.json`）一致。研究有据性包用到的 240 个 context 全部在审计范围内。另有 50 个 context 含补充平面字符（如 emoji），所以说明中写明位置是 Unicode 码位，不是 UTF-16 单位。40 个校准锚点都是单块、单来源标签（`[Source S1 | p.1]`），没有合并块。

## F3：引用重做包

一个重做包就是原有据性包（`e6b_packets.build()` 重建，与身份映射逐包核对），只改三处：

| 字段 | 内容 |
| --- | --- |
| `claims_candidates` → `claims` | 第 1 期导入的有据性 claims：`claim_id`、原文 `text`、程序定位的 `occurrences`。不带标签、证据、理由、`normalized_claim`、`conditions` |
| 新增 `source_fragments`（紧跟 `context`） | 每块的 `block_id`、`alignment`、`header_span`、`body_span`，每个片段的 `fragment_id`（如 `B2-F3`）、`header_index`、`source`（块头原样标识）、`span` |
| `instruction` | 换成 r03 的简短说明：claims 已固定，只输出 citation_pairs 与 citation_extraction_unknown |

`query`、`context`、`raw_answer` 和两个 SHA 字段原样保留。输出中的 `source_id` 填 `fragment_id`，T5a 和评分流水线可以借此识别被引的块是否为合并块（[评分规格 6.4、第 9 节](scoring-pipeline-spec.md)）。

研究包干跑（T3c 只在内存中构建，没有写工作包）：704 包，绑定 720 格，没有精确重复；6,118 条 claims；5,376 个来源块，其中合并块 3,758 个，对不齐 0 个；单包消息 29,564–56,318 字节（中位数 35,116）。编号沿用有据性包：`citation-0030` 对应 `grounding-0030`。

grounding-0406 的主审没有抽出 claims，但回答里有引用。它照样出包，`claims` 为空，校验器只接受空的 `citation_pairs`。校准锚点 cal-33（纯拒答、无 claims）也是这样处理。

## F4：r03 规则文本

系统提示 = cgpt-r02 有据性系统提示中的全部判断规则（Layer 4 judge prompt、rubric、引用归属补充 r02、“本次任务 grounding”），**逐字不变**，程序核对：这部分的 SHA 为 `fea18fbb…`，cgpt-r02 原提示的 SHA 为 `925f68aa…`。只把末尾的 harness 输出格式换成两段：

1. [输入格式说明 r03](../../experiments/pearl-chunking-dev80-20261005/e6b-citation-input-format-r03.md)：只讲 `claims`、`source_fragments` 怎么读，以及位置的计数方式，不含任何判断口径；
2. Output format（citation redo r03）：只输出 `citation_pairs`（字段与冻结格式相同，`source_id` 填 `fragment_id`）、`citation_extraction_unknown`、`reason`，不得输出 claims。

r03 系统提示 SHA `82eb3eeb…`。

## F5：校准复核与比对方法（评审前冻结）

40 个包取冻结的有据性校准锚点，claims 取自通过校准的 cgpt-r02 有据性回答（cgpt-r02 的抽取一致率为 40/40）。比对在 T3e 用 `e6b_workpackage.compare_citation` 执行：

- 调用冻结的 `compare_calibration.compare`，代码不改。每个锚点的有据性输入 = cgpt-r02 的 claims 和 `extraction_unknown`，但 citation_pairs 换成 r03 回答，并用冻结的 `locate_grounding` 定位；可回答性、事实性、行为照用 cgpt-r02 的回答。
- **只看引用。** 门禁条件：`metrics.citation.agreement ≥ 0.95`（原阈值）；没有 `citation_schema` 失败（pair 数量和 (claim_id, citation_text, citation_span) 集合与 expected 相同）；8 个哨兵锚点都没有引用失败；40 个回答全部通过校验，引用全部定位成功。其他指标只作输入核对，必须等于 cgpt-r02 的结果。
- `citation_extraction_unknown` 和 `source_id` 只记录，不比对（冻结比对程序不比这两项）。
- 未通过时写 blocked，不改阈值、规则、说明或格式，也不导出研究包。

T3c 做过一次干跑：用 cgpt-r02 原有的引用回答代入比对得 36/36，哨兵全过；人为改动 3 个锚点的标签后判为未通过。干跑没有写任何记录。

**局限（报告必须写明）：** 40 个锚点都是单块、单来源，没有合并块。复核通过只能说明新格式没有扰动已校准的引用行为，不能证明合并块的处理正确。

## F6：执行规则

已写入 [calibration-citation-r03/README.md](calibration-citation-r03/README.md)，与 research-primary-2 的六条规则相同：说明逐字相同、派发模板固定；协调者不得下发判断规则，只能给固定回复；未覆盖的情况记 unknown 并写进 run-notes；机械修正留记录并备份；已写回答不得追加判断；显示时不得删改。另外明确不得打开 `calibration/`、`calibration-r02/`，那里有同一批锚点以前的回答。T3e 写研究包的说明时沿用同一文本。

## F7：分段一致性验收标准（草案，T3e 导出时原样冻结）

标准写在 `e6b_workpackage.F7_STANDARD`，统计由 `e6b_lane_audit.py --f7` 计算。

| 项 | 内容 |
| --- | --- |
| 分段 | 每个裁判上下文（协调者或子代理）为一段，范围取自 run-notes；一个上下文处理多段范围时合为一段。范围必须恰好覆盖每个包一次，否则不可评估，按不达标处理。只有一个上下文时，按 blind 顺序切成 4 个伪分段，检查前后漂移 |
| S1 | 分段 × pair 标签（7 类）列联表的 Pearson X² |
| S2 | 分段 × `citation_extraction_unknown`（按包）列联表的 X² |
| S3 | 包数 ≥ 30 的分段中，本段 unknown pair 比例与其余各段合并比例之差的最大绝对值（D4 的失效方式） |
| 零分布 | 10,000 次置换：把整个包（连同其全部 pairs）随机重新分到各段，各段包数不变；`random.Random(20261005)`；p = (1 + 置换统计量 ≥ 观测值的次数) / 10,001。置换的是包而不是 pair，因为同一包内的 pairs 不独立 |
| 达标 | p(S1) ≥ 0.01，p(S2) ≥ 0.01，p(S3) ≥ 0.01（没有 ≥ 30 包的分段时，S3 不适用） |
| 只作描述 | 各段标签比例；按被引块是否合并拆分（经 `source_id` → `source_fragments` 识别，识别不了记 unclassified）；各配置的标签比例（配置差异是研究对象，不作门禁） |
| 不达标 | 写 not_met；不改任何标签，不删分段，不改阈值。逐段排查：哪些分段推高了 S1–S3，对应的 run-notes（协调者往来、澄清、截断、续做），合并块与单片段块，事件前后的包。报告中引用指标标为 blocked（评分规格 G7、6.4），其他指标照常。向用户汇报发现和选项（例如在新上下文中按同一 README 重评受影响的范围，作为新修订），由用户决定 |

对照（用已作废的第 1 期引用标签，只读；此时还没有任何重做标签）：

| 分段方式 | S1 p | S2 p | S3（最大差，p） | 判定 | 预期 |
| --- | --- | --- | --- | --- | --- |
| 第 1 期实际上下文（D4） | 0.0001 | 0.0103 | 0.61，0.0001 | 不达标 | 不达标 |
| 交错分段（编号 mod 4） | 0.134 | 0.346 | 0.12，0.054 | 达标 | 达标 |
| 交错分段（mod 7） | 0.925 | 0.864 | 0.08，0.743 | 达标 | 达标 |
| 交错分段（mod 14） | 0.913 | 0.973 | 0.14，0.650 | 达标 | 达标 |
| 单段 → 4 个伪分段 | 0.0001 | 0.909 | 0.45，0.0001 | 不达标 | 第 1 期上下文按编号连续，应检出 |

**草案修改记录：** 最初的草案对 unknown 差用固定上限 0.10。交错分段把各上下文均匀混合，本不该报警，但它在 mod 4、mod 14 上给出 0.12、0.14 的差：unknown 在包内成簇，固定上限会误报。因此在 T3c 内、任何重做标签产生之前，把它换成同样由置换校准的 S3。

## 待决事项

- **单元上限。** 冻结上限 4,680 = Layer 3 720 + 144 + 72，加 Layer 4 2,880 + 576 + 288。实际主审 3,050 包（第 1 期 1,648、第 2 期 1,402）；加上引用重做 704，主审合计 3,754；次审至多 693，裁决至多 360。最坏情况合计 4,807，超出 127。只有当裁决实际用量不超过 233 时，合计才不超上限（校准复核 40 包未计入）。如果按分层单元核对，Layer 4 主审已有 2,346 包（可回答性 240、有据性 704、行为 704、事实性 698），加上重做 704 为 3,050，无论裁决用量多少都超过分项 2,880。需要用户在 T5b 核对单元数之前决定：引用重做是否计入、上限如何处理。T3c 没有改动任何上限。
- 研究包的 README（F6 文本）在 T3e 导出时写；导出程序 `export --phase research-citation-r03` 在 F5 门禁通过之前拒绝运行。
