# 知识侧 RAG 资产组织报告

*知识侧 RAG 组织整理 · status: current · 2026-10-10*

本轮执行[计划](../superpowers/plans/2026-10-10-rag-asset-organization.md)，只新增组织层资料，并向[总导航](../README.md)增加一个入口。运行核验包见[交接](../../outputs/rag-asset-organization-20261010-01/handoff.md)。未移动、删除、改名、合并任何原件；未改问题、答案、标签、登记身份或既有设计/实验正文。

## 覆盖口径

| 项 | 本轮计数 |
| --- | ---: |
| 枚举文件（含 ignored，含封存文件元数据） | 42706 |
| 枚举 Markdown | 679 |
| 逐文件纳入说明文档 | 601 |
| 包级资产（目录；含分层子包） | 159 |
| CSV 总行数 | 825 |
| mixed 资产 | 16 |
| lifecycle=unknown | 51 |
| authority_role=unknown | 65 |
| 基线 SHA-256 文件 | 2760 |

枚举根、初始 Git 状态、总导航原件备份见[基线范围](../../outputs/rag-asset-organization-20261010-01/baseline/scope.md)和[补充](../../outputs/rag-asset-organization-20261010-01/baseline/supplement.md)。最终逐文件元数据见[files-before.csv](../../outputs/rag-asset-organization-20261010-01/baseline/files-before.csv)，每份 Markdown 的纳入/排除/包内收纳理由见[document-coverage.csv](../../outputs/rag-asset-organization-20261010-01/baseline/document-coverage.csv)：{"included": 601, "excluded": 18, "package_only": 60}。包统计包含子包，不能相加得全仓总量。CSV 为逐说明文档、逐版本身份和逐包登记，不按 chunk、packet 或逐题记录展开。

大型 PDF、数据库、模型、向量、派生数据只统计数量/大小、定位已有 manifest；小型说明、配置、脚本、清单与登记冻结输入计算哈希。登记表题集/参考核对见[registry-hashes.csv](../../outputs/rag-asset-organization-20261010-01/validation/registry-hashes.csv)，仅二进制散列，不读取封存题干、答案、证据。哈希一致不等于语义复核或评价效果复现。

## 权威与来源关系

| 层次 | 权威或优先入口 | 本轮解释 |
| --- | --- | --- |
| 当前实现 | [Knowledge-Base README](../../Knowledge-Base/README.md)、[源码](../../Knowledge-Base/src/ped_knowledge/)、[架构](../project-architecture.md) | 原件；模块 README 说明默认/候选，代码决定行为；不重新运行验证 |
| 当前设计与后续主线 | [设计规范](../rag-design-spec.md)、[路线](../rag-development-roadmap.md) | 前者当前设计汇总，后者 plan；综合文档只纳入知识侧用途 |
| 评价身份 | [规范](../../experiments/EVALUATION-STANDARD.md)、[登记表](../../experiments/EVALUATION-REGISTRY.yaml) | 身份/路径/冻结 SHA 为依据；登记原件不改 |
| 规范 Gold | [pearl-adobe106](../../memPed/knowledge/gold/pearl-adobe106/README.md) | 规范副本；原 outputs/paper 文件被 manifest/脚本绑定，保持来源链 |
| 新候选 | [集中整理交接](../../outputs/pearl-question-redesign-pilot-20261008-01/question-set-consolidation-20261010-01/handoff.md) | 38可用、2未决；问法v3，答案/QA v2；没有 candidates_v4，没有冻结Gold |
| 终止研究 | [切块归档](../../Past/child-parent-Sum/README.md) | 2026-10-08终止；Past为摘要副本和索引，原件仍在 experiments/paper/outputs |
| 调研 | [RAG_Report](../../paper/RAG_Report/README.md) | 方法调研和公开PDF资料，不证明模型复现实验 |

CSV 的 related_assets 只使用清单内 ID，表示归属/来源/证据关系，不表示采用或可删除。canonical_or_source_path 保存明确来源；未核定的权威保留 unknown。归档摘要的字节相同结论来自本轮基线 SHA；内容相似没有被当作可删除重复。

## 观察与未覆盖项

- [设计规范](../rag-design-spec.md)第4.2/7节的“6B评价进行中”、[登记表](../../experiments/EVALUATION-REGISTRY.yaml)的 in_progress_6B 与终止说明存在时点差异；仅登记到[后续清单](follow-up-backlog.md)。
- [docs导航](../README.md)称旧V1/V2索引已迁failed，但本轮在outputs仍可见；位置判断来自基线，不用旧快照代替现状。
- [旧审计](../rag-asset-audit-2026-10-07.md)为2026-10-07快照；题集规范副本、候选Phase2与集中整理的后续事实另行导航，不追改快照。
- 未专项读取/整理 Agent、Agent-Harness、动态控制器、工具调度、视频与Layer5；Layer6只登记知识侧成本入口。Contracts仅作既有契约引用，不重组。
- 包内逐题、提示/评审包和封存运行说明仅收纳到上级包，不逐篇内容分析；基线覆盖记录给出理由。源码只枚举/哈希及确认入口，没有全量代码审查。
- 不遍历 .venv、缓存或凭据；非RAG的Git整合备份、figures等outputs目录不纳入。本地资产可见不代表远端或新worktree可见；不核验远端，不复制数据库/PDF/权重。
- 无法证明完成/来源的运行包保留unknown，不以编号、latest/final命名择权威。本文不评价历史切块效果，不作新技术采纳决策。

本轮验证仅覆盖组织结构、路径/关联、哈希保全和允许的导航增量；未运行模型/索引/实验测试，未验证检索效果。完成交接后停止，正文修订和迁移另行决定。

三个空历史运行目录已单列为包，不省略、不删除，不认定为已执行；outputs根部命令/日志亦独立登记其保全边界。

最终复查将failed/outputs-void-scores下41个历史运行逐包登记，并将根部scripts作为reference包补充；补充哈希起点和范围见[根部脚本说明](../../outputs/rag-asset-organization-20261010-01/baseline/root-scripts-supplement.md)。每个实验关联其已见协议/报告、原README中明确引用的输入/运行包；未登记的实验不补造编号。
