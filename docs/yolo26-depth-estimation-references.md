# YOLO26 单目深度估计技术文献

> **status: historical** · 2026-10-07 审计标注：本文是写作当日的快照，其中“当前”“完成”等表述只指当时状态。当前 RAG 状态见 [RAG 资产与一致性审计](rag-asset-audit-2026-10-07.md)。

_Technical references and literature for YOLO26 monocular depth estimation_

---

## 📋 概述

本文档整理了 YOLO26 单目深度估计功能的相关技术说明和学术文献，供研究参考。

**核心要点**：
- YOLO26-Depth 是基于单目相机的深度估计功能
- 从单张 RGB 图像预测逐像素深度图（单位：米）
- 发布于 Ultralytics v8.4.104（2026年7月）

---

## 1️⃣ YOLO26 架构论文

### 主要论文

**An Analysis of NMS-Free End to End Framework for Real-Time Object Detection**
- arXiv: [2601.12882](https://arxiv.org/abs/2601.12882)
- 内容: YOLO26 端到端无 NMS 框架分析
- 关键创新: 移除非极大值抑制，实现端到端推理

**YOLO26: Key Architectural Enhancements and Performance Benchmarking**
- arXiv: [2509.25164](https://arxiv.org/abs/2509.25164)
- 内容: YOLO26 架构增强和性能基准测试
- 关键特性:
  - Dual-head 设计
  - ProgLoss（渐进损失）
  - STAL（小目标感知标签分配）
  - MuSGD 优化器

**Unified Real-Time End-to-End Vision Models**
- arXiv: [2606.03748](https://arxiv.org/abs/2606.03748)
- 内容: 统一实时端到端视觉模型
- 相关性: YOLO26 多任务统一架构的理论基础

**A Comprehensive Architecture Overview and Key Improvements**
- arXiv: [2602.14582](https://arxiv.org/abs/2602.14582)
- 内容: YOLO26 全面架构概述和关键改进

---

## 2️⃣ 单目深度估计理论综述

### 最新综述（必读）

**Deep Learning-based Depth Estimation Methods: A Comprehensive Survey (2024)**
- 论文: arXiv [2406.19675](https://arxiv.org/abs/2406.19675)
- 发表: ACM Computing Surveys, October 2024
- 内容: 深度学习深度估计方法全面综述
- 覆盖范围:
  - 输入/输出模态分类法
  - 网络架构演进历史
  - 学习方法（监督/自监督/半监督）
  - 主要里程碑和评估指标
  - 数据集和基准测试

**Survey on Monocular Metric Depth Estimation (2025)**
- 论文: arXiv [2501.11841](https://arxiv.org/abs/2501.11841)
- 发表: January 2025
- 内容: 专注于度量深度估计（绝对尺度）
- 核心问题: 解决相对深度缺乏度量尺度的限制
- 应用领域: 空间理解、3D 重建、自主导航

**Monocular Depth Estimation Based On Deep Learning (2020)**
- 论文: arXiv [2003.06620](https://arxiv.org/abs/2003.06620)
- 内容: 早期深度学习深度估计基础
- 价值: 了解技术演进历史

### 核心挑战

单目深度估计是**病态问题（ill-posed problem）**和**固有模糊问题（inherently ambiguous）**：
- 3D 到 2D 投影过程中丢失深度信息
- 需要从单张图像的视觉线索推断深度
- 相对深度易于估计，但度量尺度（绝对深度）困难

---

## 3️⃣ 深度估计基础模型

### MiDaS v3.1 (2023)

**MiDaS v3.1 – A Model Zoo for Robust Monocular Relative Depth Estimation**
- 论文: arXiv [2307.14460](https://arxiv.org/abs/2307.14460)
- 机构: Intel Labs
- 架构: Transformer encoder + DPT decoder
- 特点: 鲁棒的相对深度估计，多种 backbone 选择
- 局限: 仅输出相对深度，缺乏度量尺度

```bibtex
@article{midas_v31_2023,
  title={MiDaS v3.1--A Model Zoo for Robust Monocular Relative Depth Estimation},
  author={Birkl, Reiner and Wofk, Diana and M{\"u}ller, Matthias},
  journal={arXiv preprint arXiv:2307.14460},
  year={2023}
}
```

### Depth Anything (CVPR 2024) ⭐

**Depth Anything: Unleashing the Power of Large-Scale Unlabeled Data**
- 论文: [GitHub](https://github.com/LiheYoung/Depth-Anything) | [Project Page](https://depth-anything.github.io/)
- 会议: CVPR 2024
- 机构: University of Hong Kong, TikTok
- 训练数据:
  - 150万张标注图像
  - 6200万+未标注图像（自监督学习）
- 架构:
  - Encoder: DINOv2（预训练视觉基础模型）
  - Decoder: DPT（Dense Prediction Transformer）
- 性能: 零样本性能超越 MiDaS v3.1
- 优势: 继承丰富的语义先验，泛化能力强

```bibtex
@inproceedings{depth_anything_2024,
  title={Depth Anything: Unleashing the Power of Large-Scale Unlabeled Data},
  author={Yang, Lihe and Kang, Bingyi and Huang, Zilong and Xu, Xiaogang and Feng, Jiashi and Zhao, Hengshuang},
  booktitle={CVPR},
  year={2024}
}
```

### Depth Anything V2 (NeurIPS 2024) ⭐⭐

**Depth Anything V2**
- 论文: [GitHub](https://github.com/DepthAnything/Depth-Anything-V2)
- 会议: NeurIPS 2024
- 改进:
  - 更精细的细节捕捉
  - 更快的推理速度
  - 更少的参数量
  - 更高的深度精度
- 对比: 显著优于 Stable Diffusion 类深度模型

```bibtex
@inproceedings{depth_anything_v2_2024,
  title={Depth Anything V2},
  author={Yang, Lihe and Kang, Bingyi and Huang, Zilong and Zhao, Hengshuang and Xu, Xiaogang and Feng, Jiashi and Zhao, Hengshuang},
  booktitle={NeurIPS},
  year={2024}
}
```

### DPT (Dense Prediction Transformer)

- 解码器架构，用于密集预测任务
- 被 MiDaS 和 Depth Anything 采用
- 处理从 encoder 提取的视觉特征

---

## 4️⃣ 评估数据集

### NYU Depth V2 ⭐ 主要基准

**Indoor Segmentation and Support Inference from RGBD Images**
- 作者: Nathan Silberman, Derek Hoiem, Pushmeet Kohli, Rob Fergus
- 会议: ECCV 2012
- 官网: [NYU Depth V2](https://cs.nyu.edu/~fergus/datasets/nyu_depth_v2.html)

**数据集规模**：
- 总帧数: 407,024（未标注）
- 标注帧数: 1,449（密集标注）
- 场景数: 464 个不同室内场景
- 场景类型: 26 类（办公室、商店、住宅等）
- 对象类别: 1,000+
- 深度范围: 0.5m - 10m
- 分辨率: 640×480
- 传感器: Microsoft Kinect（RGB-D）

**Eigen Split**（标准评估协议）：
- 训练集: 约 24K 图像
- 验证集: 654 图像
- 测试集: 697 图像
- 用途: 零样本深度估计评估的事实标准

**YOLO26-Depth 评估**: 在 NYU Depth V2 Eigen split 上进行评估

```bibtex
@inproceedings{nyu_depth_v2_2012,
  title={Indoor Segmentation and Support Inference from RGBD Images},
  author={Silberman, Nathan and Hoiem, Derek and Kohli, Pushmeet and Fergus, Rob},
  booktitle={European Conference on Computer Vision (ECCV)},
  year={2012},
  organization={Springer}
}
```

### 其他常用数据集

**KITTI (2012)**
- 用途: 自动驾驶场景室外深度估计
- 规模: 约 93K 训练图像，Eigen split 常用
- 特点: 激光雷达真值，稀疏深度

**Make3D (2007)**
- 用途: 早期单目深度估计基准
- 规模: 534 张图像（400 训练 + 134 测试）

**SUN RGB-D (2015)**
- 用途: 室内场景理解
- 规模: 10,335 张 RGB-D 图像

---

## 5️⃣ 评估指标

### 标准度量公式

基于论文 **On the Metrics for Evaluating Monocular Depth Estimation** (arXiv [2302.10007](https://arxiv.org/abs/2302.10007), 2023)：

#### 误差指标

**1. AbsRel（绝对相对误差）** ⭐ 最重要
```
AbsRel = (1/N) Σ |d_i - d*_i| / d*_i
```
- 与下游任务性能相关性最高
- 典型值: <0.1 优秀，<0.15 良好

**2. RMSE（均方根误差）**
```
RMSE = sqrt((1/N) Σ (d_i - d*_i)²)
```
- 单位: 米（m）
- 对大误差敏感
- 典型值: <0.5m（室内），<5m（室外）

**3. RMSE log（对数空间 RMSE）**
```
RMSE_log = sqrt((1/N) Σ (log d_i - log d*_i)²)
```
- 优点: 尺度不变性

**4. MAE（平均绝对误差）**
```
MAE = (1/N) Σ |d_i - d*_i|
```
- 单位: 米（m）

#### 准确度指标

**Delta 阈值准确度**
```
δ_t = % of pixels where max(d_i/d*_i, d*_i/d_i) < threshold
```
常用阈值:
- δ₁: threshold = 1.25
- δ₂: threshold = 1.25² = 1.5625
- δ₃: threshold = 1.25³ = 1.953125

解读:
- δ₁ > 80%: 优秀
- δ₁ > 70%: 良好
- δ₁ > 60%: 可接受

```bibtex
@article{depth_metrics_2023,
  title={On the Metrics for Evaluating Monocular Depth Estimation},
  author={...},
  journal={arXiv preprint arXiv:2302.10007},
  year={2023}
}
```

---

## 6️⃣ 深度估计的视觉线索

深度学习模型学习从以下线索推断深度：

### 几何线索
1. **透视收敛**: 平行线在远处汇聚，物体随距离变小
2. **遮挡关系**: 前景遮挡背景，部分可见性暗示深度顺序
3. **相对尺寸**: 已知物体的大小推断距离

### 光学线索
4. **纹理梯度**: 远处纹理更密集，细节随距离衰减
5. **大气透视**: 远处物体对比度降低，颜色饱和度下降
6. **阴影与光照**: 光照变化暗示表面方向

### 语义线索
7. **场景理解**: 识别"地面"、"墙壁"、"天空"
8. **对象识别**: "人"通常在地面上，"天花板灯"在顶部

---

## 7️⃣ BibTeX 引用集合

```bibtex
% YOLO26 Architecture
@article{yolo26_nms_free_2026,
  title={An Analysis of NMS-Free End to End Framework for Real-Time Object Detection},
  author={...},
  journal={arXiv preprint arXiv:2601.12882},
  year={2026}
}

@article{yolo26_architecture_2026,
  title={YOLO26: Key Architectural Enhancements and Performance Benchmarking for Real-Time Object Detection},
  author={...},
  journal={arXiv preprint arXiv:2509.25164},
  year={2026}
}

@article{yolo26_unified_2026,
  title={Unified Real-Time End-to-End Vision Models},
  author={...},
  journal={arXiv preprint arXiv:2606.03748},
  year={2026}
}

% Depth Estimation Surveys
@article{depth_survey_2024,
  title={Deep Learning-based Depth Estimation Methods from Monocular Image and Videos: A Comprehensive Survey},
  author={...},
  journal={ACM Computing Surveys},
  year={2024},
  note={arXiv:2406.19675}
}

@article{metric_depth_survey_2025,
  title={Survey on Monocular Metric Depth Estimation},
  author={...},
  journal={arXiv preprint arXiv:2501.11841},
  year={2025}
}

@article{depth_dl_2020,
  title={Monocular Depth Estimation Based On Deep Learning: An Overview},
  author={...},
  journal={arXiv preprint arXiv:2003.06620},
  year={2020}
}

% Foundation Models
@inproceedings{depth_anything_2024,
  title={Depth Anything: Unleashing the Power of Large-Scale Unlabeled Data},
  author={Yang, Lihe and Kang, Bingyi and Huang, Zilong and Xu, Xiaogang and Feng, Jiashi and Zhao, Hengshuang},
  booktitle={CVPR},
  year={2024}
}

@inproceedings{depth_anything_v2_2024,
  title={Depth Anything V2},
  author={Yang, Lihe and Kang, Bingyi and Huang, Zilong and Zhao, Hengshuang and Xu, Xiaogang and Feng, Jiashi and Zhao, Hengshuang},
  booktitle={NeurIPS},
  year={2024}
}

@article{midas_v31_2023,
  title={MiDaS v3.1--A Model Zoo for Robust Monocular Relative Depth Estimation},
  author={Birkl, Reiner and Wofk, Diana and M{\"u}ller, Matthias},
  journal={arXiv preprint arXiv:2307.14460},
  year={2023}
}

% Datasets
@inproceedings{nyu_depth_v2_2012,
  title={Indoor Segmentation and Support Inference from RGBD Images},
  author={Silberman, Nathan and Hoiem, Derek and Kohli, Pushmeet and Fergus, Rob},
  booktitle={European Conference on Computer Vision (ECCV)},
  pages={746--760},
  year={2012},
  organization={Springer}
}

% Evaluation Metrics
@article{depth_metrics_2023,
  title={On the Metrics for Evaluating Monocular Depth Estimation},
  author={...},
  journal={arXiv preprint arXiv:2302.10007},
  year={2023}
}
```

---

## 8️⃣ 在线资源

### 官方文档
- [Ultralytics YOLO26 Depth Estimation](https://docs.ultralytics.com/tasks/depth)
- [Ultralytics Blog: YOLO26 Depth](https://www.ultralytics.com/blog/ultralytics-yolo26-now-supports-monocular-depth-estimation)

### 开源项目
- [Depth Anything GitHub](https://github.com/LiheYoung/Depth-Anything)
- [Depth Anything V2 GitHub](https://github.com/DepthAnything/Depth-Anything-V2)
- [MiDaS GitHub](https://github.com/isl-org/MiDaS)

### 数据集
- [NYU Depth V2 Official](https://cs.nyu.edu/~fergus/datasets/nyu_depth_v2.html)
- [KITTI Dataset](http://www.cvlibs.net/datasets/kitti/)

---

## 9️⃣ 推荐阅读顺序

### 快速了解（1-2天）
1. ✅ YOLO26 官方文档
2. ✅ Depth Anything 项目页面
3. ✅ NYU Depth V2 数据集介绍

### 深入理解（1周）
4. 📄 Deep Learning-based Depth Estimation Survey (2024) - arXiv:2406.19675
5. 📄 YOLO26 Architecture - arXiv:2509.25164
6. 📄 On the Metrics for Evaluating - arXiv:2302.10007

### 进阶研究（2-4周）
7. 📄 Depth Anything 论文（CVPR 2024）
8. 📄 MiDaS v3.1 - arXiv:2307.14460
9. 📄 Survey on Metric Depth - arXiv:2501.11841
10. 📄 NYU Depth V2 原始论文（Silberman et al., ECCV 2012）

---

## 🔟 总结

**YOLO26-Depth 技术特点**：
- 单目深度估计，无需立体相机
- 端到端推理，与 YOLO 检测统一架构
- 训练于 ~219万图像，评估于 NYU Depth V2
- 精度约 ±10-30cm，适合快速分析场景

**在行人流研究中的定位**：
- 辅助工具，不替代几何标定
- 适用于探索性分析和历史视频
- 正式实验仍推荐传统几何标定方法

**相关研究前沿**：
- Depth Anything V2 (NeurIPS 2024) 代表当前最强基础模型
- 度量深度估计（绝对尺度）仍是活跃研究方向
- 深度估计与其他视觉任务的联合学习是趋势
