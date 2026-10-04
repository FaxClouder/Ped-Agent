# 旧内容整理与交付范围

*E 盘 Agent / Agent-Harness 的资产核查与文档状态校正 · status: current · 2026-10-04*

## 整理原则

清理重点是错误完成状态、重复入口和旧版本结论。研究源码、测试、数据、输出和历史依据都有保留价值；本轮不删除它们。旧文档保留原文，在顶部加 historical 与替代入口，避免断开已有链接或追改冻结研究记录。

E 盘 `docs/README.md` 和 `docs/project-architecture.md` 已有本地修改，Harness 为未跟踪目录；更新采用基于现有内容的增补，不用 C 盘旧文件覆盖它们。文件操作清单与检查结果在 [交付核验记录](delivery-verification.md) 中记录。

## 逐项处理

| 资产 | 核查事实 | 处理 |
| --- | --- | --- |
| `Agent/src/`、`Agent/tests/` | 固定证据图、规则与模型/外部搜索适配均有实现 | 保留；更新 README 说明真实能力与接入报告 |
| `Agent-Harness/src/ped_agent_harness/protocols.py` | 模型与 Protocol 存在，无执行器实现 | 保留；不改 API、不下沉共享契约 |
| `Agent-Harness/tests/test_protocols.py` | 有 8 个 Pydantic 模型测试，不能证明动态工具执行 | 保留；历史通过次数不作本轮测试结果 |
| 空包与 `examples/tool_calling_demo.py` | 占位示例，不具备端到端能力 | 保留占位身份；README 不再显示为可用示例 |
| `Agent-Harness/README.md` | 树中有未实际存在的 registry/executor/base/session 文件；状态与总结不同 | 用新的研究入口与精确实现状态替换 |
| `Agent-Harness/SETUP_SUMMARY.md` | 旧创建与测试快照 | 标 historical，保留旧正文 |
| `Agent-Harness/docs/design-notes.md` | 旧问题列表和未来模块划分 | 标 historical，链接配置设计与研究计划 |
| `Agent-Harness/docs/dsh-research-and-integration.md` | 较早上游分析，无本次固定提交；部分 SDK/环境结论已漂移 | 标 historical，替代为新固定提交研究 |
| `docs/dsh-research-{complete-summary,final-report,summary}.md`（若存在） | 旧上游调研系列 | 标 historical，导航统一指向新固定提交研究；保留原文作追溯 |
| `docs/multi-agent-and-tool-integration-plan.md`（若存在） | 较早集成计划 | 标 historical，链接新研究计划 |
| `docs/README.md` | 当前与旧推荐调研混合 | 增加本轮 maintained 文档表，给旧 dsh 入口标历史 |
| `docs/project-architecture.md` | 有 Harness in-design，容易被理解为新增独立能力 | 增补其执行支撑身份和新文档入口；不宣称已接入 |

缓存 `.pytest_cache` 与其他临时目录不是本轮研究设计的障碍；没有为了目录整洁删除它们。memPed、模型、索引、PEARL 冻结配置和输出未变更。

## 对旧结论的具体纠正

1. 有 ToolRegistry Protocol 不等于有注册器实现；8 个模型测试不是执行与编排测试。
2. 图中的 `final_persist` 不落盘、`load_conversation` 不读取数据库；以实际函数为准。
3. dsh Python SDK 是子进程协议边界；不能等同于 Python 原生运行时，也不能继续笼统要求运行 SDK 必须另装 Node.js。
4. `sdk-minimal` 为显式独立树，默认 shell 和访问策略不等于领域只读工具集。
5. Harness 日志与 Session 可提供追溯，但 canonical output 与“模型看到的内容”可能不同，科研复算需另外保存结构化值。
6. 旧 PEARL 状态与最新 experiment/nav 有差异，不追改已冻结快照；本轮 plan 不执行新分数评价，不将旧 31 问 Pilot 当新正式集。

## 交付身份

本轮文档以 E 盘项目为最终目的地。C 盘会话工作区只承担可写暂存与检查，不能被解释为已同步 E 盘全部较新源码或实验资产。
