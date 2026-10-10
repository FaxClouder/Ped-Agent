# Gold Questions 准备指南

_历史示例 · status: historical；其中人工标注流程和示例资源 ID 不适用于当前 Gold v2_

当前 RAG 评测流程以 [`../memPed/knowledge/gold/2026-09-23-rebuild/annotation_protocol.md`](../memPed/knowledge/gold/2026-09-23-rebuild/annotation_protocol.md)
和 [`../experiments/benchmark-gold-20260923/README.md`](../experiments/benchmark-gold-20260923/README.md)
为准。下文仅保留早期 30 题示例，不作为实验启动或人工复核要求。

---

## 🎯 什么是 Gold Questions？

Gold Questions（黄金问题集）是一套**人工标注的标准测试问题**，用于评估知识库检索系统的质量。

### 核心作用
1. **评测检索质量**：衡量系统能否找到正确答案
2. **基准对比**：不同版本/配置的效果对比
3. **发现问题**：识别检索失败的案例
4. **持续改进**：指导系统优化方向

---

## 📋 Gold Questions 的组成

每个 Gold Question 包含：

### 1. 问题本身（Query）
**示例**：
- "什么是行人流基本图？"
- "瓶颈对行人流量有什么影响？"
- "Love Parade 踩踏事故的主要原因是什么？"

### 2. 相关文献（Relevant Documents）
标注哪些文献包含答案：
```json
{
  "question_id": "gq-001",
  "query": "什么是行人流基本图？",
  "relevant_docs": ["lit-001", "lit-006"],  // 相关文献 ID
  "relevant_pages": [[5, 6], [10, 12]]      // 具体页码
}
```

### 3. 难度等级（可选）
- **Easy**: 直接概念查询
- **Medium**: 需要理解关系
- **Hard**: 需要综合多篇文献

### 4. 主题标签（可选）
- `fundamental_diagram`
- `evacuation`
- `bottleneck`
- `safety`

---

## 🎨 Gold Questions 的设计原则

### 1. 覆盖性（Coverage）
确保问题覆盖所有主题：
- ✅ T1 基础理论：6 个问题
- ✅ T2 实验测量：6 个问题
- ✅ T3 设施流动：6 个问题
- ✅ T4 疏散建模：6 个问题
- ✅ T5 安全干预：6 个问题

**总计**：30 个问题（Pilot 阶段）

---

### 2. 多样性（Diversity）
包含不同类型的问题：

#### 类型 A: 概念查询
- "什么是基本图？"
- "社会力模型是什么？"

#### 类型 B: 关系查询
- "密度与速度的关系是什么？"
- "瓶颈如何影响流量？"

#### 类型 C: 数值查询
- "行人流的最大密度是多少？"
- "疏散前延迟时间的典型范围？"

#### 类型 D: 案例查询
- "Love Parade 事故中发生了什么？"
- "海啸疏散演练的主要发现？"

#### 类型 E: 方法查询
- "如何测量行人轨迹？"
- "疏散模拟用什么方法？"

---

### 3. 真实性（Authenticity）
问题应该是：
- ✅ 研究人员真实会问的问题
- ✅ 用自然语言表达
- ✅ 不是为了"考倒"系统而设计

**好的问题**：
```
❌ "请列举所有提到基本图的文献的作者、年份和引用次数"
✅ "基本图的研究有哪些重要文献？"
```

---

### 4. 可验证性（Verifiability）
答案必须能在文献中找到：
- ✅ 明确标注相关文献
- ✅ 标注具体页码
- ✅ 至少 1 篇文献包含答案
- ✅ 答案可以人工验证

---

## 📊 Gold Questions 示例（30 个）

### T1: 基础理论（6 个）

```jsonl
{"question_id": "gq-t1-01", "query": "什么是行人流基本图？它描述了什么关系？", "relevant_docs": ["lit-001", "lit-006"], "relevant_pages": [[5, 6], [10, 12]], "difficulty": "easy", "topics": ["fundamental_diagram", "flow_theory"]}

{"question_id": "gq-t1-02", "query": "Helbing 的社会力模型的核心思想是什么？", "relevant_docs": ["lit-003"], "relevant_pages": [[2, 3, 4]], "difficulty": "medium", "topics": ["social_force", "model"]}

{"question_id": "gq-t1-03", "query": "行人流中的拥堵转变（jamming transition）是如何发生的？", "relevant_docs": ["lit-005"], "relevant_pages": [[6, 7, 8]], "difficulty": "hard", "topics": ["jamming", "phase_transition"]}

{"question_id": "gq-t1-04", "query": "速度与密度的关系在不同文化背景下有差异吗？", "relevant_docs": ["lit-002"], "relevant_pages": [[8, 9]], "difficulty": "medium", "topics": ["cultural_difference", "velocity_density"]}

{"question_id": "gq-t1-05", "query": "单列行人流的特征与自由流动有什么不同？", "relevant_docs": ["lit-004"], "relevant_pages": [[5, 6]], "difficulty": "medium", "topics": ["single_file", "fundamental_diagram"]}

{"question_id": "gq-t1-06", "query": "行人流基本图的分段线性特征是什么？", "relevant_docs": ["lit-001", "lit-004"], "relevant_pages": [[7], [10, 11]], "difficulty": "medium", "topics": ["fundamental_diagram", "piecewise_linear"]}
```

---

### T2: 实验测量（6 个）

```jsonl
{"question_id": "gq-t2-01", "query": "如何使用 LiDAR 技术测量高密度人群？", "relevant_docs": ["lit-012"], "relevant_pages": [[4, 5, 6]], "difficulty": "medium", "topics": ["measurement", "lidar", "high_density"]}

{"question_id": "gq-t2-02", "query": "楼梯上行人流的概率基本图有什么特点？", "relevant_docs": ["lit-010"], "relevant_pages": [[8, 9, 10]], "difficulty": "hard", "topics": ["stairway", "probabilistic", "fundamental_diagram"]}

{"question_id": "gq-t2-03", "query": "OpenTraj 数据集包含哪些经典的行人轨迹数据？", "relevant_docs": ["lit-013"], "relevant_pages": [[3, 4]], "difficulty": "easy", "topics": ["dataset", "trajectory"]}

{"question_id": "gq-t2-04", "query": "铁路站台的 3D 轨迹测量使用了什么技术？", "relevant_docs": ["lit-012"], "relevant_pages": [[5, 6]], "difficulty": "medium", "topics": ["railway_station", "3d_tracking"]}

{"question_id": "gq-t2-05", "query": "楼梯双向流的死锁现象是如何观测到的？", "relevant_docs": ["lit-009"], "relevant_pages": [[6, 7, 8]], "difficulty": "medium", "topics": ["stairway", "deadlock", "bidirectional"]}

{"question_id": "gq-t2-06", "query": "疫情期间行人保持社交距离的实验如何设计？", "relevant_docs": ["lit-011"], "relevant_pages": [[4, 5]], "difficulty": "medium", "topics": ["physical_distancing", "experiment"]}
```

---

### T3: 设施流动（6 个）

```jsonl
{"question_id": "gq-t3-01", "query": "残障人士如何影响瓶颈处的人群流动？", "relevant_docs": ["lit-015"], "relevant_pages": [[7, 8, 9]], "difficulty": "medium", "topics": ["disability", "bottleneck"]}

{"question_id": "gq-t3-02", "query": "走廊宽度对双向流分道现象有什么影响？", "relevant_docs": ["lit-017"], "relevant_pages": [[5, 6]], "difficulty": "medium", "topics": ["corridor_width", "lane_formation"]}

{"question_id": "gq-t3-03", "query": "儿童和成人通过瓶颈的特征时间有何差异？", "relevant_docs": ["lit-018"], "relevant_pages": [[8, 9, 10]], "difficulty": "hard", "topics": ["children", "adults", "bottleneck"]}

{"question_id": "gq-t3-04", "query": "楼梯平台的非对称动力学指的是什么？", "relevant_docs": ["lit-020"], "relevant_pages": [[6, 7]], "difficulty": "hard", "topics": ["staircase_landing", "asymmetric"]}

{"question_id": "gq-t3-05", "query": "Seyfried 的瓶颈实验发现了什么新现象？", "relevant_docs": ["lit-016"], "relevant_pages": [[4, 5, 6]], "difficulty": "medium", "topics": ["bottleneck", "seyfried"]}

{"question_id": "gq-t3-06", "query": "校园广场的行人活动模式有什么特征？", "relevant_docs": ["lit-019"], "relevant_pages": [[7, 8]], "difficulty": "easy", "topics": ["campus_square", "activity_pattern"]}
```

---

### T4: 疏散建模（6 个）

```jsonl
{"question_id": "gq-t4-01", "query": "火灾烟雾如何影响疏散行为？", "relevant_docs": ["lit-021"], "relevant_pages": [[8, 9, 10]], "difficulty": "medium", "topics": ["fire", "smoke", "evacuation"]}

{"question_id": "gq-t4-02", "query": "高层建筑疏散的主要挑战是什么？", "relevant_docs": ["lit-022"], "relevant_pages": [[5, 6, 7]], "difficulty": "medium", "topics": ["highrise", "evacuation"]}

{"question_id": "gq-t4-03", "query": "疏散前延迟时间（pre-movement delay）由哪些因素决定？", "relevant_docs": ["lit-025"], "relevant_pages": [[6, 7, 8]], "difficulty": "hard", "topics": ["pre_movement", "delay"]}

{"question_id": "gq-t4-04", "query": "元胞自动机在疏散模拟中如何应用？", "relevant_docs": ["lit-026"], "relevant_pages": [[4, 5, 6]], "difficulty": "medium", "topics": ["cellular_automaton", "simulation"]}

{"question_id": "gq-t4-05", "query": "从众行为如何影响疏散决策？", "relevant_docs": ["lit-027"], "relevant_pages": [[7, 8]], "difficulty": "medium", "topics": ["herd_behavior", "decision_making"]}

{"question_id": "gq-t4-06", "query": "海啸疏散演练揭示了什么行为特征？", "relevant_docs": ["lit-028"], "relevant_pages": [[9, 10, 11]], "difficulty": "medium", "topics": ["tsunami", "drill", "behavior"]}
```

---

### T5: 安全风险与干预（6 个）

```jsonl
{"question_id": "gq-t5-01", "query": "Love Parade 踩踏事故是如何从系统失效角度分析的？", "relevant_docs": ["lit-029"], "relevant_pages": [[3, 4, 5, 6]], "difficulty": "hard", "topics": ["love_parade", "systemic_failure"]}

{"question_id": "gq-t5-02", "query": "保持安全社交距离的人群密度阈值是多少？", "relevant_docs": ["lit-030"], "relevant_pages": [[7, 8]], "difficulty": "medium", "topics": ["density_limit", "safe_distancing"]}

{"question_id": "gq-t5-03", "query": "Kumbh Mela 大型活动中使用了哪些人群管理策略？", "relevant_docs": ["lit-031"], "relevant_pages": [[8, 9, 10]], "difficulty": "medium", "topics": ["kumbh_mela", "crowd_management"]}

{"question_id": "gq-t5-04", "query": "如何实时检测人群中的恐慌行为？", "relevant_docs": ["lit-008"], "relevant_pages": [[5, 6, 7]], "difficulty": "medium", "topics": ["panic_detection", "deep_learning"]}

{"question_id": "gq-t5-05", "query": "踩踏事故预防的关键措施有哪些？", "relevant_docs": ["lit-029", "lit-031"], "relevant_pages": [[10, 11], [12]], "difficulty": "hard", "topics": ["stampede", "prevention"]}

{"question_id": "gq-t5-06", "query": "高密度人群的社会力模型需要做哪些改进？", "relevant_docs": ["lit-007"], "relevant_pages": [[6, 7, 8]], "difficulty": "hard", "topics": ["high_density", "social_force", "improvement"]}
```

---

## 📁 文件格式

### 格式 1: JSONL（推荐）
```jsonl
{"question_id": "gq-001", "query": "问题内容", "relevant_docs": ["lit-001"], "relevant_pages": [[5, 6]], "difficulty": "medium", "topics": ["tag1", "tag2"]}
{"question_id": "gq-002", "query": "问题内容", "relevant_docs": ["lit-002"], "relevant_pages": [[8]], "difficulty": "easy", "topics": ["tag3"]}
```

保存为：`memPed/knowledge/pilot_gold.jsonl`

---

### 格式 2: JSON
```json
{
  "version": "pilot-v1",
  "created": "2026-09-09",
  "total_questions": 30,
  "questions": [
    {
      "question_id": "gq-001",
      "query": "问题内容",
      "relevant_docs": ["lit-001"],
      "relevant_pages": [[5, 6]],
      "difficulty": "medium",
      "topics": ["tag1", "tag2"]
    }
  ]
}
```

---

## 🔄 创建流程

### 步骤 1: 浏览文献（1-2 小时）
- 快速浏览 34 篇文献
- 记录每篇的核心内容
- 标记重要发现和数据

### 步骤 2: 设计问题（2-3 小时）
- 每个主题设计 6 个问题
- 确保覆盖不同难度
- 使用自然语言表达

### 步骤 3: 标注答案（2-3 小时）
- 标注每个问题的相关文献
- 定位具体页码
- 验证答案可追溯

### 步骤 4: 审核优化（1 小时）
- 检查问题质量
- 确保无重复
- 调整难度分布

---

## 🎯 质量标准

### 必须满足
- ✅ 每个问题至少有 1 篇相关文献
- ✅ 页码标注准确
- ✅ 问题表达清晰自然
- ✅ 覆盖所有 5 个主题

### 建议满足
- ⭐ 难度分布合理（Easy:Medium:Hard = 3:4:3）
- ⭐ 类型多样（概念、关系、数值、案例、方法）
- ⭐ 长度适中（10-50 字）

---

## 🚀 下一步

我可以帮您：
1. **自动生成 30 个 Gold Questions**（基于现有 34 篇文献）
2. **创建模板**（您手动填写）
3. **部分生成 + 人工审核**（推荐）

请告诉我您想如何进行！

---

**预计总时间**: 6-9 小时（人工） 或 1-2 小时（AI 辅助）
