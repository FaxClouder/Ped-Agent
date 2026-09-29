# 标注规范与质量控制

*标注要素、质量分级、一致性验证 · status: 部分定义 · 2026-09-28*

本目录收录 PEARL 各层共用的标注规范。当前标注资产的实际状态见 [Stage 2 标注说明](../../../experiments/stage2-annotation/README.md)。

## 文档规划

| 文件 | 内容 |
| --- | --- |
| `annotation-guideline.md` | 统一标注指南：各字段定义、填写规则、示例 |
| `quality-tiers.md` | 标注质量分级（Tier 0–3）与发表适用性 |
| `gold-standard.md` | Gold 标准构建流程与冻结规则 |
| `inter-annotator-agreement.md` | 一致性验证方法与抽样方案 |

## 标注要素

来自 [framework.md](../framework.md) §2，每个 underlying intent 至少记录：

`intent_id`、题型、推理深度、答案类型、语言变体、参考答案及必要 atomic claims、可回答性、条件依赖、冲突状态、Gold evidence groups、等价证据、来源文档及页码。

数值题另记单位、合理容差和实验条件；拒答题注明缺失的证据以及为何不足。

## 质量分级

拟定四级，用于声明标注可信度与发表适用范围：

| 层级 | 来源 | 质控 | 发表适用性 |
| --- | --- | --- | --- |
| Tier 0 | 纯 LLM 生成 | 无 | 不适合 |
| Tier 1 | Agent 复核 | 人工抽样，报告一致性 | Workshop / 短文 / 技术报告 |
| Tier 2 | Agent 初标 + 人工全量复核 | 全部审查，争议仲裁 | 会议主赛道 |
| Tier 3 | 多标注员独立标注 | Fleiss' Kappa，专家仲裁 | 数据集论文 |

**当前状态**：Stage 2 开发集为 Agent 复核，**未做人工抽样**，因此尚未满足 Tier 1 的质控条件。标注来源须写成 agent review，不得写成 `human_verified=true` 或人工 Gold。

## 当前标注资产

| 项目 | 状态 |
| --- | --- |
| 开发集 intent | 20（18 可计分，2 `agent_disputed` 且必要事实为空） |
| 定位粒度 | 页级（`pdf_page_1based`），全部标 `needs_finer_locator_review=true` |
| 证据组结构 | 全部单组单页，无多组、无等价来源 |
| 参考答案 | 18 题有双语候选（`agent_reviewed_candidate`），2 题争议 |
| 拒答 intent | 不在开发集范围内 |
| 封存测试集 | 未构建 |
| 人工一致性 | 未测量 |

已记录的具体争议：`rgq-015` 公式应定位至 PDF 第 4–6 页（旧页 1 标注不足）；`rgq-122` 原文同时出现 58% 与 59%，不得强行选单值；`rgq-048` 的约数 0.6 m 无来源支持的绝对容差。

## 设计时须解决的问题

1. **一致性验证方案**：抽样比例、标注员人数、Kappa 接受阈值须先定。当前无任何人工复核数据，标签可信度无法量化，这直接影响所有层级结果的可声明强度。

2. **页级 → chunk 级的精化路径**：Layer 1 的信息单元级指标（[metrics.md](../layer-1-retrieval/metrics.md) §5）需要 chunk 级标注。精化的选题优先级、工作量和版本化规则须规划。

3. **等价证据的发现方法**：当前等价来源全部为空，导致召回被低估。发现流程（候选生成、语义验证、等价等级判定）与接受标准须定义。

4. **多组证据 intent 的扩充**：当前全部单组，导致 Coverage 退化、Hop 指标无测试用例。扩充来源（`pilot_gold.jsonl`、`core_gold.jsonl`）与标注方案须规划。

5. **充分性与 Factuality 标签**：Layer 1.5 的 Sufficiency Accuracy 和 Layer 3 的 Factuality 需要当前不存在的标签字段。

6. **版本化与冻结规则**：标注修订须新建版本、保留旧结果、重算受影响指标，不覆盖已有研究输出，不使用 sealed test 调参。

## 相关文件

- [Stage 2 标注说明](../../../experiments/stage2-annotation/README.md)：当前流程与产物
- [可选人工 Gold 审查计划](../../../docs/superpowers/plans/2026-09-27-optional-human-gold-review.md)：将来若需发表声明"人工核验"的 Gold 版本时执行
