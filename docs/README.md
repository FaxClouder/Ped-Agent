# PedRAGent 文档导航

## 当前入口

- [`../paper/PedRAGent/README.md`](../paper/PedRAGent/README.md)：PedRAGent 总体设计、五部分能力框架、功能预设与研究主线（target；细节由各模块维护）。
- [`../paper/PedRAGent/existing-assets-inventory-2026-09-29.md`](../paper/PedRAGent/existing-assets-inventory-2026-09-29.md)：PedRAGent 现存代码、设计、实验与标注的复用盘点，含实现缺口和文档偏差（current）。
- [`../README.md`](../README.md)：项目目的、模块清单、验证命令和研究开发顺序。
- [`../AGENTS.md`](../AGENTS.md)：Agent 与贡献者的边界、验证和安全规则。
- [`project-architecture.md`](project-architecture.md)：当前架构、模块依赖、数据边界，以及 V1/V2 知识检索链路和发布状态。
- [`module-division-and-design.md`](module-division-and-design.md)：模块划分、职责边界与功能清单 (全面)。
- [`dsh-research-complete-summary.md`](dsh-research-complete-summary.md)：DeepSeek Harness 调研完整总结 ⭐ **推荐阅读**。
- [`dsh-research-final-report.md`](dsh-research-final-report.md)：DeepSeek Harness 完整调研报告（文档+源码分析）。
- [`dsh-research-summary.md`](dsh-research-summary.md)：DeepSeek Harness 调研与集成建议。

## 模块与数据

- [`../Contracts/README.md`](../Contracts/README.md)：跨模块数据契约。
- [`../Knowledge-Base/README.md`](../Knowledge-Base/README.md)：知识与证据模块。
- [`memped-knowledge-feasibility-review-2026-09-22.md`](memped-knowledge-feasibility-review-2026-09-22.md)：memPed/知识库可行性评审、研究与开源项目参考、实验矩阵和阶段验收建议（target）。
- [`memped-storage-memory-project-review-2026-09-22.md`](memped-storage-memory-project-review-2026-09-22.md)：memU、OpenViking、Mem0、Graphiti、Zotero 的存储与记忆设计比较，以及 memPed 文献/附件/研究卡组织建议（target）。
- [`../Video-Analysis/README.md`](../Video-Analysis/README.md)：检测追踪与流动分析模块。
- [`../Agent/README.md`](../Agent/README.md)：证据编排与科研问答模块。
- [`../Agent-Harness/README.md`](../Agent-Harness/README.md)：Agent编排与工具调用框架（设计中）。
- [`../experiments/README.md`](../experiments/README.md)：可复现实验约定。
- [`../memPed/README.md`](../memPed/README.md)：研究数据根目录、资产生命周期、Git 边界与验证入口。
- [`../memPed/knowledge/collection_standard.md`](../memPed/knowledge/collection_standard.md)：行人流与疏散交通 RAG 实验语料、处理链路和评测输入。
- [`../memPed/knowledge/reports/content-score-threshold-reclassification-2026-09-23.md`](../memPed/knowledge/reports/content-score-threshold-reclassification-2026-09-23.md)：五批文献按高于 65 分门槛重分类的现行补充记录（current）。
- [`../memPed/knowledge/literature/records/manifest_readiness_2026-09-23.csv`](../memPed/knowledge/literature/records/manifest_readiness_2026-09-23.csv)：104 篇文献的非导入式 Manifest 准备表（current）。
- [`../memPed/knowledge/reports/manifest-readiness-2026-09-23.md`](../memPed/knowledge/reports/manifest-readiness-2026-09-23.md)：旧精选规则下的 104 篇准备表快照与输入哈希（historical；其中治理标记不阻断现行探索实验）。
- [`../experiments/exploration-literature-preflight-20260923/README.md`](../experiments/exploration-literature-preflight-20260923/README.md)：batch-1 五篇试点与五批 104 篇集中实验 Manifest、只读技术预检及复现边界（current）。
- [`../experiments/benchmark-index-20260924/README.md`](../experiments/benchmark-index-20260924/README.md)：104 篇活动语料的独立 FTS5 与 BGE-M3 索引构建入口（current；V1/V2 索引目录已迁至 `../failed/outputs-void-scores/`）。
- [`../experiments/benchmark-gold-20260923/README.md`](../experiments/benchmark-gold-20260923/README.md)：Gold v5 候选开发集协议、P0 审计与 P1 逐题对照入口（current；评分目录已迁至 `../failed/outputs-void-scores/`）。
- ~~[`../paper/evaluation-reports/stage1-analysis-20260926-02/README.md`](../paper/evaluation-reports/stage1-analysis-20260926-02/README.md)~~ **已作废** — Stage 1 分析脚本已迁至 [`../failed/stage1-analysis/`](../failed/stage1-analysis/)（输入路径缺失；PEARL 协议已退出该评测口径）。
- ~~[`../paper/F-Report/rag-agentic-metrics-experiment-design.md`](../paper/F-Report/rag-agentic-metrics-experiment-design.md)~~ **路径不存在** — `paper/F-Report/` 目录未纳入版本控制。
- ~~[`../paper/F-Report/metrics-formulas-and-sources.md`](../paper/F-Report/metrics-formulas-and-sources.md)~~ **路径不存在** — 同上。
- [`../paper/pearl-framework/README.md`](../paper/pearl-framework/README.md)：PedRAGent 系统的 PEARL 评价流程与六层指标体系，含当前实验口径差异（target；非独立系统）。
- [`../paper/pearl-framework/layer-1-retrieval/README.md`](../paper/pearl-framework/layer-1-retrieval/README.md)：Retrieval 层的 RAG 文献依据、指标公式、三方法轻量对照和检索模块替换规则（plan）。
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

## Agentic / Harness 研究（2026-10-04）

| 文档 | 内容 | 状态 |
| --- | --- | --- |
| [Agent-Harness 入口](../Agent-Harness/README.md) | 实现边界与推荐阅读顺序 | current |
| [模块接入评估](../Agent/docs/harness-integration-assessment.md) | 当前调用链、契约与接入缺口 | current |
| [Agentic RAG 开发准备](../Agent/docs/agentic-rag-dev-prep.md) | Agent 代码复用分级、代码级缺口、拟定结构与固定案例 | plan |
| [AGI-Saber 设计研究](../Agent-Harness/docs/agi-saber-design-study.md) | 本地 Go 路由、图执行与移植边界 | current |
| [DeepSeek Harness 设计研究](../Agent-Harness/docs/deepseek-harness-design-study.md) | 固定提交的配置、执行与 SDK | current |
| [配置设计](../Agent-Harness/docs/configuration-design.md) | Agent / Harness / 模块分层配置 | target |
| [研究开发计划](../Agent-Harness/docs/agentic-research-plan.md) | 分阶段实施、消融、停止与成本评价 | plan |
| [旧内容整理](../Agent-Harness/docs/legacy-content-review.md) | 历史身份与保留资产 | current |
| [交付核验](../Agent-Harness/docs/delivery-verification.md) | 文档检查与代码保全范围 | current |

以上为后续 Agentic 的研究准备，不表示动态 Harness、真实模型对照或 Layer 3–6 实验已经完成。

## 分支资产核定（2026-10-07）

- [Agentic RAG 开发准备](../Agent/docs/agentic-rag-dev-prep.md)：基线组件抽取已核定，其余开发为 plan。
- [文献准备表历史设计](superpowers/specs/2026-09-23-literature-manifest-readiness-design.md)：原设计存档，旧人工确认要求不作为当前默认门禁（historical）。
- [Agent 与文献设计分支资产核定](branch-asset-integration-2026-10-07.md)：来源、资产清单、验证范围和保全记录（current）。
