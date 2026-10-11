# 知识侧 RAG 文档与研究资产导航

*知识侧 RAG 组织整理 · status: current · 2026-10-10*

本入口更新于2026-10-10，仅组织知识侧资料。原件保留在原位置；不涉及 Agent-Core、Agent编排、Agent-Harness、动态控制器或视频专项。mixed综合文档只使用其RAG相关内容。完整范围和口径见[组织报告](organization-report.md)，逐文件/包关系见[资产清单](asset-inventory.csv)，待讨论项见[后续清单](follow-up-backlog.md)。

## 主线设计

| 首选入口/来源 | 用途 | 状态与限定 |
| --- | --- | --- |
| [开发路线](../rag-development-roadmap.md) | PRISMA参考筛选、Adobe产物组织、父子切块与双路索引约定 | plan；方向已确认，参数与实现验证待完成 |
| [设计规范](../rag-design-spec.md) | 当前设计整理和待决事项 | current设计；原文为2026-10-07观察，6B状态差异见后续清单 |
| [项目架构](../project-architecture.md) | 当前知识职责和依赖方向 | current；综合文档，仅RAG用途 |
| [研究验收标准](../research-review-standard.md) | 已完成Agent评价的验收和provenance规则 | current；不新增默认人工门槛 |

## 实际实现与配置

| 首选入口/来源 | 用途 | 状态与限定 |
| --- | --- | --- |
| [Knowledge-Base README](../../Knowledge-Base/README.md)、[源码](../../Knowledge-Base/src/ped_knowledge/) | 当前知识实现与本地调用方式 | current；默认Adobe、parent-child-v1；本轮不执行API |
| [BGE-M3配置说明](../../Knowledge-Base/config/embeddings/bge-m3/README.md) | 固定模型/tokenizer参数和复现入口 | current配置；本轮未运行模型 |
| [英文词法配置](../../Knowledge-Base/config/retrieval/lexical-english-v1.yaml) | FTS5/BM25词法版本 | current；不等同历史实验所有配置 |
| [V2配置](../../Knowledge-Base/config/retrieval/chunking-v2.yaml) | 已实现候选切块 | candidate，尚未替换模块默认 |

## 语料资产

| 首选入口/来源 | 用途 | 状态与限定 |
| --- | --- | --- |
| [数据根说明](../../memPed/README.md)、[收集规范](../../memPed/knowledge/collection_standard.md) | 领域文献与法规标准的资产边界 | current；源码与研究数据分离 |
| [原文Vault](../../memPed/knowledge/literature/files/)、[来源记录](../../memPed/knowledge/literature/records/) | PDF与筛选/登记出处 | 本地资产；只读盘点 |
| [派生资产](../../memPed/knowledge/derived/)、[Catalog](../../memPed/knowledge/knowledge.sqlite3) | Adobe ZIP、规范文档、chunk、Catalog | 本地资产；数据库未打开，内容质量未验收 |
| [106篇索引实验](../../experiments/pearl-index-106-adobe-20260929/README.md)、[冻结运行索引](../../outputs/pearl-index-106-adobe-20260929-01/) | 既有实验语料和索引身份 | 冻结实验；不代表与当前Catalog指纹一致 |
| [两篇移除记录](../../memPed/knowledge/reports/pymupdf-two-papers-removal-2026-10-08.md) | 后续检索前的指纹检查要求 | current记录；本轮没有重建/激活索引 |

## 题集与候选来源链

2026-10-10 后续正文维护：新增 [Gold v1.2 统一规范](gold-question-standard-v1.2.md)与[文档处置清单](gold-document-disposition-2026-10-10.md)。以下旧集中整理和补题文件是阶段快照；最新接收为[云端修订包](../../outputs/pearl-question-redesign-pilot-20261008-01/cloud-revision-import-20261010-01/README.md)，39 ACCEPT、D-004 未决，非盲、未冻结。原资产清单与组织报告保留交付时点，未静默更新其哈希绑定内容。

| 首选入口/来源 | 用途 | 状态与限定 |
| --- | --- | --- |
| [评测规范](../../experiments/EVALUATION-STANDARD.md)、[登记表](../../experiments/EVALUATION-REGISTRY.yaml) | qs-dev80-r02 / qs-eval200-r01及参考身份 | 现行登记；封存正文不读取；不得以新候选替代 |
| [规范副本](../../memPed/knowledge/gold/pearl-adobe106/README.md) | 冻结输入规范路径与原件来源 | current副本，outputs/paper原件继续保留 |
| [最初候选报告](../../outputs/pearl-question-redesign-pilot-20261008-01/candidate_report.md)、[v2报告](../../outputs/pearl-question-redesign-pilot-20261008-01/candidate_report_v2.md) | 40题问法候选初版与修订 | 候选历史版本均保留 |
| [Phase2问法v3说明](../../outputs/pearl-question-redesign-pilot-20261008-01/phase2-evidence-review-20261009-01/question_revision_notes_v3.md) | v3问法身份与revision来源 | 候选；仅导航版本说明，不复制题目正文 |
| [单Agent重跑交接](../../outputs/pearl-question-redesign-pilot-20261008-01/phase2-evidence-review-20261009-01/single-agent-rerun-01/handoff.md) | Phase2答案/证据v1及自复核来源 | 38题自复核、2题历史沿用；不是独立盲审 |
| [集中整理交接](../../outputs/pearl-question-redesign-pilot-20261008-01/question-set-consolidation-20261010-01/handoff.md) | 后续答案/QA v2与处置记录 | 38可用（10/10/9/9），C-007/D-004未决；问法仍v3，没有冻结Gold |
| [50题补足安排](../../outputs/pearl-question-redesign-pilot-20261008-01/question-set-consolidation-20261010-01/dev50_completion_plan.md) | 缺额、依赖与来源互斥核查 | plan；未生成新增题或正式200题 |

## 既有评价实验

| 首选入口/来源 | 用途 | 状态与限定 |
| --- | --- | --- |
| [PEARL框架](../../paper/pearl-framework/README.md)、[Layer1](../../paper/pearl-framework/layer-1-retrieval/README.md) | 指标和评价对象 | 评价协议，不决定模块默认；综合文档不拓展Layer5 |
| [Layer2](../../experiments/pearl-evidence-dev80-20261004/README.md) | 上下文/完整性开发评价 | 已有阶段交付；配置由该实验定义 |
| [Layer3](../../experiments/pearl-answer-dev80-20261004/README.md)、[Layer4](../../experiments/pearl-layer4-dev80-20261004/README.md) | 知识侧答案与引用/可靠性评价入口 | 既有开发评价；本轮不改编排实现或复跑 |
| [200题评价入口](../../experiments/pearl-retrieval-eval200-20261003/README.md) | 独立检索评价的公开说明 | 当前登记已有交付；本轮不读取封存题集内容 |
| [Layer6效率](../../paper/pearl-framework/layer-6-efficiency/README.md) | 知识侧token/成本评价的预留入口 | plan；仅知识成本用途 |

## 方法调研与历史

| 首选入口/来源 | 用途 | 状态与限定 |
| --- | --- | --- |
| [RAG方法调研](../../paper/RAG_Report/README.md) | 报告、论文卡、指标和公开PDF | current资料包；非模型复现实验 |
| [切块研究归档](../../Past/child-parent-Sum/README.md) | 终止记录、复制摘要与原件索引 | historical；2026-10-08终止，6B未完成；Past不是唯一原件 |
| [6B历史原件](../../paper/pearl-6b-judge-workpackage/README.md) | 工作安排及已导入标签的来源 | historical；保留阶段身份，不表示最终评分完成 |
| [旧Gold v5](../../memPed/knowledge/gold/2026-09-23-rebuild/README.md)、[failed说明](../../failed/README.md) | PEARL前题集与作废评分出处 | historical；不进入现行PEARL输入/分母 |
| [2026-10-07审计](../rag-asset-audit-2026-10-07.md) | 旧盘点和整理的时点证据 | 快照；数量和“当前”只指原时点 |

本轮交付与验证见[handoff](../../outputs/rag-asset-organization-20261010-01/handoff.md)和[验证报告](../../outputs/rag-asset-organization-20261010-01/validation/report.md)。正文调整、重复合并和迁移候选只记录到后续清单；本阶段已到停止边界。
