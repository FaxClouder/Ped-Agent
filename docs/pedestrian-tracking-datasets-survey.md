# 行人流轨迹与多目标跟踪（MOT）公开数据集调研报告

> **status: historical** · 2026-10-07 审计标注：本文是写作当日的快照，其中“当前”“完成”等表述只指当时状态。当前 RAG 状态见 [RAG 资产与一致性审计](rag-asset-audit-2026-10-07.md)。

> **调研日期**: 2026年09月16日\
> **目标**: 为视觉模块提供行人检测、跟踪与轨迹预测的数据支撑

---

## 目录

1. [数据集分类概览](#数据集分类概览)
2. [行人轨迹预测数据集](#行人轨迹预测数据集)
3. [视频MOT数据集](#视频mot数据集)
4. [多摄像头/跨视角数据集](#多摄像头跨视角数据集)
5. [合成数据集](#合成数据集)
6. [推荐数据组合方案](#推荐数据组合方案)
7. [数据获取优先级](#数据获取优先级)

---

## 数据集分类概览

本报告将数据集分为以下四大类：

- **A类：行人轨迹预测** - 提供鸟瞰/俯视视角的轨迹坐标数据
- **B类：视频MOT** - 提供视频帧+边界框标注，用于检测与跟踪
- **C类：多摄像头** - 跨视角/多视图同步数据
- **D类：合成数据** - 计算机生成的训练数据

---

## 行人轨迹预测数据集

### 1. ETH / UCY 数据集

**官方来源**:
- ETH: [OpenTraj GitHub](https://github.com/crowdbotp/OpenTraj/blob/master/datasets/ETH/README.md)
- UCY: 通常与ETH打包使用

**数据定位**: 行人轨迹预测的经典基准数据集

**数据规模**:
- ETH包含2个场景: ETH、HOTEL
- UCY包含3个场景: UNIV、ZARA1、ZARA2
- 标注格式: 2D坐标轨迹（像素坐标或米制坐标）

**标注类型**:
- 行人位置轨迹（时间序列）
- 场景划分标签

**适用场景**:
- 轨迹预测模型训练
- 社交力模型验证
- 交互建模研究

**使用限制**: 学术使用为主

**优点**:
- 轻量级，易于快速验证
- 广泛使用，便于对比
- 预处理版本多（如Trajectron++处理版本）

**缺点**:
- 数据规模较小
- 场景多样性有限
- 分辨率较低

**获取难度**: ⭐ 简单

**下载链接**:
- [OpenTraj ETH](https://github.com/crowdbotp/OpenTraj/blob/master/datasets/ETH/README.md)
- 多数轨迹预测项目（如Social-GAN、Trajectron++）已包含预处理版本

**论文引用**:
- ETH: Pellegrini et al., "You'll never walk alone: Modeling social behavior for multi-target tracking" (ICCV 2009)
- UCY: Lerner et al., "Crowds by example" (2007)

---

### 2. Stanford Drone Dataset (SDD)

**官方主页**: [https://cvgl.stanford.edu/projects/uav_data](https://cvgl.stanford.edu/projects/uav_data)

**数据定位**: 无人机俯视视角的大规模多目标轨迹数据集

**数据规模**:
- 8个独特场景（斯坦福大学校园）
- 20,000+ 个标注目标
- 100+ 个场景/视频
- 涵盖行人、骑行者、滑板、汽车、公交车、高尔夫车等

**标注类型**:
- 边界框（bounding box）
- 目标类别
- 轨迹ID（时间一致性）

**适用场景**:
- 轨迹预测
- 多目标跟踪
- 拥挤场景行为分析
- 交互建模

**使用限制**: 学术研究使用

**优点**:
- 规模大、多样性高
- 俯视视角减少遮挡
- 多种目标类型
- 场景复杂（室外、行人密集区）

**缺点**:
- 视角单一（俯视）
- 标注复杂性中等（有研究指出标注问题）[参考](https://arxiv.org/abs/2203.11743)

**获取难度**: ⭐⭐ 中等

**下载链接**:
- 官方页面: [https://cvgl.stanford.edu/projects/uav_data](https://cvgl.stanford.edu/projects/uav_data)
- [GitHub标注文件](https://github.com/flclain/StanfordDroneDataset)

**论文引用**:
- Robicquet et al., "Learning Social Etiquette: Human Trajectory Understanding In Crowded Scenes" (ECCV 2016)

---

### 3. TrajNet++

**官方主页**: [http://trajnet.epfl.ch/](http://trajnet.epfl.ch/)

**数据定位**: 轨迹预测的统一基准平台，整合多个数据集

**数据规模**:
- 整合了ETH/UCY、Stanford Drone Dataset等多个数据集
- 提供统一的场景分类和交互标注
- 包含显式的交互场景（agent-agent scenarios）

**标注类型**:
- 轨迹坐标
- 交互类型标注（leader-follower、collision avoidance等）
- 场景类型分类

**适用场景**:
- 轨迹预测基准测试
- 社交交互建模
- 多模态预测评估

**使用限制**: 开源，学术研究友好

**优点**:
- 统一评估框架
- 显式交互标注
- 标准化的训练/测试划分
- 在线排行榜

**缺点**:
- 基础数据来自其他数据集
- 数据量受限于源数据集

**获取难度**: ⭐ 简单

**下载链接**:
- [官方网站](http://trajnet.epfl.ch/)
- [GitHub baselines](https://github.com/pedro-mgb/trajnetplusplusbaselines)

**论文引用**:
- Kothari et al., "Human Trajectory Forecasting in Crowds: A Deep Learning Perspective" (2021)

---

### 4. JRDB (JackRabbot Dataset and Benchmark)

**官方主页**: [https://jrdb.erc.monash.edu/](https://jrdb.erc.monash.edu/)

**数据定位**: 机器人自我中心视角（egocentric）的3D行人检测、跟踪与社交导航数据集

**数据规模** (待核实具体数字):
- 60+ 分钟的数据
- 2.3M+ 2D边界框
- 1.8M+ 3D立方体标注
- 3,500+ 时间一致的轨迹
- 54个室内外场景

**标注类型**:
- 2D边界框（5个相机）
- 3D立方体（立体相机+LiDAR）
- 轨迹ID
- 场景标签（室内/室外）

**适用场景**:
- 机器人视角的行人检测
- 3D MOT
- 社交导航
- 室内外混合场景

**使用限制**: 学术研究使用

**优点**:
- 机器人视角（罕见）
- 2D+3D标注
- 室内场景丰富
- 多模态数据（RGB、深度、点云）

**缺点**:
- 数据下载和处理复杂度较高
- 视角特殊（非俯视、非车载）

**获取难度**: ⭐⭐⭐ 较难

**下载链接**:
- [官方数据集页面](https://jrdb.erc.monash.edu/dataset/)

**论文引用**:
- Martín-Martín et al., "JRDB: A Dataset and Benchmark for Visual Perception for Navigation in Human Environments" (2021)

---

### 5. inD Dataset (Intersection Drone Dataset)

**官方来源**: 通过文献引用可知

**数据定位**: 无人机拍摄的交叉路口行人与车辆轨迹

**数据规模** (待核实):
- 32段录像
- 4个不同的交叉路口
- 训练/验证/测试按70-10-20划分

**标注类型**:
- 轨迹坐标
- 目标类别（行人、车辆）

**适用场景**:
- 交叉路口行人轨迹预测
- 车辆-行人交互建模

**使用限制**: (待核实)

**优点**:
- 真实交通场景
- 交叉路口专用数据

**缺点**:
- 场景类型单一（仅交叉路口）

**获取难度**: ⭐⭐ 中等

**下载链接**: (待查找官方链接)

**论文引用**:
- Bock et al., "The inD Dataset: A Drone Dataset of Naturalistic Road User Trajectories at German Intersections" (2020)

---

## 视频MOT数据集

### 6. MOTChallenge系列 (MOT15/16/17/20)

**官方主页**: [https://motchallenge.net/](https://motchallenge.net/)

**数据定位**: 多目标跟踪的权威基准测试平台

#### MOT17

**数据规模**:
- 训练集: 7个序列
- 测试集: 7个序列
- 提供3种检测器结果（DPM、FRCNN、SDP）

**标注类型**:
- 边界框
- 行人ID
- 可见性标签
- 遮挡程度

**适用场景**:
- 多目标跟踪算法评估
- 检测与跟踪联合训练
- 遮挡处理研究

#### MOT20

**数据定位**: 针对拥挤场景的MOT基准

**数据规模**:
- 8个新序列
- 极度拥挤场景（平均每帧22.6人）

**标注类型**:
- 与MOT17相同
- 更多遮挡和拥挤标注

**使用限制**: 开源，需注册下载

**优点**:
- 社区公认的标准基准
- 在线排行榜
- 详细的评估指标（MOTA、IDF1等）
- 持续更新

**缺点**:
- 数据规模相对较小
- 场景多样性有限（主要是街道监控）

**获取难度**: ⭐⭐ 中等

**下载链接**:
- [MOTChallenge官网](https://motchallenge.net/)
- 需注册账号

**评估工具**:
- [TrackEval官方工具](https://github.com/JonathonLuiten/TrackEval)

**论文引用**:
- MOT17: Milan et al., "MOT16: A Benchmark for Multi-Object Tracking" (2016)
- MOT20: Dendorfer et al., "MOT20: A benchmark for multi object tracking in crowded scenes" (2020)

---

### 7. DanceTrack

**官方主页**: [https://dancetrack.github.io/](https://dancetrack.github.io/)\
**GitHub**: [https://github.com/DanceTrack/DanceTrack](https://github.com/DanceTrack/DanceTrack)

**数据定位**: 外观均一、运动多样的多目标跟踪数据集（舞蹈场景）

**数据规模**:
- 100个视频
- 训练集: 40个视频（标注公开）
- 验证集: 25个视频（标注公开）
- 测试集: 35个视频（标注私密）

**标注类型**:
- 边界框
- 目标ID

**数据特点**:
1. **均一外观**: 人物穿着相似，难以通过外观区分
2. **多样运动**: 复杂的运动模式和交互
3. **频繁遮挡**: 相对位置频繁交换

**适用场景**:
- 测试运动模型的跟踪能力
- 弱化外观依赖的跟踪算法
- 复杂交互场景

**使用限制**: CVPR 2022发布，学术使用

**优点**:
- 独特的挑战（外观相似）
- 强制算法依赖运动信息
- 标注质量高

**缺点**:
- 场景单一（舞蹈）
- 不适合通用场景评估

**获取难度**: ⭐⭐ 中等

**下载链接**:
- [GitHub仓库](https://github.com/DanceTrack/DanceTrack)

**论文引用**:
- Sun et al., "DanceTrack: Multi-Object Tracking in Uniform Appearance and Diverse Motion" (CVPR 2022)

---

### 8. CrowdHuman

**官方主页**: [http://www.crowdhuman.org/](http://www.crowdhuman.org/)

**数据定位**: 拥挤场景中的行人检测基准数据集

**数据规模**:
- 训练集: 15,000张图像
- 验证集: 4,370张图像
- 测试集: 5,000张图像
- 总计470K+人体实例（训练+验证）
- 平均每张图22.6人

**标注类型**:
- 可见边界框（visible bbox）
- 全身边界框（full-body bbox）
- 头部边界框（head bbox）
- 遮挡程度标注

**适用场景**:
- 拥挤场景行人检测
- 遮挡处理
- 预训练检测模型
- 跨数据集泛化测试

**使用限制**: 学术研究使用

**优点**:
- 规模大、标注丰富
- 遮挡标注详细
- 泛化性能优秀（在Caltech、CityPersons上表现出色）
- 高密度场景

**缺点**:
- 仅提供图像，非视频
- 无轨迹ID

**获取难度**: ⭐ 简单

**下载链接**:
- [官方网站](http://www.crowdhuman.org/)
- [Hugging Face镜像](http://huggingface.co/datasets/sshao0516/CrowdHuman)

**论文引用**:
- Shao et al., "CrowdHuman: A Benchmark for Detecting Human in a Crowd" (2018)

---

### 9. KITTI Tracking Benchmark

**官方主页**: [http://www.cvlibs.net/datasets/kitti/](http://www.cvlibs.net/datasets/kitti/)

**数据定位**: 自动驾驶场景的多目标跟踪基准

**数据规模**:
- 训练集: 21个序列
- 测试集: 29个序列
- 包含RGB图像、LiDAR点云、GPS/IMU数据

**标注类型**:
- 8个类别（汽车、货车、卡车、行人、坐着的人、骑行者、有轨电车、杂项）
- 3D边界框
- 轨迹ID
- 遮挡和截断标签

**适用场景**:
- 自动驾驶行人跟踪
- 3D MOT
- 传感器融合

**使用限制**: 学术研究与非商业使用

**优点**:
- 权威的自动驾驶基准
- 多模态数据（相机+LiDAR）
- 3D标注

**缺点**:
- 行人密度较低（平均<30人/帧）
- 主要是道路场景
- 数据规模中等

**获取难度**: ⭐⭐ 中等

**下载链接**:
- [KITTI官网](http://www.cvlibs.net/datasets/kitti/)

**论文引用**:
- Geiger et al., "Vision meets Robotics: The KITTI Dataset" (IJRR 2013)

---

### 10. BDD100K

**官方主页**: [https://www.bdd100k.com/](https://www.bdd100k.com/)

**数据定位**: 大规模多样化驾驶数据集，支持多任务学习

**数据规模**:
- 100,000个视频片段
- 1,100小时驾驶视频
- 多种天气、时间、场景条件

**标注类型**:
- 目标检测边界框
- 多目标跟踪ID
- 车道线标注
- 可驾驶区域
- 全帧语义/实例分割
- MOT和MOTS标注

**适用场景**:
- 驾驶场景行人检测/跟踪
- 多任务学习
- 场景多样性评估

**使用限制**: 需注册，学术与商业使用均需授权

**优点**:
- 规模极大
- 场景多样性极高
- 多任务标注
- 持续更新

**缺点**:
- 数据量大，处理复杂
- 下载和存储要求高

**获取难度**: ⭐⭐⭐ 较难

**下载链接**:
- [BDD100K官网](https://www.bdd100k.com/)

**论文引用**:
- Yu et al., "BDD100K: A Diverse Driving Dataset for Heterogeneous Multitask Learning" (CVPR 2020)

---

### 11. VisDrone

**官方主页**: [VisDrone GitHub](https://github.com/VisDrone/VisDrone-Dataset)

**数据定位**: 无人机视角的目标检测与跟踪数据集

**数据规模** (待核实准确数字):
- 2.6M+ 边界框标注
- 多种高度、视角、光照条件

**标注类型**:
- 10个类别（行人、人群、汽车、面包车、公交车、卡车、摩托车、自行车、三轮车、遮阳棚三轮车）
- 边界框
- 目标ID（跟踪任务）
- 遮挡和截断标签
- 场景可见性

**适用场景**:
- 无人机/航拍视角的检测跟踪
- 小目标检测
- 拥挤场景

**使用限制**: 开源，学术研究

**优点**:
- 独特的无人机视角
- 小目标多
- 场景多样

**缺点**:
- 标注密度不均
- 小目标标注挑战大

**获取难度**: ⭐⭐ 中等

**下载链接**:
- [GitHub](https://github.com/VisDrone/VisDrone-Dataset)
- [Ultralytics文档](https://docs.ultralytics.com/datasets/detect/visdrone/)

**论文引用**:
- Zhu et al., "Detection and Tracking Meet Drones Challenge" (2021)

---

### 12. CityPersons

**官方主页**: [GitHub](https://github.com/cvgroup-njust/CityPersons)

**数据定位**: 城市街景行人检测数据集，基于Cityscapes构建

**数据规模**:
- 基于Cityscapes的高质量标注
- 35,000个行人标注
- 涵盖多种欧洲城市

**标注类型**:
- 行人边界框
- 遮挡程度
- 可见性标签

**适用场景**:
- 城市场景行人检测
- 多样化环境评估

**使用限制**: 需下载Cityscapes原始图像

**优点**:
- 高分辨率图像
- 多样化城市场景
- 详细遮挡标注

**缺点**:
- 仅提供标注，需从Cityscapes获取图像
- 非视频序列（静态图像为主）

**获取难度**: ⭐⭐⭐ 较难（需先获取Cityscapes）

**下载链接**:
- [CityPersons标注](https://github.com/cvgroup-njust/CityPersons)
- [Cityscapes官网](https://www.cityscapes-dataset.com/)

**论文引用**:
- Zhang et al., "CityPersons: A Diverse Dataset for Pedestrian Detection" (CVPR 2017)

---

### 13. Caltech Pedestrian Detection Benchmark

**官方主页**: [Caltech Vision](https://data.caltech.edu/records/f6rph-90m20)

**数据定位**: 车载视角的行人检测经典基准

**数据规模**:
- 约10小时的视频
- 250,000帧
- 350,000个边界框
- 2,300个独特行人

**标注类型**:
- 行人边界框
- 遮挡标签
- 可见性评分

**适用场景**:
- 行人检测算法评估
- 低分辨率行人检测
- 遮挡处理

**使用限制**: 学术研究使用

**优点**:
- 经典基准，广泛认可
- 详细的遮挡标注
- 多种评估协议

**缺点**:
- 数据较老（2009年）
- 分辨率较低
- 场景单一（车载视角）

**获取难度**: ⭐⭐ 中等

**下载链接**:
- [Caltech官方](https://data.caltech.edu/records/f6rph-90m20)

**论文引用**:
- Dollár et al., "Pedestrian Detection: A Benchmark" (CVPR 2009)

---

### 14. PETS Dataset

**官方来源**: 历年PETS Workshop

**数据定位**: 监控场景的行人检测与跟踪数据集（历史基准）

**数据规模**:
- PETS 2009: 多个校准相机的人群场景
- PETS 2017: 移动平台监控

**标注类型**:
- 边界框
- 轨迹ID
- 人群事件标注

**适用场景**:
- 监控场景
- 人群分析
- 多相机跟踪

**使用限制**: 学术研究

**优点**:
- 经典基准
- 多相机同步

**缺点**:
- 数据较老
- 规模小
- 分辨率低

**获取难度**: ⭐⭐ 中等

**下载链接**:
- [OpenTraj PETS-2009](https://github.com/crowdbotp/OpenTraj/blob/master/datasets/PETS-2009/README.md)

**论文引用**:
- Ferryman & Shahrokni, "PETS2009: Dataset and Challenge" (2009)

---

## 多摄像头/跨视角数据集

### 15. WILDTRACK

**官方主页**: 通过论文获取

**数据定位**: 7摄像头同步的高清多视图行人检测数据集

**数据规模**:
- 7个静态相机
- 高清视频（1920×1080）
- 公共开放区域的行人行走场景

**标注类型**:
- 多视图边界框
- 地面平面位置
- 相机标定参数

**适用场景**:
- 多视图行人检测
- 跨相机跟踪
- 遮挡消解
- 相机标定研究

**使用限制**: 学术研究

**优点**:
- 高清多视图同步
- 精确的相机标定
- 减少遮挡问题

**缺点**:
- 场景单一
- 数据规模中等

**获取难度**: ⭐⭐ 中等

**下载链接**: (需查找官方EPFL链接)

**论文引用**:
- Chavdarova et al., "WILDTRACK: A Multi-Camera HD Dataset for Dense Unscripted Pedestrian Detection" (CVPR 2018)

---

## 合成数据集

### 16. MOTSynth

**官方来源**: 论文与代码

**数据定位**: 大规模合成的行人检测、重识别与跟踪数据集

**数据规模** (待核实):
- 使用游戏引擎生成
- 规模远超真实数据集
- 高度多样化的场景、外观、光照

**标注类型**:
- 完美的边界框
- 精确的轨迹ID
- 分割mask
- 深度图
- 重识别特征

**适用场景**:
- 仅使用合成数据训练
- 域自适应研究
- 数据增强
- 隐私保护场景

**使用限制**: 需查阅论文获取细节

**优点**:
- 规模巨大
- 标注完美
- 无隐私问题
- 高度可控

**缺点**:
- 存在域偏移（synthetic-to-real gap）
- 需要域自适应技术

**获取难度**: ⭐⭐⭐ 较难

**下载链接**: (待查找)

**论文引用**:
- Fabbri et al., "MOTSynth: How Can Synthetic Data Help Pedestrian Detection and Tracking?" (ICCV 2021)

---

## 推荐数据组合方案

### 方案一：轻量级快速验证

**目标**: 快速搭建轨迹预测与MOT原型

**推荐数据集**:
1. **ETH/UCY** - 轨迹预测基础验证
2. **CrowdHuman** - 检测模型预训练
3. **MOT17** - MOT算法基准测试

**优点**: 数据量小，下载快，社区支持好\
**适用阶段**: 项目初期、算法原型验证

---

### 方案二：标准研究配置

**目标**: 完整的视觉模块训练与评估

**推荐数据集**:

**轨迹建模层**:
1. **TrajNet++** - 统一的轨迹预测基准
2. **Stanford Drone Dataset** - 大规模俯视轨迹

**检测跟踪层**:
3. **MOT17 + MOT20** - 标准MOT基准
4. **CrowdHuman** - 检测器预训练
5. **DanceTrack** - 运动依赖跟踪评估

**优点**: 覆盖主流基准，论文可对比性强\
**适用阶段**: 论文发表、算法评估

---

### 方案三：多场景泛化配置

**目标**: 提升模型在多种场景下的泛化能力

**推荐数据集**:

**室内外混合**:
1. **JRDB** - 机器人视角，室内外混合

**多视角覆盖**:
2. **WILDTRACK** - 多摄像头
3. **VisDrone** - 无人机视角

**驾驶场景**:
4. **BDD100K** - 大规模驾驶场景
5. **KITTI** - 自动驾驶标准

**城市街景**:
6. **CityPersons** - 城市多样性

**优点**: 场景覆盖全面，泛化性能强\
**适用阶段**: 产品化、实际部署前

---

### 方案四：大规模预训练配置

**目标**: 利用大规模数据训练强检测/跟踪模型

**推荐数据集**:
1. **MOTSynth** - 大规模合成数据预训练
2. **CrowdHuman** - 真实数据精调
3. **BDD100K** - 多样性泛化
4. **MOT17/20 + DanceTrack** - 基准测试

**优点**: 数据量大，模型性能天花板高\
**适用阶段**: 资源充足的研究团队

---

## 数据获取优先级

### 🔴 高优先级（立即获取）

| 数据集 | 类型 | 理由 |
|--------|------|------|
| **ETH/UCY** | 轨迹预测 | 轻量、易获取、必备基准 |
| **CrowdHuman** | 检测 | 大规模、下载简单、预训练必备 |
| **MOT17** | MOT | 标准基准、社区认可度高 |

---

### 🟡 中优先级（2周内获取）

| 数据集 | 类型 | 理由 |
|--------|------|------|
| **TrajNet++** | 轨迹预测 | 统一基准、交互标注 |
| **Stanford Drone Dataset** | 轨迹预测 | 规模大、俯视视角 |
| **MOT20** | MOT | 拥挤场景专用 |
| **DanceTrack** | MOT | 测试运动依赖能力 |

---

### 🟢 低优先级（按需获取）

| 数据集 | 类型 | 理由 |
|--------|------|------|
| **JRDB** | 3D MOT | 机器人视角、处理复杂 |
| **BDD100K** | 驾驶MOT | 数据量大、需充足存储 |
| **WILDTRACK** | 多相机 | 特定研究方向需要 |
| **VisDrone** | 无人机 | 小目标专用 |
| **KITTI** | 驾驶3D | 需3D标注时 |
| **CityPersons** | 检测 | 需Cityscapes原图 |
| **MOTSynth** | 合成 | 隐私敏感或数据增强需求 |

---

## 待核实信息清单

以下信息在本次调研中未能完全核实，需要后续访问官方网站或联系数据集作者确认：

1. **JRDB**: 精确的数据规模数字、下载流程
2. **inD Dataset**: 官方下载链接、许可协议
3. **MOTSynth**: 官方下载地址、数据规模
4. **WILDTRACK**: 官方下载链接
5. **VisDrone**: 准确的标注数量统计
6. **TrajNet++**: 当前数据集版本号和最新更新

---

## 引用与来源

本报告基于以下来源整理：

### 官方数据集主页
- [MOTChallenge](https://motchallenge.net/)
- [CrowdHuman](http://www.crowdhuman.org/)
- [DanceTrack](https://dancetrack.github.io/)
- [Stanford Drone Dataset](https://cvgl.stanford.edu/projects/uav_data)
- [TrajNet++](http://trajnet.epfl.ch/)
- [JRDB](https://jrdb.erc.monash.edu/)
- [BDD100K](https://www.bdd100k.com/)

### GitHub官方仓库
- [OpenTraj](https://github.com/crowdbotp/OpenTraj) - 多个轨迹数据集整合
- [DanceTrack GitHub](https://github.com/DanceTrack/DanceTrack)
- [CityPersons](https://github.com/cvgroup-njust/CityPersons)
- [VisDrone](https://github.com/VisDrone/VisDrone-Dataset)
- [TrackEval](https://github.com/JonathonLuiten/TrackEval) - MOT评估工具

### 学术论文
- arXiv上的各数据集论文
- CVPR/ICCV/ECCV会议论文

---

## 后续行动建议

1. **立即下载**: ETH/UCY、CrowdHuman、MOT17
2. **建立数据管理**: 统一的数据集根目录和版本控制
3. **核实待确认项**: 访问被阻止的官方网站，确认数据规模和下载方式
4. **构建数据加载器**: 为每个数据集编写统一的PyTorch DataLoader
5. **制定标注转换**: 统一不同数据集的标注格式
6. **设置基线实验**: 在标准数据集上建立性能基线

---

**报告更新**: 如有新数据集发布或信息更正，请及时更新本文档。

**联系**: 如需补充特定数据集的详细信息，可针对性搜索或联系数据集维护者。
