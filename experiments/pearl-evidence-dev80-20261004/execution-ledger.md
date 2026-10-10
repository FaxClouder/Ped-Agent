# PEARL Evidence 分阶段执行记录

*Layer 2 实际执行进度与证据入口 · status: current · 2026-10-04*

用户授权执行全部 Evidence 阶段，完成后停止；不重复 Retrieval，不运行新的 200 题 Evidence，不执行 Layer 3/4，不提交、推送或清理既有工作区。正式 Agent 评估遵循现行研究审查标准；`human_verified=false` 如实记录。

| 阶段 | 状态 | 完成证据 |
| --- | --- | --- |
| A 盘点、核验与冻结 | 完成 | protocol.md；assembly-reuse-inventory.json；stage20/input-manifest.json；绑定原R4首遍、6,433 child／2,830 parent、r02与tokenizer |
| B 合成验证 | 完成 | 54项定向测试通过；synthetic保存及重读；assembly-test-evidence.json保留红绿与首次路径错误修复 |
| C 20题诊断 | 完成 | 四类各5题；80上下文、100实际盲审；逐题、题型、配对、步骤和bootstrap独立复算一致；见stage20-analysis.md |
| D 80题评估 | 完成 | 320最终上下文、398实际盲包、1,280步骤绑定；逐题/总体/题型/配对/bootstrap独立复算；见evidence-analysis-2026-10-04.md与delivery-manifest-r01.json |

开始时工作区已有大量已修改及未跟踪文件，当前为 `main`（ahead 1）。本轮在用户指定工作目录新增独立实验及输出，保留原工作区内容；不将已有修改归入本轮成果。

阶段 A/B 的主代理复查命令：`PYTHONPATH=Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src`，`.venv/Scripts/python -m pytest experiments/pearl-evidence-dev80-20261004 -q`，实测 **54 passed in 0.75s**。初期测试运行保留新增功能缺失的红测；此处只以最后全绿结果验收。输入保护检查覆盖1,154个既有文件；stage20运行前后全部SHA不变。200个关联child完整包含于parent，fallback=0；80份最终上下文中40份发生预算截断。结构包含关系不能替代实际语义审查。

计划入口：[下一会话任务说明](../../docs/superpowers/plans/2026-10-04-pearl-evidence-next-session.md)。现行标准：[研究评估与审查验收标准](../../docs/research-review-standard.md)。本记录仅描述实测进度；没有落盘核验的条目不记为完成。

阶段C完成后，阶段D按同一协议组装并保存完整80题；800个query-child关联全部通过完整包含检查，fallback=0，164/320最终上下文发生预算截断。100个完整packet与阶段C逐字段精确相同，复用既有实际记录；其余298个不同packet均由独立语义角色实际全文阅读并保存，没有把未读记录记为unknown。20个新增批次已全部完成；所有审查修订和独立裁决保留原件与版本选择映射。

全量评分实测CGC为C0-4096 63/80、C0-8192 64/80、C1-4096 62/80、C1-8192 71/80，unknown=0。独立评分、统计、bootstrap与步骤单元指标重算均一致；320个上下文的去重前后支持标签一致，未发现去重损失。最终核心定向测试94 passed in 3.29s，独立代码审查Critical/Important/Minor均为0。未改变跨模块契约，无全仓或生成模型运行声明。

汇总辅助脚本首次因阶段C复用文件路径少写batches层级而在输出创建前失败；核对实际冻结清单后修正，失败记录保留。完成后更新当前文档并另存新版provenance审计，早期审计保持历史快照。交付[中文分析](evidence-analysis-2026-10-04.md)后停止于Layer 2；没有新200题Evidence、Layer 3/4或Git提交/推送/清理。
