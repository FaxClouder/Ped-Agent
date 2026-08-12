# Video-Analysis

`Video-Analysis/` 是 Ped-Agent 内部独立开发和测试的轨迹处理与分析模块。
模块按三个平级业务板块组织，各板块都可以作为使用入口，不要求依次执行完整链路：

1. `extraction/`：从视频中检测、跟踪并提取像素轨迹；
2. `processing/`：完成投影变换和轨迹优化，形成分析就绪轨迹；
3. `analysis/`：直接分析满足契约的轨迹，生成指标、事件、图表和导出产物。

已有处理好的世界坐标轨迹可以绕过 `extraction/` 和 `processing/`，经过分析输入预检后直接进入 `analysis/`。

## 正式目录

```text
Video-Analysis/
├─ docs/                              # 模块内部设计和迁移说明
├─ models/                            # 检测模型清单与本地权重
├─ trackers/                          # 追踪器配置与专属资源
├─ runtime/                           # 本地运行产物；Git 忽略
├─ src/ped_video_analysis/
│  ├─ api.py                          # 三个板块的公共门面与可选组合入口
│  ├─ contracts/                     # 板块输入、输出和质量状态契约
│  ├─ extraction/                    # 轨迹检测与提取
│  ├─ processing/                    # 投影变换与轨迹优化
│  ├─ analysis/                      # 轨迹分析
│  ├─ infrastructure/                # 配置、资源、存储和运行时支撑
│  ├─ vision/                        # 现有视觉实现，迁移期兼容目录
│  └─ tools/                         # 模块内部开发工具，不承载业务主链
└─ tests/
   ├─ contracts/
   ├─ extraction/
   ├─ processing/
   ├─ analysis/
   └─ infrastructure/
```

详细职责、依赖规则和现有文件迁移映射见
[`docs/directory-design.md`](docs/directory-design.md)。当前阶段只确立目录边界，
现有实现仍保留原路径，后续按板块逐项迁移，不在本次目录调整中批量移动代码。

## 可选使用路径

```text
原始视频          -> extraction -> processing -> analysis
外部像素轨迹      ----------------> processing -> analysis
外部世界坐标轨迹  ------------------------------> analysis
```

是否能够跳过前置板块，由输入数据是否满足下一板块契约决定，而不是由数据来源决定。

## 模型与追踪器

默认模型配置：

`models/yolo26x/model.yaml`

默认追踪器配置：

`trackers/bytetrack/tracker.yaml`

首次运行前需要：

1. 将模型权重放入 `models/yolo26x/weights/yolo26x.pt`；
2. 将 `model.yaml` 中的占位 `sha256` 替换为权重文件的真实 SHA-256；
3. 根据需要调整模型推理参数或 ByteTrack 参数。

模型配置不再包含追踪器参数。注册器加载模型时，会将选定的追踪器配置组合为现有运行链路所需的兼容清单。

## 当前公共调用

```python
from ped_video_analysis import create_model_registry, run_video_inference

registry = create_model_registry(tracker_id="bytetrack")
pixel_tracks = run_video_inference(
    "sample.mp4",
    task_id="demo-001",
    model_id="mixed-flow-yolo26-bytetrack",
    registry=registry,
)
```

上述函数属于当前兼容 API。后续会在不依赖 HTTP、前端或 Ped-Agent 后端的前提下，
逐步收敛为检测提取、投影优化和直接分析三个独立入口。外部 HTTP 接口只作为后续适配层预留。

独立使用时可以通过 `PED_VIDEO_ANALYSIS_HOME` 指定 `Video-Analysis` 根目录。
