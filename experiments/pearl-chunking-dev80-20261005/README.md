# PEARL 切片开发研究：当前入口

*E4 前缀消融与最终冻结交接（Session 5B）；研究已于 2026-10-08 终止 · status: historical · 2026-10-08*

**2026-10-08 起终止**：用户决定停止切块与父子块优化，6B 评价一并停止（原因：问题集题干普遍点名作者或研究，指向性太强）。已完成内容、终止原因与资产索引见 [Past/child-parent-Sum](../../Past/child-parent-Sum/README.md)；本目录与各运行目录原样保留，不再推进。

当前已完成 E0、E1 全矩阵与 r06/r07 补审候选冻结，以及 r07 配对统计、差异案例和旧评分入口兼容核验。
候选 `C2-L384-O0-M0`、`C3-L256-O0-M0` 是开发入选，不代表显著优胜。
E3 已使用相同冻结 R4 完成 P0/P1/P2 × 4K/8K，并分别保存 Top100 主面板与 Top10 诊断。实际文本补审与条件排除统一形成 r10 评分；共同 E2 恢复策略冻结为 P0，依据 C2 主面板及可比组装成本，保留 unknown 与 B0/C3 局部选择限制（[E3 报告](session4-e3-2026-10-06.md)）。
E2 已完成 C2-L384/C3-L256 × O0/O10/O20（P0，O10/O20 真实建库与检索）、r11 补审与统一重评及独立核验：C2-L384 重叠选择冻结为 O0；C3-L256 保持 pending_review（O0 仅为现有身份）。当前说明见 [E2 报告](session5-e2-2026-10-06.md)。
E4 已完成 C2-L384-O0 × M0/M1（M1 原文标题／章节前缀独立建库并真实检索）、r12 补审与统一重评及独立核验：M0/M1 保持 pending_review（M0 为现有身份，不宣称最优）。最终冻结 `C2-L384-O0-M0`、`C3-L256-O0-M0`、`B0-regex320-overlap48-M0`（P0、4K）及 E5 调用计划与评价版本，见 [E4 报告](session5b-e4-2026-10-06.md)；下一会话唯一入口为 [E4 handoff](../../outputs/pearl-chunking-dev80-20261006-13/handoff.md)。E5 未启动；答案生成 0。[E1 收尾报告](session3-closeout-2026-10-06.md)与会话 A 交接保留阶段身份。
6A 已完成 720 次真实生成（deepseek-flash，0 重试）并核验。6B 评价未完成：API 裁判 deepseek-v4-pro 校准未通过并 blocked（[6B a2 交接](../../outputs/pearl-chunking-dev80-20261006-15/handoff.md)）；用户改由 ChatGPT 代理评审，工作包与失误、偏差记录见 [paper/pearl-6b-judge-workpackage](../../paper/pearl-6b-judge-workpackage/README.md)，校准 r02 已通过；研究主审第 1 期已完成，引用部分将重做（准备 T3c 已完成：[片段边界与 r03 设计](../../paper/pearl-6b-judge-workpackage/citation-redo-r03.md)，程序 `e6b_fragments.py`），后续见 [6B 工作安排](../../paper/pearl-6b-judge-workpackage/6b-work-plan.md)。

以下为 Session 1 的冻结资产与历史交付导航；其中 E0 待完成是当时状态，不是当前状态。

| 文件 | 内容 |
| --- | --- |
| [研究依据](research-rationale.md) | 原始来源已读范围、操作定义、反例、成本、未复现差异和五个RQ |
| [资产审计](inventory.md) | H0/B0、真实参数、Gold迁移候选及未决 |
| [公共协议](protocol.md) | 科学规则、三值、预算、面板、筛选、缓存、失败和授权 |
| [来源登记](source_registry.json) | 106来源真实路径/SHA与研究原始来源版本 |
| [解析清单](resolved_manifest.yaml) | 已解析值、null缺口、正式运行阻止范围 |
| [适配任务](implementation-tasks.md) | Session 2逐文件复用、拟建接口、固定反例与真实CLI确认 |
| [交接](../../outputs/pearl-chunking-dev80-20261005-02/handoff.md) | 本阶段实际检查与唯一下一入口 |
| [输出清单](../../outputs/pearl-chunking-dev80-20261005-02/delivery-manifest.json) | 冻结SHA、数量和检查记录 |

audit_session1.py为本阶段只读辅助脚本，package_session1.py只打包已经观察的事实，均不是E0实验运行入口。已执行audit命令的-01失败（element_ids JSON字符串处理）保留，新-02成功；不覆盖现有结果重跑。下一阶段只能按实施任务适配后核验新CLI，不能把拟建接口说成已实现。

执行范围来自[Session计划](../../docs/superpowers/plans/2026-10-05-pearl-chunking-sessions.md)及[策略说明](../../docs/superpowers/specs/2026-10-05-pearl-chunking-research-design.md)。协议后续变更须新增版本并说明影响，本阶段完成后停止。
