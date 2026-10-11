# 知识侧 RAG 整理新 Session 交接说明

*执行计划的启动说明；只做组织层整理，正文修改留待后续 · status: plan · 2026-10-10*

## 启动方式

在完整本地工作目录 `E:\F_Workspace\F-Agent-Paper` 打开新 session，将下方指令交给执行者。不要自动创建新会话或迁入缺少本地研究资产的 checkout。

## 可直接复制的指令

```text
请执行 docs/superpowers/plans/2026-10-10-rag-asset-organization.md。

本次任务是知识侧 RAG 文档与研究资产的组织整理，不涉及 Agent-Core、Agent 编排、Agent-Harness、动态控制器或视频分析。

先按 AGENTS.md 阅读仓库入口、架构、Knowledge-Base README、docs 导航和评测规范，然后按计划完成：
1. 只读盘点并保存基线；
2. 建立 docs/rag/asset-inventory.csv 和 organization-report.md；
3. 建立 docs/rag/README.md，给 docs/README.md 增加一个入口；
4. 建立 docs/rag/follow-up-backlog.md；
5. 在独立 outputs/rag-asset-organization-<日期>-<编号>/ 中交付验证、哈希清单与 handoff.md。

本阶段不移动、删除、重命名或合并既有文件，不修改既有技术文档、实验报告、历史计划的正文或状态标签。发现过期/冲突说明，只在新导航和后续清单中指出并附依据。正文内部调整等本轮完成后再讨论。

保留已有 tracked、untracked、ignored 资产。不得重建索引、跑实验、调用外部 API、改题/答案/标签、冻结 Gold、修改评测登记表，或读取封存题目正文。不要 commit/push，不要自动清理仓库。

特别核对 outputs/pearl-question-redesign-pilot-20261008-01/ 下的 Phase 2 和 question-set-consolidation-20261010-01/，不要把最新候选工作误当已冻结 Gold；Past/child-parent-Sum/ 是旧切块研究的复制归档，原件仍在原位置。

按计划完成结构、链接、清单和源文件保全验证。交付实际路径、覆盖数量、未决问题与核验结果，然后停止，不进入文档正文修订阶段。
```

## 接收成果时检查什么

- 总入口是否能找到设计、代码、语料、题集、实验与历史资料。
- 资产表是否区分原件、副本、快照、候选和正式登记资产。
- 最新问题集与已终止切块研究是否分别归属，未知项是否如实保留。
- 原件是否保留，变更是否仅限计划允许的组织文件与导航条目。
- 下一轮正文问题是否集中在 follow-up-backlog，而不是提前改写。

完整步骤和验收条件见[执行计划](2026-10-10-rag-asset-organization.md)。本交接不授权执行后续清单中的正文修订或迁移候选。
