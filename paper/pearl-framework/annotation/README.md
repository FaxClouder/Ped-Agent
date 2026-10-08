# 标注规范与质量控制

*PEARL 新评估数据的标注要素与质量控制 · status: plan · 2026-09-29*

本目录收录 PEARL 各层共用的标注要求。旧评估标注全部退出新实验；新标注须按 PEARL 的证据组语义、定位粒度、质量等级和版本规则重新定义、构建及冻结。

## 文档规划

| 文件 | 内容 |
| --- | --- |
| `annotation-guideline.md` | 统一标注指南：各字段定义、填写规则、示例 |
| `quality-tiers.md` | 标注质量分级（Tier 0–3）与发表适用性 |
| `gold-standard.md` | Gold 标准构建流程与冻结规则 |
| `inter-annotator-agreement.md` | 一致性验证方法与抽样方案 |

本轮 Layer 1 的实际试标操作规范见 [retrieval-guideline.md](retrieval-guideline.md)。

## 标注要素

依据 [PEARL 主框架](../PEARL-framework.md) §3，每个 underlying intent 至少记录：

`intent_id`、题型、推理深度、答案类型、英文查询、参考答案及必要 atomic claims、可回答性、条件依赖、冲突状态、Gold evidence groups、等价证据、来源文档及页码。若有英文改写，记录其与原 intent 的归属关系，不当作独立题目。

数值题另记单位、合理容差和实验条件；拒答题注明缺失的证据以及为何不足。

Retrieval 标注须为每项必要证据保存版本化来源、原文锚点、事实内容和适用条件（如对象、场景、单位）。资源 ID 与页码可帮助定位，但不能单独证明某个返回 child 承载目标信息。实验对照中的 chunk ID 是**映射结果**而非 Gold 身份；每个内容命中判断须能回溯到返回文本和被支持的证据单位。一个或多个 Top-K child 可共同提供所需信息，组合与聚合规则见 [指标协议](../layer-1-retrieval/metrics.md) §2–3。

## Retrieval 最小标注结构

| 对象 | 必填字段与规则 |
| --- | --- |
| intent | `intent_id`、`family_id`、split、英文 query、主题型与交叉标签、参考答案、corpus-answerable、Gold 版本 |
| requirement | `requirement_id`、事实、对象、研究／实验身份、场景、单位、必要条件与来源限制；条件不同的事实不能共用身份 |
| source atom | `atom_id`、source ID／哈希、原文引句或表格值、页与精确位置、内容限定；原子不依赖 chunk ID |
| support bundle | 一个 requirement 的一个完整支持组合，非空 atom ID 列表；组合内 AND，等价组合 OR |
| evidence group | 一条完整答案路径，非空 requirement ID 列表；组内 AND，替代组 OR；去除逻辑重复和冗余 |
| support mapping | run／asset 版本、child ID／文本哈希、支持哪些原子、是否需联合 child、支持引句、判定／未决状态及依据 |
| provenance | 标注者或 Agent 模型／提示版本、核验范围、争议、仲裁、时间及修订记录 |

语义 Gold 在评估运行前冻结，输出支持映射在排名密封后的盲化核验环节完成，再冻结并评分。补充既有要求的等价支持不改变答案范围；新增完整路径或改动事实／条件必须修订语义 Gold，并对所有方法一致复核。具体流程见 [实验协议](../layer-1-retrieval/experiments.md) §4。

## 质量分级

拟定四级，用于声明标注可信度与发表适用范围：

| 层级 | 来源 | 质控 | 发表适用性 |
| --- | --- | --- | --- |
| Tier 0 | 纯 LLM 生成 | 无 | 不适合 |
| Tier 1 | Agent 复核 | 人工抽样，报告一致性 | Workshop / 短文 / 技术报告 |
| Tier 2 | Agent 初标 + 人工全量复核 | 全部审查，争议仲裁 | 会议主赛道 |
| Tier 3 | 多标注员独立标注 | Fleiss' Kappa，专家仲裁 | 数据集论文 |

**当前状态**：已有 [8 题开发集试标](../datasets/retrieval-pilot/README.md)，经两名子 Agent 独立复核并冻结为初步 Gold；已生成单组 R1 初步流程结果。当前优先跑通四方法流程并报告初步结果；上表的人工审查等级不构成此阶段的门槛。人工审查后置，用于开发集难例核查与调优；质量等级须依据实际完成的审查声明，不沿用旧资产等级，也不把子 Agent 复核称为人工复核。

## 新标注状态

Retrieval 已确定 80 个开发／200 个独立评估 intent 的计划与来源片段／requirement 粒度；8 题初稿用于核验标注方法，初步 Gold 尚未冻结。实际等价来源、核验范围和质量等级须依据新数据记录。拒答子集另行设计；旧题号及其争议记录不转入新标签。

## 设计时须解决的问题

1. **一致性验证方案**：按目标质量等级预先确定抽样比例、标注员人数、适用的一致性统计量和仲裁规则。

2. **定位与支持核验**：Layer 1 的内容命中需要来源锚点和可复核的片段支持判断；同页其他片段不可自动视为支持。解析或切块配置变化时重新核验映射，保留标注版本与判定依据。

3. **等价证据的发现方法**：定义候选生成、语义验证、等价等级判定与接受标准，避免把唯一指定来源误当唯一正确证据。

4. **多组证据设计**：若评价部分覆盖、多跳和替代推理路径，须在新数据中设计相应 intent 与证据组实例。

5. **充分性与 Factuality 标签**：若报告 Layer 2 的 Sufficiency Accuracy 或 Layer 4 的 Factuality，须在新标注协议中定义相应参考字段。

6. **版本化与冻结规则**：标注修订须新建版本、保留旧结果、重算受影响指标，不覆盖已有研究输出，不使用 sealed test 调参。

## 相关文件

- [PEARL 主框架](../PEARL-framework.md)：证据组语义与标注边界
- [数据集设计](../datasets/README.md)：新评估数据的划分与题型要求
