# Layer 4 · Grounding

*证据忠实与引用评价 · status: current · 2026-09-28*

> **执行状态（2026-10-07 同步）**：本页是协议说明；80 题开发评价已执行，结果与限制见[Layer 4 实验入口](../../../experiments/pearl-layer4-dev80-20261004/README.md)。下文中“待定义”“尚未执行”等表述保留为协议起草时的状态。

> **编号**：本目录是 PEARL Layer 4 的 **Grounding 部分**，原为独立的 Layer 3（目录 `layer-3-grounding/`）。Layer 4 的另一部分 Reliability 在 [layer-4-reliability/](../layer-4-reliability/)。合并理由见 [PEARL-framework.md](../PEARL-framework.md) §8.4，两部分分工见 §2.4。

本部分检验答案中的每条可核查 claim 是否获得所给证据支持，以及所标引文是否真正支持其对应 claim。评价的失败模式是**无依据推断**。

**与 Reliability 部分的关系**：两者合并为 Layer 4，因为回答同一问题的两面——答案是否只说证据支持的内容。Grounding 评价已作答内容的证据支持，Reliability 评价"是否应当作答"这一决策。**合并编号不等于混算**：两部分指标分别汇总、主表分别出现，不构造合成分数。

## 职责边界

| 项目 | 归属 |
| --- | --- |
| claim 是否被本次证据支持（Faithfulness） | 本部分 |
| claim 是否与客观事实一致（Factuality） | 本部分 |
| claim 是否与证据冲突 | 本部分 |
| 引文与 claim 的配对是否成立 | 本部分 |
| claim 是否与参考答案一致 | Layer 3 |
| 是否应当作答（拒答决策） | Layer 4 · Reliability |

**四个对照基准的区分**（[PEARL-framework.md](../PEARL-framework.md) §2.3）：Answer Correctness 对照参考答案；Factuality 对照 Gold 事实；Faithfulness 对照系统本次看到的证据；Citation Precision 判断所标来源是否真正支持对应 claim。事实正确但未被当前证据支持，仍属不忠实。

## 待定义指标

来自 [framework.md](../framework.md) §3：

| 指标 | 原始口径 |
| --- | --- |
| Faithfulness | 获所给检索证据支持的可核查 claims / 全部可核查 claims |
| Unsupported Claim Rate | 未获支持的可核查 claims / 全部可核查 claims |
| Factuality | 对照 Gold/事实判断结论是否成立 |
| Contradicted Claim Rate | 与检索证据或 Gold 明确冲突的 claims 占比 |
| Citation Precision | 实际引文中确实支持其对应 claim 的比例 |
| Citation Recall | 应由外部证据支持的回答 claims 中，具有有效引文支持的比例 |

## 设计时须解决的问题

1. **claim 抽取的可复现性**：Faithfulness 的分母是"全部可核查 claims"，该集合由抽取过程决定。抽取粒度不同会直接改变分母，从而改变指标值。抽取方法、模型版本和提示须固定并版本化，规划 `claim-extraction.md` 单独记录。

2. **"部分支持"的计分**：若采用三级标签（支持/部分支持/不支持），部分支持的计分规则须预先固定，不能在看到结果后选择有利口径。

3. **拒答输出的处理**：没有实质性回答 claim 的拒答输出，不把 Faithfulness 人为记为满分。拒答走 [Layer 4 · Reliability](../layer-4-reliability/) 计分，本部分须报告回答类指标的适用样本数。

4. **Citation 配对核验**：Citation Precision 须按 claim–citation 配对核验，不能只检验引文是否存在。这要求答案生成时就记录 claim 与引文的对应关系。

5. **领域特异的支持判定**：行人交通领域的数值、单位和实验条件须一并核对。证据给出 0.9 m 瓶颈的结果，答案陈述为 1.0 m 条件下成立，属不忠实而非近似正确。

6. **Factuality 的 Gold 来源**：Factuality 需要独立于检索证据的事实判断依据，须在新 PEARL 标注中明确其来源与成本。

## 文档规划

| 文件 | 内容 |
| --- | --- |
| `design.md` | 目标、范围、四个基准的区分、拒答处理、与 Reliability 部分的联合报告 |
| `metrics.md` | 六个指标的形式化定义 |
| `claim-extraction.md` | claim 抽取方法、粒度约定、版本化规则 |
| `experiments.md` | 忠实性评测、引文核验、评审器校准 |

## 前置依赖

- Layer 3 产出答案与 claim–citation 对应记录
- claim 抽取流程固定并版本化
- Factuality 的 Gold 事实标注方案确定
