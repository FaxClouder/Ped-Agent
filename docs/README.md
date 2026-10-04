# Ped-Agent 文档导航

## 当前入口

- [`../README.md`](../README.md)：项目目的、模块清单、验证命令和研究开发顺序。
- [`../AGENTS.md`](../AGENTS.md)：Agent 与贡献者的边界、验证和安全规则。
- [`project-architecture.md`](project-architecture.md)：当前架构、模块依赖、数据边界，以及 V1/V2 知识检索链路和发布状态。

## 模块与数据

- [`../Contracts/README.md`](../Contracts/README.md)：跨模块数据契约。
- [`../Knowledge-Base/README.md`](../Knowledge-Base/README.md)：知识与证据模块。
- [`../Video-Analysis/README.md`](../Video-Analysis/README.md)：检测追踪与流动分析模块。
- [`../Agent/README.md`](../Agent/README.md)：证据编排与科研问答模块。
- [`../experiments/README.md`](../experiments/README.md)：可复现实验约定。
- [`../memPed/README.md`](../memPed/README.md)：研究数据目录。
- [`../memPed/knowledge/collection_standard.md`](../memPed/knowledge/collection_standard.md)：文献与法规入库标准。

- [`superpowers/specs/2026-09-23-adobe-pdf-extract-design.md`](superpowers/specs/2026-09-23-adobe-pdf-extract-design.md)：Adobe PDF Extract 可选解析器设计（target）。
- [`superpowers/plans/2026-09-23-adobe-pdf-extract.md`](superpowers/plans/2026-09-23-adobe-pdf-extract.md)：Adobe 解析器实施清单（plan）。

## 研究设计与工程规范

- [`data-analysis-module-design.md`](data-analysis-module-design.md)：数据分析目标设计。
- [`superpowers/specs/2026-09-15-pytorch-cuda-unification-design.md`](superpowers/specs/2026-09-15-pytorch-cuda-unification-design.md)：PyTorch CUDA 版本统一计划。
- [`vision-module-design.md`](vision-module-design.md)：视觉分析目标设计。
- [`superpowers/specs/2026-09-07-bge-m3-local-deployment-design.md`](superpowers/specs/2026-09-07-bge-m3-local-deployment-design.md)：BGE-M3 本地部署配置计划。
- [`superpowers/specs/2026-09-17-rag-tokenization-v2-design.md`](superpowers/specs/2026-09-17-rag-tokenization-v2-design.md)：RAG 分词、切块、词法检索与版本化发布设计；实现状态见 Knowledge-Base README。
- [`superpowers/plans/2026-09-07-bge-m3-local-deployment.md`](superpowers/plans/2026-09-07-bge-m3-local-deployment.md)：BGE-M3 本地部署实施步骤。
- [`superpowers/plans/2026-09-17-rag-tokenization-v2.md`](superpowers/plans/2026-09-17-rag-tokenization-v2.md)：RAG 分词、切块、词法检索与版本化发布实施计划（代码已完成，候选索引与实测待执行）。

模块 README 是当前实现边界；设计文档只描述目标深度，是否完成必须以代码和测试为准。

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

以上为后续 Agentic 的研究准备，不表示动态 Harness、真实模型对照或 Layer 3–6 实验已经完成。
