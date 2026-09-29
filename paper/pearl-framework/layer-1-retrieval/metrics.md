# Layer 1 指标形式化定义

*Retrieval 层指标的操作化定义，适配当前标注粒度 · status: plan · 2026-09-28*

> 本文把 [design.md](design.md) §3 的指标落到当前可用标注上。design.md 采用 RARE 的 Coverage@10 / PerfRecall@10，其 required information 定义在 chunk 语义层；当前 Stage 2 标注定位到 `(resource_id, pdf_page_1based)`，是页级物理位置。两者不等价，因此本文建立三层指标，并明确每层的标注前置条件。

## 1. 指标分层

| 层级 | 指标 | 标注前置条件 | 当前可算 |
| --- | --- | --- | --- |
| 资源级 | Resource-Hit@K、Resource-MRR@K | `resource_id` | 是 |
| 页级 | Page-Hit@K、Page-Coverage@K、Page-MRR@K | `resource_id` + `pdf_page_1based` | 是 |
| 信息单元级 | Info-PerfRecall@K、Info-Coverage@K | 必要信息 → 可接受 chunk 集合 | 否，需细化标注 |
| 语义等价级 | Equiv-PerfRecall@K | 跨资源等价证据网络 | 否，需等价发现 |

首轮主报页级。信息单元级是 RARE 定义的精确实现，在获得 chunk 级标注的子集上追加报告。资源级用于失败归因，不进主表。

**命名约定**：本文不把页级结果命名为 PerfRecall@10 或 Coverage@10，避免与 RARE 的 chunk 级定义混淆。指标前缀标明测量粒度。

## 2. 符号

- $Q$：具有可用检索标签的可回答 intent 集合，$|Q| = N$。
- $q \in Q$：一个 underlying intent。
- $n_q$：intent $q$ 的必要信息单元数。
- $f_{q,j}$：第 $j$ 个必要信息单元，$j \in [1, n_q]$。
- $R_q^K = (c_1, \dots, c_K)$：返回的前 $K$ 个 child chunk，按排名有序。
- $\mathrm{rank}(c)$：chunk $c$ 在 $R_q^K$ 中的排名，从 1 起。
- $\mathrm{res}(c)$、$\mathrm{ps}(c)$、$\mathrm{pe}(c)$：chunk $c$ 的来源资源、起始页、结束页。

## 3. 资源级指标

### 3.1 可接受资源集合

$$
\mathcal{R}_{q,j} = \{r_{q,j}\} \cup \mathcal{E}^{\mathrm{res}}_{q,j}
$$

其中 $r_{q,j}$ 是标注来源资源，$\mathcal{E}^{\mathrm{res}}_{q,j}$ 是已识别的等价来源资源（当前为空集）。

### 3.2 Resource-Hit@K

$$
\mathrm{Resource\text{-}Hit}@K(q) = \mathbf{1}\left[\forall j \in [1, n_q]: \exists c \in R_q^K,\ \mathrm{res}(c) \in \mathcal{R}_{q,j}\right]
$$

$$
\mathrm{Resource\text{-}Hit}@K = \frac{1}{N}\sum_{q \in Q} \mathrm{Resource\text{-}Hit}@K(q)
$$

**用途**：判断检索器能否定位到正确论文。Resource-Hit=0 说明失败发生在论文层，与页内定位无关。

## 4. 页级指标

### 4.1 可接受 chunk 集合

给定必要信息单元 $f_{q,j}$，其标注为资源 $r_{q,j}$ 的第 $p_{q,j}$ 页（1-based）。定义：

$$
A_{q,j} = \left\{c \in \mathrm{Chunks}(r_{q,j}) \;\middle|\; \mathrm{ps}(c) \le p_{q,j} \le \mathrm{pe}(c)\right\}
$$

即**任何覆盖标注页的 child chunk 都视为可接受**。这是页级宽松映射（page-level permissive），记为映射规则 `mapping-v1-page-permissive`。

**该规则的性质**：

- $|A_{q,j}|$ 在当前索引上通常为 5–12（单页含多个 child chunk），因此命中一个可接受 chunk 不等于命中目标信息。
- 由此得到的指标测量"标注页是否进入 Top-K"，不测量"必要信息是否完整取得"。
- 该规则**高估** RARE 意义下的 PerfRecall，因为同页无关 chunk 也算命中。
- 未识别的等价来源造成**低估**。两种偏差方向相反，不互相抵消，须分别记录。

### 4.2 命中指示量

$$
h_{q,j}(K) = \mathbf{1}\left[R_q^K \cap A_{q,j} \ne \varnothing\right]
$$

这是计算中间量，不是指标。命中 $A_{q,j}$ 中任意一个 chunk 即满足该信息单元；重复命中不重复计分。

### 4.3 Page-Hit@K

单题全命中指示：

$$
\mathrm{Page\text{-}Hit}@K(q) = \mathbf{1}\left[\sum_{j=1}^{n_q} h_{q,j}(K) = n_q\right]
$$

题集宏平均：

$$
\mathrm{Page\text{-}Hit}@K = \frac{1}{N}\sum_{q \in Q} \mathrm{Page\text{-}Hit}@K(q)
$$

**语义**：所有必要信息所在页都进入 Top-K 的 intent 比例。对应 RARE PerfRecall 的页级近似，是首要比较指标。

### 4.4 Page-Coverage@K

$$
\mathrm{Page\text{-}Coverage}@K(q) = \frac{1}{n_q}\sum_{j=1}^{n_q} h_{q,j}(K)
$$

$$
\mathrm{Page\text{-}Coverage}@K = \frac{1}{N}\sum_{q \in Q} \mathrm{Page\text{-}Coverage}@K(q)
$$

**语义**：必要信息页的平均覆盖比例，用于解释部分命中程度。需要三个信息单元、命中两个时，单题得 $2/3$。

### 4.5 Page-MRR@K

对每个必要信息单元定义首次命中排名：

$$
\rho_{q,j}(K) = \min\left(\{\mathrm{rank}(c) \mid c \in R_q^K \cap A_{q,j}\} \cup \{\infty\}\right)
$$

单元倒数排名：

$$
\mathrm{RR}_{q,j}(K) = \begin{cases} 1/\rho_{q,j}(K), & \rho_{q,j}(K) \le K \\ 0, & \text{否则} \end{cases}
$$

单题平均后取题集平均：

$$
\mathrm{Page\text{-}MRR}@K = \frac{1}{N}\sum_{q \in Q} \frac{1}{n_q}\sum_{j=1}^{n_q} \mathrm{RR}_{q,j}(K)
$$

**与 OmniEval MRR 的差异**：OmniEval 的 $\mathrm{RR} = 1/\mathrm{FRP}$ 只看首个相关文档，不按信息单元分解，且不截断。本定义按信息单元分解并截断到 $K$，因此不声称与其同口径。若需与 OmniEval 可比，另报单题首个相关 chunk 的 $\mathrm{MRR}@K$（记为 First-Hit-MRR@K）。

## 5. 信息单元级指标（需细化标注）

获得 chunk 级标注后，$A_{q,j}$ 由页级宽松集合替换为人工确认的可接受 chunk 集合：

$$
A^{\mathrm{info}}_{q,j} = \left\{c \;\middle|\; c \text{ 的文本确实承载 } f_{q,j}\right\}
$$

代入 §4.3、§4.4 的公式即得 $\mathrm{Info\text{-}PerfRecall}@K$ 和 $\mathrm{Info\text{-}Coverage}@K$，此时与 RARE 定义一致，可正当使用 PerfRecall / Coverage 命名。

**等价来源扩展**：$A^{\mathrm{equiv}}_{q,j} = A^{\mathrm{info}}_{q,j} \cup \mathcal{E}^{\mathrm{chunk}}_{q,j}$，其中 $\mathcal{E}^{\mathrm{chunk}}_{q,j}$ 是跨资源等价证据。等价性须包含场景、条件、单位和对象一致，不能仅凭主题相似认定。

## 6. 当前标注的结构性限制

对 `outputs/stage2-agent-adjudicated-20260927-03/annotations.jsonl` 的核查结果（2026-09-28）：

| 项目 | 实测 |
| --- | --- |
| intent 总数 | 20 |
| 可计分 intent | 18（2 题 `agent_disputed` 且 `required_facts` 为空） |
| 每题必要事实数 | 1–3 |
| 每题不同 `(resource, page)` 组合数 | **全部为 1** |
| 每题证据组数 | **全部为 1** |
| 标注页的 child chunk 数 | 均值 7.7，范围 5–12 |
| 标注页为第 1 页的 intent | 15/18 |

### 6.1 Coverage 与 PerfRecall 的退化

由于每题的全部必要事实共享同一 $(resource, page)$，页级映射下所有 $A_{q,j}$ 相同：

$$
A_{q,1} = A_{q,2} = \dots = A_{q,n_q} \implies h_{q,1}(K) = \dots = h_{q,n_q}(K)
$$

因此在当前标注上：

$$
\mathrm{Page\text{-}Coverage}@K(q) \in \{0, 1\} = \mathrm{Page\text{-}Hit}@K(q)
$$

两个指标**数值恒等**，Coverage 不提供额外信息，design.md §3.3 的"三个单元命中两个得 2/3"在当前开发集上不可能出现。

这一退化与 RARE 自身结果一致：RARE 附录 D 的 1-hop 列中 Coverage@10 与 PerfRecall@10 完全相同（如 BM25 Finance 82.9/82.9、OpenAI-Large 90.1/90.1），两者只在 2-hop 及以上分离。当前开发集全部为单组单页，等价于 1-hop 场景。

**处理**：首轮主报 Page-Hit@10，Page-Coverage@10 仅在表中标注"当前标注下与 Page-Hit 恒等"，不作为独立证据。要让 Coverage 产生信息量，需引入多页或多组证据的 intent。

### 6.2 第 1 页集中

15/18 题的标注页是第 1 页（标题页/摘要页）。摘要主题密度高、术语集中，检索难度显著低于正文页。这使页级指标偏乐观，且削弱了对正文定位能力的测量。报告须说明该分布。

### 6.3 等价来源缺失

当前每个证据组只有一个 alternative，$\mathcal{E}^{\mathrm{res}}_{q,j} = \varnothing$。design.md §3.2 的等价来源机制在当前数据上无测试用例，Page-Hit 会因未识别的等价来源而低估真实召回。

## 7. 计分资格规则

| 情形 | 处理 |
| --- | --- |
| `required_facts` 为空或必要信息无法确定 | 不可计分，报告其数量，不记作失败也不记作满分 |
| 原文确有证据但解析/切块丢失内容 | 保留该信息单元，计未命中；不通过删题提高分数 |
| 标注资源不在当前索引 | 视为标签缺陷，不可计分，单独报告 |
| 争议题但必要信息可确定 | 可进入汇总，标注争议状态 |
| 空标签 | 不触发"全部命中" |

## 8. 双语汇总约定

同一 intent 的中英查询变体先取均值，再对 intent 取均值：

$$
\mathrm{Metric}(q) = \frac{1}{|L_q|}\sum_{\ell \in L_q} \mathrm{Metric}(q, \ell), \quad L_q \subseteq \{\mathrm{zh}, \mathrm{en}\}
$$

这是项目汇总约定，不是新增指标，也不把双语查询视为独立意图。中英文另分别汇总以支持语言效应分析。报告须同时给出可计分 intent 数和查询数。

## 9. 指标使用边界

| 指标 | 地位 | 边界 |
| --- | --- | --- |
| Page-Hit@10 | 首要 | 测量页命中，非信息完整性 |
| Page-Coverage@10 | 辅助 | 当前标注下与 Page-Hit 恒等 |
| Page-MRR@10 | 辅助 | 只看位置，不能替代完整性评价 |
| Resource-Hit@10 | 诊断 | 不进主表，用于失败归因 |
| Info-PerfRecall@10 | 待启用 | 需 chunk 级标注 |

本轮不加入 MAP、nDCG，避免额外准备完整相关性标签和等级标签；不扩展多个 $K$ 的主报告。不可回答题不进入必要信息召回汇总，拒答评价属 Layer 4。

不设置无研究依据的通过阈值。完整检索不保证生成答案正确——后者属 Layer 2。
