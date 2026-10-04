# Agent-Harness 研究入口

*Agent 的通用执行支撑与后续研究方案入口 · status: current · 2026-10-04；开发方案为 plan*

本目录组织工具调用、预算控制、运行记录和外部 Harness 对照的研究。Agent 保留证据需求、引用约束、充分性判断与科研回答职责。Harness 不构成独立产品能力。

## 阅读顺序

| 顺序 | 文档 | 内容与状态 |
| --- | --- | --- |
| 1 | [模块接入评估](../Agent/docs/harness-integration-assessment.md) | 当前源码事实、两份工作树差异、接口断点；current |
| 2 | [AGI-Saber 设计研究](docs/agi-saber-design-study.md) | Go 项目的真实路由、任务图和可借鉴算法；current |
| 3 | [DeepSeek Harness 设计研究](docs/deepseek-harness-design-study.md) | 固定提交的插件配置、执行链与 Python 边界；current |
| 4 | [Agent 与 Harness 配置设计](docs/configuration-design.md) | 配置职责、字段、解析顺序与冻结要求；target |
| 5 | [Agentic 研究开发计划](docs/agentic-research-plan.md) | 阶段任务、研究假设、对照与验收；plan |
| 6 | [旧内容整理记录](docs/legacy-content-review.md) | 保留资产、纠正文档和清理边界；current |
| 7 | [来源清单](docs/source-manifest.json) | 本地源码哈希、上游固定提交和验证范围 |

## 实现状态

最终交付位置是 `E:\F_Workspace\F-Agent-Paper\Agent-Harness`。其原有 `protocols.py`、8 个协议模型测试和占位包保留；骨架没有工具注册器、执行器、Agent 循环或运行记录实现，历史“测试通过”是旧记录，不能解释为本轮执行验证。C 盘会话工作区只暂存本轮研究文档，没有移植 E 盘源码。

本轮没有新增运行时代码、安装 DeepSeek SDK、运行真实模型、执行视频推理或改变 RAG 基线。配置文档里的 YAML 是目标示例，当前代码不能加载它。

研究组合先进入 `experiments/`；接口通过固定案例和跨模块验证后再下沉。使用方式与旧示例之间有出入时，以本入口及 [接入评估](../Agent/docs/harness-integration-assessment.md) 的状态标注为准。
