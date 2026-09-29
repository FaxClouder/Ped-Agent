# PEARL：PedRAGent 分层评价框架

*PedRAGent 的 RAG / Agentic RAG 评价流程与指标体系入口 · status: target*

**PedRAGent 是本项目研究和构建的系统；PEARL 是用于评价 PedRAGent 的方法框架，不是另一个系统。** PEARL 是 *Pedestrian Evidence-based Assessment of Retrieval-augmented Language Systems* 的缩写，中文可称"面向行人交通领域 RAG 与 Agentic RAG 的证据驱动评估框架"。它规定评价对象、标注与指标口径、静态 RAG 与 Agentic RAG 的对照实验，以及结果和成本的报告方式。

PEARL 的结构是**四层顺序链条（检索 → 证据充分性 → 答案正确性 → 忠实与拒答）+ 一个控制器（Agent 决策）+ 一个横切维度（成本）**。论文和项目以 PedRAGent 为主线，PEARL 作为验证系统效果的评价协议；使用 PEARL 名称不表示各层实验已经完成。

## 入口

**主文档：[PEARL-framework.md](PEARL-framework.md)** — 评价链条、层间接口约定、报告口径与编号映射。

[framework.md](framework.md) 是 2026-09-27 的原始框架定义，保留旧项目名 Ped-Agent 与旧编号作历史记录。两者冲突时以主文档为准。

## 目录结构

**目录名保留历史命名，其中的数字不是层编号**，按下表对应（映射同见 [PEARL-framework.md](PEARL-framework.md) §0.3）。

| 层 | 角色 | 目录 | 内容 | 状态 |
| --- | --- | --- | --- | --- |
| 1 Retrieval | 链条 | [layer-1-retrieval/](layer-1-retrieval/) | 检索召回：设计、指标、实验、统计方法、失败分类 | design 与指标完成，实验未运行 |
| 2 Evidence | 链条 | [layer-1.5-evidence/](layer-1.5-evidence/) | 上下文充分性 | 待设计 |
| 3 Answer | 链条 | [layer-2-answer/](layer-2-answer/) | 答案正确性 | 待设计 |
| 4 Grounding & Reliability | 链条 | [layer-3-grounding/](layer-3-grounding/)<br>[layer-4-reliability/](layer-4-reliability/) | 忠实性与引用<br>拒答与可靠性 | 待设计 |
| 5 Agentic | 控制器 | [layer-5-agentic/](layer-5-agentic/) | Agent 决策过程 | 待设计 |
| 6 Efficiency | 横切维度 | [layer-6-efficiency/](layer-6-efficiency/) | 成本与效率 | 待设计 |

跨层与支撑目录：

| 目录 | 内容 | 状态 |
| --- | --- | --- |
| [cross-layer/](cross-layer/) | 端到端对照、错误传播、压力测试 | 待设计 |
| [annotation/](annotation/) | 标注规范与质量分级 | 部分定义 |
| [datasets/](datasets/) | 开发集/测试集设计、题型体系 | 部分定义 |
| [reporting/](reporting/) | 主表模板、统计规范、发表清单 | 部分定义 |
| [references/](references/) | 指标来源文献与框架对比 | 部分完成 |

## 当前范围

本目录保存**拟采用的评价口径**，不代表各层指标已经实现或完成实验。当前代码、候选开发集结果及标签限制，分别以 [Knowledge-Base README](../../Knowledge-Base/README.md)、[Gold v5 实验说明](../../experiments/benchmark-gold-20260923/README.md) 和 [Stage 2 标注说明](../../experiments/stage2-annotation/README.md) 为准。

Layer 1 已完成设计与指标形式化：主指标为 Page-Hit@10（RARE PerfRecall 的页级近似），5 组检索对照，$N = 18$ 可计分 intent。因当前标注为页级单组，Coverage 与 Page-Hit 数值恒等，详见 [layer-1-retrieval/metrics.md](layer-1-retrieval/metrics.md) §6。Layer 2–6 目前只有 README 界定职责边界，六层实验全部未运行。

## 对外定位

给定当前样本量（$N = 18$ 可计分 intent）、页级标注、agent-adjudicated 标签来源和 15/18 题标注页为摘要页，PEARL 的差异化**不立在检索效果的实证结果上**，而立在方法论上。三条可以现在主张：

| 卖点 | 内容 | 依据 |
| --- | --- | --- |
| 跨语言检索不对称的评测设置 | 语料 104 篇全英文、Gold 查询含中文，词法检索在中文侧结构性失效。对照组含 BM25 英文译文变体以隔离语言因素 | [layer-1-retrieval/experiments.md](layer-1-retrieval/experiments.md) RQ1.2、[datasets/](datasets/) |
| 归因不重复计数 | 层间契约规定每层只对本层新增失败计分：命中正确论文但片段不含目标信息，Layer 1 不算命中；Layer 1 命中而展开后仍不足，算 Layer 2 失败不回溯 | [PEARL-framework.md](PEARL-framework.md) §2 |
| 口径透明 | 主动声明标注来源为 agent-adjudicated、定位粒度为页级、Coverage 在当前标注下退化、标注页集中于第 1 页 | [reporting/](reporting/) 声明口径表 |

"分层评测"本身不是卖点——RAGAS、ARES、RGB、OmniEval 都是多维度评测。可主张的是层间契约与不重复计分规则。

暂不主张：领域条件/单位约束（设计已写入 §6，但当前标注无多条件用例可演示）、chunk 级定位精度、人工 Gold、样本规模。

## 已知口径差异

在使用既有数据填入 PEARL 表格前，需要先处理三项差异：

1. PEARL 原文将一个完整证据组内的必要证据设为 AND、替代证据组间设为 OR；当前 Gold v2 评分器将必需组间设为 AND、组内替代来源设为 OR。两者的完整证据分数不能直接混用。
2. PEARL 计划主报 `@10`，当前 Gold v5 开发集主报 `@5`。既有 Top-K 离线重算不是独立检索运行。
3. 答案、忠实性、拒答及 Agent 过程指标在 PEARL 中是目标设计。当前开发集标签和已执行结果的适用范围须按上述实验说明单独标注，不得写成封存测试或人工 Gold 的结果。

现有 `paper/evaluation-reports/` 与 `experiments/` 保持原路径；后续实验只有在指标定义、标注版本和输入哈希固定后，才可声明为 PEARL 对照结果。
