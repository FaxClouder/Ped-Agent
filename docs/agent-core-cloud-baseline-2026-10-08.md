# Agent core 云端开发基线

*Agent 与 Agent-Harness 后续开发入口 · status: current · 2026-10-08*

## 分支与工作区

- 仓库：`FaxClouder/Ped-Agent`，GitHub ID `1284945987`。
- 开发分支：`codex/agent-core`；创建前远端没有同名分支。
- 起点：`codex/cloud-dev-prep-20261008` 的 `d737d0ffeacc697124a23a5dbed58e1390558a66`，
  创建时与此前核实的 SHA 一致。云端默认快照 `f3b4621` 未作为开发起点。
- 本次工作区：`/workspace/Ped-Agent`，Python 3.12.14，虚拟环境 `.venv`。
- `agent-core` 是分支用途；沿用现有目录和包名。本轮只更新开发说明，不实现新业务功能。
- 已读仓库贡献、架构和模块说明；仓库无 `.agents/skills`，环境 `/workspace/.agents` 为空。
  原有云端发布边界见 [准备说明](cloud-development-preparation-2026-10-08.md)。

## 现有边界、接口和调用关系

| 模块 | 现有实现与入口 | 依赖及边界 |
| --- | --- | --- |
| [Agent](../Agent/README.md) | `ped_research_agent.EvidenceGraph`、`ResearchQuery`、`EvidenceGraphResult`；固定条件图，检索、草稿、引用/语义验证、至多一次修订 | Contracts、Pydantic、LangGraph、HTTPX、LangChain OpenAI/Anthropic 适配；决定证据与答案 |
| [Agent-Harness](../Agent-Harness/README.md) | `ToolSpec` / `ToolCall` / `ToolOutcome`、`ToolRegistry`、`ToolExecutor.execute`、`ToolScheduler.run_batch`、`RunBudget` / `BudgetMeter`、`JsonlRecorder` | Pydantic 与标准库；执行工具、限额、超时、取消、有限重试、运行记录；不承担领域推理 |
| [Contracts](../Contracts/README.md) | EvidenceItem、RetrievalBatch、AnswerDocument、TrajectoryData | Pydantic；共享稳定数据形状，不承担算法与存储 |

Agent 通过 [ports.py](../Agent/src/ped_research_agent/ports.py) 注入 `ModelGateway`、
`LocalEvidenceRetriever.retrieve(query) -> RetrievalBatch` 和
`ExternalEvidenceSearcher.search(query) -> list[EvidenceItem]`。
`EvidenceGraph.execute(context, emit, is_cancelled)` 返回答案、证据与指标；
`final_persist` 只构造答案，不写文件。

Harness 的执行链是注册工具 → 参数验证 → allowlist/预算 → 调用及超时/取消 →
输出验证 → render → 记录；调度器按并行安全性分组，保留请求结果顺序。
`JsonlRecorder` 保存 canonical 值并拒绝追加已有文件。
旧 `protocols.py` 是兼容接口，新开发沿用类型化工具契约。

目前 Agent 没有调用 Harness，也没有 `HybridRetriever` 到 Agent 检索端口的实验适配器。
模型工具调用端口、配置 loader、动态控制器和跨轮证据规划仍待实现。
组合适配器先放 `experiments/`，知识与视频模块不反向依赖 Harness。
架构文档中 2026-10-04 的 Harness 骨架描述已按 2026-10-07 源码更新；
旧 [接入评估](../Agent/docs/harness-integration-assessment.md) 的骨架观察只适用于其记录时点。

## 云端轻量安装与离线验证

本次 `.venv` 已具备测试和 Agent 运行依赖，只补装三个本地 editable 包；
未同步含 Windows/CUDA 轮子地址的根锁文件，也未安装模型/embedding/reranker extras。
现有版本：pytest 9.1.1、pytest-asyncio 1.4.0、Pydantic 2.13.5、HTTPX 0.28.1、
LangGraph 1.2.12、langchain-openai 1.6.7、langchain-anthropic 1.7.5。

```bash
cd /workspace/Ped-Agent
UV_CACHE_DIR=/tmp/ped-agent-uv-cache uv pip install --python .venv/bin/python \
  --no-deps -e ./Contracts -e ./Agent -e ./Agent-Harness
export PYTHONPATH="Contracts/src:Agent/src:Agent-Harness/src:Knowledge-Base/src:Video-Analysis/src"
.venv/bin/python -m pytest Contracts/tests Agent/tests Agent-Harness/tests -q
.venv/bin/python -m pytest Contracts/tests Agent/tests Agent-Harness/tests Knowledge-Base/tests Video-Analysis/tests -q
```

`--no-deps` 仅用于已准备好依赖的本次环境；全新 Linux 环境先按
[云端准备说明](cloud-development-preparation-2026-10-08.md) 安装模块所需依赖。

| 检查 | 本次结果 |
| --- | --- |
| Agent / Harness / Contracts 离线测试 | 64 passed，4.85 秒 |
| 五模块离线测试 | 220 passed，1 skipped，21.64 秒 |
| 跳过项 | Video-Analysis 可选 PedPy 检查；环境未安装 PedPy |
| CI 触发范围 | 当前 workflow 仅 PR 和 main push；本分支 push 不触发，不能称 CI 通过；workflow 尚未显式覆盖 Harness |

这些测试不验证真实模型服务、OCR、BGE-M3、reranker、GPU/视频权重或真实 Gold。
未下载模型、PDF、完整 Gold、索引或数据库，未调用收费模型服务。
真实资产验证应由后续明确授权的实验完成，保留输入哈希、版本与 provenance，
遵守 [评价规范](../experiments/EVALUATION-STANDARD.md) 的封存集访问边界。

## 后续需要明确的开发规格

1. 首个目标是连接现有固定图/检索适配器，还是实施工具调用端口与动态证据控制器。
2. 首批工具及输入输出契约、允许的副作用、取消传播和失败策略。
3. 模型/provider、结构化工具调用与 usage 接口、调用/token/deadline 预算及停止规则。
4. 冻结配置、运行记录路径、复现标准，以及开发案例和正式评测的验收口径。

现有 [Agent 开发准备](../Agent/docs/agentic-rag-dev-prep.md) 与
[Harness 研究计划](../Agent-Harness/docs/agentic-research-plan.md) 是后续参考计划，
不代表本次已获授权实施其中全部功能。
