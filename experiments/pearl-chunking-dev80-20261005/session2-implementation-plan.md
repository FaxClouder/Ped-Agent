# Session 2 接口实施计划

*仅 E0 工程准备与真实冒烟 · status: plan · 2026-10-05*

Session 1 delivery SHA 为 d90df1326c95c0098bedc7a96a1d758ad76fb23a39e90d76c9a31ab11f703341；36 个交付文件现场复核无漂移。保持 Session 1 文件不变，新文件实现实验内接口，不修改 Contracts 或历史评分器。使用 codex/pearl-chunking-session2 分支保留当前工作区研究依赖。

1. `source_view.py`, `table_snapshot.py`, `parent_graph.py`, `chunkers.py`：先固定可逆 span 数据接口、公共表格规则、连续句切片与父图。接口 `build_source_view(doc, view_config=None)`, `freeze_tables(views,counter,table_config=None)`, `build_parent_graph(view,counter,max_tokens=1536)`, `chunk(view,C,L,counter,semantic_manifest=None)`。所有对象使用 JSON 字典；span 字段 doc_id/source_version/element_id/start/end，文本读取只从原文。
2. `assemble.py`, `support.py`：公共来源区间合并和 P0/P1/P2；支持评价只在离线侧读取 Gold，运行时只读 query。共同映射保留未知，需真实来源审查才给支持判定。接口 `assemble(ranking,views,parents,P,B,panel,counter)`；保存 raw/expanded/dedup/final 和实际序列化。
3. `smoke.py`：固定 seed=20261005、每类两题、至多八题，在成绩前保存样本。新增独立小规模索引，复用真实 Models/capture_forward_inputs 和既有 BM25/RRF/重排算法，记录实际模型输入与 SHA。C4 阈值只来自无标签相邻句；不建 E1 全量网格。
4. 接口反例测试、既有 chunk/token 和 Evidence 测试、实际 CLI help、成功命令与返回码保存。独立审查和保存后复算核验通过才允许 E0_complete；若有实质阻塞保持 failed/blocked 及准确范围。
5. 新 run 中保留所有失败、hash 核验、命令、交付与唯一下一入口。生成授权缺失时 skipped；不调用远程生成/裁判，不运行 E1，不按冒烟成绩选策略。

验收反例与科学规则以 [实施任务](implementation-tasks.md)、[协议](protocol.md) 和 [Session 计划](../../docs/superpowers/plans/2026-10-05-pearl-chunking-sessions.md) 为准。新增文件必须先有失败反例再实现；固定数值参考和真实模型验证分开报告。
