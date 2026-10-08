# Layer 2: Expansion Strategies

*Parent-child 展开规则的形式化定义与实现 · status: plan · 2026-09-29*

> **本文档规定上下文组装的技术细节**：展开、去重、排序和截断的算法及其配置参数。每个策略给出形式化定义、伪代码和配置模板，确保实验可复现。

## 1. 组装管道概览

### 1.1 四阶段管道

```mermaid
flowchart LR
    A[Top-K Child Chunks] --> B[Expansion]
    B --> C[Deduplication]
    C --> D[Ordering]
    D --> E[Truncation]
    E --> F[Final Context]

    style B fill:#e1f5ff
    style C fill:#fff4e1
    style D fill:#e8f5e9
    style E fill:#fce4ec
```

**各阶段职责**：

| 阶段 | 输入 | 输出 | 可配置 |
|---|---|---|---|
| **Expansion** | Top-K child chunks | Child + parent chunks | 展开策略、条件 |
| **Deduplication** | Expanded chunks | Unique chunks | 去重方法、阈值 |
| **Ordering** | Unique chunks | Sorted chunks | 排序依据 |
| **Truncation** | Sorted chunks | Final context (≤ B tokens) | Token 预算、截断策略 |

### 1.2 配置版本化

每个实验须冻结完整配置：

```yaml
layer2_assembly_config:
  version: "v1.0"
  expansion:
    strategy: "direct_parent"
    conditions:
      rank_threshold: 10
      parent_must_exist: true
    merge_mode: "replace_child"
  deduplication:
    method: "exact"
    semantic_threshold: null
  ordering:
    strategy: "by_document_position"
  truncation:
    token_budget: 8192
    strategy: "by_rank"
    tokenizer: "cl100k_base"
```

## 2. Expansion（展开）

### 2.1 策略定义

#### 策略 1：None（无展开）

**定义**：不展开，直接使用 Top-K child chunks。

**形式化**：
$$
E_{\text{none}}(C) = C
$$

**用途**：基线对照，测量 parent 展开的增益。

**伪代码**：
```python
def expand_none(children):
    return children
```

#### 策略 2：Direct Parent（直接父节点）

**定义**：用每个 child 的直接 parent 替换该 child。

**形式化**：
$$
E_{\text{direct}}(C) = \{p_i \mid c_i \in C, p_i \text{ exists}\} \cup \{c_i \mid c_i \in C, p_i \text{ not exists}\}
$$

**伪代码**：
```python
def expand_direct_parent(children, chunk_store):
    expanded = []
    for child in children:
        parent_id = child.parent_id
        if parent_id and parent_id in chunk_store:
            parent = chunk_store[parent_id]
            expanded.append(parent)
        else:
            # Parent 不存在，保留 child
            expanded.append(child)
    return expanded
```

**注意事项**：
- 若多个 child 共享同一 parent，会出现重复 → 交给 Deduplication 处理
- 保留原始 child 的 rank 信息，传递给 parent

#### 策略 3：Parent with Siblings（父节点及兄弟）

**定义**：展开每个 child 的 parent 及该 parent 的所有 children（siblings）。

**形式化**：
$$
E_{\text{siblings}}(C) = \bigcup_{c_i \in C} \left\{\text{siblings}(p_i) \mid p_i = \text{parent}(c_i)\right\}
$$

其中 $\text{siblings}(p) = \{c \mid \text{parent}(c) = p\}$。

**伪代码**：
```python
def expand_parent_with_siblings(children, chunk_store):
    expanded = []
    seen_parents = set()

    for child in children:
        parent_id = child.parent_id
        if not parent_id or parent_id in seen_parents:
            continue
        seen_parents.add(parent_id)

        parent = chunk_store.get(parent_id)
        if parent:
            # 获取该 parent 的所有 children (siblings)
            siblings = chunk_store.get_children(parent_id)
            expanded.extend(siblings)
        else:
            expanded.append(child)

    return expanded
```

**优点**：覆盖连续文本，有利于理解上下文。

**缺点**：高冗余，可能大幅增加 token 数。

#### 策略 4：Selective Expansion（选择性展开）

**定义**：仅当 child 被判断为"不完整"时才展开 parent。

**形式化**：
$$
E_{\text{selective}}(C) = \left\{
\begin{aligned}
&p_i, && \text{if } \text{incomplete}(c_i) \land p_i \text{ exists} \\
&c_i, && \text{otherwise}
\end{aligned}
\right\}
$$

**完整性判断**（启发式）：
- Chunk 以不完整句结尾（无句号）
- Chunk 长度 < 阈值（如 200 tokens）
- Chunk 首尾有截断标记

**伪代码**：
```python
def expand_selective(children, chunk_store, incomplete_threshold=200):
    expanded = []
    for child in children:
        is_incomplete = (
            len(child.text) < incomplete_threshold or
            not child.text.strip().endswith('.') or
            child.metadata.get('truncated', False)
        )

        if is_incomplete and child.parent_id:
            parent = chunk_store.get(child.parent_id)
            if parent:
                expanded.append(parent)
            else:
                expanded.append(child)
        else:
            expanded.append(child)

    return expanded
```

**优点**：平衡精准与覆盖，减少不必要的展开。

**缺点**：依赖启发式判断，可能误判。

### 2.2 条件控制

#### 2.2.1 Rank Threshold（排名阈值）

**定义**：只展开 Top-N 的 child，其余保持原样。

**用途**：控制展开范围，避免低排名 chunk 引入过多噪声。

**实现**：
```python
def expand_with_rank_threshold(children, chunk_store, rank_threshold=10):
    expanded = []
    for child in children:
        if child.rank <= rank_threshold and child.parent_id:
            parent = chunk_store.get(child.parent_id)
            if parent:
                expanded.append(parent)
            else:
                expanded.append(child)
        else:
            expanded.append(child)
    return expanded
```

**推荐值**：
- 严格：$N = 5$
- 中等：$N = 10$
- 宽松：$N = 20$

#### 2.2.2 Merge Mode（合并模式）

**两种模式**：

| 模式 | 行为 | 优点 | 缺点 |
|---|---|---|---|
| **Replace Child** | 用 parent 替换 child | 避免重复，token 数较少 | 可能丢失 child 的精准定位 |
| **Append Parent** | 保留 child，追加 parent | 保留原始排名信息 | Token 数增加，高冗余 |

**实现**：
```python
def expand_with_merge_mode(children, chunk_store, mode="replace_child"):
    if mode == "replace_child":
        return expand_direct_parent(children, chunk_store)
    elif mode == "append_parent":
        expanded = []
        for child in children:
            expanded.append(child)
            if child.parent_id:
                parent = chunk_store.get(child.parent_id)
                if parent:
                    expanded.append(parent)
        return expanded
    else:
        raise ValueError(f"Unknown merge mode: {mode}")
```

**推荐**：主实验用 "replace_child"，诊断实验对比两种模式。

### 2.3 展开元数据

**追踪信息**（用于后续分析）：

```python
class ExpandedChunk:
    def __init__(self, chunk, source_type, original_rank):
        self.chunk = chunk
        self.source_type = source_type  # "child" | "parent"
        self.original_rank = original_rank  # 原始 child 的排名
        self.expansion_strategy = None  # 记录使用的策略
```

**用途**：
- 分析 parent 补证情况
- 追溯噪声来源（child vs parent）
- 评估不同策略的效果

## 3. Deduplication（去重）

### 3.1 去重方法

#### 方法 1：Exact Match（精确匹配）

**定义**：完全相同的文本只保留一份。

**形式化**：
$$
D_{\text{exact}}(E) = \{e \in E \mid \forall e' \in E, e' \ne e \implies \text{text}(e) \ne \text{text}(e')\}
$$

**伪代码**：
```python
def deduplicate_exact(chunks):
    seen_texts = set()
    unique_chunks = []

    for chunk in chunks:
        text_hash = hash(chunk.text.strip())
        if text_hash not in seen_texts:
            seen_texts.add(text_hash)
            unique_chunks.append(chunk)

    return unique_chunks
```

**优点**：确定性，无参数。

**缺点**：无法处理改写或部分重叠。

#### 方法 2：Semantic Deduplication（语义去重）

**定义**：嵌入相似度超过阈值视为重复。

**形式化**：
$$
D_{\text{semantic}}(E, \theta) = \{e \in E \mid \forall e' \in E, e' \prec e \implies \text{sim}(\text{emb}(e), \text{emb}(e')) < \theta\}
$$

其中 $e' \prec e$ 表示 $e'$ 在 $e$ 之前处理。

**伪代码**：
```python
def deduplicate_semantic(chunks, embedder, threshold=0.95):
    unique_chunks = []
    embeddings = [embedder.embed(c.text) for c in chunks]

    for i, chunk in enumerate(chunks):
        is_duplicate = False
        for j in range(i):
            similarity = cosine_similarity(embeddings[i], embeddings[j])
            if similarity >= threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            unique_chunks.append(chunk)

    return unique_chunks
```

**阈值选择**：
- 严格：$\theta = 0.98$（几乎相同才去重）
- 中等：$\theta = 0.95$
- 宽松：$\theta = 0.90$（高相似即去重）

**成本**：需要计算嵌入，$O(n^2)$ 相似度比较。

#### 方法 3：Span-based Deduplication（区间去重）

**定义**：来自同一文档且 token 重叠超过阈值视为重复。

**形式化**：
$$
\text{overlap}(e_1, e_2) = \frac{|\text{span}(e_1) \cap \text{span}(e_2)|}{|\text{span}(e_1) \cup \text{span}(e_2)|}
$$

若 $\text{doc}(e_1) = \text{doc}(e_2)$ 且 $\text{overlap}(e_1, e_2) > \theta$，则视为重复。

**伪代码**：
```python
def deduplicate_span_based(chunks, overlap_threshold=0.7):
    unique_chunks = []

    for chunk in chunks:
        is_duplicate = False
        for existing in unique_chunks:
            if chunk.doc_id == existing.doc_id:
                overlap = compute_token_overlap(chunk, existing)
                if overlap > overlap_threshold:
                    is_duplicate = True
                    break

        if not is_duplicate:
            unique_chunks.append(chunk)

    return unique_chunks

def compute_token_overlap(chunk1, chunk2):
    span1 = set(range(chunk1.start_token, chunk1.end_token))
    span2 = set(range(chunk2.start_token, chunk2.end_token))

    intersection = len(span1 & span2)
    union = len(span1 | span2)

    return intersection / union if union > 0 else 0
```

**适用场景**：parent-child 场景，parent 和 child 必然重叠。

### 3.2 去重顺序

**问题**：多个相似 chunks，保留哪一个？

**策略**：

| 策略 | 保留规则 | 理由 |
|---|---|---|
| **First** | 保留最早遇到的 | 保持原始排名 |
| **Highest Rank** | 保留检索排名最高的 | 优先保留更相关的 |
| **Longest** | 保留文本最长的 | 更完整的上下文 |
| **Parent Priority** | 优先保留 parent | Parent 通常更完整 |

**推荐**：First（保持排名一致性）。

**实现**：
```python
def deduplicate_with_priority(chunks, method="first"):
    if method == "first":
        # chunks 已按顺序排列，正常去重即保留 first
        return deduplicate_exact(chunks)

    elif method == "highest_rank":
        # 先按 rank 排序，再去重
        sorted_chunks = sorted(chunks, key=lambda c: c.original_rank)
        return deduplicate_exact(sorted_chunks)

    elif method == "longest":
        # 遇到重复时，保留更长的
        seen_texts = {}
        for chunk in chunks:
            text_hash = hash(chunk.text.strip())
            if text_hash not in seen_texts:
                seen_texts[text_hash] = chunk
            else:
                if len(chunk.text) > len(seen_texts[text_hash].text):
                    seen_texts[text_hash] = chunk
        return list(seen_texts.values())

    elif method == "parent_priority":
        # Parent 优先于 child
        seen_texts = {}
        for chunk in chunks:
            text_hash = hash(chunk.text.strip())
            if text_hash not in seen_texts:
                seen_texts[text_hash] = chunk
            else:
                if chunk.source_type == "parent":
                    seen_texts[text_hash] = chunk
        return list(seen_texts.values())
```

### 3.3 去重统计

**记录指标**（用于分析）：

```python
dedup_stats = {
    "num_before_dedup": len(expanded_chunks),
    "num_after_dedup": len(unique_chunks),
    "num_removed": len(expanded_chunks) - len(unique_chunks),
    "dedup_rate": (len(expanded_chunks) - len(unique_chunks)) / len(expanded_chunks),
    "avg_similarity_removed": avg_sim  # 若使用语义去重
}
```

## 4. Ordering（排序）

### 4.1 排序策略

#### 策略 1：By Rank（按检索排名）

**定义**：按原始 child 的检索排名排序。

**伪代码**：
```python
def order_by_rank(chunks):
    return sorted(chunks, key=lambda c: c.original_rank)
```

**优点**：保持检索器的判断。

**缺点**：打乱文档原始顺序，可能影响理解。

#### 策略 2：By Document Position（按文档位置）

**定义**：按来源文档和在文档中的位置排序。

**伪代码**：
```python
def order_by_document_position(chunks):
    return sorted(chunks, key=lambda c: (c.doc_id, c.start_token))
```

**优点**：恢复原文顺序，有利于保持上下文连贯性。

**缺点**：不同文档的 chunks 交错排列，可能混乱。

#### 策略 3：By Document + Rank（文档内排名）

**定义**：先按 doc_id 分组，组内按 rank 排序。

**伪代码**：
```python
def order_by_document_and_rank(chunks):
    # 按 doc_id 分组
    from collections import defaultdict
    doc_groups = defaultdict(list)
    for chunk in chunks:
        doc_groups[chunk.doc_id].append(chunk)

    # 每组内按 rank 排序
    for doc_id in doc_groups:
        doc_groups[doc_id].sort(key=lambda c: c.original_rank)

    # 按 doc_id 的最高 rank 排序组
    sorted_groups = sorted(doc_groups.items(),
                           key=lambda item: min(c.original_rank for c in item[1]))

    # 展平
    ordered_chunks = []
    for doc_id, group in sorted_groups:
        ordered_chunks.extend(group)

    return ordered_chunks
```

**优点**：同一文档的内容相邻，且高排名文档优先。

**缺点**：实现复杂。

#### 策略 4：By Relevance Score（按相关性分数）

**定义**：按检索分数降序排列。

**伪代码**：
```python
def order_by_score(chunks):
    return sorted(chunks, key=lambda c: c.score, reverse=True)
```

**优点**：最相关的内容优先。

**缺点**：parent 没有原始检索分数，需要继承或重新计算。

### 4.2 推荐策略

**主实验**：By Document Position
- 理由：保持原文连贯性，有利于理解科学论述
- 适用：行人交通文献通常逻辑清晰，顺序阅读更易理解

**对照实验**：By Rank
- 理由：测试排序对充分性的影响

## 5. Truncation（截断）

### 5.1 Token 预算

**常用预算**：

| 预算 | 用途 | 估计 chunks |
|---|---|---|
| 2K | 资源受限 | ~5-8 |
| 4K | 标准短上下文 | ~10-15 |
| 8K | 推荐主实验 | ~20-30 |
| 16K | 长上下文模型 | ~40-60 |
| 32K | 极长上下文 | ~80-120 |

**Tokenizer**：与生成模型一致（如 `cl100k_base` for GPT-4）。

### 5.2 截断策略

#### 策略 1：By Rank（按排名截断）

**定义**：按排序后的顺序，累计 tokens 直到达到预算。

**伪代码**：
```python
def truncate_by_rank(chunks, token_budget, tokenizer):
    truncated = []
    total_tokens = 0

    for chunk in chunks:
        chunk_tokens = len(tokenizer.encode(chunk.text))
        if total_tokens + chunk_tokens <= token_budget:
            truncated.append(chunk)
            total_tokens += chunk_tokens
        else:
            break  # 达到预算，停止

    return truncated, total_tokens
```

**优点**：简单，确定性。

**缺点**：可能截断重要证据。

#### 策略 2：By Coverage（按证据覆盖截断）

**定义**：优先保留覆盖必要证据的 chunks，直到预算用尽或证据完整。

**伪代码**：
```python
def truncate_by_coverage(chunks, token_budget, tokenizer, required_evidence):
    # 标记每个 chunk 覆盖的证据
    chunk_evidence_map = {}
    for i, chunk in enumerate(chunks):
        chunk_evidence_map[i] = detect_evidence_in_chunk(chunk, required_evidence)

    # 贪心选择：每次选覆盖最多新证据的 chunk
    selected_indices = []
    covered_evidence = set()
    total_tokens = 0

    while len(covered_evidence) < len(required_evidence):
        best_idx = None
        best_new_coverage = 0

        for i, chunk in enumerate(chunks):
            if i in selected_indices:
                continue

            chunk_tokens = len(tokenizer.encode(chunk.text))
            if total_tokens + chunk_tokens > token_budget:
                continue

            new_coverage = len(chunk_evidence_map[i] - covered_evidence)
            if new_coverage > best_new_coverage:
                best_new_coverage = new_coverage
                best_idx = i

        if best_idx is None:
            break  # 无法再添加 chunk

        selected_indices.append(best_idx)
        covered_evidence.update(chunk_evidence_map[best_idx])
        total_tokens += len(tokenizer.encode(chunks[best_idx].text))

    # 按原始顺序排列
    selected_indices.sort()
    truncated = [chunks[i] for i in selected_indices]

    return truncated, total_tokens
```

**优点**：最大化证据覆盖。

**缺点**：
- 需要实时证据检测（成本高）
- 打乱原始排序
- 实验结果难以归因（截断策略本身成为变量）

**推荐**：仅用于诊断实验，主实验仍用 By Rank。

#### 策略 3：Soft Truncation（软截断）

**定义**：允许超出预算一个 chunk，避免截断到句子中间。

**伪代码**：
```python
def truncate_soft(chunks, token_budget, tokenizer):
    truncated = []
    total_tokens = 0

    for chunk in chunks:
        chunk_tokens = len(tokenizer.encode(chunk.text))
        truncated.append(chunk)
        total_tokens += chunk_tokens

        if total_tokens >= token_budget:
            break  # 已达预算，允许最后一个 chunk 超出

    return truncated, total_tokens
```

**优点**：避免截断不完整，更自然。

**缺点**：token 数不严格受控，可能超出模型限制。

### 5.3 截断元数据

**记录信息**：

```python
truncation_stats = {
    "token_budget": 8192,
    "num_chunks_before_truncation": 25,
    "num_chunks_after_truncation": 18,
    "final_tokens": 7856,
    "utilization_rate": 7856 / 8192,
    "num_chunks_truncated": 7,
    "truncated_chunk_ids": ["chunk_19", "chunk_20", ...]
}
```

**用途**：分析截断对证据覆盖的影响。

## 6. 完整管道实现

### 6.1 主函数

```python
def assemble_context(
    top_k_children,
    chunk_store,
    config
):
    """
    完整的上下文组装管道

    Args:
        top_k_children: Layer 1 输出的 Top-K child chunks
        chunk_store: Chunk 存储（包含 parent）
        config: 配置字典

    Returns:
        final_context: 最终上下文文本
        assembly_log: 组装日志（用于分析）
    """
    # Stage 1: Expansion
    expanded = expand(
        top_k_children,
        chunk_store,
        strategy=config["expansion"]["strategy"],
        **config["expansion"].get("conditions", {})
    )

    # Stage 2: Deduplication
    unique = deduplicate(
        expanded,
        method=config["deduplication"]["method"],
        threshold=config["deduplication"].get("semantic_threshold")
    )

    # Stage 3: Ordering
    ordered = order(
        unique,
        strategy=config["ordering"]["strategy"]
    )

    # Stage 4: Truncation
    truncated, final_tokens = truncate(
        ordered,
        token_budget=config["truncation"]["token_budget"],
        strategy=config["truncation"]["strategy"],
        tokenizer=config["truncation"]["tokenizer"]
    )

    # Concatenate to final context
    final_context = "\n\n".join([c.text for c in truncated])

    # Assembly log
    assembly_log = {
        "num_children": len(top_k_children),
        "num_after_expansion": len(expanded),
        "num_after_dedup": len(unique),
        "num_after_truncation": len(truncated),
        "final_tokens": final_tokens,
        "config": config
    }

    return final_context, truncated, assembly_log
```

### 6.2 配置示例

**Baseline（无展开）**：
```yaml
expansion:
  strategy: "none"
deduplication:
  method: "exact"
ordering:
  strategy: "by_rank"
truncation:
  token_budget: 8192
  strategy: "by_rank"
  tokenizer: "cl100k_base"
```

**Direct Parent（推荐）**：
```yaml
expansion:
  strategy: "direct_parent"
  conditions:
    rank_threshold: 10
  merge_mode: "replace_child"
deduplication:
  method: "exact"
ordering:
  strategy: "by_document_position"
truncation:
  token_budget: 8192
  strategy: "by_rank"
  tokenizer: "cl100k_base"
```

**Aggressive（高覆盖）**：
```yaml
expansion:
  strategy: "parent_with_siblings"
deduplication:
  method: "semantic"
  semantic_threshold: 0.95
ordering:
  strategy: "by_document_position"
truncation:
  token_budget: 16384
  strategy: "soft"
  tokenizer: "cl100k_base"
```

## 7. 实验对照

### 7.1 展开策略对比

| 配置 | Expansion | Dedup | Order | Truncation | 预期 Coverage | 预期 Noise |
|---|---|---|---|---|---|---|
| **Baseline** | None | Exact | Rank | 8K / Rank | 低 | 低 |
| **Direct** | Direct Parent | Exact | Rank | 8K / Rank | 中 | 中 |
| **Siblings** | Parent+Siblings | Semantic(0.95) | DocPos | 16K / Rank | 高 | 高 |
| **Selective** | Selective | Exact | Rank | 8K / Rank | 中高 | 低中 |

### 7.2 Token 预算对比

固定 Expansion=Direct Parent，变化 Token Budget：

| Budget | 预期覆盖率 | 预期噪声率 | 用途 |
|---|---|---|---|
| 2K | 50-60% | 15-20% | 资源受限基线 |
| 4K | 70-80% | 20-25% | 短上下文 |
| 8K | 85-95% | 25-30% | 推荐主实验 |
| 16K | 95-99% | 30-35% | 长上下文测试 |

## 8. 实现注意事项

### 8.1 边界情况处理

**Parent 不存在**：
```python
if parent_id and parent_id in chunk_store:
    parent = chunk_store[parent_id]
else:
    # Fallback: 保留 child
    parent = child
```

**Token 超限**：
```python
if final_tokens > model_max_tokens:
    logger.warning(f"Context exceeds model limit: {final_tokens} > {model_max_tokens}")
    # 选项 1: 进一步截断
    # 选项 2: 报错并记录
    # 选项 3: 切换到更大上下文模型
```

**空上下文**：
```python
if not truncated:
    logger.error("Final context is empty after assembly")
    # 返回原始 Top-1 child 作为 fallback
    return top_k_children[0].text
```

### 8.2 性能优化

**嵌入缓存**（Semantic Dedup）：
```python
embedding_cache = {}

def get_embedding_cached(text, embedder):
    text_hash = hash(text)
    if text_hash not in embedding_cache:
        embedding_cache[text_hash] = embedder.embed(text)
    return embedding_cache[text_hash]
```

**批量去重**：
```python
# 使用向量化相似度计算
similarities = cosine_similarity_matrix(embeddings)  # O(n^2) but vectorized
```

### 8.3 日志与调试

**详细日志**（调试模式）：
```python
logger.debug(f"Expansion: {len(top_k_children)} → {len(expanded)}")
logger.debug(f"Deduplication: {len(expanded)} → {len(unique)}")
logger.debug(f"Truncation: {len(ordered)} → {len(truncated)}, {final_tokens} tokens")
logger.debug(f"Final context length: {len(final_context)} chars")
```

**保存中间结果**（用于分析）：
```python
intermediate_outputs = {
    "top_k_children": serialize(top_k_children),
    "after_expansion": serialize(expanded),
    "after_dedup": serialize(unique),
    "after_ordering": serialize(ordered),
    "final_truncated": serialize(truncated)
}
save_json(intermediate_outputs, f"debug/{intent_id}_assembly.json")
```

## 9. 版本兼容性

### 9.1 配置向后兼容

**v1.0 → v1.1 变更**：
- 新增 `expansion.merge_mode`
- 新增 `truncation.soft` 选项

**处理**：
```python
def load_config(config_dict):
    # 设置默认值，确保向后兼容
    config = {
        "expansion": {
            "strategy": config_dict.get("expansion", {}).get("strategy", "direct_parent"),
            "merge_mode": config_dict.get("expansion", {}).get("merge_mode", "replace_child"),
        },
        # ...
    }
    return config
```

### 9.2 配置验证

```python
def validate_config(config):
    """验证配置合法性"""
    assert config["expansion"]["strategy"] in ["none", "direct_parent", "parent_with_siblings", "selective"]
    assert config["deduplication"]["method"] in ["exact", "semantic", "span_based"]
    assert config["truncation"]["token_budget"] > 0

    if config["deduplication"]["method"] == "semantic":
        assert config["deduplication"]["semantic_threshold"] is not None

    return True
```

## 10. 下一步

1. **实现管道**：按本文档实现完整的组装管道代码
2. **单元测试**：测试每个阶段的正确性
3. **集成测试**：端到端测试完整管道
4. **性能基准**：测试各策略的运行时间
5. **实验设计**：编写 `experiments.md`，冻结对照组配置

## 11. 参考

- **Parent-child chunking**：LlamaIndex, LangChain 的实现
- **Semantic deduplication**：近似最近邻（ANN）算法
- **Token counting**：tiktoken (OpenAI), transformers (HuggingFace)

---

**文档版本**：v1.0\
**生效日期**：待实现验证后冻结\
**维护者**：Layer 2 设计团队
