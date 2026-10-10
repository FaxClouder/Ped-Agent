# Layer 2: Metrics Formalization

*上下文充分性的指标形式化定义 · status: plan · 2026-09-29*

> **本文定义 Layer 2 的四个指标**：Evidence Coverage、Sufficiency Accuracy、Context Relevance、Noise Ratio。每个指标给出形式化定义、计算方法、标注前置条件和与 Layer 1 指标的明确区分。

## 0. 符号约定

### 0.1 基本符号

- $Q$：具有可用标注的 intent 集合，$|Q| = N$
- $q \in Q$：一个 underlying intent
- $\mathcal{R}_q = \{f_{q,1}, f_{q,2}, \ldots, f_{q,n_q}\}$：intent $q$ 的必要证据需求集合
- $n_q = |\mathcal{R}_q|$：必要证据需求数量
- $f_{q,j}$：第 $j$ 个必要证据需求（atomic requirement）

### 0.2 Layer 1 输出

- $C_q^K = \{c_1, c_2, \ldots, c_K\}$：Layer 1 返回的 Top-K child chunks
- $\mathrm{rank}(c)$：chunk $c$ 的排名，$1 \le \mathrm{rank}(c) \le K$
- $\mathrm{parent}(c)$：chunk $c$ 的父节点

### 0.3 Layer 2 处理

- $E(C_q^K)$：展开后的 chunk 集合（含 parent）
- $D(E(C_q^K))$：去重后的 chunk 集合
- $T(D(E(C_q^K)), B)$：截断到预算 $B$ tokens 后的集合
- $\mathrm{Ctx}_q = \text{concat}(T(D(E(C_q^K)), B))$：最终上下文文本

### 0.4 证据覆盖

- $h^{(1)}_{q,j} \in \{0, 1\}$：Layer 1 中必要证据 $f_{q,j}$ 是否被 Top-K child 覆盖
- $h^{(2)}_{q,j} \in \{0, 1\}$：Layer 2 中必要证据 $f_{q,j}$ 是否被最终上下文 $\mathrm{Ctx}_q$ 覆盖

**判定规则**：
$$
h^{(2)}_{q,j} = \mathbf{1}[\exists \text{evidence in } \mathrm{Ctx}_q \text{ that supports } f_{q,j}]
$$

## 1. Evidence Coverage

### 1.1 定义

**语义**：最终上下文覆盖的必要证据需求比例。

**单题 Coverage**：
$$
\mathrm{EC}(q) = \frac{1}{n_q} \sum_{j=1}^{n_q} h^{(2)}_{q,j}
$$

**题集宏平均**：
$$
\mathrm{Evidence\,Coverage} = \frac{1}{N} \sum_{q \in Q} \mathrm{EC}(q)
$$

**Atomic requirement 微平均**：
$$
\mathrm{Evidence\,Coverage}_{\text{micro}} = \frac{\sum_{q \in Q} \sum_{j=1}^{n_q} h^{(2)}_{q,j}}{\sum_{q \in Q} n_q}
$$

### 1.2 与 Layer 1 的区分

| 对比维度 | Layer 1 | Layer 2 |
|---|---|---|
| **观察对象** | 原始 Top-K child chunks | 展开、去重、截断后的最终上下文 |
| **定义公式** | $\frac{1}{N}\sum_q \frac{1}{n_q}\sum_j h^{(1)}_{q,j}$ | $\frac{1}{N}\sum_q \frac{1}{n_q}\sum_j h^{(2)}_{q,j}$ |
| **失败原因** | 检索算法未召回 | 组装策略导致证据丢失或被截断 |

**重要性质**：
$$
\mathrm{EC}(q) \ge \mathrm{Layer1\,Coverage}(q) \quad \text{(单调性)}
$$

理由：展开 parent 只会增加（或保持）证据，不会减少，除非截断不当。

### 1.3 证据组聚合（Evidence Group Aggregation）

**问题**：PEARL 的证据组语义是"组内 AND，组间 OR"（见 [PEARL-framework.md](../PEARL-framework.md) §3）。如何形式化？

**定义**：设 intent $q$ 有 $m_q$ 个可替代的证据组 $G_1, G_2, \ldots, G_{m_q}$，每组 $G_i = \{f_{i,1}, f_{i,2}, \ldots, f_{i,k_i}\}$。

**完整证据组覆盖**：
$$
\mathrm{Complete\,Group\,Coverage}(q) = \mathbf{1}\left[\exists i \in [1, m_q]: \sum_{f \in G_i} h^{(2)}_{q,f} = |G_i|\right]
$$

即：至少存在一个证据组的所有证据都被覆盖。

**题集平均**：
$$
\mathrm{Complete\,Group\,Coverage} = \frac{1}{N} \sum_{q \in Q} \mathrm{Complete\,Group\,Coverage}(q)
$$

**关系**：
- 当每题只有一个证据组（$m_q = 1$）时：
$$
\mathrm{Complete\,Group\,Coverage}(q) = \mathbf{1}[\mathrm{EC}(q) = 1]
$$

- 当每个证据组只有一个证据（$k_i = 1 \,\forall i$）时：
$$
\mathrm{Complete\,Group\,Coverage}(q) = \mathbf{1}[\mathrm{EC}(q) > 0]
$$

### 1.4 Coverage 退化问题

依据 [layer-1-retrieval/metrics.md](../layer-1-retrieval/metrics.md) §6.1，旧标注中每题所有必要证据共享同一 `(resource, page)`，导致：

$$
h^{(1)}_{q,1} = h^{(1)}_{q,2} = \cdots = h^{(1)}_{q,n_q} \implies \mathrm{EC}(q) \in \{0, 1\}
$$

此时 Coverage 与 Complete Group Coverage 数值恒等，不提供额外信息。

**新标注要求**：为避免退化，需要：
1. **多页证据**：不同必要证据位于不同页
2. **多组证据**：至少部分 intent 有可替代证据组
3. **跨文档证据**：综合题的证据来自不同论文

### 1.5 标注前置条件

**必需**：
- 每个 intent 的必要证据需求 $\mathcal{R}_q$
- 每个证据 $f_{q,j}$ 的锚定来源（文档、页码、片段）
- 证据组划分（单组 / 多组可替代）

**判定方法**：
1. **人工标注**：专家阅读最终上下文，判断每个证据是否被覆盖
2. **自动 + 人工验证**：LLM 初步判断，人工抽样复核
3. **基于锚点的自动映射**：检查上下文是否包含标注片段（需处理改写）

**推荐**：Tier 2（Agent 初标 + 人工全量复核）

## 2. Sufficiency Accuracy

### 2.1 定义

**语义**：系统判断"上下文充分/不足"与人工 Gold 标签的一致性。

**二分类问题**：
- **Gold 标签**：$y_q \in \{\text{sufficient}, \text{insufficient}\}$
- **系统预测**：$\hat{y}_q \in \{\text{sufficient}, \text{insufficient}\}$

**Sufficiency Accuracy**：
$$
\mathrm{Sufficiency\,Accuracy} = \frac{1}{N} \sum_{q \in Q} \mathbf{1}[y_q = \hat{y}_q]
$$

### 2.2 混淆矩阵

|  | Gold: Sufficient | Gold: Insufficient |
|---|---|---|
| **Pred: Sufficient** | True Positive (TP) | **False Positive (FP)** |
| **Pred: Insufficient** | **False Negative (FN)** | True Negative (TN) |

**关键指标**：

**Precision**（预测充分的准确率）：
$$
P = \frac{\text{TP}}{\text{TP} + \text{FP}}
$$

**Recall**（真充分的召回率）：
$$
R = \frac{\text{TP}}{\text{TP} + \text{FN}}
$$

**False Positive Rate**（假阳性率，不足误判为充分）：
$$
\mathrm{FPR} = \frac{\text{FP}}{\text{FP} + \text{TN}}
$$

**False Negative Rate**（假阴性率，充分误判为不足）：
$$
\mathrm{FNR} = \frac{\text{FN}}{\text{FN} + \text{TP}}
$$

### 2.3 错误类型的严重性

**FP（不足误判为充分）**：
- **后果**：系统停止检索，但证据不足 → 生成幻觉或错误答案
- **严重性**：高（直接导致质量下降）
- **优化目标**：最小化 FPR

**FN（充分误判为不足）**：
- **后果**：系统继续检索，浪费资源 → 增加延迟和成本
- **严重性**：中（影响效率，但不影响正确性）
- **优化目标**：平衡 FNR 与成本

**报告要求**：
- 主报告 Sufficiency Accuracy、FPR、FNR
- 辅助报告 Precision、Recall、F1
- 分别报告 sufficient 子集和 insufficient 子集的表现

### 2.4 充分性阈值

**问题**：当使用 Evidence Coverage 作为充分性代理时，需要设定阈值。

**定义**：
$$
\hat{y}_q = \begin{cases}
\text{sufficient}, & \mathrm{EC}(q) \ge \theta \\
\text{insufficient}, & \mathrm{EC}(q) < \theta
\end{cases}
$$

**阈值选择**：
- **严格**：$\theta = 1.0$（全部证据必须覆盖）
- **宽松**：$\theta = 0.8$（80% 证据覆盖即可）
- **数据驱动**：在开发集上优化 $\theta$ 使 Sufficiency Accuracy 最大

**实验要求**：
- 阈值 $\theta$ 须在开发集上选定，不在测试集上调优
- 报告中须明确声明选定的 $\theta$ 值
- 敏感性分析：报告 $\theta \in [0.5, 0.6, \ldots, 1.0]$ 下的 Accuracy 曲线

### 2.5 与 Layer 1 的区分

| 对比维度 | Layer 1 | Layer 2 |
|---|---|---|
| **评估对象** | 检索是否命中必要证据 | 上下文是否充分回答问题 |
| **Gold 标签** | 证据在/不在 Top-K | 上下文充分/不充分 |
| **失败原因** | 检索算法排序不当 | 充分性判断不准确 |
| **应用场景** | 评价检索器质量 | 评价 Agent 停止决策 |

**不重复计分**：Layer 1 不评估充分性判断，Layer 2 不评估检索召回。

### 2.6 标注前置条件

**必需**：
- 每个 intent 的最终上下文 $\mathrm{Ctx}_q$（展开、去重、截断后）
- 人工 Gold 标签 $y_q \in \{\text{sufficient}, \text{insufficient}\}$
- 标注指南定义"充分"的操作化标准

**标注指南要点**（详见 `annotation-guidelines.md`）：
1. 上下文**充分**当且仅当：包含回答问题所需的全部关键事实和必要条件
2. **部分充分**视为不充分（除非实验设定三级标签）
3. 标注员不应看到原始检索排名，避免锚定偏差
4. 多标注员标注，计算 Fleiss' Kappa

**质量要求**：Kappa > 0.75（实质性一致）

## 3. Context Relevance

### 3.1 定义

**语义**：最终上下文中相关内容的比例。

**Chunk-level Context Relevance**：
设最终上下文由 $M$ 个 chunks 组成，$\mathrm{Ctx}_q = \{e_1, e_2, \ldots, e_M\}$。

定义相关性标签 $r_{q,i} \in \{0, 1\}$：
$$
r_{q,i} = \mathbf{1}[\text{chunk } e_i \text{ is relevant to } q]
$$

**单题 Context Relevance**：
$$
\mathrm{CR}(q) = \frac{1}{M} \sum_{i=1}^{M} r_{q,i}
$$

**题集平均**：
$$
\mathrm{Context\,Relevance} = \frac{1}{N} \sum_{q \in Q} \mathrm{CR}(q)
$$

### 3.2 Token-level Context Relevance

更精细的度量，按 token 计算：

$$
\mathrm{CR}_{\text{token}}(q) = \frac{\sum_{i=1}^{M} r_{q,i} \cdot |e_i|}{\sum_{i=1}^{M} |e_i|}
$$

其中 $|e_i|$ 是 chunk $e_i$ 的 token 数。

### 3.3 三级相关性（可选）

更细致的分级：

- $r_{q,i} = 2$：**必要**（必须有才能回答）
- $r_{q,i} = 1$：**有帮助**（提供支持但非必需）
- $r_{q,i} = 0$：**无关**（与问题无关）

**加权 Context Relevance**：
$$
\mathrm{CR}_{\text{weighted}}(q) = \frac{\sum_{i=1}^{M} w_{r_{q,i}} \cdot |e_i|}{\sum_{i=1}^{M} |e_i|}
$$

其中权重 $w_2 = 1.0, w_1 = 0.5, w_0 = 0.0$。

### 3.4 与 Layer 1 的区分

**Layer 1 可能也测量相关性**（如资源级、页级定位），但观察对象不同：

| 对比维度 | Layer 1 | Layer 2 |
|---|---|---|
| **观察对象** | Top-K child chunks | 展开后的最终上下文（含 parent） |
| **相关性判断** | Child 是否相关 | 展开的 parent 是否相关 |
| **用途** | 诊断检索精度 | 评估组装策略的噪声控制 |

**关键差异**：Layer 2 的 Context Relevance 受展开规则影响。即使 Layer 1 的 child 全部相关，展开后的 parent 可能引入无关内容。

### 3.5 标注前置条件

**必需**：
- 最终上下文的 chunk 分割（保留组装后的 chunk 边界）
- 每个 chunk 的相关性标签 $r_{q,i}$

**判定方法**：
1. **人工标注**：标注员逐 chunk 判断相关性
2. **LLM-as-a-judge**：使用 LLM 判断，人工抽样验证
3. **基于证据映射**：若 chunk 包含必要证据，自动标为相关（可能遗漏有帮助的内容）

**推荐**：LLM 初判 + 人工抽样复核（20% 样本）

## 4. Noise Ratio

### 4.1 定义

**语义**：最终上下文中无关或无帮助内容的占比。

**与 Context Relevance 的关系**：
$$
\mathrm{Noise\,Ratio}(q) = 1 - \mathrm{CR}(q)
$$

若使用三级相关性：
$$
\mathrm{Noise\,Ratio}(q) = \frac{\sum_{i=1}^{M} \mathbf{1}[r_{q,i} = 0] \cdot |e_i|}{\sum_{i=1}^{M} |e_i|}
$$

**题集平均**：
$$
\mathrm{Noise\,Ratio} = \frac{1}{N} \sum_{q \in Q} \mathrm{Noise\,Ratio}(q)
$$

### 4.2 噪声来源分析

**分解公式**（诊断用）：

$$
\mathrm{Noise} = \mathrm{Noise}_{\text{child}} + \mathrm{Noise}_{\text{parent}} + \mathrm{Noise}_{\text{redundancy}}
$$

- **$\mathrm{Noise}_{\text{child}}$**：原始 Top-K child 中已有的无关内容
- **$\mathrm{Noise}_{\text{parent}}$**：展开 parent 引入的新无关内容
- **$\mathrm{Noise}_{\text{redundancy}}$**：去重不彻底导致的冗余

**用途**：定位组装策略的问题（展开过度 vs 去重不足）

### 4.3 噪声对生成的影响

**研究问题**：Noise Ratio 是否与答案质量负相关？

**联合分析**：
$$
\mathrm{Answer\,Correctness} = f(\mathrm{Evidence\,Coverage}, \mathrm{Noise\,Ratio})
$$

**假设**：存在最优区间，Coverage 高且 Noise 低时答案质量最好。

### 4.4 标注前置条件

**与 Context Relevance 共享**：
- 最终上下文的 chunk 分割
- 相关性标签 $r_{q,i}$

**无额外标注成本**（Noise Ratio 是 Context Relevance 的补集）

## 5. 指标关系与约束

### 5.1 逻辑约束

**Coverage 与 Relevance 的关系**：
$$
\mathrm{EC}(q) = 1 \implies \mathrm{CR}(q) > 0
$$
理由：若覆盖全部必要证据，则至少存在相关内容。

**但反向不成立**：
$$
\mathrm{CR}(q) = 1 \not\Rightarrow \mathrm{EC}(q) = 1
$$
理由：全部内容相关，但可能缺失某些必要证据。

### 5.2 四象限分析

| Evidence Coverage | Context Relevance | 解释 | 处理 |
|---|---|---|---|
| 高 | 高 | **理想状态** | 保持 |
| 高 | 低 | 证据完整但噪声多 | 改进去重和截断 |
| 低 | 高 | 精准但不完整 | 改进检索或展开 |
| 低 | 低 | **最差状态** | 检索和组装都有问题 |

### 5.3 指标优先级

**主报告**：
1. **Evidence Coverage**（核心，测量证据完整性）
2. **Sufficiency Accuracy**（关键，测量 Agent 判断能力）

**辅助报告**：
3. **Noise Ratio**（质量诊断）
4. **Context Relevance**（可由 Noise 推导）

**理由**：Coverage 和 Sufficiency 直接关联评价目标；Relevance/Noise 是诊断性指标。

## 6. 计算示例

### 6.1 示例数据

**Intent Q001**：
- 必要证据：$\mathcal{R} = \{f_1, f_2, f_3\}$（需 3 个证据）
- 证据组：单组（$G_1 = \{f_1, f_2, f_3\}$，组内 AND）

**Layer 1 Top-5 child**：
- $c_1$：包含 $f_1$
- $c_2$：包含 $f_2$
- $c_3, c_4, c_5$：不含必要证据

Layer 1 Coverage：$\frac{2}{3} = 0.67$

**Layer 2 展开**（Direct Parent）：
- $p_1 = \mathrm{parent}(c_1)$：包含 $f_1$ 和 $f_3$
- $p_2 = \mathrm{parent}(c_2)$：包含 $f_2$
- $p_3, p_4, p_5$：无关内容

**最终上下文**（去重后）：$\{p_1, p_2, p_3\}$

### 6.2 指标计算

**Evidence Coverage**：
- $h^{(2)}_{1} = 1$（$f_1$ 在 $p_1$ 中）
- $h^{(2)}_{2} = 1$（$f_2$ 在 $p_2$ 中）
- $h^{(2)}_{3} = 1$（$f_3$ 在 $p_1$ 中）
- $\mathrm{EC}(Q001) = \frac{3}{3} = 1.0$

**Complete Group Coverage**：
- $G_1$ 的所有证据都覆盖：$\mathrm{CGC}(Q001) = 1$

**Context Relevance**（假设）：
- $p_1$：相关（含必要证据）
- $p_2$：相关（含必要证据）
- $p_3$：无关
- $\mathrm{CR}(Q001) = \frac{2}{3} = 0.67$

**Noise Ratio**：
$$
\mathrm{NR}(Q001) = 1 - 0.67 = 0.33
$$

**Sufficiency Accuracy**（假设）：
- Gold 标签：sufficient（EC = 1.0）
- 系统预测：sufficient（EC ≥ 0.9）
- 一致：$\mathbf{1}[y = \hat{y}] = 1$

### 6.3 Parent 挽回案例

**关键观察**：
- Layer 1 Coverage：0.67（不完整，缺 $f_3$）
- Layer 2 Coverage：1.0（完整）
- **归因**：parent $p_1$ 补出了 child $c_1$ 未含的 $f_3$

**记录**：
```json
{
  "intent_id": "Q001",
  "layer1_coverage": 0.67,
  "layer2_coverage": 1.0,
  "recovery": {
    "recovered_evidence": ["f3"],
    "recovery_source": "parent_p1",
    "mechanism": "parent_expansion"
  }
}
```

**不追改 Layer 1**：Layer 1 的 Coverage 保持 0.67，不因 parent 补证而修改。

## 7. 与其他 Layer 的联合分析

### 7.1 Layer 2 → Layer 3 传递

**研究问题**：Evidence Coverage 能否预测 Answer Correctness？

**相关性分析**：
$$
\rho = \text{corr}(\mathrm{EC}, \mathrm{Answer\,Correctness})
$$

**预期**：$\rho > 0.6$（强正相关）

**回归模型**：
$$
\mathrm{Answer\,Correctness} = \beta_0 + \beta_1 \cdot \mathrm{EC} + \beta_2 \cdot \mathrm{CR} + \epsilon
$$

### 7.2 Layer 1 + Layer 2 错误传播

**四态统计**（见 [design.md](design.md) §2.3）：

| 状态 | Layer 1 | Layer 2 | 频次 | 占比 |
|---|---|---|---|---|
| 成功 | ✓ | ✓ | $n_{11}$ | $p_{11}$ |
| Layer 2 失败 | ✓ | ✗ | $n_{10}$ | $p_{10}$ |
| Parent 挽回 | ✗ | ✓ | $n_{01}$ | $p_{01}$ |
| 均失败 | ✗ | ✗ | $n_{00}$ | $p_{00}$ |

**挽回率**：
$$
\mathrm{Recovery\,Rate} = \frac{n_{01}}{n_{01} + n_{00}}
$$

**新增失败率**：
$$
\mathrm{New\,Failure\,Rate} = \frac{n_{10}}{n_{11} + n_{10}}
$$

### 7.3 Layer 2 × Layer 5 (Agentic)

**Sufficiency Accuracy 对 Agent 的影响**：

- **高 FPR**（不足误判为充分）→ Agent 过早停止 → 答案质量下降
- **高 FNR**（充分误判为不足）→ Agent 过度检索 → 成本增加，但质量不变

**成本-质量权衡**：
$$
\mathrm{Utility} = w_1 \cdot \mathrm{Answer\,Correctness} - w_2 \cdot \mathrm{Cost}
$$

优化 Sufficiency 判断阈值 $\theta$ 使 Utility 最大。

## 8. 实现与计算

### 8.1 计算流程

```python
def compute_layer2_metrics(intent, layer1_output, layer2_output, gold):
    # 1. Evidence Coverage
    covered = [evidence in layer2_output.context
               for evidence in gold.required_evidence]
    ec = sum(covered) / len(covered)

    # 2. Complete Group Coverage
    cgc = any(all(e in layer2_output.context for e in group)
              for group in gold.evidence_groups)

    # 3. Sufficiency Accuracy
    gold_sufficient = (ec >= gold.sufficiency_threshold)
    pred_sufficient = layer2_output.sufficiency_judgment
    sufficiency_match = (gold_sufficient == pred_sufficient)

    # 4. Context Relevance
    relevance_scores = [chunk.relevance for chunk in layer2_output.chunks]
    cr = sum(relevance_scores) / len(relevance_scores)

    # 5. Noise Ratio
    nr = 1 - cr

    # 6. Recovery analysis
    layer1_ec = sum([e in layer1_output.top_k for e in gold.required_evidence]) / len(gold.required_evidence)
    recovery = (layer1_ec < 1.0 and ec >= 1.0)

    return {
        "evidence_coverage": ec,
        "complete_group_coverage": cgc,
        "sufficiency_accuracy": sufficiency_match,
        "context_relevance": cr,
        "noise_ratio": nr,
        "recovery": recovery,
        "layer1_to_layer2_gain": ec - layer1_ec
    }
```

### 8.2 批量汇总

```python
def aggregate_metrics(all_results):
    N = len(all_results)

    return {
        "evidence_coverage": sum(r["evidence_coverage"] for r in all_results) / N,
        "complete_group_coverage": sum(r["complete_group_coverage"] for r in all_results) / N,
        "sufficiency_accuracy": sum(r["sufficiency_accuracy"] for r in all_results) / N,
        "context_relevance": sum(r["context_relevance"] for r in all_results) / N,
        "noise_ratio": sum(r["noise_ratio"] for r in all_results) / N,
        "recovery_rate": sum(r["recovery"] for r in all_results if not r["layer1_complete"]) /
                        sum(1 for r in all_results if not r["layer1_complete"]),
    }
```

## 9. 报告模板

### 9.1 主表

| 方法 | Evidence Coverage | Complete Group Coverage | Sufficiency Acc. | Noise Ratio |
|---|---|---|---|---|
| Baseline (No expansion) | — | — | — | — |
| Direct Parent | — | — | — | — |
| Parent + Siblings | — | — | — | — |
| Adaptive | — | — | — | — |

### 9.2 诊断表

| 方法 | Recovery Rate | New Failure Rate | FPR | FNR | Avg. Context Tokens |
|---|---|---|---|---|---|
| Baseline | 0% | — | — | — | 2847 |
| Direct Parent | — | — | — | — | 4123 |
| Parent + Siblings | — | — | — | — | 7856 |

## 10. 与旧指标的区分

| 旧名称（可能） | 新定义 | 差异 |
|---|---|---|
| Coverage | Evidence Coverage（Layer 2） | 明确为组装后上下文的覆盖 |
| Sufficiency | Sufficiency Accuracy | 测量判断准确性，非覆盖度 |
| Relevance | Context Relevance（Layer 2） | 明确为最终上下文的相关性 |

**命名约定**：所有 Layer 2 指标冠以 "Layer 2" 或明确标注观察对象，避免与 Layer 1 混淆。

## 11. 下一步

1. **标注指南**：编写 `annotation-guidelines.md`，定义充分性和相关性的人工标注流程
2. **展开规则**：编写 `expansion-strategies.md`，固化展开、去重、截断算法
3. **实验设计**：编写 `experiments.md`，冻结对照组、控制变量和统计方法
4. **标注执行**：按指南完成开发集标注，计算 Kappa
5. **指标验证**：在开发集上验证指标的区分度和稳定性

## 12. 参考文献

| 文献 | 相关指标 | 引用点 |
|---|---|---|
| RARE (ACL 2026) | Coverage@K, PerfRecall@K | Evidence Coverage 的定义基础 |
| S2G-RAG (ACL 2026) | 充分性判断 | Sufficiency Accuracy 的动机 |
| ARES (NAACL 2024) | Context Relevance | Context Relevance 的命名来源 |

完整文献引用见 [references/README.md](../references/README.md)。
