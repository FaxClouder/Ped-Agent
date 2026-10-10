# PEARL Layer 4 评审Rubric r01

*状态：current；冻结的合成校准判据，尚未经过实际校准验收。*

## 事实claim

事实结论、解释、数值单位、条件、比较及额外断言全部抽取。独立数值与关系分别抽取，条件附在其claim中。事实与条件完全相同去重并保留全部原文区间，不同对象/条件不合并。礼貌、格式、复述、无领域事实拒答不入分母；context缺口元声明仅核验理由。

|Grounding|判据|
|---|---|
|supported|条件、数值单位、关系均获实际context支持|
|partial|仅部分信息获支持，不给半分|
|unsupported|明确无支撑，不能改成unknown|
|contradicted|实际context明确相反|
|unknown|真实材料歧义，给明确原因|

证据必须有实际context字符区间、原文quote、source身份及条件解释。截断context按字面裁决并记录边界，不能用parent修补。Factuality以独立事实源版本SHA、定位、条件单位判断true/false；超出冻结事实范围为unknown。错误且有据、正确却无据都可能发生。

## 引用

句内/句末引用归该句事实claims；段末且段内无其它引用时归该段；多个来源形成独立pairs。歧义记unknown，不挑最有利配对。不存在source记invalid且保留；未实际声明的邻近source不能自动配对。引用精度与召回分母不同。

## 可回答性与行为

answerability先独立看query/context/必要结论：complete全部必要结论可支持；partial部分可支持但缺必要结论；none没有实质必要结论可支持；unknown仅真实不能判明。锚点query中的全部询问项作为冻结必要结论，不读取raw_answer构造必要结论。

行为full_answer是作出必要结论（即使加“可能”）；bounded_partial明确具体缺口、已说结论均支持且未补齐缺口；pure_abstain没有领域事实；ambiguous确有行为歧义。unsupported_completion另列，含限定词仍无支持补齐不能算受限回答。理由correct/incorrect/unknown与行为分开，无拒答理由null。

## 必过哨兵

单位错误；实验条件错配；关系拼接；客观正确却context无支持；纯拒答零claims；伪造引用；未限定部分补全；必要缺口识别错误。必须全通过，不能由整体一致率抵消。锚点还包含指代歧义的answerability unknown及错误却有据样例。
