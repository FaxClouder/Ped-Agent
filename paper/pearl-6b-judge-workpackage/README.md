# PEARL 6B 外部裁判工作包

*E5 答案评审改由 ChatGPT 代理完成的盲化工作包；校准 r02 已通过，研究主审第 1、2 期与引用重做已完成并导入；引用重做 F7 未达标；6B 已于 2026-10-08 终止 · status: historical · 2026-10-08*

本目录交给 ChatGPT（用户指定 sol6.1，medium）逐包评审。评审结果由 Claude 会话导入，并用冻结的程序按原阈值比对、评分。**只有程序判定校准通过，才会导出研究包。** 失误与偏差见 [incidents-and-deviations.md](incidents-and-deviations.md)；剩余任务的分工与顺序见 [6b-work-plan.md](6b-work-plan.md)；研究评审的依赖与期次见 [research-periods.md](research-periods.md)。

| 阶段 | 目录 | 包数 | 状态 |
| --- | --- | --- | --- |
| 校准 cgpt-r01 | `calibration/` | 200 | 已完成，**未通过**：只有 behavior 的 `unsupported_completion` 有定义歧义，其余指标全部满分。保留作记录，**不要再改动** |
| 校准 cgpt-r02 | `calibration-r02/` | 200（与 r01 相同；只有 behavior 规则末尾附了澄清条款 r02） | **已通过**：全部指标 1.0，哨兵 5/5、8/8（[门禁](../../outputs/pearl-chunking-dev80-20261007-16/calibration-gate-cgpt-r02.json)）。保留作记录，不要再改动 |
| 研究主审第 1 期 | `research-primary-1/` | 1,648（Layer 3 704、可回答性 240、有据性 704） | **已完成**，格式全部通过。有据性的**引用标签按上下文分化**，引用部分将重做；其余可用（[偏差 D3–D6](incidents-and-deviations.md)）。**不要再改动** |
| 研究主审第 2 期 | `research-primary-2/` | 1,402（行为 704、事实性 698） | **已完成并导入**（T5a，[导入记录](../../outputs/pearl-chunking-dev80-20261007-16/research/import-research-primary-2.json)）；有执行偏差 D11、D12、D15、D16。**不要再改动** |
| 引用重做校准复核 | `calibration-citation-r03/` | 40（有据性校准锚点，claims 固定，只评引用；规则末尾附输入格式说明 r03） | **T3d／T3e 已完成，F5 门禁通过**：40/40 有效、引用 36/36、8/8 哨兵。说明见 [calibration-citation-r03/README.md](calibration-citation-r03/README.md)；设计与比对方法见 [citation-redo-r03.md](citation-redo-r03.md) |
| 引用重做（研究） | [research-citation-r03/](research-citation-r03/README.md) | 704（绑定 720 格） | **已完成并导入**（T5a，[导入记录](../../outputs/pearl-chunking-dev80-20261007-16/research/import-research-citation-r03.json)）；**F7 未达标**（S2、S3；[判定](../../outputs/pearl-chunking-dev80-20261007-16/research/lane-audit-citation-r03-r01.json)，偏差 D13、D14），引用指标暂时阻断。**不要再改动** |
| 固定次审、分歧裁决 | 待导出 | 见计划 | 本轮未执行，顺序与启动语句见 [6b-work-plan.md](6b-work-plan.md) |

## 给裁判（ChatGPT）的操作说明

**6B 已终止**（[原因与归档](../../Past/child-parent-Sum/README.md)），不再有评审轮次。当前没有待评审的目录。`research-primary-2/` 与 `research-citation-r03/` 已评审并导入，只作记录。下一轮评审要等用户就 F7 补救方案和次审事实性 claims 作出决定，见 [6b-work-plan.md](6b-work-plan.md)。已完成的 `calibration/`、`calibration-r02/`、`research-primary-1/` 只作记录，**不要打开或改动**。

## 之后的流程（由 Claude 会话执行）

1. 校准（已完成）：`e6b_workpackage.py import --phase calibration-r02` 校验并导入回答，用冻结的 `score.py` 和 `compare_calibration.py` 按原阈值比对，结果为全部指标 1.0、哨兵全过。阈值没有因结果调整。
2. 研究期次：`e6b_workpackage.py export --phase research-primary-1` 已导出第 1 期，并在 `outputs/pearl-chunking-dev80-20261007-16/research/` 冻结了身份映射和固定次审抽样（早于任何研究标签）。第 1 期已由 `e6b_workpackage.py import --phase research-primary-1` 导入（T3a，记录在同一目录的 `import-research-primary-1.json`）。第 2 期已由 `export --phase research-primary-2` 导出（T3b，导出记录 `export-research-primary-2.json`，事实性绑定 `factuality-bindings-primary-2-r01.json`）。第 2 期已由 `import --phase research-primary-2` 导入（T5a，`import-research-primary-2.json`）。次审和裁决按 [6b-work-plan.md](6b-work-plan.md) 的 T5b–T8 进行；研究阶段沿用 r02 规则。
3. 引用重做（[偏差 D8](incidents-and-deviations.md)，[设计](citation-redo-r03.md)）：T3c 已用 `fragments-audit` 冻结片段边界，用 `citation-dryrun` 在内存中构建 704 个研究包，用 `export --phase calibration-citation-r03` 导出校准复核包并在评审前冻结比对方法。T3e 用 `import --phase calibration-citation-r03` 比对，只有门禁通过，`export --phase research-citation-r03` 才会运行。T5a 用 `import --phase research-citation-r03` 导入，用 `citation-f7` 按冻结标准判定，判定结果为未达标；`citation-f7-investigate` 写逐段排查记录。
4. 裁判身份按用户和 run-notes 记录，`human_verified=false`。裁判身份变化和 r02 澄清都登记为协议偏差。

导出和导入脚本：[e6b_workpackage.py](../../experiments/pearl-chunking-dev80-20261005/e6b_workpackage.py)。r02 与 API 校准计划 r01 相比，只有 40 个 behavior 包的消息不同（见 manifest 中的 `messages_changed_vs_api_plan_r01`），r01 工作包可以逐包复现。
