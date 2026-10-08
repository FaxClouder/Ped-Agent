# Layer 3: Answer Correctness

*答案正确性评价 · status: current · 2026-09-28*

> **执行状态（2026-10-07 同步）**：本页是协议说明；80 题开发评价已执行，结果与限制见[Layer 3 实验入口](../../../experiments/pearl-answer-dev80-20261004/README.md)。下文中“待定义”“尚未执行”等表述保留为协议起草时的状态。

> **编号**：本层原编号为 Layer 2（目录 `layer-2-answer/`），v1.1 起为 Layer 3。变更理由见 [PEARL-framework.md](../PEARL-framework.md) §8.4。

Layer 3 在 Layer 2 给出的上下文上评价生成答案的正确性。评价的失败模式是**读错证据**：上下文含有正确信息，但答案与参考答案不符。

## 职责边界

| 项目 | 归属 |
| --- | --- |
| 答案与参考答案是否一致 | 本层 |
| 必要 claims 是否覆盖 | 本层 |
| 多证据是否完成跨来源整合 | 本层 |
| 答案是否有证据支持 | Layer 4 · Grounding |
| 答案是否符合客观事实 | Layer 4 · Grounding（Factuality） |
| 该拒答却作答 | Layer 4 · Reliability |

**对照基准**：Layer 3 对照参考答案。这与 Layer 4 的 Faithfulness（对照系统本次看到的证据）和 Factuality（对照 Gold 事实）不可互换，见 [PEARL-framework.md](../PEARL-framework.md) §2.3。

## 待定义指标

来自 [framework.md](../framework.md) §3：

| 指标 | 原始口径 |
| --- | --- |
| Answer Correctness | 按题型评分：事实题归一化匹配；数值题单位归一化后按容差判对并报 MAE/相对误差；比较和综合题按必要 claims；机制题按预先制定的 rubric。总体宏平均前先把各题型映射到统一 0–1 量表 |
| Claim Coverage | 正确覆盖的参考必要 claims / 参考必要 claims |
| Integration Success | 多证据题是否完成跨来源整合 |

## 按题型的评分细则

规划 `rubrics/` 子目录，每种题型一份：

| 文件 | 题型 | 关键问题 |
| --- | --- | --- |
| `rubrics/factual.md` | 单来源事实 | 归一化规则（同义词、缩写、语言变体） |
| `rubrics/numerical.md` | 数值/表格 | 单位归一化、容差来源、MAE 报告口径 |
| `rubrics/comparison.md` | 跨论文比较 | 必要 claims 的拆分粒度 |
| `rubrics/mechanism.md` | 机制解释 | rubric 维度与评分锚点 |
| `rubrics/conditional.md` | 条件推理 | 条件是否必须显式陈述 |

## 设计时须解决的问题

1. **数值容差的来源**：容差不能事后拟合。新标注须记录单位、条件、约数与来源冲突；没有来源支持的绝对容差不得用于自动评分，原文冲突也不得强行选单值。

2. **统一量表的映射**：各题型评分尺度不同（二值匹配 vs. 连续误差 vs. rubric 等级），宏平均前的映射方式须写定，且不得在看到结果后调整。

3. **英文答案的评判**：当前主实验使用英文查询，须在新协议中固定答案语言、术语归一化及英文改写的 intent 汇总方式，并与 Layer 1 的统计单位保持一致。

4. **自动评审器的校准**：LLM judge 须先在开发集上，以独立构建并复核的参考答案、固定评分锚点和独立 Agent 裁决检查一致性，报告分歧与裁决依据。依照[研究评估与审查验收标准](../../../docs/research-review-standard.md)，完成验证的 Agent 评估默认作为正式内容；只有用户明确要求本环节人工审查时，才将人工标注对齐纳入验收前置条件。本层校准已在 Layer 3 开发实验中执行（见页首执行状态）。

5. **参考答案的状态**：新 PEARL 参考答案须独立构建并标明来源、争议与质量等级；旧候选答案不转入新评估。

## 文档规划

| 文件 | 内容 |
| --- | --- |
| `design.md` | 目标、范围、题型体系、量表映射 |
| `metrics.md` | 三个指标的形式化定义 |
| `experiments.md` | 生成器对照、评审器校准实验 |
| `rubrics/*.md` | 各题型评分细则 |

## 前置依赖

- Layer 2 冻结上下文组织规则
- 新 PEARL 参考答案构建并完成复核
- LLM judge 与固定评分锚点、独立复核参考答案的一致性校准；人工审查仅在用户明确要求时作为前置条件
