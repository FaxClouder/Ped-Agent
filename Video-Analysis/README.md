# Video-Analysis

`Video-Analysis/` 是 Ped-Agent 的独立视频检测与轨迹分析模块。当前先完成模型资源、追踪器资源和公共接口骨架的拆分；`tools/` 仅作为预留能力目录，不预设具体分析实现。

## 当前目录

```text
Video-Analysis/
├─ models/                           # 按模型存放配置和权重
│  └─ yolo26x/
│     ├─ model.yaml
│     └─ weights/
├─ trackers/                         # 按追踪器存放配置和专属资源
│  └─ bytetrack/
│     └─ tracker.yaml
├─ src/ped_video_analysis/
│  ├─ api.py                         # 对外稳定函数
│  ├─ schemas.py                     # 公共数据契约
│  ├─ registry.py                    # 模型与追踪器资源加载
│  ├─ pipeline.py                    # 已确认的检测与追踪编排
│  ├─ paths.py                       # 模块资源路径
│  └─ tools/README.md                # 未确定能力的预留边界
├─ runtime/                          # 本地任务和运行产物；Git 忽略
└─ tests/                            # 模块级测试
```

现有 `vision/`、`analysis/` 和内部配置暂时作为兼容实现保留，待 `tools` 的功能清单确认后再决定迁移位置，不在本阶段做推测性重构。

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

## 外部调用

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

Ped-Agent 后端继续提供 `/api/vision/*` HTTP 接口。独立使用时可以通过 `PED_VIDEO_ANALYSIS_HOME` 指定 `Video-Analysis` 根目录。
