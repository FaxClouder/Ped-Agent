# Agent-Harness 研究入口

*Agent 的通用执行支撑与后续研究方案入口 · status: current · 2026-10-07；开发方案为 plan*

本目录组织工具调用、预算控制、运行记录和外部 Harness 对照的研究。Agent 保留证据需求、引用约束、充分性判断与科研回答职责。Harness 不构成独立产品能力。

## 阅读顺序

| 顺序 | 文档 | 内容与状态 |
| --- | --- | --- |
| 1 | [模块接入评估](../Agent/docs/harness-integration-assessment.md) | 当前源码事实、两份工作树差异、接口断点；current |
| 2 | [AGI-Saber 设计研究](docs/agi-saber-design-study.md) | Go 项目的真实路由、任务图和可借鉴算法；current |
| 3 | [DeepSeek Harness 设计研究](docs/deepseek-harness-design-study.md) | 固定提交的插件配置、执行链与 Python 边界；current |
| 4 | [Agent 与 Harness 配置设计](docs/configuration-design.md) | 配置职责、字段、解析顺序与冻结要求；target |
| 5 | [Agentic 研究开发计划](docs/agentic-research-plan.md) | 阶段任务、研究假设、对照与验收；plan |
| 6 | [工具契约与控制器设计](docs/contract-and-controller-design.md) | 对齐 dsh 工具契约与 AGI-Saber 有限重规划的接口设计；步骤 1–5 已实现；通用运行入口和重放随后接入 |
| 7 | [旧内容整理记录](docs/legacy-content-review.md) | 保留资产、纠正文档和清理边界；current |
| 8 | [来源清单](docs/source-manifest.json) | 本地源码哈希、上游固定提交和验证范围 |

## 实现状态

2026-10-07 起已实现执行层（[设计文档](docs/contract-and-controller-design.md) 第 4 节步骤 1–2）：

| 模块 | 内容 |
| --- | --- |
| `contracts.py` | `ToolSpec`（Pydantic 输入/输出模型、side_effect、timeout、retry、parallel_safe）、冻结的 `ToolCall`、`ToolSuccess \| ToolFailure` 与错误码 |
| `registry.py` | 工具注册与模型可见定义导出 |
| `executor.py` | 单次调用流水线：参数校验 → allowlist 与预算 → 超时/取消 → 输出校验 → render → 记录；只读工具受限重试 |
| `scheduler.py` | 并行安全调用分组、独占调用作屏障、结果按请求顺序返回 |
| `budget.py` | 工具/模型调用、token、deadline 计量；每次尝试都计入 |
| `recorder.py` | 单调 seq 的 `events.jsonl`，canonical 值完整落盘，拒绝追加到已有文件 |

测试：`tests/test_executor.py`、`tests/test_budget.py` 与原 `test_protocols.py`，共 29 个。旧 `protocols.py` 保留作兼容，已标记待移除，新代码不应引用。

2026-10-08 已在 `Agent` 的可选生产集成包接入知识检索工具和固定图事件，
并提供阶段性严格 profile loader；适配器不放实验目录，见 [Agent core 开发进度](../docs/agent-core-development.md)。
阶段 3 已增加模型请求/回复、原生 tool-call 字段、usage/unknown 与预算执行器；新组合
支持模型/工具共享预算和整图 deadline，SDK 隐藏重试禁用。
阶段 4 的动态证据需求控制器及领域规划/判断端口位于 Agent，Harness 没有依赖领域状态。
尚未实现：完整模型配置解析、通用运行入口和完整 run replay。
本模块没有运行真实模型、安装 DeepSeek SDK 或改变 RAG 基线。

实验运行入口和实验配置仍位于 `experiments/`，可复用生产适配器位于 `Agent/integrations`。
使用方式与旧示例之间有出入时，以本入口及 [Agent core 开发进度](../docs/agent-core-development.md) 的当前状态为准。
