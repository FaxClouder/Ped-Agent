# PedRAGent 文档导航

*维护文档与阶段交付入口 · status: current*

## 当前入口

- [Gold 问题设计与质量控制 v1.2](rag/gold-question-standard-v1.2.md)：106 篇语料、50＋200 新题目标、任务分类、证据/行为要求、审核和冻结边界；[相关文档处置清单](rag/gold-document-disposition-2026-10-10.md)列出合并、更新与删除候选（current；规范已修订，题集未冻结；2026-10-10）。

- [新版 40 题云端修订本地接收](../outputs/pearl-question-redesign-pilot-20261008-01/cloud-revision-import-20261010-01/README.md)：用户提供的最新 Excel/JSON 原件、无损分表导出与版本核对；39 ACCEPT、D-004 未决，非盲、非人工、未冻结 Gold；旧本地 v2 保留（current；接收记录；2026-10-10）。

- [知识侧 RAG 文档与研究资产总入口](rag/README.md)：设计、实现、语料、登记题集与新候选、评价和历史资料的统一导航；清单与保全核验已交付，原件保留，正文修订见后续清单（current；2026-10-10）。

- [知识侧 RAG 文档与资产整理计划](superpowers/plans/2026-10-10-rag-asset-organization.md)、[新 Session 交接说明](superpowers/plans/2026-10-10-rag-asset-organization-handoff.md)：排除 Agent/Core/Harness；先完成清单与统一导航，原件不移动，正文调整留待后续（plan；2026-10-10）。

- [RAG 开发主线与讨论记录](rag-development-roadmap.md)：PRISMA 筛选、Adobe 产物组织、父子切块实验规划、BM25／BGE-M3 建库约定及待办；Offline 总体设计已确认，参数与实现验证待完成；不评价历史切块结果（plan；2026-10-08）。

- **[评测问题集与实验规范](../experiments/EVALUATION-STANDARD.md)**、[登记表](../experiments/EVALUATION-REGISTRY.yaml)：问题集身份、规范存放位置（`memPed/knowledge/gold/pearl-adobe106/`）、封存评估集访问规则、实验设置规范与扩充计划；新建或使用问题集、启动评测实验前必读（current；扩充计划为 plan；2026-10-07）。

- [RAG 设计规范](rag-design-spec.md)：RAG 当前设计整理：文档优先级、系统流程与 PEARL 评价实验的关系（PEARL 只作评价，是否绑定待评估）、各环节当前设计与观察、版本与溯源字段、设计变更流程和设计待决事项 D1–D13（current；2026-10-07）。

- [RAG 资产与一致性审计](rag-asset-audit-2026-10-07.md)：RAG/PEARL 文档与实验产物的逐目录分类（现行交付、谱系输入、PEARL 前历史、失败尝试、重复与空目录）、关键数字复核、文档不一致清单和待确认的整理方案（current；2026-10-07）。

- **[PEARL 切块与父子块研究归档](../Past/child-parent-Sum/README.md)**：切块研究（E0–E5 与 6B 评价）于 2026-10-08 终止；记录已完成的工作、主要结果、终止原因（问题集题干点名作者，指向性太强）、可复用资产，以及复制的摘要和全部原件的 SHA 索引；原件不移动（historical；2026-10-08）。

- [PEARL 切片当前入口](../experiments/pearl-chunking-dev80-20261005/README.md)、[E3 报告](../experiments/pearl-chunking-dev80-20261005/session4-e3-2026-10-06.md)、[E2 报告](../experiments/pearl-chunking-dev80-20261005/session5-e2-2026-10-06.md)、[E4 报告](../experiments/pearl-chunking-dev80-20261005/session5b-e4-2026-10-06.md)：E0、E1 候选冻结、E3 恢复/预算比较（共同恢复 P0）、E2 重叠消融与 E4 前缀消融完成；C2-L384 重叠冻结为 O0，C3-L256 保持 pending_review；M0/M1 pending_review（M0 为现有身份）；评分 r12 为 r11 严格扩展。最终冻结 C2-L384-O0-M0、C3-L256-O0-M0、B0（P0、4K）及 E5 调用计划；开发选择不等于显著优胜。6A 已完成 720 次生成（[6A 交接](../outputs/pearl-chunking-dev80-20261006-14/handoff.md)）；6B API 裁判校准未通过后改由外部代理评审，停止时的进度见 [6B 工作安排](../paper/pearl-6b-judge-workpackage/6b-work-plan.md)（historical；研究已于 2026-10-08 终止）。原 [E4 交接](../outputs/pearl-chunking-dev80-20261006-13/handoff.md)保留阶段身份。原 [E1 收尾报告](../experiments/pearl-chunking-dev80-20261005/session3-closeout-2026-10-06.md)、[资产审计](../experiments/pearl-chunking-dev80-20261005/inventory.md)、[公共协议](../experiments/pearl-chunking-dev80-20261005/protocol.md)及 [Session 2任务](../experiments/pearl-chunking-dev80-20261005/implementation-tasks.md)保留阶段身份。

- [PEARL 切片研究与策略说明](superpowers/specs/2026-10-05-pearl-chunking-research-design.md)、[分 session 实验与交接计划](superpowers/plans/2026-10-05-pearl-chunking-sessions.md)：C1–C4边界与长度、上下文恢复、重叠和原文前缀的受控比较；分6个session完成研究审计、适配冒烟、E1、E3、E2/E4及E5（2026-10-06修订：Session 5拆为5A E2与5B E4＋冻结，Session 6拆为6A生成与6B评价报告），包含启动语句和验收边界（plan；各阶段实际交付见对应run目录handoff）。

- [PEARL Layer 1至4结果汇总与架构问题分析](../paper/pearl-framework/reporting/layer1-4-results-and-architecture-review-2026-10-05.md)：200题检索评价与80题Evidence/Answer/Grounding开发结果分别汇总，说明跨文献取证、预算截断、关系整合、引用及缺口识别问题；正式Agent评价，统计范围与未知项分别保留（current；2026-10-05）。

- [Layer 4 下一会话执行说明](superpowers/plans/2026-10-04-pearl-layer4-next-session.md)：复用Layer 3冻结400回答与实际context，分别评价有据性、事实、引用和拒答；先冻结可回答性及事实依据，再做校准、20题诊断和80题完整评价；不重复生成、不要求人工审查，完成后停止Layer 4，不推进Layer 5/新增Layer 6或200题（plan；计划快照保留，2026-10-05阶段A–D执行结果见Layer 4中文分析）。

- [Layer 3 Answer 中文分析](../experiments/pearl-answer-dev80-20261004/answer-analysis-2026-10-04.md)、[实验入口](../experiments/pearl-answer-dev80-20261004/README.md)：阶段A–D完成；DeepSeek V4.1 Flash，80题×五臂400真实单元，C100精确复用、D新300；Strict60/58/57/61、oracle73（各N=80），400单元413绑定独立复算与60测试通过，正式Agent开发评价，human_verified=false；盲审角色复用限制及费用估算已披露；交付止于Layer 3（current）。

- [Layer 3 Answer 下一会话执行说明](superpowers/plans/2026-10-04-pearl-answer-next-session.md)：Evidence冻结后进入答案参考复核、judge校准、20题诊断及80题开发评价；四个实际context臂加独立完整参考context对照，真实模型预检前置；本文是未执行计划，完成Layer 3后停止，不推进Layer 4/5（plan）。

- [Layer 2 Evidence 中文分析](../experiments/pearl-evidence-dev80-20261004/evidence-analysis-2026-10-04.md)、[实验入口](../experiments/pearl-evidence-dev80-20261004/README.md)：阶段A–D完成；固定R4 Top-10，80题×四组320上下文、398实际盲包及1,280步骤绑定独立复算；CGC为63/64/62/71（各N=80），正式Agent开发评估，human_verified=false（current）。[原阶段计划](superpowers/plans/2026-10-04-pearl-evidence-next-session.md)保留，不追改计划快照；该交付止于Evidence，本次Layer 3结果见上方入口；未执行新的200题Evidence；Layer 4独立交付见上方入口。

- [研究评估与审查验收标准](research-review-standard.md)：2026-10-04 起，完成规定评估与验证的 Agent 评估默认作为正式项目内容；仅用户明确指定的环节要求人工审查。历史 `agent_reviewed_preliminary`、`human_verified=false` 字段保留，不单凭字段否定正式验收；现有 Retrieval 阶段 D 据此正式验收（current）。

- [200题固定评价分析](../experiments/pearl-retrieval-eval200-20261003/evaluation-analysis-2026-10-03.md)：阶段D三遍固定检索、200题共同支持映射、800单元与3,200前缀评分、48总体指标独立复算、预设配对／来源统计、失败／深层未知及实际成本；CEGR@10为116/118/126/139（N=200；current；agent_reviewed_preliminary，human_verified=false）。完整交付清单见分析所链本次输出目录。
- [完整发布入口](../experiments/pearl-retrieval-eval200-20261003/README.md)、[预注册](../experiments/pearl-retrieval-eval200-20261003/preregistration.md)、[阶段C发布报告](../experiments/pearl-retrieval-eval200-20261003/stage-C-public-report.md)：阶段C完整release、隔离query-only导出与独立真实启动门禁已通过；保留C结束时零次正式运行的冻结快照，后续真实评价见上述阶段D分析（current）。

- [`../experiments/pearl-retrieval-eval-entry-20261003/README.md`](../experiments/pearl-retrieval-eval-entry-20261003/README.md)：阶段 B 独立评估入口、合成 80/200、query-only 运行与 Gold 保管分离、动态评分及启动前 release 门禁；实际命令与验证边界（current；B结束时真实200题仍封存）。
- [`../experiments/pearl-retrieval-eval-entry-20261003/adaptation-analysis-2026-10-03.md`](../experiments/pearl-retrieval-eval-entry-20261003/adaptation-analysis-2026-10-03.md)：阶段 B 适配分析、合成验证证据、独立审查、旧入口兼容与保存核验，以及阶段 C/D 剩余门槛（current；非真实评价结果）。
- [`superpowers/plans/2026-10-03-pearl-retrieval-post-r02-next-session.md`](superpowers/plans/2026-10-03-pearl-retrieval-post-r02-next-session.md)：Gold r02 之后的原 B–D 执行要求、验收及封存边界；实际B/C/D证据与交付入口见上，原计划条目不追改（plan）。

- [`../experiments/pearl-retrieval-gold-revision-r02/README.md`](../experiments/pearl-retrieval-gold-revision-r02/README.md)：阶段 A 新 Gold、三题独立实际 child 复核、80×4 共同重算和独立验证；原输入及排名不变，A结束时200题仍封存（current；agent_reviewed_preliminary）。
- [`../experiments/pearl-retrieval-gold-revision-r02/development-gold-r02-analysis-2026-10-03.md`](../experiments/pearl-retrieval-gold-revision-r02/development-gold-r02-analysis-2026-10-03.md)：开发 Gold r02 修订分析；CEGR@10 为 47/49/51/58，逐题差异、统计、原文限制及 provenance（current；非正式评估）。
- [`superpowers/plans/2026-10-03-pearl-retrieval-next-session.md`](superpowers/plans/2026-10-03-pearl-retrieval-next-session.md)：原分阶段交接计划；原计划时完整发布／正式评价未执行的描述保留，后续实际A–D证据见当前入口（plan）。

- [`../experiments/pearl-dev-review-freeze-20261003/README.md`](../experiments/pearl-dev-review-freeze-20261003/README.md)：七道开发难例独立原文复核、三道重排退步追溯与四方法配置冻结的原阶段记录；三处提案后续采用见r02，当时200题入口与完整发布未完成，后续B–D见当前入口（current；阶段快照）。

- [`../experiments/pearl-retrieval-dev80-20261003/README.md`](../experiments/pearl-retrieval-dev80-20261003/README.md)：80 题开发 R1–R4 真实运行、独立实际 child 盲审、共同映射、320 单元计分及独立复算已完成；原开发复现入口（current；开发结束时200题封存未运行）。
- [`../experiments/pearl-retrieval-dev80-20261003/development-analysis-2026-10-03.md`](../experiments/pearl-retrieval-dev80-20261003/development-analysis-2026-10-03.md)：80 题开发初步主表、三项预设比较、来源依赖、失败与未知深度、真实时延、处理追溯及验证记录（current；Agent 复核，非正式评估）。

- [RAG 研究调研资料包](../paper/RAG_Report/README.md)：103 篇去重 RAG 方法与评价文献、48 篇核心 PDF（928 页）、变种／模块／前沿、16 项原论文实验设置与指标设计（current；后续实验建议为 plan，未执行模型复现）。

- [`../experiments/pearl-dataset-80-200-20261003/README.md`](../experiments/pearl-dataset-80-200-20261003/README.md)：106篇Adobe题集冻结记录，80道开发与200道独立评价题分开；原封存／只读身份保留，冻结记录时未运行，后续实际评价见阶段D分析（current；非人工Gold）。
- [`../experiments/pearl-index-106-adobe-20260929/README.md`](../experiments/pearl-index-106-adobe-20260929/README.md)：106 篇 Adobe-only 统一索引，以及新 Gold 上 8 题 R1–R4 的盲化支持核验与开发初步对照。
- [`../experiments/pearl-index-106-adobe-20260929/r1-r3-pilot-analysis-2026-09-29.md`](../experiments/pearl-index-106-adobe-20260929/r1-r3-pilot-analysis-2026-09-29.md)：同一 8 题 R1–R3 初步开发对照的逐题完整证据位置、候选截断和计分范围分析（current）。
- [`../experiments/pearl-index-106-adobe-20260929/r4-pilot-analysis-2026-09-29.md`](../experiments/pearl-index-106-adobe-20260929/r4-pilot-analysis-2026-09-29.md)：冻结 R3 Top-100 的 R4 本地重排、逐题收益与退步、四方法统一重算（current）。

- [`../paper/pearl-framework/datasets/retrieval-pilot/equivalent-evidence-r1-v4-2026-09-29.md`](../paper/pearl-framework/datasets/retrieval-pilot/equivalent-evidence-r1-v4-2026-09-29.md)：8 题开发试标的等价证据核定、Li running 条件修复及不改原排名的 R1 v4 重算（current；非正式对照）。

- [`../paper/PedRAGent/README.md`](../paper/PedRAGent/README.md)：PedRAGent 总体设计、五部分能力框架、功能预设与研究主线（target；细节由各模块维护）。
- [`../paper/PedRAGent/existing-assets-inventory-2026-09-29.md`](../paper/PedRAGent/existing-assets-inventory-2026-09-29.md)：PedRAGent 现存代码、设计、实验与标注的复用盘点，含实现缺口和文档偏差（current）。
- [`../README.md`](../README.md)：项目目的、模块清单、验证命令和研究开发顺序。
- [`../AGENTS.md`](../AGENTS.md)：Agent 与贡献者的边界、验证和安全规则。
- [`project-architecture.md`](project-architecture.md)：当前架构、模块依赖、数据边界，以及 V1/V2 知识检索链路和发布状态。
- [`module-division-and-design.md`](module-division-and-design.md)：模块划分、职责边界与功能清单 (全面)。
- [`dsh-research-complete-summary.md`](dsh-research-complete-summary.md)：historical；固定版本的新研究见 [Agent-Harness 设计研究](../Agent-Harness/docs/deepseek-harness-design-study.md)。
- [`dsh-research-final-report.md`](dsh-research-final-report.md)：historical；固定版本的新研究见 [Agent-Harness 设计研究](../Agent-Harness/docs/deepseek-harness-design-study.md)。
- [`dsh-research-summary.md`](dsh-research-summary.md)：historical；固定版本的新研究见 [Agent-Harness 设计研究](../Agent-Harness/docs/deepseek-harness-design-study.md)。

## 模块与数据

- [`../Contracts/README.md`](../Contracts/README.md)：跨模块数据契约。
- [`../Knowledge-Base/README.md`](../Knowledge-Base/README.md)：知识与证据模块。
- [`memped-knowledge-feasibility-review-2026-09-22.md`](memped-knowledge-feasibility-review-2026-09-22.md)：memPed/知识库可行性评审、研究与开源项目参考、实验矩阵和阶段验收建议（target）。
- [`memped-storage-memory-project-review-2026-09-22.md`](memped-storage-memory-project-review-2026-09-22.md)：memU、OpenViking、Mem0、Graphiti、Zotero 的存储与记忆设计比较，以及 memPed 文献/附件/研究卡组织建议（target）。
- [`../Video-Analysis/README.md`](../Video-Analysis/README.md)：检测追踪与流动分析模块。
- [`../Agent/README.md`](../Agent/README.md)：证据编排与科研问答模块。
- [`../Agent-Harness/README.md`](../Agent-Harness/README.md)：类型化工具执行、预算、调度与运行记录已实现；动态 Agent 控制器仍为设计。
- [`../experiments/README.md`](../experiments/README.md)：可复现实验约定。
- [`../memPed/README.md`](../memPed/README.md)：研究数据根目录、资产生命周期、Git 边界与验证入口。
- [`../memPed/knowledge/collection_standard.md`](../memPed/knowledge/collection_standard.md)：行人流与疏散交通 RAG 实验语料、处理链路和评测输入。
- [`../memPed/knowledge/reports/content-score-threshold-reclassification-2026-09-23.md`](../memPed/knowledge/reports/content-score-threshold-reclassification-2026-09-23.md)：五批文献按高于 65 分门槛重分类的现行补充记录（current）。
- [`../memPed/knowledge/reports/pymupdf-two-papers-removal-2026-10-08.md`](../memPed/knowledge/reports/pymupdf-two-papers-removal-2026-10-08.md)：两篇 PyMuPDF 补录文献的移除范围、备份、移除后 Catalog 指纹与后续实验前索引检查（current）。
- [`../memPed/knowledge/literature/records/manifest_readiness_2026-09-23.csv`](../memPed/knowledge/literature/records/manifest_readiness_2026-09-23.csv)：原 104 篇文献的非导入式 Manifest 准备表，2026-10-08 移除两篇后为 102 篇（current）。
- [`../memPed/knowledge/reports/manifest-readiness-2026-09-23.md`](../memPed/knowledge/reports/manifest-readiness-2026-09-23.md)：旧精选规则下的 104 篇准备表快照与输入哈希（historical；其中治理标记不阻断现行探索实验）。
- [`../experiments/exploration-literature-preflight-20260923/README.md`](../experiments/exploration-literature-preflight-20260923/README.md)：batch-1 五篇试点与五批 104 篇集中实验 Manifest、只读技术预检及复现边界（current）。
- [`../experiments/benchmark-index-20260924/README.md`](../experiments/benchmark-index-20260924/README.md)：104 篇旧语料的 FTS5 与 BGE-M3 构建记录（historical；不进入 PEARL，V1/V2 索引目录已迁至 `../failed/outputs-void-scores/`）。
- [`../experiments/benchmark-gold-20260923/README.md`](../experiments/benchmark-gold-20260923/README.md)：Gold v5 候选开发集协议、P0 审计与 P1 历史记录（historical；不进入 PEARL，评分目录已迁至 `../failed/outputs-void-scores/`）。
- ~~`../paper/evaluation-reports/stage1-analysis-20260926-02/README.md`~~ **已作废** — Stage 1 分析脚本已迁至 [`../failed/stage1-analysis/`](../failed/stage1-analysis/)（输入路径缺失；PEARL 协议已退出该评测口径）。
- ~~`../paper/F-Report/rag-agentic-metrics-experiment-design.md`~~ **路径不存在** — `paper/F-Report/` 目录未纳入版本控制。
- ~~`../paper/F-Report/metrics-formulas-and-sources.md`~~ **路径不存在** — 同上。
- [`../paper/pearl-framework/README.md`](../paper/pearl-framework/README.md)：PedRAGent 的 PEARL 评价协议：四层顺序链条、Agent 控制器与成本横切维度；旧评估资产不进入新实验（target；非独立系统）。
- [`../paper/pearl-framework/layer-1-retrieval/README.md`](../paper/pearl-framework/layer-1-retrieval/README.md)：Retrieval-v0.2协议、CEGR指标与四方法边界；原开发阶段的200题封存状态描述保留，正式完整release及200题评价以当前C/D入口为准。
- [`../experiments/stage2-annotation/README.md`](../experiments/stage2-annotation/README.md)：20 个开发意图的 agent 复核与当前可用范围（current；非人工 Gold）。

## 研究设计与工程规范

- [`superpowers/plans/2026-09-27-optional-human-gold-review.md`](superpowers/plans/2026-09-27-optional-human-gold-review.md)：可选人工 Gold 审查，不是当前研究门槛（plan）。
- [`superpowers/plans/2026-09-23-literature-manifest-readiness.md`](superpowers/plans/2026-09-23-literature-manifest-readiness.md)：104 篇文献准备表的离线构建、PDF 技术核对与验证步骤（plan）。
- [`superpowers/specs/2026-09-23-content-score-threshold-design.md`](superpowers/specs/2026-09-23-content-score-threshold-design.md)：五批文献全文评分改为高于 65 分通过的规则变更设计（plan）。
- [`superpowers/plans/2026-09-23-content-score-threshold.md`](superpowers/plans/2026-09-23-content-score-threshold.md)：全文评分门槛调整的测试、迁移和核验步骤（plan）。
- [`superpowers/specs/2026-09-22-memped-knowledge-update-design.md`](superpowers/specs/2026-09-22-memped-knowledge-update-design.md)：memPed/知识库目标设计，包含流程前后对比、数据身份、模块边界、研究卡与发布规则（target）。
- [`superpowers/plans/2026-09-22-memped-knowledge-update.md`](superpowers/plans/2026-09-22-memped-knowledge-update.md)：分阶段更新计划、文件变更清单、迁移/回滚、固定验收样例与可选 memU 旁路实验（plan）。

- [`literature-expansion-to-100-batch-1.md`](literature-expansion-to-100-batch-1.md)：知识库扩充至 100 篇的首批 25 篇历史候选清单（50→75）。
- [`literature-expansion-to-100-batch-2.md`](literature-expansion-to-100-batch-2.md)：知识库扩充至 100 篇的第二批 25 篇历史候选清单（75→100）。
- [`data-analysis-module-design.md`](data-analysis-module-design.md)：数据分析目标设计。
- [`vision-module-design.md`](vision-module-design.md)：视觉分析目标设计。
- [`multi-agent-and-tool-integration-plan.md`](multi-agent-and-tool-integration-plan.md)：多Agent编排与Tool Calling集成策略。
- [`superpowers/specs/2026-09-15-pytorch-cuda-unification-design.md`](superpowers/specs/2026-09-15-pytorch-cuda-unification-design.md)：PyTorch CUDA 版本统一计划。
- [`superpowers/plans/2026-09-16-pytorch-cuda-unification.md`](superpowers/plans/2026-09-16-pytorch-cuda-unification.md)：PyTorch CUDA 版本统一实施步骤。
- [`superpowers/specs/2026-09-07-bge-m3-local-deployment-design.md`](superpowers/specs/2026-09-07-bge-m3-local-deployment-design.md)：BGE-M3 本地部署配置计划。
- [`superpowers/specs/2026-09-17-rag-tokenization-v2-design.md`](superpowers/specs/2026-09-17-rag-tokenization-v2-design.md)：RAG 分词、切块、词法检索与版本化发布设计；实现状态见 Knowledge-Base README。
- [`superpowers/specs/2026-09-21-journal-metrics-schema-design.md`](superpowers/specs/2026-09-21-journal-metrics-schema-design.md)：多学科期刊指标的长表存储设计与核验规则。
- [`superpowers/specs/2026-09-21-journal-admission-quartile-design.md`](superpowers/specs/2026-09-21-journal-admission-quartile-design.md)：期刊最佳分区准入规则与未收录来源清理设计。
- [`superpowers/specs/2026-09-21-remove-frontiers-and-jif-score-design.md`](superpowers/specs/2026-09-21-remove-frontiers-and-jif-score-design.md)：删除 Frontiers in Physics 活动资产并停止采集 JIF 数值的设计。
- [`superpowers/plans/2026-09-21-populate-journal-metrics.md`](superpowers/plans/2026-09-21-populate-journal-metrics.md)：已核验期刊指标长表的写入与校验步骤。
- [`superpowers/plans/2026-09-21-journal-admission-quartile.md`](superpowers/plans/2026-09-21-journal-admission-quartile.md)：最佳分区准入、治理代码同步与未收录文献清理步骤。
- [`superpowers/plans/2026-09-21-remove-frontiers-and-jif-score.md`](superpowers/plans/2026-09-21-remove-frontiers-and-jif-score.md)：Frontiers in Physics 活动资产清理与 JIF 数值字段退役步骤。
- [`superpowers/plans/2026-09-07-bge-m3-local-deployment.md`](superpowers/plans/2026-09-07-bge-m3-local-deployment.md)：BGE-M3 本地部署实施步骤。
- [`superpowers/plans/2026-09-17-rag-tokenization-v2.md`](superpowers/plans/2026-09-17-rag-tokenization-v2.md)：RAG 分词、切块、词法检索与版本化发布实施记录（代码已完成，候选索引与实测待执行）。

模块 README 是当前实现边界；设计文档只描述目标深度，是否完成必须以代码和测试为准。

## 历史记录

- [`memped-knowledge-model-context.md`](memped-knowledge-model-context.md)：2026-09-22 的资产与算法快照；其中“当前”仅指快照日期。
- [`superpowers/specs/2026-09-23-adobe-pdf-extract-design.md`](superpowers/specs/2026-09-23-adobe-pdf-extract-design.md)：Adobe 可选解析器原始设计；现行用法见 [`../Knowledge-Base/README.md`](../Knowledge-Base/README.md)。
- [`superpowers/plans/2026-09-23-adobe-pdf-extract.md`](superpowers/plans/2026-09-23-adobe-pdf-extract.md)：已完成的 Adobe 实施清单，不作为后续执行计划。

### 2026-10-07 审计补登记

以下文档此前未登记、未进 Git，审计时统一标为 historical（`gold-questions-guide.md` 原已标注）；其中数字和“当前”只指写作当日。

| 分组 | 文档 |
| --- | --- |
| 知识库构建与测试（2026-09-09 至 09-17） | [实际文献入库测试报告](actual-ingestion-test-report.md)<br>[Ped-Agent 知识库测试综合报告](comprehensive-test-summary.md)<br>[测试环境检查报告](environment-check-report.md)<br>[环境检查报告](environment-check-status.md)<br>[UV 环境检查报告](uv-environment-status.md)<br>[索引构建与检索测试报告](indexing-test-report.md)<br>[向量索引构建成功报告](vector-index-build-report.md)<br>[Knowledge-Base 测试验证报告](knowledge-base-test-report.md)<br>[Ped-Agent 知识库完整构建报告](knowledge-base-expansion-report.md)<br>[Knowledge Base Inventory Report](knowledge-base-inventory-20260917.md)<br>[🎉 Ped-Agent 知识库完整构建完成报告](final-completion-report.md)<br>[Ped-Agent 知识库系统测试方案](system-testing-plan.md) |
| 文献收集批次与扩充计划 | [第一批扩展文献清单 (20篇)](batch-2-literature-list.md)<br>[Batch 3 文献最终清单与重命名方案](batch-3-final-manifest.md)<br>[Batch 3 文献候选名单](batch-3-literature-candidates.md)<br>[Batch 3 文献元数据汇总报告](batch-3-metadata-summary.md)<br>[Batch 3 文献PDF清单](batch-3-pdf-inventory.md)<br>[Ped-Agent 知识库扩展计划：从34篇到100篇](expansion-plan-to-100.md)<br>[文献收集扩展计划：9 篇 → 40 篇](literature-collection-expansion-plan.md)<br>[文献选择标准对比分析](literature-selection-comparison.md) |
| 评测准备（PEARL 之前） | [实验验证准备情况与评测进展报告](experiment-readiness-status-20260924.md)<br>[RAG 评测中的"训练-测试混用"问题分析](rag-evaluation-data-leakage-analysis.md)<br>[Gold Questions 准备指南](gold-questions-guide.md) |
| DeepSeek Harness 早期调研 | [DeepSeek Harness 调研 - 文档导航](dsh-research-navigation.md)<br>[DeepSeek Harness 本地源码分析笔记](dsh-source-code-notes.md)<br>[Agent-Harness 与 DeepSeek Harness 调研总结](task-summary-dsh-research.md)<br>[项目整理与Agent-Harness模块创建总结](task-summary-module-organization.md) |
| 视频模块调研快照 | [行人流实验数据集补充报告](pedestrian-flow-experiment-datasets.md)<br>[行人流轨迹与多目标跟踪（MOT）公开数据集调研报告](pedestrian-tracking-datasets-survey.md)<br>[YOLO26 单目深度估计技术文献](yolo26-depth-estimation-references.md) |

目标设计另补登记：[坐标变换双路线设计](coordinate-transform-dual-routes.md)（target）；规划：[文献入库方向与领域规划](literature-collection-framework.md)（plan）。

## Agentic / Harness 研究（2026-10-04）

| 文档 | 内容 | 状态 |
| --- | --- | --- |
| [Agent-Harness 入口](../Agent-Harness/README.md) | 实现边界与推荐阅读顺序 | current |
| [模块接入评估](../Agent/docs/harness-integration-assessment.md) | 当前调用链、契约与接入缺口 | current |
| [AGI-Saber 设计研究](../Agent-Harness/docs/agi-saber-design-study.md) | 本地 Go 路由、图执行与移植边界 | current |
| [DeepSeek Harness 设计研究](../Agent-Harness/docs/deepseek-harness-design-study.md) | 固定提交的配置、执行与 SDK | current |
| [配置设计](../Agent-Harness/docs/configuration-design.md) | Agent / Harness / 模块分层配置 | target |
| [研究开发计划](../Agent-Harness/docs/agentic-research-plan.md) | 分阶段实施、消融、停止与成本评价 | plan |
| [旧内容整理](../Agent-Harness/docs/legacy-content-review.md) | 历史身份与保留资产 | current |
| [交付核验](../Agent-Harness/docs/delivery-verification.md) | 文档检查与代码保全范围 | current |

以上为后续 Agentic 的研究准备，不表示动态 Harness 或 Layer 5–6 实验已经完成；独立的 Layer 3与Layer 4开发评价见上方入口。

- [Layer 4 Grounding 与 Reliability 中文分析](../experiments/pearl-layer4-dev80-20261004/grounding-reliability-analysis-2026-10-04.md)、[实验入口](../experiments/pearl-layer4-dev80-20261004/README.md)：阶段A–D完成，冻结400回答、5530原子与5676引用对；独立核验、固定次审和版本化裁决完成，正式Agent开发评价，human_verified=false；停止于Layer 4（current）。

- [PEARL 切片 Session 2 E0 执行交接](../experiments/pearl-chunking-dev80-20261005/session2-execution.md)、[重现命令](../experiments/pearl-chunking-dev80-20261005/reproduction_commands.md)：8个固定开发意图真实冒烟、公共来源/表格/parent、双面板与独立复算完成；停止于E0，72题语义映射仍pending/unknown，未运行E1（current）。

## 分支资产核定（2026-10-07）

- [Agentic RAG 开发准备](../Agent/docs/agentic-rag-dev-prep.md)：基线组件抽取已核定，其余开发为 plan。
- [文献准备表历史设计](superpowers/specs/2026-09-23-literature-manifest-readiness-design.md)：原设计存档，旧人工确认要求不作为当前默认门禁（historical）。
- [Agent 与文献设计分支资产核定](branch-asset-integration-2026-10-07.md)：来源、资产清单、验证范围和保全记录（current）。
