# 坐标变换双路线设计

_视频分析模块的像素到世界坐标转换方案 · status: target_

---

## 设计目标

提供两条独立的坐标变换路线，用户根据场景选择：

1. **路线A：几何标定法**（传统方法，高精度）
2. **路线B：深度估计法**（深度学习，便捷性）

两条路线通过配置切换，不做性能对比实验，仅作为工具选项提供。

---

## 路线对比

| 维度 | 路线A：几何标定 | 路线B：深度估计 |
|------|---------------|---------------|
| **精度** | 高（±2-5cm） | 中（±10-30cm） |
| **前置工作** | 需要人工标定 | 无需标定 |
| **适用场景** | 固定相机，平面场景 | 快速分析，历史视频 |
| **依赖** | 标定文件 | YOLO26-depth权重 |
| **计算成本** | 低（矩阵变换） | 中（深度推理） |
| **可解释性** | 强（几何变换明确） | 弱（深度学习黑盒） |
| **科研认可** | 标准方法 | 辅助工具 |

---

## 路线A：几何标定法

### 支持的标定方式

#### A1. 单应矩阵标定（Homography）
**适用场景**：平面地面，固定相机

**输入**：
- 至少4对对应点（像素坐标 ↔ 世界坐标）
- 通过人工标记或标定板获取

**标定文件示例**：
```yaml
# calibration_homography.yaml
method: homography
homography_matrix:
  - [0.0234, 0.0012, -2.156]
  - [0.0008, 0.0289, -4.321]
  - [0.0000, 0.0000, 1.0000]
pixel_points:
  - [120, 200]
  - [520, 200]
  - [520, 680]
  - [120, 680]
world_points:
  - [0.0, 0.0]
  - [15.0, 0.0]
  - [15.0, 20.0]
  - [0.0, 20.0]
reprojection_error_m: 0.023
unit: meters
```

**使用方式**：
```python
from ped_video_analysis import solve_homography

# 人工标记对应点
pixel_pts = [[120, 200], [520, 200], [520, 680], [120, 680]]
world_pts = [[0, 0], [15, 0], [15, 20], [0, 20]]

# 计算单应矩阵
H = solve_homography(pixel_pts, world_pts)
```

#### A2. 完整相机标定（Full Camera Calibration）
**适用场景**：需要校正畸变，非平面场景

**输入**：
- CharUco标定板图像（10-20张不同角度）
- 或棋盘格标定板图像

**标定文件示例**：
```yaml
# calibration_camera.yaml
method: full_camera
camera_matrix:
  - [1200.5, 0.0, 960.0]
  - [0.0, 1205.3, 540.0]
  - [0.0, 0.0, 1.0]
distortion_coefficients: [-0.28, 0.09, 0.001, -0.002, -0.01]
ground_plane_normal: [0.0, 1.0, 0.0]
camera_height_m: 3.5
reprojection_error_px: 0.45
```

**使用方式**：
```python
from ped_video_analysis import calibrate_charuco_images

# 使用标定板图像
calibration = calibrate_charuco_images(
    image_paths=["calib_01.jpg", "calib_02.jpg", ...],
    board_size=(8, 6),
    square_length=0.04,  # 4cm
    marker_length=0.03   # 3cm
)
```

#### A3. 简易缩放（Scale Transform）
**适用场景**：正俯视相机，仅需粗略坐标

**标定文件示例**：
```yaml
# calibration_scale.yaml
method: scale
pixel_per_meter: 35.6
unit: meters
```

---

## 路线B：深度估计法

### 原理

使用 YOLO26-Depth 模型从单张RGB图像估计逐像素深度，结合相机内参反投影到世界坐标。

### 配置文件示例

```yaml
# calibration_depth.yaml
method: depth_estimation
depth_model: yolo26x-depth.pt
camera_intrinsics:
  fx: 1200.5  # 焦距x
  fy: 1205.3  # 焦距y
  cx: 960.0   # 主点x
  cy: 540.0   # 主点y
ground_plane_assumption:
  enabled: true
  camera_height_m: 3.5
  pitch_degrees: 15
depth_confidence_threshold: 0.7  # 低置信度深度值标记为降级
```

### 工作流程

```
视频帧 → 检测/跟踪 → 像素坐标(x_px, y_px)
        ↓
  YOLO26-Depth 推理 → 深度图(H×W)
        ↓
  提取深度值: depth_m = depth_map[y_px, x_px]
        ↓
  反投影: (x_world, y_world) = backproject(x_px, y_px, depth_m, K)
        ↓
  可选：地面约束优化
        ↓
  世界坐标 + 置信度标记
```

### 使用方式

```python
from ped_video_analysis.vision.depth import DepthEstimator

# 初始化深度估计器
depth_estimator = DepthEstimator(
    model_path="yolo26x-depth.pt",
    camera_intrinsics={
        "fx": 1200.5, "fy": 1205.3,
        "cx": 960.0, "cy": 540.0
    }
)

# 对每一帧估计深度并转换
for frame in video:
    depth_map = depth_estimator.estimate(frame)
    world_coords = depth_estimator.transform(
        pixel_points, depth_map
    )
```

---

## 统一配置接口

### 配置切换

通过 `coordinate_transform` 配置块选择路线：

```yaml
# experiment_config.yaml
coordinate_transform:
  # 选择路线A1: 单应矩阵
  method: homography
  calibration_file: memPed/calibrations/scene_001/homography.yaml
```

```yaml
# experiment_config.yaml
coordinate_transform:
  # 选择路线B: 深度估计
  method: depth_estimation
  calibration_file: memPed/calibrations/scene_001/depth.yaml
```

### 推理时自动选择

```python
# 自动根据配置选择路线
transformer = CoordinateTransformer(config["coordinate_transform"])

# 统一接口
world_coords = transformer.transform(pixel_points, frame=frame)
# - 路线A: 忽略frame参数，直接矩阵变换
# - 路线B: 使用frame进行深度估计
```

---

## 实现建议

### 扩展现有 `CoordinateTransformer`

```python
# Video-Analysis/src/ped_video_analysis/vision/transform.py
class CoordinateTransformer:
    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.method = self.config.get("method", "none")
        self.pixel_per_meter = self.config.get("pixel_per_meter")
        self.homography_matrix = None
        self.depth_estimator = None

        if self.method == "homography":
            self.homography_matrix = self._load_matrix(
                self.config["calibration_file"]
            )
        elif self.method == "depth_estimation":
            self.depth_estimator = DepthEstimator(
                model_path=self.config["depth_model"],
                camera_intrinsics=self.config["camera_intrinsics"]
            )

    def transform(
        self,
        pixel_points: np.ndarray,
        frame: np.ndarray | None = None
    ) -> np.ndarray:
        """统一接口：像素坐标 → 世界坐标"""
        if self.method == "none":
            return pixel_points

        elif self.method == "scale":
            return pixel_points / float(self.pixel_per_meter)

        elif self.method == "homography":
            # 路线A：几何标定
            return self._transform_homography(pixel_points)

        elif self.method == "depth_estimation":
            # 路线B：深度估计
            if frame is None:
                raise ValueError("frame required for depth estimation")
            return self._transform_depth(pixel_points, frame)

        raise ValueError(f"Unknown method: {self.method}")

    def _transform_homography(self, points: np.ndarray) -> np.ndarray:
        """路线A实现"""
        import cv2
        pts = points.reshape(-1, 1, 2).astype(np.float64)
        return cv2.perspectiveTransform(
            pts, self.homography_matrix
        ).reshape(-1, 2)

    def _transform_depth(
        self,
        points: np.ndarray,
        frame: np.ndarray
    ) -> np.ndarray:
        """路线B实现"""
        depth_map = self.depth_estimator.estimate(frame)
        world_points = []

        for x_px, y_px in points:
            depth_m = depth_map[int(y_px), int(x_px)]
            x_w, y_w = self.depth_estimator.backproject(
                x_px, y_px, depth_m
            )
            world_points.append([x_w, y_w])

        return np.array(world_points)
```

### 新增深度估计器

```python
# Video-Analysis/src/ped_video_analysis/vision/depth.py
class DepthEstimator:
    """YOLO26-Depth 深度估计与反投影"""

    def __init__(self, model_path: str, camera_intrinsics: dict):
        from ultralytics import YOLO
        self.model = YOLO(model_path)
        self.fx = camera_intrinsics["fx"]
        self.fy = camera_intrinsics["fy"]
        self.cx = camera_intrinsics["cx"]
        self.cy = camera_intrinsics["cy"]

    def estimate(self, frame: np.ndarray) -> np.ndarray:
        """估计深度图"""
        results = self.model(frame)
        return results[0].depth  # (H, W) 深度图（米）

    def backproject(
        self,
        x_px: float,
        y_px: float,
        depth_m: float
    ) -> tuple[float, float]:
        """反投影到世界坐标"""
        # 针孔相机模型反投影
        x_world = (x_px - self.cx) * depth_m / self.fx
        y_world = (y_px - self.cy) * depth_m / self.fy
        return x_world, y_world
```

---

## 使用场景建议

### 何时选择路线A（几何标定）

✅ **推荐场景**：
- 主要研究实验，需要高精度指标
- 固定相机位置，可以完成标定工作
- 平面地面场景（车站、广场、走廊）
- 论文发表的正式实验

✅ **优势**：
- 精度高，误差可控
- 方法明确，科研认可度高
- 计算成本低，实时性好

⚠️ **限制**：
- 需要前期标定工作（10-30分钟/场景）
- 相机移动后需重新标定
- 非平面场景需要完整相机标定

---

### 何时选择路线B（深度估计）

✅ **推荐场景**：
- 探索性分析，快速验证算法
- 历史视频，无法重新标定
- 大规模视频批量处理
- 临时场景、应急事件分析

✅ **优势**：
- 无需人工标定，即开即用
- 适用于任意视频
- 可处理非平面场景

⚠️ **限制**：
- 精度较低，不适合精密研究
- 依赖深度模型质量
- 计算成本较高（深度推理）
- 科研论文中需说明为辅助方法

---

## 文档说明建议

在模块 README 中添加：

```markdown
## 坐标变换配置

视频分析模块提供两种坐标变换方案：

**方案A：几何标定**（推荐用于正式实验）
- 单应矩阵标定（平面场景）
- 完整相机标定（复杂场景）
- 精度：±2-5cm

**方案B：深度估计**（用于快速分析）
- YOLO26-Depth 单目深度估计
- 无需人工标定
- 精度：±10-30cm

详细说明见 `docs/coordinate-transform-dual-routes.md`
```

---

## 代码组织

```
Video-Analysis/src/ped_video_analysis/vision/
├── transform.py              # 统一接口（已存在，需扩展）
├── depth.py                  # 新增：深度估计器
├── calibration.py            # 几何标定工具（已存在）
└── projection.py             # 投影变换（已存在）
```

---

## 实验/演示内容

### 不做对比实验，仅提供使用示例

#### 示例1：路线A使用示例
```python
# examples/coordinate_transform_geometric.py
from ped_video_analysis import run_video_inference, solve_homography

# 1. 标定
pixel_pts = [[120, 200], [520, 200], [520, 680], [120, 680]]
world_pts = [[0, 0], [15, 0], [15, 20], [0, 20]]
H = solve_homography(pixel_pts, world_pts)

# 2. 推理
config = {
    "coordinate_transform": {
        "method": "homography",
        "calibration_file": "homography.yaml"
    }
}
result = run_video_inference(video_path, config=config)
```

#### 示例2：路线B使用示例
```python
# examples/coordinate_transform_depth.py
from ped_video_analysis import run_video_inference

# 无需标定，直接推理
config = {
    "coordinate_transform": {
        "method": "depth_estimation",
        "depth_model": "yolo26x-depth.pt",
        "camera_intrinsics": {
            "fx": 1200, "fy": 1200,
            "cx": 960, "cy": 540
        }
    }
}
result = run_video_inference(video_path, config=config)
```

---

## 模型权重准备

### 路线A所需
- 无需额外模型权重
- 仅需检测/跟踪模型：`yolo26x.pt` + ByteTrack

### 路线B所需
- 检测/跟踪：`yolo26x.pt` + ByteTrack
- 深度估计：`yolo26x-depth.pt`（额外下载）

---

## 测试清单

### 路线A测试
- [ ] 单应矩阵标定工具可用
- [ ] 标定文件正确加载
- [ ] 坐标转换精度符合预期（可视化检查）

### 路线B测试
- [ ] 深度模型正确加载
- [ ] 深度图可视化正常
- [ ] 反投影坐标合理（可视化检查）

### 集成测试
- [ ] 配置切换正确生效
- [ ] 两条路线均可完整运行
- [ ] 输出格式统一

---

## 总结

本方案设计两条独立的坐标变换路线，满足不同使用场景：

- **路线A（几何标定）**：高精度，标准方法，适合正式研究
- **路线B（深度估计）**：便捷性，辅助工具，适合快速分析

通过配置文件统一接口，用户根据需求选择，模块不做性能对比实验。
