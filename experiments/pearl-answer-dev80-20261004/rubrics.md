# PEARL Layer 3 语义裁决规则

*独立参考与答案评分规则 · status: current · rubric r01 · 2026-10-04*

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


## 独立角色与隔离

参考构建者只读查询、必要需求及冻结来源原文；复核者逐项核对候选参考与实际原文。两个角色分别使用fork_turns=none，不见旧答案、被测答案、context策略或成绩。裁决者应保存实际阅读、精确原文引文与适用范围，不用脚本自动生成语义结论。

答案judge只见query、匿名answer、冻结reference及本rubric。逐项记录targets/conditions/claims的correct、incorrect、missing、unknown，整合yes/no/unknown及数值抽取；语义unknown须注明具体歧义。严禁以字符串一致或引用存在代替语义判断。校准期望与盲评包分开。
