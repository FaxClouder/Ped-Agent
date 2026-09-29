# 报告规范

*主表、诊断表、统计报告、发表检查清单 · status: 部分定义 · 2026-09-28*

## 文档规划

| 文件 | 内容 |
| --- | --- |
| `main-table-template.md` | 主表六项指标的模板与填写规则 |
| `diagnostic-tables.md` | 诊断表结构与附录内容 |
| `statistical-reporting.md` | 跨层统一的统计报告规范 |
| `publication-checklist.md` | 发表前的口径与声明检查清单 |

Layer 1 的统计方法已在 [layer-1-retrieval/statistical-methods.md](../layer-1-retrieval/statistical-methods.md) 定义，可作跨层规范的蓝本。

## 主表六项

口径见 [PEARL-framework.md](../PEARL-framework.md) §5.1。层编号为 v1.1 新编号，与目录名的映射见同文 §0.3。

主表是**报告模板**，不是结果表。当前只有 Layer 1 的指标可算，其余五项未执行，填表时写"—（未执行）"而不留空——留空会被读成 0 或读成遗漏。

| # | 指标 | 方向 | 层 | 当前状态 |
| --- | --- | --- | --- | --- |
| 1 | Page-Hit@10 <sup>a</sup> | ↑ | 1 Retrieval | 可算，实验未运行 |
| 2 | Answer Correctness | ↑ | 3 Answer | —（未执行） |
| 3 | Faithfulness | ↑ | 4 · Grounding | —（未执行） |
| 4 | Unsupported Claim Rate | ↓ | 4 · Grounding | —（未执行） |
| 5 | Abstention F1 | ↑ | 4 · Reliability | —（未执行） |
| 6 | Latency | ↓ | 6 Efficiency | —（未执行） |

<sup>a</sup> Complete Evidence Group Recall 在当前页级标注下的实现，映射规则 `mapping-v1-page-permissive`；chunk 级标注就绪后升级为 Info-PerfRecall@10。定义见 [layer-1-retrieval/metrics.md](../layer-1-retrieval/metrics.md) §4.3。

**列名用可算的指标名**：主表写 Page-Hit@10 而非 Complete Evidence Group Recall@10，目标指标名只出现在表注。后者在前会让读者把页级结果读成证据组级结果。

资源受限场景可用 Tokens 替换 Latency，但须在实验前选定并对所有方法保持一致，不能按结果择优。

## 诊断表

MRR、nDCG、Citation P/R、hop 指标、数值误差与题型细分放诊断表或附录。

**Page-Coverage@10 进诊断表，不进主表**：当前 18 题全为单组单页，它与 Page-Hit@10 数值恒等（[layer-1-retrieval/metrics.md](../layer-1-retrieval/metrics.md) §6.1）。两列相同数字并列会被当作两项独立证据，表中须标注"当前标注下与 Page-Hit 恒等"。

**不使用** BLEU/ROUGE 或单一 LLM 总评分替代主表指标。

## 统计报告要求

来自 [framework.md](../framework.md) §5：

1. 报告总体均值、每题型结果、样本数和置信区间。
2. 成对比较与 bootstrap 以 **underlying intent** 聚类，不把同一问题的中英/改写版本当独立样本。
3. 同时报告 answerable 与 insufficient-evidence 子集，区分"正确回答""正确拒答""有证据但答错""证据不足却编造"。
4. 对数值、冲突和条件问题提供错误案例审计。
5. 所有阈值、rubric 和缺失值规则在封存测试前写定。

## 声明口径

报告与论文中须准确声明以下事项，不得夸大：

| 事项 | 正确表述 | 禁止表述 |
| --- | --- | --- |
| 标注来源 | agent review / agent-adjudicated | 人工 Gold、`human_verified=true` |
| 定位粒度 | 页级 | 元素级精确引用 |
| 指标口径 | Page-Hit@10（RARE PerfRecall 的页级近似） | PerfRecall@10 |
| 样本性质 | 开发集探索性结果 | 封存测试结论 |
| 双语查询 | 18 intent / 36 条查询 | 36 个独立样本 |
| 复现程度 | 采用其指标定义 | 复现 RARE / OmniEval 的完整流程 |
| 层数表述 | 四层顺序链条 + 一个控制器 + 一个横切维度 | 泛称"N 层框架"而不说明角色 |
| 主表状态 | 报告模板，五项未执行 | 主表结果 |
| 项目命名 | PedRAGent | Ped-Agent、PedAgent（后者为 Xie et al. 的先行系统） |

## 可复现信息

每次实验须保留：输入哈希、代码与标签版本、模型和索引指纹、检索配置、随机种子。结果写入 `outputs/` 下独立命名目录，不覆盖已有研究输出。

## 设计时须解决的问题

1. **小样本脚注的统一格式**：$N = 18$ 的警告须在所有表格出现，格式统一。

2. **跨层统计规范的统一**：各层的 bootstrap 参数、检验方法和校正方式应一致，避免各层用不同口径。

3. **发表检查清单**：投稿前须逐项核对标注等级声明、样本量披露、指标命名准确性、可复现信息完整性。
