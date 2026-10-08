# 行人流实验数据集补充报告

> **status: historical** · 2026-10-07 审计标注：本文是写作当日的快照，其中“当前”“完成”等表述只指当时状态。当前 RAG 状态见 [RAG 资产与一致性审计](rag-asset-audit-2026-10-07.md)。

> **专注领域**: 受控实验环境下的行人流动、疏散、瓶颈效应研究\
> **数据特点**: 实验室/现场受控环境、高精度轨迹、物理参数标定\
> **调研日期**: 2026年09月16日

---

## 目录

1. [行人流实验数据集概述](#行人流实验数据集概述)
2. [德国Jülich研究中心数据档案](#德国jülich研究中心数据档案)
3. [CroMa人群管理实验](#croma人群管理实验)
4. [Lyon灯光节密集人群数据集](#lyon灯光节密集人群数据集)
5. [车辆-人群交互数据集](#车辆人群交互数据集)
6. [ATC购物中心数据集](#atc购物中心数据集)
7. [其他重要实验数据集](#其他重要实验数据集)
8. [与视觉模块的集成建议](#与视觉模块的集成建议)

---

## 行人流实验数据集概述

### 🔬 什么是行人流实验数据集？

与自然场景数据集（如MOT17、Stanford Drone）不同，**行人流实验数据集**是在**受控环境**下采集的：

**特征**：
- ✅ **精确的实验设计** - 特定场景（瓶颈、走廊、交叉口）
- ✅ **高精度轨迹** - 通常精确到厘米级
- ✅ **物理参数标定** - 密度、流量、速度的精确测量
- ✅ **可重复性** - 实验条件可控
- ✅ **理论验证** - 用于验证行人动力学模型

**典型实验场景**：
1. **瓶颈实验** - 研究通过狭窄出口的流动特性
2. **双向流** - 相向行人流的相互影响
3. **交叉流** - 垂直交叉的行人流
4. **疏散实验** - 紧急疏散场景
5. **走廊流动** - 单向/双向走廊实验
6. **楼梯实验** - 上下楼梯的动力学

---

## 德国Jülich研究中心数据档案

### 📦 PED Data Archive (Pedestrian Dynamics Data Archive)

**官方主页**: [http://ped.fz-juelich.de/da](http://ped.fz-juelich.de/da)\
**研究机构**: Forschungszentrum Jülich (德国于利希研究中心) - IAS-7 民用安全研究所

**数据定位**: **最权威、最系统的行人动力学实验数据档案库**

### 📊 数据规模与内容

**包含的实验类型** (待核实完整列表):
1. **瓶颈实验** (Bottleneck Experiments)
   - 不同宽度的出口流动特性
   - 时间间隔分布
   - 流量-密度关系

2. **单向流实验** (Unidirectional Flow)
   - 走廊中的单向行人流
   - 基本图（Fundamental Diagram）数据

3. **双向流实验** (Bidirectional Flow)
   - 相向行人流的车道形成
   - 相互干扰效应

4. **交叉流实验** (Crossing Flows)
   - 垂直交叉的行人流
   - 容量测量

5. **疏散实验** (Evacuation Experiments)
   - 紧急疏散场景
   - 竞争行为与礼貌行为对比

### 🎯 数据特点

**轨迹精度**:
- 俯视摄像头拍摄
- 头部位置追踪
- 精度：厘米级
- 采样率：通常 16-25 fps

**标注内容**:
- 每个行人的完整轨迹（x, y, t）
- 行人ID
- 实验场景几何参数
- 环境条件（密度、流量）

**数据格式**:
- 通常为纯文本文件（txt/dat）
- 轨迹坐标 + 时间戳
- 元数据文件（实验设置）

### ✅ 适用场景

**理论研究**:
- 验证社会力模型
- 基本图（Fundamental Diagram）标定
- 行人动力学参数估计

**模型训练**:
- 物理约束的轨迹预测模型
- 疏散仿真模型校准
- 拥挤场景行为建模

**工程应用**:
- 建筑物设计（出口宽度、走廊容量）
- 疏散时间计算
- 人群管理策略

### ⚠️ 使用限制

- 学术研究使用
- 需要从官方网站下载
- 部分数据可能需要申请权限

### 📥 获取难度

⭐⭐ **中等**
- 官方网站公开
- 可能需要注册/申请
- 文档为英文/德文

### 📚 相关论文

**核心文献**:
1. Seyfried et al., "Enhanced empirical data for the fundamental diagram and the flow through bottlenecks" (2008)
   - [arXiv链接](https://arxiv.org/abs/0810.1945)

2. Seyfried et al., "Experimental study of pedestrian flow through a bottleneck" (2006)
   - [arXiv链接](https://arxiv.org/pdf/physics/0610077)

3. "Data archive for exploring pedestrian dynamics and its application in dimensioning of facilities for multidirectional streams"
   - [ResearchGate](https://www.researchgate.net/publication/340286041_Data_archive_for_exploring_pedestrian_dynamics_and_its_application_in_dimensioning_of_facilities_for_multidirectional_streams)

---

## CroMa人群管理实验

### 🚉 CroMa: Crowd Management in Transport Infrastructures

**项目主页**: [https://www.croma-projekt.de/](https://www.croma-projekt.de/)

**数据定位**: 大规模交通基础设施（火车站）的人群管理实验数据

### 📊 数据规模

**实验规模**:
- 约1000名参与者
- 多个实验场景
- 火车站环境模拟

**实验类型**:
1. **人群管理措施测试**
   - 物理引导设施
   - 标识系统
   - 信息显示

2. **社会心理学假设验证**
   - 群体行为
   - 决策过程
   - 压力条件下的行为

3. **特定场景**:
   - 单向流实验（Single-File Experiment）
   - 火车站台场景
   - 入口/出口流动

### 🎯 数据特点

**多学科方法**:
- 物理数据（轨迹、密度、流量）
- 心理数据（决策、感知）
- 社会学数据（群体效应）

**火车站场景**:
- 真实交通基础设施环境
- 复杂几何布局
- 多种人群管理措施

### ✅ 适用场景

- 交通枢纽设计
- 人群管理策略
- 疏散规划
- 行为建模（考虑心理因素）

### 📥 获取方式

**论文**:
- Crociani et al., "Pedestrian Crowd Management Experiments" (2023)
- [arXiv链接](https://arxiv.org/abs/2303.02319)

**数据获取**: (待核实)
- 论文中提供数据引导（Data Guidance Paper）
- 可能需要联系项目组

### 📥 获取难度

⭐⭐⭐ **较难**
- 数据可能需要申请
- 项目网站为德语
- 需要查阅论文获取详细信息

---

## Lyon灯光节密集人群数据集

### 🎆 Festival of Lights in Lyon Dataset (MADRAS Project)

**官方论文**: [Nature Scientific Data (2025)](https://www.nature.com/articles/s41597-025-04732-3)\
**arXiv版本**: [Dense Crowd Dynamics and Pedestrian Trajectories](https://arxiv.org/abs/2410.05288)

**数据定位**: **真实大型活动的密集人群动力学多尺度数据集**

### 📊 数据规模

**采集环境**:
- 2022年法国里昂灯光节
- 真实大型公共活动
- 极高人群密度（最高4人/平方米）

**数据量**:
- 约7,000条记录轨迹
- 多个尺度：从宏观流动（数百米）到微观个体轨迹
- 覆盖数小时的活动时间

### 🎯 数据特点

**多尺度特性**:
1. **宏观层面**
   - 大范围人群流动（数百米范围）
   - 整体密度分布
   - 流动模式

2. **中观层面**
   - 局部拥挤区域
   - 瓶颈效应
   - 密度波动

3. **微观层面**
   - 个体轨迹（精确到厘米）
   - 个体间交互
   - 步行速度和方向

**高密度场景**:
- 密度最高达4人/m²
- 接近极限密度条件
- 包含"crowd turbulence"等极端现象

**真实性**:
- ✅ 非受控的真实场景
- ✅ 自然行人行为
- ✅ 复杂的环境约束
- ✅ 多样化的人口统计特征

### ✅ 适用场景

**科研价值**:
- 高密度人群动力学建模
- 极端拥挤条件下的行为研究
- 多尺度模型验证
- 大型活动仿真

**工程应用**:
- 大型活动安全规划
- 场馆设计
- 应急预案制定
- 人群管理策略

### 📥 获取方式

**官方发布**:
- Nature Scientific Data 期刊（开放获取）
- [官方链接](https://www.nature.com/articles/s41597-025-04732-3)
- [arXiv预印本](https://arxiv.org/pdf/2410.05288)

**数据访问**: (待核实)
- 论文附带数据仓库链接
- 可能在Zenodo或类似平台

### 📥 获取难度

⭐⭐ **中等**
- 顶级期刊发布，规范性强
- 开放获取
- 2025年最新数据

### 🌟 推荐指数

⭐⭐⭐⭐⭐ **强烈推荐**

**理由**:
1. 2025年最新发布
2. 真实大型活动数据
3. 极高密度（罕见）
4. 多尺度完整数据
5. 顶级期刊质量保证

---

## 车辆-人群交互数据集

### 🚗 VCI-CITR Dataset (Vehicle-Crowd Interaction)

**GitHub**: [vci-dataset-citr](https://github.com/dongfang-steven-yang/vci-dataset-citr)\
**官方文档**: [美国交通部档案](https://rosap.ntl.bts.gov/view/dot/56255/dot_56255_DS1.pdf)

**数据定位**: 受控实验环境下的车辆与行人群体交互数据

### 📊 数据规模

**实验设置**:
- 俯视轨迹数据
- 停车场控制实验环境
- 行人群体与车辆（高尔夫球车）交互

**交互场景**:
1. **前向交互** (Front VCI) - 车辆从前方接近行人群
2. **后向交互** (Back VCI) - 车辆从后方接近行人群
3. **侧向交互** (Lateral VCI) - 车辆从侧面接近行人群

**数据内容**:
- 行人轨迹（x, y, heading, speed）
- 车辆状态（x, y, heading, speed，符合自行车模型）
- 时间戳
- 群体标识

### 🎯 数据特点

**精确标定**:
- 扩展卡尔曼滤波优化的车辆轨迹
- 高精度行人轨迹
- 俯视视角消除遮挡

**受控实验**:
- 特定VCI场景设计
- 每个行人有唯一ID
- 可重复实验条件

### 🔗 姊妹数据集

**DUT Dataset** (Dalian University of Technology)
- 校园日常场景
- 车辆-行人自然交互
- 配套VCI-CITR使用

### ✅ 适用场景

- 自动驾驶中的行人预测
- 车辆-行人交互建模
- 社会感知导航
- 机器人路径规划

### 📥 获取方式

**GitHub开源**:
- [https://github.com/dongfang-steven-yang/vci-dataset-citr](https://github.com/dongfang-steven-yang/vci-dataset-citr)
- 完整数据+代码+文档

**论文**:
- Yang et al., "Top-view Trajectories: A Pedestrian Dataset of Vehicle-Crowd Interaction from Controlled Experiments and Crowded Campus" (2019)
- [arXiv链接](https://arxiv.org/abs/1902.00487)

### 📥 获取难度

⭐ **简单**
- GitHub直接下载
- 文档完善
- 美国交通部支持项目

---

## ATC购物中心数据集

### 🛍️ ATC Shopping Mall Dataset (Osaka)

**数据来源**: 日本大阪亚太贸易中心（Asian Pacific Trade Center）

**数据定位**: 3D激光雷达传感器采集的购物中心行人流动数据

### 📊 数据特点

**传感器类型**:
- 3D范围传感器（3D Range Sensor）
- 购物中心实际环境
- 长时间连续采集

**分析维度**:
1. **流量分析**
   - 不同区域的人流量
   - 不同时间段对比
   - 折扣期与平日对比

2. **行为分析**
   - 群体行走 vs 独立行走
   - 探索行为（活动范围）
   - 移动模式聚类

3. **空间分析**
   - 热力图
   - 流动路径
   - 停留点

### ✅ 适用场景

**零售研究**:
- 顾客行为分析
- 商场布局优化
- 市场营销策略

**行人流研究**:
- 室内行人流动
- 自由探索行为
- 群体检测

### 📥 获取方式

**GitHub项目**:
- [ATC-pedestrian-tracking](https://github.com/Sapphirine/ATC-pedestrian-tracking-)
- 包含数据处理代码和可视化

**原始数据**: (待核实)
- 可能需要联系原始数据提供方

### 📥 获取难度

⭐⭐⭐ **较难**
- GitHub项目存在但数据来源不明确
- 可能需要申请原始数据
- 3D传感器数据处理复杂

---

## 其他重要实验数据集

### 7. Grand Central Station Dataset

**数据定位**: 纽约中央车站的行人流动数据

**数据来源**:
- 多个研究项目引用
- [CIDNN论文](https://github.com/svip-lab/CIDNN)中提到

**特点**:
- 真实大型交通枢纽
- 高密度行人流
- 多方向交叉流动

**获取方式**:
- CIDNN GitHub可能提供处理后的数据
- [BaiduYun或DropBox](https://github.com/svip-lab/CIDNN)

**获取难度**: ⭐⭐ 中等

---

### 8. 室内会议场景数据集

**论文**: "An Indoor Crowd Movement Trajectory Benchmark Dataset" (2021)\
**arXiv**: [https://arxiv.org/pdf/2109.01091.pdf](https://arxiv.org/pdf/2109.01091.pdf)

**数据规模**:
- 5,000+ 参与者
- 三天大型学术会议
- 两层室内场馆

**特点**:
- 室内多层建筑
- 会议场景（特定行为模式）
- 完整轨迹记录

**获取难度**: ⭐⭐ 中等

---

### 9. 文化人群数据集 (Cultural Crowds)

**论文**: "Cultural Crowds: a video dataset" (ResearchGate)

**数据定位**: 研究不同文化背景下的人群行为差异

**特点**:
- 多文化场景
- 视频片段数据集
- 行为分类标注

**获取难度**: ⭐⭐⭐ 较难

---

### 10. Crowd-11 数据集

**论文**: "Crowd-11: A Dataset for Fine Grained Crowd Behaviour Analysis" (ResearchGate)

**数据规模**:
- 6,000+ 视频片段
- 平均100帧/序列
- 11种人群运动模式

**特点**:
- 细粒度人群行为分类
- 多种运动模式
- 浅层和深度方法基线

**获取难度**: ⭐⭐ 中等

---

### 11. 瓶颈与疏散相关实验数据

**多个论文提到的实验数据**:

1. **礼貌与自私行为实验**
   - 论文: "Dynamics of pedestrian evacuations through a narrow doorway" (2016)
   - [arXiv链接](https://arxiv.org/pdf/1610.05909v1.pdf)
   - 特点：对比不同行为模式下的疏散效率

2. **推挤行为实验**
   - 论文: "Exploring the Dynamic Relationship between Pushing Behavior and Crowd Dynamics"
   - 14个视频材料
   - 走廊宽度与动机指令的影响

3. **多瓶颈实验**
   - 论文: "Pedestrian flow through multiple bottlenecks"
   - [arXiv链接](https://arxiv.org/abs/1209.2778)
   - 局部优化 vs 全局优化

---

## 与视觉模块的集成建议

### 🎯 行人流实验数据的独特价值

**相比自然场景数据集（MOT17、SDD等）**:

| 维度 | 自然场景数据集 | 行人流实验数据集 |
|------|---------------|-----------------|
| **精度** | 像素级（数十厘米） | 厘米级 |
| **物理参数** | 需要估计 | 精确标定 |
| **场景复杂度** | 高（真实场景） | 低（受控环境） |
| **理论验证** | 难以验证模型 | 易于验证 |
| **规模** | 大 | 中小 |
| **多样性** | 高 | 低（特定场景） |

---

### 🔄 推荐的数据集组合策略

#### 策略A：理论驱动 + 数据驱动结合

```
第一阶段：物理模型学习
├── Jülich数据档案（瓶颈、双向流）
├── 提取基本图参数
├── 学习物理约束
└── 建立动力学先验

第二阶段：真实场景适配
├── MOT17/20（地面视角）
├── Stanford Drone Dataset（俯视视角）
└── 在物理约束下微调

第三阶段：极端场景测试
├── Lyon灯光节（高密度）
├── CroMa实验（复杂场景）
└── 验证模型鲁棒性
```

---

#### 策略B：场景分层

**室内场景**:
```
基础: ATC购物中心 / 室内会议数据集
验证: JRDB（室内部分）
```

**室外场景**:
```
基础: ETH/UCY
实验: Jülich数据档案
大规模: Stanford Drone Dataset, Lyon灯光节
```

**交通场景**:
```
基础: KITTI, BDD100K
交互: VCI-CITR数据集
枢纽: CroMa, Grand Central Station
```

---

#### 策略C：密度分层

**低密度（< 1人/m²）**:
- ETH/UCY
- Stanford Drone Dataset（部分场景）
- BDD100K

**中密度（1-2人/m²）**:
- MOT17/20
- Jülich单向流实验
- Grand Central Station

**高密度（2-4人/m²）**:
- Jülich瓶颈实验
- Lyon灯光节
- CroMa实验

**极高密度（> 4人/m²）**:
- Lyon灯光节（部分时段）
- 疏散实验数据

---

### 🔧 视觉模块的实际使用建议

#### 1. **检测器训练阶段**

使用大规模视频数据集：
- CrowdHuman（预训练）
- MOT17/20（精调）
- VisDrone（特定视角）

❌ **不需要**行人流实验数据

---

#### 2. **跟踪器训练阶段**

**基础跟踪能力**:
- MOT17/20
- DanceTrack

**物理约束学习**:
✅ **加入**行人流实验数据
- Jülich数据档案（学习合理的运动模式）
- 作为正则化或辅助损失

---

#### 3. **轨迹预测阶段**

**核心训练数据**:
✅ **优先使用**行人流实验数据
- ETH/UCY（基线）
- TrajNet++（基准）
- Jülich数据档案（物理约束）
- Lyon灯光节（高密度）

**理由**:
- 轨迹精度要求高
- 需要物理合理性
- 密度效应明显

---

#### 4. **端到端系统评估**

**标准基准**:
- MOT17/20（必测）
- DanceTrack（运动依赖）

**特定场景测试**:
✅ **补充**行人流实验数据
- CroMa（交通枢纽）
- VCI-CITR（车辆交互）
- Lyon灯光节（极端密度）

---

### 📊 数据集优先级矩阵

| 数据集 | 检测 | 跟踪 | 轨迹预测 | 密度建模 | 优先级 |
|--------|------|------|---------|---------|--------|
| **Jülich数据档案** | ❌ | ⚠️ | ✅✅✅ | ✅✅✅ | 🔴 高 |
| **Lyon灯光节** | ❌ | ⚠️ | ✅✅ | ✅✅✅ | 🔴 高 |
| **CroMa实验** | ❌ | ⚠️ | ✅✅ | ✅✅ | 🟡 中 |
| **VCI-CITR** | ❌ | ⚠️ | ✅ | ⚠️ | 🟡 中 |
| **ATC购物中心** | ❌ | ⚠️ | ✅ | ⚠️ | 🟢 低 |
| **Grand Central** | ⚠️ | ✅ | ✅ | ✅ | 🟡 中 |

**图例**:
- ✅✅✅ 核心用途
- ✅✅ 重要用途
- ✅ 可用
- ⚠️ 辅助用途
- ❌ 不适用

---

## 总结与行动建议

### 🎯 立即行动

**第一优先级**（行人流实验的核心）:
1. ✅ **Jülich数据档案** - 访问 [http://ped.fz-juelich.de/da](http://ped.fz-juelich.de/da)
2. ✅ **Lyon灯光节数据** - 下载 [Nature论文](https://www.nature.com/articles/s41597-025-04732-3)

**第二优先级**:
3. ⚠️ **VCI-CITR** - GitHub直接下载
4. ⚠️ **CroMa实验** - 查阅论文获取数据链接

### 📈 价值评估

**对您视觉模块项目的独特价值**:

✅ **必须使用** - 如果研究方向包括：
- 轨迹预测（特别是密集场景）
- 行人动力学建模
- 物理约束的深度学习
- 疏散仿真

⚠️ **选择性使用** - 如果研究方向包括：
- 端到端检测+跟踪（可作为测试集）
- 多模态预测（补充物理先验）

❌ **可以不用** - 如果只关注：
- 纯检测任务
- 通用目标跟踪（非行人特化）

### 🔗 与之前报告的关系

**结合使用**:
- **视频MOT数据集**（MOT17、DanceTrack等）→ 训练检测+跟踪
- **行人流实验数据集**（Jülich、Lyon等）→ 轨迹预测+物理约束

**完整流程**:
```
原始视频
    ↓ (使用MOT数据集训练)
检测+跟踪
    ↓ (输出轨迹)
轨迹数据
    ↓ (使用实验数据集+自然轨迹训练)
轨迹预测
    ↓
未来路径
```

---

## 参考文献

### 核心论文

1. **Jülich数据档案相关**:
   - Seyfried et al., "Enhanced empirical data for the fundamental diagram and the flow through bottlenecks" (2008) - [arXiv](https://arxiv.org/abs/0810.1945)
   - Seyfried et al., "Experimental study of pedestrian flow through a bottleneck" (2006) - [arXiv](https://arxiv.org/pdf/physics/0610077)

2. **Lyon灯光节数据集**:
   - "Dense Crowd Dynamics and Pedestrian Trajectories: A Multiscale Field Dataset from the Festival of Lights in Lyon" (2025) - [Nature](https://www.nature.com/articles/s41597-025-04732-3)

3. **CroMa实验**:
   - Crociani et al., "Pedestrian Crowd Management Experiments" (2023) - [arXiv](https://arxiv.org/abs/2303.02319)

4. **VCI-CITR数据集**:
   - Yang et al., "Top-view Trajectories: A Pedestrian Dataset of Vehicle-Crowd Interaction from Controlled Experiments and Crowded Campus" (2019) - [arXiv](https://arxiv.org/abs/1902.00487)

5. **疏散动力学**:
   - "Dynamics of pedestrian evacuations through a narrow doorway" (2016) - [arXiv](https://arxiv.org/pdf/1610.05909v1.pdf)

---

**文档版本**: v1.0\
**最后更新**: 2026年09月16日\
**待更新内容**: 官方下载链接核实、数据格式详细说明、具体使用示例
