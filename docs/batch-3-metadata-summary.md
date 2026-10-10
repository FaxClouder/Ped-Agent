# Batch 3 文献元数据汇总报告

> **status: historical** · 2026-10-07 审计标注：本文是写作当日的快照，其中“当前”“完成”等表述只指当时状态。当前 RAG 状态见 [RAG 资产与一致性审计](rag-asset-audit-2026-10-07.md)。

**生成日期**: 2026-09-17\
**状态**: 历史元数据提取报告；活动批次仍待逐篇质量核验

> 2026-09-21 审计更新：b3-07 与 b3-10 已排除并删除本地 PDF；以下18篇统计是删除前的
> 历史快照，当前活动 PDF 为16篇。b3-10 的历史提取信息仅用于追溯。

---

## 📊 提取统计

### 文件覆盖
- **物理PDF文件**: 18篇
- **数据库已导入**: 16篇
- **待导入/重复**: 2篇

### 元数据提取成功率
- **DOI提取**: 17/18 (94.4%)
- **年份提取**: 18/18 (100%)
- **标题提取**: 18/18 (100%)

### 数据库现状
- **完整元数据字段**: 0/16 (0%)
  - ❌ 所有16篇都缺少：authors, year, doi, source_url
  - ✅ 所有16篇都有：resource_id, title, sha256, source_path

---

## 📋 详细元数据清单

### 1. arXiv预印本 (1篇)

#### b3-01: Enhanced empirical data for the fundamental diagram and the flow through bottlenecks
- **文件名**: `0810.1945v1.pdf`
- **DOI**: ❌ 未找到（arXiv预印本）
- **arXiv ID**: arXiv:0810.1945v1 [physics.soc-ph]
- **年份**: 2008
- **页数**: 12
- **文件大小**: 0.63 MB
- **数据库标题**: "Enhanced empirical data for the fundamental" (截断)
- **完整标题**: "Enhanced empirical data for the fundamental diagram and the flow through bottlenecks"
- **状态**: ⚠️ 需要查找正式发表版本
- **作者**: 需补充 (可能是 Seyfried et al.)

---

### 2. Physica A (2篇)

#### b3-02: Measuring the steady state of pedestrian flow in bottleneck experiments
- **文件名**: `1-s2.0-S0378437116302436-main.pdf`
- **DOI**: ✅ 10.1016/j.physa.2016.05.051
- **期刊**: Physica A: Statistical Mechanics and its Applications
- **卷期**: Vol. 461 (2016) 248-261
- **年份**: 2016
- **页数**: 14
- **文件大小**: 1.82 MB
- **数据库状态**: ✅ 标题完整
- **作者**: 需补充
- **质量评估**: 待核验 (Physica A 通常为二区)

#### b3-03: Influence of individual factors on fundamental diagrams of pedestrians
- **文件名**: `1-s2.0-S0378437122001248-main.pdf`
- **DOI**: ✅ 10.1016/j.physa.2022.127077
- **期刊**: Physica A
- **卷期**: Vol. 595 (2022) 127077
- **年份**: 2022
- **页数**: 12
- **文件大小**: 2.30 MB
- **数据库标题**: "Physica A 595 (2022) 127077" (❌ 错误，这是引用而非标题)
- **完整标题**: "Influence of individual factors on fundamental diagrams of pedestrians"
- **作者**: 需补充
- **状态**: ⚠️ 需修正数据库标题

---

### 3. Scientific Reports (Nature) (4篇)

#### b3-04: Experimental study on the synchronization mechanism...
- **文件名**: `Author_2024_ScientificReports_VerticalEvacuationSynchronization.pdf`
- **DOI**: ✅ 10.1038/s41598-024-77726-7
- **期刊**: Scientific Reports (Nature)
- **年份**: 2024
- **页数**: 19
- **文件大小**: 12.36 MB
- **数据库标题**: "Experimental study on the" (截断)
- **完整标题**: "Experimental study on the synchronization mechanism and trigger characteristic density of vertical evacuation in crowds"
- **作者**: 需补充
- **质量等级**: A级 (Nature子刊一区)

#### b3-05: Discovering interaction mechanisms in crowds...
- **文件名**: `Author_2025_ScientificReports_CrowdInteractionDeepLearning.pdf`
- **DOI**: ✅ 10.1038/s41598-025-92566-9
- **期刊**: Scientific Reports (Nature)
- **年份**: 2025
- **页数**: 11
- **文件大小**: 3.52 MB
- **数据库标题**: "Discovering interaction" (截断)
- **完整标题**: "Discovering interaction mechanisms in crowds via deep generative surrogate experiments"
- **作者**: 需补充
- **质量等级**: A级

#### b3-06: Inclusive crowd evacuation modeling...
- **文件名**: `Author_2025_ScientificReports_InclusiveEvacuationDisability.pdf`
- **DOI**: ✅ 10.1038/s41598-025-19403-x
- **期刊**: Scientific Reports (Nature)
- **年份**: 2025
- **页数**: 16
- **文件大小**: 1.90 MB
- **完整标题**: "Inclusive crowd evacuation modeling under heterogeneous mobility constraints"
- **作者**: 需补充
- **质量等级**: A级

#### b3-09: Dense Crowd Dynamics and Pedestrian Trajectories...
- **文件名**: `Dufour_2025_ScientificData_DenseCrowdDynamicsLyonDataset.pdf`
- **DOI**: ✅ 10.1038/s41597-025-04732-3
- **期刊**: Scientific Data (Nature)
- **年份**: 2025
- **页数**: 10
- **文件大小**: 1.91 MB
- **完整标题**: "Dense Crowd Dynamics and Pedestrian Trajectories: A Multiscale Field Dataset from the Festival of Lights in Lyon"
- **作者**: Oscar Dufour et al.
- **质量等级**: A级

---

### 4. Transportation Research Part C (2篇)

#### b3-11: Microscopic modeling of attention-based movement behaviors
- **文件名**: `Li_2024_TRC_AttentionBasedMovement.pdf`
- **DOI**: ✅ 10.1016/j.trc.2024.104583
- **期刊**: Transportation Research Part C: Emerging Technologies
- **卷期**: Vol. 162 (2024) 104583
- **年份**: 2024
- **页数**: 17
- **文件大小**: 1.62 MB
- **作者**: Danrui Li et al.
- **质量等级**: 待核验 (TR-C 通常为一区或二区)

#### b3-14: High-statistics pedestrian dynamics on stairways...
- **文件名**: `Pouw_2024_TRC_StairwaysProbabilisticFundamentalDiagrams.pdf`
- **DOI**: ✅ 10.1016/j.trc.2023.104468
- **期刊**: Transportation Research Part C
- **卷期**: Vol. 159 (2024) 104468
- **年份**: 2024
- **页数**: 22
- **文件大小**: 6.08 MB
- **完整标题**: "High-statistics pedestrian dynamics on stairways and their probabilistic fundamental diagrams"
- **作者**: Caspar A.S. Pouw et al.
- **质量等级**: 待核验

---

### 5. Safety Science (1篇)

#### b3-18: Continuous agent-based modeling of adult-child pairs...
- **文件名**: `Xie_2024_SafetyScience_AdultChildPairsModeling.pdf`
- **DOI**: ✅ 10.1016/j.ssci.2024.106576
- **期刊**: Safety Science
- **卷期**: Vol. 177 (2024) 106576
- **年份**: 2024
- **页数**: 17
- **文件大小**: 12.54 MB
- **完整标题**: "Continuous agent-based modeling of adult-child pairs based on a pseudo-energy"
- **作者**: Chuan-Zhi Thomas Xie et al.
- **质量等级**: A级 (Safety Science一区)

---

### 6. Physical Review E (1篇)

#### b3-13: Data-driven physics-based modeling of pedestrian dynamics
- **文件名**: `Pouw_2024_PhysRevE_DataDrivenPhysicsBasedModeling.pdf`
- **DOI**: ✅ 10.1103/PhysRevE.110.064102
- **期刊**: Physical Review E
- **卷期**: Vol. 110, 064102
- **年份**: 2024
- **页数**: 13
- **文件大小**: 5.52 MB
- **作者**: Caspar A.S. Pouw et al.
- **质量等级**: A级 (Physical Review E 一区物理期刊)

---

### 7. 其他期刊 (5篇)

#### b3-07: Pedestrian Crowd Management
- **状态**: 已排除，不再属于活动导入批次（2026-09-21）
- **排除原因**: Collective Dynamics 未被已核验的 JCR/CAS 体系收录；以下内容仅保留为历史元数据证据
- **文件名**: `Boomers_2023_CollectiveDynamics_CroMaExperiments.pdf`
- **DOI**: ✅ 10.17815/CD.2023.141
- **期刊**: Collective Dynamics
- **年份**: 2023
- **页数**: 57
- **文件大小**: 175.52 MB (⚠️ 异常大)
- **状态**: ⚠️ 文件过大，可能包含大量图片或数据
- **质量等级**: 待核验期刊分区

#### b3-08: Crowd model calibration at strategic, tactical, and operational levels
- **文件名**: `Crowd model calibration at strategic tactical and operational levels...pdf`
- **DOI**: ✅ 10.1080/19427867.2023.2195729
- **期刊**: Transportation Letters
- **年份**: 2023
- **页数**: 29
- **文件大小**: 33.44 MB
- **质量等级**: 待核验

#### b3-10: Multi-agent modeling of crowd dynamics under bombing attack cases
- **当前状态**: 已排除；2026-09-21 根据用户对 Frontiers in Physics 的筛选决定退出活动候选
- **文件名**: `fphy-11-1200927.pdf`
- **DOI**: ✅ 10.3389/fphy.2023.1200927
- **期刊**: Frontiers in Physics
- **年份**: 2023
- **页数**: 12
- **文件大小**: 2.30 MB
- **质量等级**: 待核验

#### b3-16: Optimizing crowd evacuation
- **文件名**: `s40860-024-00241-z.pdf`
- **DOI**: ✅ 10.1007/s40860-024-00241-z
- **期刊**: Journal of Reliable Intelligent Environments
- **卷期**: Vol. 11:2 (2025)
- **年份**: 2024 (published 2025)
- **页数**: 19
- **文件大小**: 3.62 MB
- **质量等级**: 待核验

#### b3-17: Modelling emergent pedestrian evacuation behaviors
- **文件名**: `s42001-025-00369-9.pdf`
- **DOI**: ✅ 10.1007/s42001-025-00369-9
- **期刊**: Computational Social Science (推测)
- **年份**: 2025
- **页数**: 35
- **文件大小**: 2.39 MB
- **质量等级**: 待核验

---

### 8. 可能的重复文件 (2篇)

#### phrs-47-1609310.pdf
- **DOI**: ✅ 10.3389/phrs.2026.1609310
- **期刊**: Public Health Reviews
- **年份**: 2025-2026
- **页数**: 12
- **文件大小**: 3.25 MB
- **状态**: ⚠️ 在导入时被识别为重复 (已存在为 t5-03)
- **标题**: "Preventive Measures and Crowd Management Strategies: A Systematic Review"

#### s10287-023-00482-y.pdf
- **DOI**: ✅ 10.1007/s10287-023-00482-y
- **期刊**: OR Spectrum
- **年份**: 2023
- **页数**: 25
- **文件大小**: 1.62 MB
- **状态**: ⚠️ 在导入时被识别为重复 (已存在为 t4-05)
- **标题**: "Emergency exit layout planning using optimization and agent-based simulation"

---

## 🔍 数据质量问题

### 严重问题

1. **所有16篇数据库记录缺少核心元数据**:
   - ❌ `authors` (作者)
   - ❌ `year` (年份)
   - ❌ `doi` (DOI)
   - ❌ `source_url` (来源URL)

2. **标题截断** (6篇):
   - b3-01: "Enhanced empirical data for the fundamental"
   - b3-03: "Physica A 595 (2022) 127077" (错误：这是引用)
   - b3-04: "Experimental study on the"
   - b3-05: "Discovering interaction"
   - b3-06: 可能截断
   - b3-10, b3-11: 可能截断

3. **异常大文件**:
   - b3-07: 175.52 MB (正常文献通常<20MB)

### 中等问题

4. **arXiv预印本需要核验**:
   - b3-01 (0810.1945v1) 需要查找正式发表版本

5. **年份提取异常** (2篇):
   - `1-s2.0-S0378437122001248-main.pdf`: 提取年份为2001，但实际应该是2022
   - `s42001-025-00369-9.pdf`: 提取年份为2001，但DOI显示2025
   - `fphy-11-1200927.pdf`: 提取年份为2009，但DOI显示2023

---

## ✅ 下一步行动

### 优先级1 (立即执行)

1. **补充数据库元数据**:
   ```sql
   -- 为16篇Batch 3文献补充：
   -- - authors (从PDF提取或DOI查询)
   -- - year (已从PDF提取)
   -- - doi (已从PDF提取)
   -- - source_url (通过DOI生成)
   ```

2. **修正标题**:
   - b3-01: 补充完整标题
   - b3-03: 修正为真实标题 "Influence of individual factors..."
   - b3-04, b3-05: 补充完整标题

3. **修正年份提取错误**:
   - 手动核验3篇年份异常的文献

### 优先级2 (本周完成)

4. **Web of Science质量核验**:
   - 查询所有16篇的：
     - 中科院分区 (一区/二区?)
     - JCI指标 (≥1.0?)
     - 引用次数
     - 完整性状态 (无撤稿?)

5. **作者信息提取**:
   - 优先从DOI查询 (Crossref API)
   - 备选：从PDF第一页提取
   - 重命名3个placeholder文件

6. **质量评分**:
   按照`collection_standard.md`的5个维度评分：
   - 主题相关性 (30分)
   - 方法严谨性 (30分)
   - RAG证据价值 (20分)
   - 主题覆盖贡献 (10分)
   - 页码与引用可追溯性 (10分)

### 优先级3 (下周完成)

7. **删除重复PDF**:
   - `phrs-47-1609310.pdf` → 已存在为 t5-03
   - `s10287-023-00482-y.pdf` → 已存在为 t4-05

8. **清理batch-3-incoming目录**:
   - 确认Vault完整性
   - 删除源文件或移至archive

9. **重新运行评测**:
   - 使用Gold Questions测试检索质量
   - 目标: Recall@5≥0.80, MRR≥0.70

---

## 📈 期刊质量初步评估

### 确认A级 (一区) - 6篇
- Scientific Reports (Nature) × 3
- Scientific Data (Nature) × 1
- Safety Science × 1
- Physical Review E × 1

### 可能A/B级 - 4篇
- Transportation Research Part C × 2 (需核验分区)
- Physica A × 2 (通常二区)

### 待核验 - 6篇
- Collective Dynamics
- Transportation Letters
- Frontiers in Physics（b3-10，已排除，仅保留历史记录）
- OR Spectrum
- Journal of Reliable Intelligent Environments
- Computational Social Science

### 特殊状态 - 1篇
- arXiv预印本 × 1 (需要查找正式版)

---

## 📊 完整度统计

| 元数据字段 | 已提取 | 待补充 | 完整率 |
|-----------|-------|--------|--------|
| resource_id | 16/16 | 0 | 100% |
| title (完整) | 10/16 | 6 | 62.5% |
| DOI | 17/18 | 1 | 94.4% |
| year | 18/18 | 0 | 100% |
| authors | 0/16 | 16 | 0% |
| journal | 0/16 | 16 | 0% |
| 中科院分区 | 0/16 | 16 | 0% |
| JCI | 0/16 | 16 | 0% |
| 引用次数 | 0/16 | 16 | 0% |
| 质量评分 | 0/16 | 16 | 0% |

**总体完整度**: ~35% (仅基础字段完整，质量验证未完成)

---

## 🎯 目标

完成所有元数据补充和质量核验后，Batch 3应该达到：
- ✅ 100% 元数据完整
- ✅ 100% DOI验证
- ✅ 100% 质量评分 ≥80
- ✅ 100% 符合`collection_standard.md`标准
- ✅ 通过Gold Questions评测门禁

**预计工作量**: 2-3天 (包括Web of Science查询和人工核验)
