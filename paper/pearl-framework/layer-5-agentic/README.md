# Layer 5: Agentic Decision

*Agent 决策过程评价 · status: 待设计 · 2026-09-28*

Layer 5 评价 Agent 的证据需求规划、迭代检索、充分性判断与停止决策。评价的失败模式是**错误停止或过度检索**。

Layer 5 不是顺序链条中的一环，而是控制 Layer 1 / Layer 1.5 反复执行的决策器。

## 职责边界

| 项目 | 归属 |
| --- | --- |
| Agent 规划的证据需求是否匹配实际需求 | 本层 |
| 每轮检索是否取得对应证据 | 本层 |
| 停止时机是否恰当 | 本层 |
| 查询改写是否带来增益 | 本层 |
| 单轮检索的召回质量 | Layer 1 |
| 最终答案质量 | Layer 2/3 |
| 额外轮次的代价 | Layer 6 |

## 待定义指标

来自 [framework.md](../framework.md) §3：

| 指标 | 原始口径 |
| --- | --- |
| Requirement Coverage | 比较 Agent 计划的证据需求与 Gold requirements |
| Hop Retrieval Success | 逐轮判断所需 hop 是否取得对应证据，仅在有多跳/多证据 Gold 的子集上报告 |
| Premature Stop | 证据不足却停止的比例 |
| Over-retrieval | 证据已充分仍无必要继续的比例 |
| Query Rewrite Gain | 改写查询相对于原查询带来的完整证据组召回变化 |

**分母与判定时点须事先固定**：Premature Stop 与 Over-retrieval 的分母（全部题目还是发生停止决策的题目）和判定时点（每轮末还是仅最终轮）不同会给出不同数值。

## 消融梯度

来自 [framework.md](../framework.md) §4 阶段 3，规划 `ablation-design.md` 展开：

| 配置 | 内容 |
| --- | --- |
| A0 | No-RAG，仅参数化知识 |
| A1 | Static RAG，固定单次检索 |
| A2 | A1 + 需求规划/分解与迭代检索 |
| A3 | A2 + 充分性判断及停止 |
| A4 | A3 + claim 验证、修订/拒答 |

消融须在同一底层检索器和生成模型下进行，使每步的收益与成本可归因到具体模块。

## 设计时须解决的问题

1. **评测口径的固定**（[PEARL-framework.md](../PEARL-framework.md) §2.4）：多轮检索必须先明确是单轮还是最终合并的 Top-K。把多轮累计的全部证据直接与静态 Top-K 比较是不公平对照——前者的有效检索预算更大。合并口径下须同时报告累计检索量。

2. **Gold requirements 的来源**：Requirement Coverage 需要"该题实际需要哪些证据"的参考标签。Stage 2 的 `required_facts` 与 `evidence_group_ids` 可作起点，但当前 18 题全为单组单页，多跳子集为空，Hop Retrieval Success 无测试用例。

3. **多跳子集的构建**：Hop 指标仅在多跳/多证据 Gold 子集上报告。该子集须先存在——需要扩充跨论文比较、多数据点综合类 intent。

4. **停止判定的观测点**：判断"证据不足却停止"需要知道停止时的证据状态。这要求逐轮记录 query、新覆盖证据、充分性结论和停止理由，记录规范须在实验前写定。

5. **Query Rewrite Gain 的基线**：改写增益相对于原查询计算，须固定原查询的定义（首轮查询还是用户原始问题）。

## 文档规划

| 文件 | 内容 |
| --- | --- |
| `design.md` | 目标、范围、评测口径、逐轮记录规范 |
| `metrics.md` | 五个指标的形式化定义与分母约定 |
| `ablation-design.md` | A0–A4 消融梯度的配置与对照控制 |
| `experiments.md` | 消融实验、Hop 诊断、改写增益分析 |

## 前置依赖

- Layer 1 选定并冻结检索底座
- Layer 1.5 的充分性判断标签
- 多跳/多证据 intent 子集存在
- 逐轮日志记录规范写定
