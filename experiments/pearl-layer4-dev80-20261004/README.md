# PEARL Layer 4 Grounding 与 Reliability 开发评价

*冻结Layer 3全部400回答与实际context的离线评价 · status: current · 2026-10-04*

执行[阶段A–D交接计划](../../docs/superpowers/plans/2026-10-04-pearl-layer4-next-session.md)。不重复Retrieval/Evidence/Answer，不新增200题，不执行Layer5/6，不要求人工审查，不commit/push/merge。

## 当前进度

阶段A–D已完成。最终400回答复用冻结Layer 3记录；C100整行精确复用，D300完成评审，固定60独立次审。最终可回答性337 complete、61 partial、2 none；5530原子声明与5676引用对通过独立复算及1600任务链核验。中文结果见[完整分析](grounding-reliability-analysis-2026-10-04.md)，阶段证据见[阶段A](stage-A-report.md)、[阶段B](stage-B-report.md)、[阶段C](stage-C-report.md)、[阶段D](stage-D-report.md)，过程限制见[执行记录](execution-ledger.md)。正式Agent开发评价，human_verified=false；交付止于Layer 4。

## 实验入口

|文件|职责|
|---|---|
|[prepare.py](prepare.py)|旧资产保护、400真实记录绑定、版本化输入|
|[extract.py](extract.py)|精确位置的待语义复核候选，不赋真值|
|[review.py](review.py)|四任务白名单及评估侧匿名映射|
|[score.py](score.py)|严格分母、宏微平均、NA/unknown界和拒答表|
|[verify.py](verify.py)|独立数值复算与保存文件/引用/区间/复用/评审链核验|
|[bootstrap.py](bootstrap.py)|五项预设描述性差、分层intent bootstrap10000|
|[assemble_d400_r01.py](assemble_d400_r01.py)、[verify_d400_r01.py](verify_d400_r01.py)|D固定60次审范围及C100整行精确复用的组装与独立核验|
|[export_d_source_packets_r01.py](export_d_source_packets_r01.py)|显式选择已审原子，隔离生成context与Grounding标签后导出源文事实包，不赋标签|
|[cross_layer.py](cross_layer.py)|旧L2/L3与新Layer4分任务诊断；不把旧Strict失败当作事实错误|
|[compare_calibration.py](compare_calibration.py)|独立合成expected与实际judge比较|
|[protocol.md](protocol.md)、[rubrics.md](rubrics.md)、[judge-prompt-r01.md](judge-prompt-r01.md)|评价口径及prompt，引用归属r02补充在输出目录保存|

本次新增产物见[输出目录](../../outputs/pearl-layer4-dev80-20261004-01/)。科学输入只读，原100C回答精确复用；事实包由本地源文独立构建，未知与单位损坏不擅自修补。实际评审角色因平台线程总数限制复用，逐包记录先前暴露，不称完全双盲或独立模型。

最终科学入口为输出目录reviewed-r03.json、scores-r03.json与score-bindings-r03.json；r01/r02是保留的QA快照。protocol/rubrics及pre-C冻结文件保留当时状态文字，不追改冻结协议；当前执行完成状态以本入口、阶段报告和中文分析为准。
