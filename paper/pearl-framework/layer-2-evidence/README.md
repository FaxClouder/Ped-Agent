# Layer 2: Evidence Sufficiency

*上下文充分性评价 · status: 待设计 · 2026-09-28*

> **编号**：本层即 PEARL Layer 2，原编号 Layer 1.5。目录名 `layer-1.5-evidence/` 保留历史命名，未改名。映射见 [PEARL-framework.md](../PEARL-framework.md) §0.3。

Layer 2 接收 Layer 1 的 Top-K chunks，按固定规则展开父上下文，评价送入生成器的上下文是否足以支持答案。评价的失败模式是**证据不够**。

本层是顺序链条的正式一环，不是 Layer 1 的子步骤：它有独立失败模式、独立指标和与上下游的不重复计分契约。但它**不含新的检索调用**——展开规则固定，只消费 Layer 1 输出的 parent ID。

## 职责边界

| 项目 | 归属 |
| --- | --- |
| chunk 是否进入 Top-K | Layer 1 |
| 父上下文展开规则 | 本层 |
| 展开后上下文是否充分 | 本层 |
| 系统对"充分/不足"的自我判断准确性 | 本层 |
| 上下文噪声比例 | 本层 |
| 基于上下文的答案正确性 | Layer 3 |

**不重复计分**：Layer 1 命中但展开后仍不足，算本层失败，不回溯为 Layer 1 失败。Layer 1 未命中的信息单元，本层不再重复记为失败。

## 待定义指标

来自 [framework.md](../framework.md) §3 的原始定义：

| 指标 | 原始口径 |
| --- | --- |
| Evidence Coverage | 已由输入上下文满足的必要 evidence requirements / 全部必要 requirements。可按 atomic requirement 微平均，另报题目宏平均 |
| Sufficiency Accuracy | 系统预测"现有上下文充分/不足"与人工 Gold 一致的比例；同时报两类混淆矩阵，尤其是把不足误判为充分的次数 |
| Context Relevance | 上下文的相关性 |
| Noise Ratio | 进入生成器的无帮助片段或 token 占比 |

## 设计时须解决的问题

1. **展开规则形式化**：`parent-child-v1` 的展开范围须精确定义——只取直接 parent，还是含 sibling chunks；是否去重；token 预算如何分配。规则变动会改变本层全部指标。

2. **与 Layer 1 指标的关系**：Evidence Coverage 的分母与 Layer 1 的必要信息单元数是否同一套。若同一套，则 Layer 1 的 Page-Coverage 与本层 Evidence Coverage 的差值正好度量"parent 展开的增益"，这是本层的核心量。

3. **充分性 Gold 标签**：Sufficiency Accuracy 需要"该上下文是否充分"的参考标签。当前 Stage 2 标注无此字段，须明确标注方案与成本。

4. **Noise Ratio 的标注单位**：片段级还是 token 级，须固定。无帮助的判定标准须可操作。

5. **L3.x 失败的交接**：[Layer 1 失败分类](../layer-1-retrieval/failure-taxonomy.md) 中 L3.x 标注了 `parent_recoverable` 字段，本层须据此验证展开规则是否真的挽回了这些案例。

## 文档规划

| 文件 | 内容 |
| --- | --- |
| `design.md` | 目标、范围、展开规则、与上下游的接口 |
| `metrics.md` | 四个指标的形式化定义与标注前置条件 |
| `experiments.md` | 展开规则对照实验、充分性判断评测 |

## 前置依赖

- Layer 1 选定并冻结检索配置
- 充分性 Gold 标签的标注方案确定（见 [annotation/](../annotation/)）
