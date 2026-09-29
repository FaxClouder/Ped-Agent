# Layer 1: Retrieval

*检索召回评价 · status: design 完成，实验未运行 · 2026-09-28*

Layer 1 接收问题和固定索引，输出有序、可定位的证据片段。评价问题：必要信息找到了多少、是否找全、首个相关结果是否靠前。

## 文档

| 文件 | 内容 | 状态 |
| --- | --- | --- |
| [design.md](design.md) | 设计方案：目标、范围、指标来源、标签复用、实验安排、检索模块替换规则 | plan |
| [metrics.md](metrics.md) | 指标形式化定义、指标分层、当前标注的结构性限制 | plan |
| [experiments.md](experiments.md) | 研究问题、实验变量、流程、报告结构 | plan |
| [statistical-methods.md](statistical-methods.md) | 小样本重复测量设计下的估计、检验、敏感性分析 | plan |
| [failure-taxonomy.md](failure-taxonomy.md) | 失败模式分类法与归因流程 | plan |

`design.md` 是原始设计记录（原 `paper/pearl-framework/retrieval-design.md`）。其余四份把设计落到可执行的口径上，与 design.md 冲突时以后者为准并在此记录。

## 核心决策

| 决策 | 取值 | 依据 |
| --- | --- | --- |
| 主指标 | Page-Hit@10 | 当前标注为页级，见 metrics.md §4 |
| 映射规则 | `mapping-v1-page-permissive` | 覆盖标注页的任意 child chunk 视为可接受 |
| 指标命名 | 加 `Page-` 前缀 | 避免与 RARE 的 chunk 级 PerfRecall 混淆 |
| 对照组 | 5 组（含 BM25 英文译文变体） | 隔离跨语言失配因素 |
| 分析单位 | underlying intent，$N = 18$ | 双语查询先取均值 |
| 统计方法 | bootstrap CI + Wilcoxon + Holm 校正 | 小样本非参数 |

## 与 design.md 的三处调整

1. **指标命名**：design.md 采用 RARE 的 Coverage@10 / PerfRecall@10。因当前标注为页级而非 chunk 级，metrics.md 改用 Page-Hit@10 / Page-Coverage@10，并说明与 RARE 定义的近似关系。RARE 命名保留给 chunk 级标注就绪后使用。

2. **对照组数量**：design.md 列三组（BM25、BGE-M3、RRF）。experiments.md 增加 BM25 英文译文变体，理由是语料全英文而查询含中文，不隔离语言因素会把跨语言失配误读为方法优劣。

3. **Coverage 的地位**：design.md 把 Coverage@10 列为主指标。实测显示当前 18 题全部为单组单页，Coverage 与 Page-Hit 数值恒等，因此降为辅助并加注说明。

## 已知限制

| 限制 | 影响 |
| --- | --- |
| 标注为页级，标注页含 5–12 个 child chunk | 指标测量页命中，高估 RARE 意义下的信息完整性 |
| 18 题全部单证据组 | Coverage 退化为 Page-Hit，多组 OR 语义无测试用例 |
| 15/18 题标注页为第 1 页 | 摘要页主题密度高，指标偏乐观 |
| 等价来源全部为空 | 低估真实召回 |
| $N = 18$ | 仅大效应可检出，CI 宽约 ±0.15–0.25 |
| 标注来源为 agent-adjudicated，未人工抽样 | 标签可信度未量化 |

前四项详见 [metrics.md](metrics.md) §6，第五项详见 [statistical-methods.md](statistical-methods.md) §5，第六项属 [annotation/](../annotation/) 范围。

## 层间接口

**输出**：Top-10 child chunks，每条含排名、chunk ID、文本、来源资源、页码、分数、parent ID。

**下游**：Layer 1.5 用 parent ID 按固定规则展开上下文并评价充分性。chunk 进入 Top-K 算本层成功；展开后仍不足算 Layer 1.5 失败。接口约定见 [PEARL-framework.md](../PEARL-framework.md) §2.1。
