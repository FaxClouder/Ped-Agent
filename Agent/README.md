# Agent

*Evidence orchestration and research QA module · status: current · 2026-10-04*

证据约束的科研问答模块。当前实现是固定条件 EvidenceGraph、引用规则、结构化模型适配和外部文献搜索；不具有动态工具选择、通用运行循环或持久化运行记录。

本模块面向实验调用，不提供 FastAPI、会话数据库、SSE、任务队列或多用户能力。

## 研究与接入入口

- [模块接入评估](docs/harness-integration-assessment.md)：当前调用链、RAG/视频契约缺口及两份工作树差异（current）。
- [Agent-Harness 研究入口](../Agent-Harness/README.md)：参考项目、配置设计、阶段计划与旧内容整理。
- [Agentic 研究开发计划](../Agent-Harness/docs/agentic-research-plan.md)：先冻结基线和工具适配，再实现有预算的迭代取证（plan；未实现）。

`load_conversation` 接收实验提供的历史，不读取数据库；`final_persist` 构造答案，不写入文件。历史名不能作为持久化能力依据。关闭语义 verifier 后显式允许的结果只标为 rules_only。
