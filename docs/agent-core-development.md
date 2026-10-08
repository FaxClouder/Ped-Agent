# Agent core 开发进度与边界

*云端原生 Python 后端实施记录 · status: current · 2026-10-08；未完成阶段为 plan*

沿用 [dsh 工具契约与 AGI-Saber 有限重规划设计](../Agent-Harness/docs/contract-and-controller-design.md)，
保留 `EvidenceGraph` 为 `G-existing`；不是 HTTP 服务或完整外部 Harness 移植。
工作分支 `codex/agent-core`，本轮起点 `936bef8296295f42b2cb63315189f5b8aef6f527`。

## 分阶段交付

| 阶段 | 范围 | 状态与验收 |
| --- | --- | --- |
| 1 | 领域状态、停止原因、工具 IO、严格配置与快照引用 | 已实现；需求图拒绝环/悬空依赖；非质量停止无答案；JSON/TOML 继承、覆盖、哈希和路径校验 |
| 2 | 生产 KB 适配、只读工具、事件桥接、固定图接通 | 已实现；人工合成 SQLite 语料经真实 FTS/HybridRetriever、Harness 工具执行和原图生成脚本化答案 |
| 3 | 模型调用契约、工具调用、usage、预算与取消 | plan；当前仅工具调用计量生效，旧模型网关未接入全运行预算 |
| 4 | 证据需求图控制器、支持判断、失败替代和有限重规划 | plan；状态类型已实现，动态循环尚未实现 |
| 5 | 动态证据标签/context cap、独立答案尾链入口 | plan；已有 AnswerChain 分步方法直接复用，基线标签/快照不改 |
| 6 | 运行入口、manifest/trace、离线状态重放及交付 | plan；当前 Recorder 已保存事件，尚无完整控制器重放器 |

## 模块落点与依赖

| 代码 | 职责 |
| --- | --- |
| [agentic/state.py](../Agent/src/ped_research_agent/agentic/state.py) | Requirement、DecisionState、RoundRecord、AgenticResult、StopReason；领域需求/支持/停止，不承担预算派发 |
| [agentic/config.py](../Agent/src/ped_research_agent/agentic/config.py) | 当前阶段的 RunProfile；Agent 决策上限、Harness 执行上限、快照引用和输出路径 |
| [integrations/knowledge.py](../Agent/src/ped_research_agent/integrations/knowledge.py) | HybridRetriever/Catalog 结构化端口、RetrievalBatch 转换、knowledge.search/read_evidence 生产工具 |
| [integrations/events.py](../Agent/src/ped_research_agent/integrations/events.py) | 原图 async emit 到 Harness Recorder；显式关闭外部搜索 |
| [integrations/runtime.py](../Agent/src/ped_research_agent/integrations/runtime.py) | 显式组合 profile、适配器、gateway、recorder；工具预算、事件身份和取消信号 |

领域 Agent 不导入 KB 算法；可选生产集成包连接领域与 Harness，结构化端口接受真实 KB
或轻量开发替身。Harness 不依赖 Agent，KB 不反向依赖二者，Contracts 保留稳定领域契约。
按本轮用户要求，**可复用适配器放生产集成包，experiments 只保留后续运行入口和实验配置**；
这更新了旧计划中将适配代码暂放 experiments 的落点，不改变 dsh/AGI-Saber 设计来源。
安装生产集成包依赖可使用 `Agent[integration]`；构造真实 KB 需另行安装 Knowledge-Base。

## 已实现的接口语义

- 配置顺序：schema 默认 → 文件 extends → 本文件 → 允许的显式 overrides。
  object 递归合并，list/tuple 整体替换；未知字段、密钥字段、非法预算、未知工具拒绝。
  JSON 重复字段与继承环拒绝；继承链最多 16 文件。路径在定义它的 profile 处解析，
  CLI 输出覆盖相对选定 profile 解析。manifest 哈希和输出不存在须在构造运行实例前通过。
- snapshot JSON 使用 `SnapshotIdentity` 的 policy_version、catalog_fingerprint、index_fingerprint。
  index 的当前指纹函数必须由实际底层 provider 注入；FTS 路线使用 source_fingerprint。
  这不是文件级事务锁；底层索引自己的 policy/tokenizer/analyzer 验证仍由 KB 承担。
- `KnowledgeAdapter.retrieve` 只为固定图注入明确的 baseline_sufficiency；没有将检索启发式
  升级为动态领域充分性。搜索保存降级和 parent_contexts，证据 ID/hash/资源/版本必须一致。
- 定向读取只读本运行已召回的证据；保留 child quote/hash，parent 单独返回。
  parent 另含内容哈希，并与召回时缓存的上下文核对；缺失 parent、非活动版本、
  身份不一致和快照变化显式失败，不用 child 冒充 parent。
  字符区间/token 数来自 Catalog，缺失区间保留 null，不伪造计算结果。
- `build_baseline(profile, knowledge, gateway, recorder, run_id=...)` 返回 BaselineRuntime；
  `runtime.execute(ResearchQuery(...))` 验证 query/run 身份，执行原图。
  工具调用经过 Harness 参数验证、allowlist、预算、超时/重试与 canonical 记录。
  Recorder 由调用者显式提供；构造器不创建运行目录、不读凭据、不实例化真实模型。
- ToolSpec 的 timeout/retry 允许按实例配置；工具名、schema 和 side_effect 仍为类级元数据，
  旧类默认值及原执行行为保持兼容。

## 验证与剩余限制

本轮仅增加一个 [集成检查文件](../Agent/tests/test_agent_core_integration.py)，10 项参数化/闭环检查，
不引入测试框架或覆盖率目标。64 项原核心回归未修改，冻结基线快照未重新生成。
核心合计 74 passed；五模块 230 passed、1 skipped（可选 PedPy 未安装）。
新增源码 Ruff/格式和针对性 mypy 检查通过；`uv lock --check --offline` 通过，
锁文件仅同步已锁定 Harness 的可选集成依赖元数据，未更改模型或 Windows/CUDA 版本。

```bash
.venv/bin/python -m pytest Contracts/tests Agent/tests Agent-Harness/tests -q
.venv/bin/python -m pytest Contracts/tests Agent/tests Agent-Harness/tests Knowledge-Base/tests Video-Analysis/tests -q
```

没有真实 LLM、OCR、embedding/reranker、PDF、Gold、GPU 或真实研究索引效果验证。
工具预算覆盖固定图检索，但模型/token 计量、模型执行取消与整个图的 deadline 均待阶段 3，
不得将当前组合宣称为全运行受限的 Agentic 后端。下一轮先补模型执行边界，再开发控制器。
现有 CI 已补齐 Harness 安装/检查范围，触发条件仍只有 PR 与 main push；本分支 push 不触发。
