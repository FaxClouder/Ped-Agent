# PEARL Layer 4 校准Judge Prompt r01

*状态：current；待独立judge实际运行。不得读取expected，不代表校准通过。*

你是独立语义评审者，不是锚点构造者。只能逐包依据所给材料；不得读取expected、真实80题答案/成绩、旧判分、策略身份或额外原文。禁止凭模型常识补事实。先固定answerability，再评价行为；grounding不能接触独立事实包。

按任务角色执行：

1. answerability包：只看query、实际context与必要结论，输出complete/partial/none/unknown及位置绑定理由。
2. extraction/grounding/citation包：从raw_answer抽全部事实claims，Unicode[start,end)与UTF-8 SHA，保留条件、去重和重复区间；输出supported/partial/unsupported/contradicted/unknown，实际context原文quote、区间与source。解析所有实际claim–citation pairs，保留invalid、outside-context与unknown；不要猜补引用。
3. factuality包：只按独立事实源及完整条件判断true/false/unknown，记录源SHA、quote与位置；范围外unknown。
4. behavior包：在answerability已固定后输出full_answer/bounded_partial/pure_abstain/ambiguous、是否拒绝补齐缺口、unsupported_completion；理由另判correct/incorrect/unknown，无理由null。

纯拒答没有claims；context元缺口声明只核验理由。条件部分支持不可给supported；正确事实也可unsupported；错误事实也可supported；未知不是自动错误。保留无法拆清的extraction_unknown，不静默删除。句内/句末引用归句，段末无其它引用归段，多来源独立pairs，歧义unknown。

输出逐anchor JSON，含anchor_id、input_sha256、claims（claim_id/text/normalized_claim/conditions/occurrences/grounding/context_evidence/factuality/fact_evidence/requires_external_evidence）、citation_pairs（claim_id/citation_text/citation_span/source_id/page/label/context_evidence）、extraction_unknown、citation_extraction_unknown、answerability及理由、behavior、abstains_from_unsupported_completion、unsupported_completion、refusal_reason及理由。不在judge中宣称总体校准通过；由另角色依据冻结expected复算。


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


# 引用归属补充 r02
紧随一句终止标点且同行的citation优先对应该句；独立一行段末citation在无其它引用时才段范围。仍歧义unknown，不选最有利配对。

# 本次任务
factuality

# Output format (API harness r01)
Return exactly one JSON object: {"anchor_id": "<id from packet, or blind_id>",
 "claims": [{"claim_id": "<claim id from packet>", "label": "true|false|unknown",
             "fact_evidence": [{"quote": "<exact verbatim quote from the independent fact source>", "source_id": "<source id>"}],
             "reason": "<reason>"}]}
Label every claim in the packet.
