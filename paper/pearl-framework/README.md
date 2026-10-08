# PEARL：PedRAGent 分层评价框架

*PedRAGent 的 RAG / Agentic RAG 评价流程与指标体系入口 · status: current · 状态表同步至 2026-10-07*

**PedRAGent 是本项目研究和构建的系统；PEARL 是用于评价 PedRAGent 的方法框架，不是另一个系统。** PEARL 是 *Pedestrian Evidence-based Assessment of Retrieval-augmented Language Systems* 的缩写，中文可称"面向行人交通领域 RAG 与 Agentic RAG 的证据驱动评估框架"。它规定评价对象、标注与指标口径、静态 RAG 与 Agentic RAG 的对照实验，以及结果和成本的报告方式。

PEARL 的结构是**四层顺序链条（检索 → 证据充分性 → 答案正确性 → 忠实与拒答）+ 一个控制器（Agent 决策）+ 一个横切维度（成本）**。论文和项目以 PedRAGent 为主线，PEARL 作为验证系统效果的评价协议；使用 PEARL 名称不表示各层实验已经完成。

## 入口

**主文档：[PEARL-framework.md](PEARL-framework.md)** — 评价链条、层间接口约定、报告口径与编号映射。

[framework.md](framework.md) 是 2026-09-27 的原始框架定义，保留旧项目名 Ped-Agent 与旧编号作历史记录。两者冲突时以主文档为准。

## 目录结构

目录名与层编号一致。Layer 4 由两个目录承载，两部分指标分别汇总、不构造合成分数。

| 层 | 角色 | 目录 | 内容 | 状态 |
| --- | --- | --- | --- | --- |
| 1 Retrieval | 链条 | [layer-1-retrieval/](layer-1-retrieval/) | CEGR 与覆盖／排序指标、英文四方法对照、统计与失败分类 | 已执行：[80 题开发对照](../../experiments/pearl-retrieval-dev80-20261003/README.md)（含 [Gold r02](../../experiments/pearl-retrieval-gold-revision-r02/README.md)）与 [200 题独立评价](../../experiments/pearl-retrieval-eval200-20261003/evaluation-analysis-2026-10-03.md)；R4 CEGR@10 为 139/200 |
| 2 Evidence | 链条 | [layer-2-evidence/](layer-2-evidence/) | 上下文充分性 | 已执行 80 题开发评价：[child／parent × 4K／8K](../../experiments/pearl-evidence-dev80-20261004/README.md)，parent 8K CGC 71/80；200 题未运行 |
| 3 Answer | 链条 | [layer-3-answer/](layer-3-answer/) | 答案正确性 | 已执行 80 题开发评价：[四实际臂＋完整参考，400 份生成](../../experiments/pearl-answer-dev80-20261004/README.md)，Strict 最高 61/80；200 题未运行 |
| 4 Grounding & Reliability | 链条 | [layer-4-grounding/](layer-4-grounding/)<br>[layer-4-reliability/](layer-4-reliability/) | 忠实性与引用<br>拒答与可靠性 | 已执行 80 题开发评价：[同 400 份回答，最终 r03](../../experiments/pearl-layer4-dev80-20261004/README.md)；200 题未运行 |
| 5 Agentic | 控制器 | [layer-5-agentic/](layer-5-agentic/) | Agent 决策过程 | 待设计 |
| 6 Efficiency | 横切维度 | [layer-6-efficiency/](layer-6-efficiency/) | 成本与效率 | 待设计 |

跨层与支撑目录：

| 目录 | 内容 | 状态 |
| --- | --- | --- |
| [cross-layer/](cross-layer/) | 端到端对照、错误传播、压力测试 | 待设计 |
| [annotation/](annotation/) | 标注规范与质量分级 | 部分定义 |
| [datasets/](datasets/) | 开发集/测试集设计、题型体系 | [80 开发题冻结、200 评估题已用于 Layer 1 独立评价](../../experiments/pearl-dataset-80-200-20261003/README.md)；Agent-reviewed，human_verified=false |
| [reporting/](reporting/) | 主表模板、统计规范、发表清单 | 部分定义；已有 [Layer 1–4 结果汇总与架构问题分析](reporting/layer1-4-results-and-architecture-review-2026-10-05.md)（2026-10-05） |
| [references/](references/) | 指标来源文献与框架对比 | 部分完成 |

## 当前范围

当前 Retrieval 语料采用 [106 篇 Adobe-only 来源版本 -02](datasets/retrieval-corpus/README.md)，两篇仅有 PyMuPDF 解析的文献暂不纳入。此前 108 篇全 PyMuPDF 临时切块的 R1 试标保留作沿革，不能作为此语料版本的结果；Layer 1–4 实验与切片研究均使用该冻结资产（106 篇、6,433 个 child）。

本目录是**后续评估工作的框架与方法底座**，规定评价对象、层间契约、指标定义、实验设计和报告规则。旧评估题集、标签、索引快照、排名及结果不进入 PEARL 实验；它们仅保留为历史研究记录。新实验须按 PEARL 协议重新定义和冻结输入、标注与配置，不能重算旧输出后改称 PEARL 结果。

算法模块的改进是具体实验中的被比较配置。解析、切块、检索器、融合与重排的变化应在实验中控制和记录，不因某个配置的结果而改变 PEARL 的层间契约或指标定义。Layer 1 已重写为 retrieval-v0.2，规定 80 个开发和 200 个独立评估 intent、四组方法及配套统计；[106 篇 Adobe-only 的 8 题 R1–R4 开发初步对照](../../experiments/pearl-index-106-adobe-20260929/README.md#8-题-adobe-only-开发对照)之后，80 题开发对照与 200 题独立评价均已完成。旧 108 篇 PyMuPDF 的[单组 R1 试标](datasets/retrieval-pilot/preliminary-r1-2026-09-29.md)不属于新资产的对照成绩。

**当前实验进度（2026-10-07）**：Layer 1 有 200 题独立评价；Layer 2–4 只在 80 题开发集上完成，尚无 200 题独立全链评价；Layer 5、Layer 6 与跨层评价未开始。切片与上下文恢复研究（[当前入口](../../experiments/pearl-chunking-dev80-20261005/README.md)）已完成 E0–E4 并冻结三套配置，E5 的 720 个答案已生成，6B 评价由[外部裁判工作包](../pearl-6b-judge-workpackage/README.md)进行中。各结果以实验目录与[汇总报告](reporting/layer1-4-results-and-architecture-review-2026-10-05.md)为准。

**当前 Retrieval 研究范围**：新主实验采用英文文献语料和英文查询。语料来源、版本及题集均须重新定义；中英差异不作为本轮研究问题或主要实验因素。

## 对外定位

PEARL 的定位首先是可复核的评估方法，而非某个检索算法的成绩。现阶段可作为设计目标讨论的特点是：

| 卖点 | 内容 | 依据 |
| --- | --- | --- |
| 科学证据检索 | 以必要事实、适用条件和替代证据组评价英文文献检索 | [datasets/](datasets/)、[layer-1-retrieval/](layer-1-retrieval/) |
| 归因不重复计数 | Layer 1 评价原始 Top-K child 的证据内容，Layer 2 评价最终上下文的充分性；同页定位不等于内容命中，parent 补证单列且不追改 Layer 1 | [PEARL-framework.md](PEARL-framework.md) §2 |
| 口径透明 | 每次实验声明新标注的来源、定位粒度、证据结构和指标适用范围 | [reporting/](reporting/) |

"分层评测"本身不是卖点——RAGAS、ARES、RGB、OmniEval 都是多维度评测。可主张的是层间契约与不重复计分规则。

具体样本规模、定位粒度、标注质量与检索性能须由新 PEARL 数据和实验确定，当前不作实证主张。

## 旧材料边界

[framework.md](framework.md) 保留历史设计；Layer 1 原有细化草案已由新协议替代。依赖旧 Gold、Stage 2、旧索引或旧样本数的安排不再是执行条件。后续实验只有在指标、语义 Gold、输入和算法配置按新协议固定，且输出支持映射完成核验后，才可报告 PEARL 对照结果。
