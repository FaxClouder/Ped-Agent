# PEARL Layer 4 dev80 评价协议

*状态：current；r01口径；合成锚点已冻结，尚未实际校准，不代表80题评价完成。*

Layer 3沿用旧冻结参考与旧判分；Layer 4分别评价实际context有据性、独立源文事实准确性、实际claim–citation配对以及可靠性。原PDF、完整parent及参考不得补成实际context支持。

## 输入与盲评

校准输入位于`../../outputs/pearl-layer4-dev80-20261004-01/calibration/anchors-r01.json`，冻结expected另存`../../outputs/pearl-layer4-dev80-20261004-01/calibration/expected-r01.json`。构造者不担任实际校准judge。judge不能读取expected；当前尚无校准通过结论。

分三次投递：answerability仅接收query/context/必要结论；grounding与citation接收query/context/raw_answer及其SHA，不接收独立事实；factuality接收claims与独立事实定位，不用context推导真值。行为在answerability独立固定之后评价。合成独立事实包是人工定义的合成世界事实，不是假称真实论文依据。

## 抽取与统计

抽全部可核查事实，保留Unicode字符区间[start,end)、UTF-8 SHA、条件与全部重复出现区间。相同事实和条件去重，数值/关系按独立职责拆分，元缺口声明只用于理由核验。不可静默漏掉难拆claim，标extraction_unknown。

N=S+P+U+C+X。Faithfulness=[S/N,(S+X)/N]；广义未支持=[(P+U+C)/N,(P+U+C+X)/N]；context冲突=[C/N,(C+X)/N]。分别列P/U/C率。N=0全部NA；分母本身未知时点估计与固定N区间NA。

Factuality=[T/N,(T+Xf)/N]，另报已解析T/(T+F)和解析覆盖率(T+F)/N；源文范围外为unknown。每臂同时报题宏平均与claim微平均，主指标题宏平均Faithfulness；报告分母与NA，不把claims当独立统计样本。

Citation Precision为supported实际pairs/全部实际pairs，unknown给上下界；无pairs为NA。invalid纳入分母；outside-context单列，不能得可见证据支持分。Recall为至少有一个正确实际pair的事实claims/应引用事实claims；事实作答无引用为0，纯拒答为NA。

可靠性正类是partial/none，complete是负类。pure_abstain与真正bounded_partial均拒绝补全，full_answer/unsupported_completion不拒绝。TP/FP/FN/TN按此定义；P=TP/(TP+FP)，R=TP/(TP+FN)，F1=2TP/(2TP+FP+FN)，False Answer=FN/(TP+FN)，误拒=FP/(FP+TN)，零分母NA。unknown从确定表剔除但报告覆盖率及最坏/最好界。理由correct/incorrect/unknown独立列出，无拒答时null。

## 冻结与验收

40锚点分为supported/partial/unsupported/contradicted各8、pure_abstain4、bounded_partial4；类型用于案例构造，不是整体打分标签。8种哨兵全部必须通过。抽取完整与区间正确、resolved grounding/factuality/citation、behavior、answerability分别≥95%，分别记录真实分母，不能总体平均遮蔽失败。

实际judge逐包评审，另角色或程序依据expected独立复算。失败修订prompt/rubric另存r02，保留r01并重校准全部相关锚点。所有规则在真实C阶段前冻结，禁止按实际成绩修改定义。

固定算例：N5(S2/P1/U1/C0/X1)有据性与广义未支持均[.4,.6]；N0为NA。三pairs两有效一invalid Precision=2/3；三事实claims两正确引用 Recall=2/3。TP2/FP1/FN1/TN2得P/R/F1=2/3、False Answer/误拒=1/3；unknown不进TN，无正类Recall/False Answer为NA。验证必须检出label/quote区间/引用身份/输入SHA/score篡改，摘要与行级复算不得调用同一评分实现。
