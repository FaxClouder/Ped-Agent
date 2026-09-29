# Layer 3: Answer Correctness

*答案正确性评价 · status: 待设计 · 2026-09-28*

> **编号**：本层即 PEARL Layer 3，原编号 Layer 2。目录名 `layer-2-answer/` 保留历史命名，未改名。映射见 [PEARL-framework.md](../PEARL-framework.md) §0.3。

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

1. **数值容差的来源**：容差不能事后拟合。Stage 2 已记录 `rgq-048` 的约数 0.6 m 无来源支持的绝对容差，该类题须明确是排除还是改判定方式。`rgq-122` 原文同时出现 58% 与 59%，禁止强行选单值——这类题的评分规则须先定义。

2. **统一量表的映射**：各题型评分尺度不同（二值匹配 vs. 连续误差 vs. rubric 等级），宏平均前的映射方式须写定，且不得在看到结果后调整。

3. **双语答案的评判**：Stage 2 有中英双语参考答案。同一 intent 的两种语言答案是否分别评分再取均值，须与 Layer 1 的双语汇总约定（[metrics.md](../layer-1-retrieval/metrics.md) §8）保持一致。

4. **自动评审器的校准**：LLM judge 须先在开发集上与人工标注对齐并报告一致性。当前无此校准数据。

5. **参考答案的状态**：Stage 2 的 18 题有 `agent_reviewed_candidate` 双语候选答案，2 题为 `agent_disputed`。候选答案只能用于探索性分析，不能写成无争议的正确性标签。

## 文档规划

| 文件 | 内容 |
| --- | --- |
| `design.md` | 目标、范围、题型体系、量表映射 |
| `metrics.md` | 三个指标的形式化定义 |
| `experiments.md` | 生成器对照、评审器校准实验 |
| `rubrics/*.md` | 各题型评分细则 |

## 前置依赖

- Layer 2 冻结上下文组织规则
- 参考答案完成复核（当前为 agent-adjudicated 候选）
- LLM judge 与人工标注的一致性校准
