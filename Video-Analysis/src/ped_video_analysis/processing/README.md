# Trajectory processing

投影变换与轨迹优化板块负责形成分析就绪的世界坐标轨迹。

内部职责包括场景配置、相机标定、标定质量门禁、坐标投影、短缺口插值、异常点标记、
轨迹平滑和质量汇总。对于已经是世界坐标但尚未优化的轨迹，可以只执行优化部分。

当前对应实现主要位于 `vision/calibration.py`、`projection.py` 和 `postprocessing.py`，
后续将在保持兼容的前提下迁入本目录。
