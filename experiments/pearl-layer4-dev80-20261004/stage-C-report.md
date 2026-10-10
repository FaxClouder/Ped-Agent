# PEARL Layer 4 阶段 C 核验报告

*原20题五臂100回答的固定输出评价 · status: current · 2026-10-04*

C100已完成全量独立主审、次审及第三裁决；1402个最终原子、1297个实际引用配对、400个任务评审链、2553项文件SHA绑定通过保存输出独立复算。当前不是D400交付。

|臂|回答数|声明数|题宏有据性下界|事实解析覆盖微平均|complete/partial/none|拒补TP/FN|
|---|---:|---:|---:|---:|---|---|
|A0-4096|20|280|0.9861|0.4464|{'complete': 18, 'partial': 2}|0/2|
|A0-8192|20|277|0.9922|0.4657|{'complete': 18, 'partial': 2}|0/2|
|A1-4096|20|287|0.9797|0.4251|{'complete': 16, 'partial': 3, 'none': 1}|1/3|
|A1-8192|20|365|0.9671|0.3699|{'complete': 18, 'partial': 2}|0/2|
|Aref-8192|20|193|0.9921|0.9067|{'complete': 20}|0/0|

原子数改变的声明已实际源文两审；只有六个语义字段完全相同的原子按原审查精确复用，逐原子记录原packet/decision SHA及旧ID，独立验证器检查标签、源证据和理由不变。冻结原子规范化不能把9126=21³实质计算断言缩成仅source印字，C21最终两个歧义均unknown。

C83实际引用作用域无法完整确定，保留citation_extraction_unknown；不把未确定分母当0。无拒补行为的额外局限不进入拒答理由准确性分母。

引用precision为NA共23条：7条无可解析实际pairs，16条scope/extraction未知；recall为NA共16条。宏微平均仅用适用集合，微平均precision有效分母为1030/1297 pairs，recall有效分母为1123/1402 claims，不把全部分母混入适用均值。独立工程审核已逐条严格检查636个精确复用atom、46个cell；检查器的新增字段遗漏漏洞修复后54项测试通过，C100在独立核验r02中再次通过，科学标签与分数未变。

[保存评分](../../outputs/pearl-layer4-dev80-20261004-01/C100-scores-final-r01.json)、[独立核验](../../outputs/pearl-layer4-dev80-20261004-01/C100-independent-verification-r01.json)、[最终选择链](../../outputs/pearl-layer4-dev80-20261004-01/C100-final-selection-r04.json)。下一步仅D剩余300、固定60二审，C100整行复用。
