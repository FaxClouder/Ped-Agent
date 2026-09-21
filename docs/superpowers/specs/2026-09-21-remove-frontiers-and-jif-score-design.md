# Frontiers in Physics 清理与 JIF 数值退役设计

_期刊筛选元数据口径调整与单篇文献可审计清理 · status: current_

---

## 目标

对现有期刊筛选资产做两项聚焦调整：

1. 从活动候选集中删除 `Frontiers in Physics` 及其唯一关联文献；
2. 停止存储和采集数值型 `JIF score`，但继续保留 JIF 排名、分区和百分位。

本调整不改变现行期刊准入逻辑：中科院分区、JCI 分区和 JIF 分区仍按“任一体系达到
一区/二区或 Q1/Q2 即通过”的关系计算，并在同一体系存在多个分类时取最佳分区。

## 指标字段调整

`journal_metrics.csv` 删除 `jif_value` 列。现有数值型 JIF（例如 3.3、6.2）随该列一并
退役，不迁移到备注字段。以下 JIF 字段继续保留：

- `jif_rank`
- `jif_quartile`
- `jif_percentile`

以下 JCI 字段继续保留，其中 `jci_value` 是后续唯一要求采集的期刊级数值指标：

- `jci_value`
- `jci_rank`
- `jci_quartile`
- `jci_percentile`

后续截图采集仍需覆盖 JCR 基本信息、JCI 数值与总被引、JCI/JIF 分类排名，以及中科院
大小类分区；不再要求提供 Journal Impact Factor 数值卡片。

## Frontiers in Physics 清理范围

目标文献：

- resource ID：`b3-10`
- DOI：`10.3389/fphy.2023.1200927`
- 本地文件：`memPed/knowledge/batch-3-incoming/fphy-11-1200927.pdf`

从活动数据中删除：

- `memPed/knowledge/literature/records/candidates.csv` 中对应候选行；
- `memPed/knowledge/literature/records/journal_metrics.csv` 中期刊指标行；
- Batch 3 活动导入 manifest 与活动 extraction 中的 `b3-10` 记录；
- 上述精确路径的本地 PDF。

历史报告、清单和提取证据不做无痕删除。相关条目改为“已排除”，注明原因是人工调整后的
期刊筛选决定，并明确其不属于当前活动候选或导入范围。

## 安全与一致性

- 删除 PDF 前解析并核对绝对路径、文件名、resource ID、DOI 和 SHA-256；
- 不删除其他 Frontiers 期刊或其他 `b3-*` 资产；
- 不重建索引，不生成 Chunk，不触碰其他用户改动；
- 保留 `Collective Dynamics` 的未收录审计记录；
- 更新当前采集标准、模块 README、Schema 设计与文档导航，使规则与数据结构一致。

## 验证标准

实施完成后必须满足：

1. `journal_metrics.csv` 可由标准 CSV 解析器读取，所有行列数一致，且不存在
   `jif_value` 列和 `Frontiers in Physics` 行；
2. 活动候选、Batch 3 manifest 和活动 extraction 中不存在 `b3-10`、目标 DOI 或目标文件名；
3. 目标 PDF 不存在，其他 Batch 3 PDF 数量只减少一份；
4. 历史文档中的保留引用均明确标记为已排除；
5. 治理单元测试继续通过，JIF 分区仍可参与最佳分区准入判断；
6. 文档不再要求采集或填写 JIF 数值。
