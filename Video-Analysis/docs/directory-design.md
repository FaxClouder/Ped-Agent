# Video-Analysis 目录设计

## 1. 设计结论

模块由三个平级、可独立进入的业务板块组成：

| 板块 | 输入 | 输出 | 是否依赖前置板块 |
| --- | --- | --- | --- |
| 轨迹检测与提取 `extraction` | 原始视频、模型与追踪器配置 | 像素轨迹 | 否 |
| 投影变换与轨迹优化 `processing` | 像素轨迹，或尚未优化的世界轨迹 | 分析就绪轨迹 | 否 |
| 轨迹分析 `analysis` | 满足分析契约的世界坐标轨迹 | 指标、事件、图表与导出产物 | 否 |

三个板块存在推荐的数据流，但不存在强制调用顺序。使用者已有处理好的世界坐标轨迹时，
可以直接调用分析板块。

## 2. 目标目录

```text
Video-Analysis/
├─ docs/
│  └─ directory-design.md
├─ models/
│  └─ <model-id>/
│     ├─ model.yaml
│     └─ weights/
├─ trackers/
│  └─ <tracker-id>/
│     ├─ tracker.yaml
│     └─ weights/
├─ runtime/
├─ src/ped_video_analysis/
│  ├─ __init__.py
│  ├─ api.py
│  ├─ contracts/
│  │  ├─ __init__.py
│  │  ├─ extraction.py              # 预留：视频和像素轨迹契约
│  │  ├─ processing.py              # 预留：投影、优化和分析就绪轨迹契约
│  │  ├─ analysis.py                # 预留：分析请求、结果和能力状态契约
│  │  └─ quality.py                 # 预留：质量状态、限制和预检结果
│  ├─ extraction/
│  │  ├─ __init__.py
│  │  ├─ detectors/                 # 检测器适配
│  │  ├─ trackers/                  # 多目标追踪适配
│  │  ├─ contact_points/            # 接触点提取
│  │  ├─ review/                    # 像素轨迹复核
│  │  └─ pipeline.py                # 本板块内部编排
│  ├─ processing/
│  │  ├─ __init__.py
│  │  ├─ calibration/               # 相机标定和质量门禁
│  │  ├─ projection/                # 像素到世界坐标投影
│  │  ├─ optimization/              # 插值、异常标记和平滑
│  │  └─ pipeline.py                # 本板块内部编排
│  ├─ analysis/
│  │  ├─ __init__.py
│  │  ├─ validation/                # 分析输入和指标可用性预检
│  │  ├─ individual/                # 个体运动指标
│  │  ├─ flow/                      # 流量和计数线指标
│  │  ├─ spatial/                   # 密度、热力图和速度场
│  │  ├─ od/                        # OD 和区域停留
│  │  ├─ interaction/               # TTC、PET 等交互代理指标
│  │  ├─ visualization/             # 图表生成
│  │  ├─ export/                    # 分析产物导出
│  │  └─ pipeline.py                # 本板块内部编排
│  ├─ infrastructure/
│  │  ├─ __init__.py
│  │  ├─ config/                    # 配置加载与版本指纹
│  │  ├─ resources/                 # 模型和追踪器资源注册
│  │  ├─ storage/                   # 不可变产物存储
│  │  └─ runtime/                   # 本地任务和执行支撑
│  ├─ vision/                        # 迁移期兼容实现
│  └─ tools/                         # 开发与诊断工具
└─ tests/
   ├─ contracts/
   ├─ extraction/
   ├─ processing/
   ├─ analysis/
   └─ infrastructure/
```

目标树中的细分目录只描述后续文件归属。当前没有真实实现的目录不提前创建，避免形成大量空包。

## 3. 依赖规则

业务板块之间通过 `contracts/` 中的数据对象协作，不直接导入彼此的内部实现。

```text
extraction ----> contracts <---- processing
                      ^
                      |
                  analysis

extraction ----> infrastructure
processing ----> infrastructure
analysis ------> infrastructure
```

约束如下：

1. `extraction`、`processing`、`analysis` 不直接互相导入内部类或函数；
2. 三个板块均可被 `api.py` 单独调用，完整流程只能在顶层门面中组合；
3. `analysis` 只依赖分析就绪轨迹契约，不要求轨迹必须由本模块产生；
4. `infrastructure` 不包含检测、投影或指标计算等业务判断；
5. HTTP、前端、LLM 和知识库连接不进入本模块，只允许后续通过适配器消费公共契约；
6. 测试优先针对单个板块，跨板块测试仅验证公共契约和可选组合路径。

## 4. 入口契约预留

目录为以下三个独立入口预留位置，当前阶段不冻结具体函数签名：

```text
extract trajectories       -> PixelTrajectorySet
transform and optimize     -> AnalysisReadyTrajectorySet
analyze trajectories       -> AnalysisBundle
```

分析入口必须先进行能力预检。缺少 ROI、计数线、入口区域等场景信息时，只跳过依赖这些信息的指标，
不应阻止速度、路径长度等仍可计算的指标。结果需要记录已执行指标、跳过指标、跳过原因和质量限制。

## 5. 现有实现迁移映射

| 当前实现 | 目标板块 |
| --- | --- |
| `vision/adapters.py`、`runner.py`、`inference.py`、`contact_points.py`、`review.py` | `extraction/` |
| `vision/calibration.py`、`projection.py`、`postprocessing.py` | `processing/` |
| `analysis/vision_pipeline.py`、`pedpy_adapter.py`、`vision_visualizer.py`、`vision_exports.py` | `analysis/` |
| `vision/contracts.py`、顶层 `schemas.py` | `contracts/` |
| 顶层 `paths.py`、`registry.py` 和 `vision/artifacts.py` | `infrastructure/` |
| `vision/pipeline.py`、`detector.py`、`tracker.py`、`transform.py`、`postprocess.py` | 评估后迁移或归档的兼容实现 |

迁移时每次只处理一个板块，并保持模块测试通过。迁移完成前，兼容目录不得被外部新代码继续直接依赖。

## 6. 测试目录规则

- `tests/contracts/`：契约校验、序列化、版本和输入预检；
- `tests/extraction/`：检测、跟踪、类别、接触点和像素轨迹复核；
- `tests/processing/`：标定、投影、插值、异常标记和平滑；
- `tests/analysis/`：直接轨迹导入、指标正确性、能力降级、图表和导出；
- `tests/infrastructure/`：配置、资源哈希、产物存储和本地运行支撑。

真实模型和真实数据验收属于模块内部实验测试，但与不依赖权重的单元测试分开执行。
