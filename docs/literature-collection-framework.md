# PedRAGent 文献入库方向与领域规划

_系统化的文献收集框架 · created: 2026-09-09 · status: plan_

---

## 📊 总体规划

### Pilot 阶段（当前）
- **文献**: 20 篇
- **法规**: 8 份
- **目标**: 验证检索系统，建立基线

### Core 阶段（后续）
- **文献**: 120 篇
- **法规**: 40 份
- **目标**: 构建完整知识库

---

## 📚 文献收集方向（5 大领域）

基于 `taxonomy.yaml`，我们将文献分为以下 5 个核心领域：

---

### 🔵 领域 1: 行人流基础理论 (Flow Fundamentals)

**research_id**: `flow_fundamentals`

#### 核心研究问题
- 基本图关系（速度-密度-流量）
- 行人流容量（capacity）
- 瓶颈效应
- 相变现象
- 自组织行为

#### 子方向与关键词

##### 1.1 基本图与宏观特性
```
Keywords: fundamental diagram, speed-density relation, flow-density,
          capacity, macroscopic flow
```
- 单向流基本图
- 双向流基本图
- 多向交叉流
- 不同文化差异
- 年龄与性别影响

##### 1.2 微观行为与社会力
```
Keywords: social force model, microscopic behavior, personal space,
          step dynamics, following behavior
```
- 个体步行特征
- 跟随行为
- 社会距离
- 群体效应

##### 1.3 瓶颈与拥堵
```
Keywords: bottleneck, congestion, phase transition, stop-and-go,
          jamming, clogging
```
- 瓶颈容量
- 拥堵形成机制
- 层流-湍流转变
- 止步-前进波

#### Pilot 配额: 4 篇
- A 级（一区高引）: ≥2 篇
- B 级: 1-2 篇
- 覆盖子方向: 基本图、瓶颈各 2 篇

#### Core 配额: 24 篇
- 基本图研究: 8 篇
- 微观行为: 8 篇
- 瓶颈拥堵: 8 篇

---

### 🟢 领域 2: 实验与测量 (Experiment & Measurement)

**research_id**: `experiment_measurement`

#### 核心研究问题
- 轨迹采集技术
- 受控实验设计
- 现场观测方法
- 数据处理与分析
- 测量精度与标定

#### 子方向与关键词

##### 2.1 轨迹采集技术
```
Keywords: trajectory tracking, video analysis, motion capture,
          marker detection, automated tracking
```
- 视频自动跟踪
- 标记检测
- 深度学习跟踪
- 多摄像机标定
- 高精度运动捕捉

##### 2.2 受控实验
```
Keywords: controlled experiment, laboratory experiment,
          single-file movement, circular movement
```
- 单列行走实验
- 环形通道实验
- 受控密度实验
- 瓶颈实验室测试

##### 2.3 现场观测
```
Keywords: field observation, real-world data, crowd monitoring,
          public space, mass gathering
```
- 公共空间观测
- 大型活动监测
- 交通枢纽数据
- 商业场所流动

##### 2.4 数据集与开放数据
```
Keywords: pedestrian dataset, open data, trajectory database,
          benchmark dataset
```
- 公开轨迹数据集
- 基准测试集
- 标注数据

#### Pilot 配额: 4 篇
- 轨迹采集: 2 篇
- 实验/观测: 2 篇

#### Core 配额: 24 篇
- 采集技术: 8 篇
- 受控实验: 8 篇
- 现场数据: 8 篇

---

### 🟡 领域 3: 设施与场景流动 (Facility & Scenario Flow)

**research_id**: `facility_scenario_flow`

#### 核心研究问题
- 不同设施类型的流动特征
- 几何结构影响
- 通道、楼梯、出入口
- 交叉流与对向流
- 设施设计优化

#### 子方向与关键词

##### 3.1 通道与走廊
```
Keywords: corridor, hallway, passage, uni-directional flow,
          bi-directional flow, lane formation
```
- 单向流动特征
- 双向流与分道
- 走廊宽度影响
- 交叉路口

##### 3.2 楼梯与扶梯
```
Keywords: stairway, staircase, escalator, vertical movement,
          ascent, descent
```
- 上下楼梯特征
- 楼梯容量
- 扶梯行为
- 楼梯平台停滞

##### 3.3 出入口与门
```
Keywords: exit, entrance, door, doorway, gate,
          egress, ingress
```
- 出口流量
- 门宽影响
- 拱形现象
- 进出口冲突

##### 3.4 开放空间
```
Keywords: open space, plaza, square, free movement,
          pedestrian zone
```
- 广场流动
- 自由行走
- 空间使用

#### Pilot 配额: 4 篇
- 瓶颈/出口: 2 篇
- 楼梯: 1 篇
- 通道/空间: 1 篇

#### Core 配额: 24 篇
- 通道走廊: 6 篇
- 楼梯: 6 篇
- 出入口: 6 篇
- 开放空间: 6 篇

---

### 🔴 领域 4: 疏散行为与模型 (Evacuation & Modeling)

**research_id**: `evacuation_behavior_modeling`

#### 核心研究问题
- 疏散行为特征
- 路径选择与决策
- 疏散模型与仿真
- 应急情境行为
- 模型验证

#### 子方向与关键词

##### 4.1 疏散行为
```
Keywords: evacuation behavior, emergency behavior, panic,
          herding, competitive behavior, altruistic behavior
```
- 恐慌行为
- 从众效应
- 竞争行为
- 利他行为
- 路径选择

##### 4.2 火灾疏散
```
Keywords: fire evacuation, smoke, visibility, toxicity,
          fire emergency
```
- 烟雾影响
- 能见度降低
- 火灾环境认知
- 疏散时间

##### 4.3 疏散模型
```
Keywords: evacuation model, agent-based model, cellular automata,
          social force, fluid dynamics
```
- 社会力模型
- 元胞自动机
- 智能体模型
- 流体力学模型
- 博弈论模型

##### 4.4 建筑疏散
```
Keywords: building evacuation, multi-story, high-rise,
          stairwell, refuge area
```
- 高层建筑
- 多层疏散
- 楼梯井拥堵
- 避难区域

#### Pilot 配额: 5 篇
- 疏散行为: 2 篇
- 火灾疏散: 1 篇
- 疏散模型: 2 篇

#### Core 配额: 30 篇
- 疏散行为: 10 篇
- 火灾疏散: 8 篇
- 疏散模型: 8 篇
- 建筑疏散: 4 篇

---

### 🟣 领域 5: 安全风险与干预 (Safety & Risk Intervention)

**research_id**: `safety_risk_intervention`

#### 核心研究问题
- 拥挤风险识别
- 踩踏预防
- 预警系统
- 干预措施
- 人群管理策略

#### 子方向与关键词

##### 5.1 拥挤风险
```
Keywords: crowding risk, crowd pressure, crushing, asphyxiation,
          density threshold, critical density
```
- 危险密度阈值
- 人群压力
- 挤压伤害
- 窒息风险

##### 5.2 踩踏事故
```
Keywords: stampede, crowd disaster, mass casualty,
          crowd accident, trampling
```
- 踩踏案例分析
- 事故机制
- 伤亡模式
- 风险因素

##### 5.3 预警系统
```
Keywords: early warning, crowd monitoring, real-time detection,
          risk prediction, alert system
```
- 实时监测
- 风险预测
- 预警指标
- 报警系统

##### 5.4 干预措施
```
Keywords: intervention, crowd management, crowd control,
          safety measure, mitigation strategy
```
- 人群管理策略
- 流量控制
- 引导措施
- 物理屏障
- 疏导预案

#### Pilot 配额: 3 篇
- 踩踏/风险: 2 篇
- 预警/干预: 1 篇

#### Core 配额: 18 篇
- 拥挤风险: 6 篇
- 踩踏事故: 6 篇
- 预警系统: 3 篇
- 干预措施: 3 篇

---

## 🏛️ 法规与标准收集方向（5 大类别）

基于 `taxonomy.yaml` 的 regulations 分类：

---

### 法规 1: 建筑消防与疏散 (Building Fire & Evacuation)

**research_id**: `building_fire_evacuation`

#### 覆盖内容
- 建筑防火设计规范
- 疏散通道要求
- 安全出口设置
- 疏散指示标识
- 应急照明

#### 关键标准
- 中国: GB 50016（建筑设计防火规范）
- 国际: NFPA 101 (Life Safety Code)
- 欧洲: EN 1838 (Emergency Lighting)

#### Pilot 配额: 3 份
#### Core 配额: 14 份

---

### 法规 2: 公共交通与公共空间 (Transport & Public Space)

**research_id**: `transport_public_space`

#### 覆盖内容
- 地铁站设计规范
- 火车站流线设计
- 机场航站楼标准
- 公共广场规范
- 步行设施标准

#### 关键标准
- 地铁设计规范
- 铁路客运站设计规范
- 城市道路设计规范

#### Pilot 配额: 2 份
#### Core 配额: 10 份

---

### 法规 3: 应急管理与大型活动 (Emergency & Mass Events)

**research_id**: `emergency_large_events`

#### 覆盖内容
- 大型活动安全管理
- 应急预案要求
- 人员密集场所管理
- 消防安全规定

#### 关键标准
- 大型群众性活动安全管理条例
- 人员密集场所消防安全管理

#### Pilot 配额: 1 份
#### Core 配额: 6 份

---

### 法规 4: 无障碍与步行设施 (Accessibility & Pedestrian Facilities)

**research_id**: `accessibility_pedestrian_facilities`

#### 覆盖内容
- 无障碍设计规范
- 步行道设计标准
- 人行天桥标准
- 地下通道规范

#### 关键标准
- 无障碍设计规范 GB 50763
- 城市步行和自行车交通系统规划标准

#### Pilot 配额: 1 份
#### Core 配额: 6 份

---

### 法规 5: 国际标准对照 (International Standards)

**research_id**: `international_comparison`

#### 覆盖内容
- ISO 国际标准
- 欧洲标准 (EN)
- 美国标准 (NFPA, IBC)
- 日本标准
- 英国标准 (BS)

#### 关键标准
- ISO 23601 (Safety identification)
- NFPA 101 (Life Safety Code)
- BS 9999 (Fire safety)

#### Pilot 配额: 1 份
#### Core 配额: 4 份

---

## 📋 批次收集策略

### 批次 1 (Pilot 首批): 10 篇文献
**目标**: 覆盖所有领域，建立基线

| 领域 | 数量 | 优先级 | 重点 |
|------|------|--------|------|
| 基础理论 | 2 | 最高 | 经典基本图研究 |
| 实验测量 | 2 | 最高 | 轨迹数据集 + 方法 |
| 设施流动 | 2 | 高 | 瓶颈 + 楼梯 |
| 疏散建模 | 3 | 高 | Helbing综述 + 行为 + 模型 |
| 安全干预 | 1 | 中 | 踩踏预防综述 |

### 批次 2 (Pilot 第二批): 10 篇文献
**目标**: 补充薄弱领域，增加深度

| 领域 | 数量 | 重点 |
|------|------|------|
| 基础理论 | 2 | 微观行为、文化差异 |
| 实验测量 | 2 | 现场观测、高精度测量 |
| 设施流动 | 2 | 通道、开放空间 |
| 疏散建模 | 2 | 火灾疏散、建筑疏散 |
| 安全干预 | 2 | 预警系统、干预措施 |

### 批次 3 (Pilot 法规): 8 份
| 类别 | 数量 |
|------|------|
| 建筑消防 | 3 |
| 公共交通 | 2 |
| 应急管理 | 1 |
| 无障碍 | 1 |
| 国际标准 | 1 |

---

## 🔍 搜索策略（按领域）

### 推荐数据库优先级
1. **Web of Science** (主力) - 高质量期刊
2. **Scopus** (补充) - 覆盖更广
3. **Google Scholar** (引用验证)
4. **arXiv** (预印本，筛选后使用)
5. **ResearchGate** (作者分享版本)

### 期刊优先级（按分区）

#### 一区期刊（优先）
- Physical Review E (物理)
- Nature 子刊 (Scientific Reports, Scientific Data)
- Transportation Research Part B/C
- Safety Science
- Fire Technology
- Building and Environment

#### 二区期刊（主力）
- PLoS ONE
- Physica A
- Journal of Statistical Mechanics
- European Transport Research Review
- Fire Safety Journal
- Collective Dynamics（已核验为 JCR/CAS 均未收录，不再作为普通期刊候选来源）

---

## ✅ 质量控制检查清单

每批文献收集完成后检查：

### 主题覆盖
- [ ] 5 个领域全覆盖
- [ ] 每个领域至少 1 个子方向
- [ ] 无重复主题

### 质量分级
- [ ] A 级（一区高引）≥ 40%
- [ ] B 级（二区中引）≥ 50%
- [ ] X 级（经典证据）≤ 10%

### 时间分布
- [ ] ≥ 60% 发表于 2018 年后
- [ ] ≤ 10% 发表于 18 个月内（需 A 级）
- [ ] 包含至少 2 篇经典高引（2015 年前）

### 期刊多样性
- [ ] 最多 2 篇/期刊
- [ ] 至少覆盖 5 个不同期刊
- [ ] 包含至少 1 篇 Nature/Science 级别

### 作者多样性
- [ ] 包含 Helbing、Seyfried 等权威作者
- [ ] 避免单一团队垄断
- [ ] 国际视野（中美欧日均有）

---

## 📊 进度追踪模板

```markdown
## 批次 X 进度

### 检索阶段
- [ ] 制定搜索式
- [ ] Web of Science 检索
- [ ] Scopus 补充
- [ ] 初步筛选（标题摘要）

### 质量验证
- [ ] 期刊分区查询
- [ ] JCI 验证
- [ ] 引用量统计

### 下载阶段
- [ ] Open Access 自动下载
- [ ] 付费期刊手动下载
- [ ] PDF 质量验证

### 评分阶段
- [ ] Agent 批量评分
- [ ] 人工复核
- [ ] 最终确认

### 入库阶段
- [ ] 生成 Manifest
- [ ] 技术预检
- [ ] 导入 Catalog
- [ ] 构建索引
```

---

## 🎯 下一步行动

1. **确认方向** - 您同意这个领域划分吗？需要调整吗？
2. **选择起点** - 从哪个批次开始？（建议：批次 1，10 篇文献）
3. **确定优先级** - 是否调整各领域的配额？

**准备好开始批次 1 的文献收集了吗？**
