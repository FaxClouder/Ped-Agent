# PEARL Layer 3 Answer 冻结实验协议

*本轮五臂与统计口径 · status: current · protocol r01 · 2026-10-04*

本文件冻结实验规则，不表示真实答案、参考验收或校准已经完成。执行范围限原80题开发集及其中原20题子集；不重跑Retrieval/Evidence，不继续Layer 4/5，不要求人工审查。仅新增独立实验资产，保留dirty工作区与所有旧科学输出。

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
