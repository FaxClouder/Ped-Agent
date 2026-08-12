# Trajectory extraction

轨迹检测与提取板块负责把原始视频转换成像素轨迹。

内部职责包括视频预检、目标检测、多目标跟踪、类别判定、接触点提取、像素轨迹质量检查和人工复核。
本板块不执行世界坐标投影、轨迹平滑或流动指标分析。

当前对应实现主要位于 `vision/adapters.py`、`runner.py`、`inference.py`、
`contact_points.py` 和 `review.py`，后续将在保持兼容的前提下迁入本目录。
