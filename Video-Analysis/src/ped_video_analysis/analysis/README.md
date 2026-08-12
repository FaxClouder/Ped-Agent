# Trajectory analysis

轨迹分析板块独立接收满足分析契约的世界坐标轨迹，不要求轨迹由检测或投影板块产生。

内部职责包括分析输入预检、个体运动指标、流量、密度、速度场、OD、区域停留、基本图、
交互代理指标、图表和导出。缺少某项场景信息时，只跳过依赖该信息的指标，并在结果中记录原因。

现有 `vision_pipeline.py`、`pedpy_adapter.py`、`vision_visualizer.py` 和 `vision_exports.py`
属于本板块的当前实现，后续再按能力拆分子目录。
