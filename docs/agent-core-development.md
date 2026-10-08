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
| 3 | 模型调用契约、工具调用、usage、预算与取消 | 已实现；新组合路径共享模型/工具预算，重试与 JSON repair 计量，整图 deadline 与协作取消 |
| 4 | 证据需求图控制器、支持判断、失败替代和有限重规划 | 已实现；依赖 ready、阻塞传播、原子重规划、ID/标签稳定、增益与硬界限离线验证；答案尾链尚未接入 |
| 5 | 动态证据标签/context cap、独立答案尾链入口 | 已实现；稳定来源标签、必要支持优先、裁剪后确认、复用 AnswerChain；仅最终验证通过可 answered |
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
阶段 1–2 核心合计 74 passed；五模块 230 passed、1 skipped（可选 PedPy 未安装）。
新增源码 Ruff/格式和针对性 mypy 检查通过；`uv lock --check --offline` 通过，
锁文件仅同步已锁定 Harness 的可选集成依赖元数据，未更改模型或 Windows/CUDA 版本。

```bash
.venv/bin/python -m pytest Contracts/tests Agent/tests Agent-Harness/tests -q
.venv/bin/python -m pytest Contracts/tests Agent/tests Agent-Harness/tests Knowledge-Base/tests Video-Analysis/tests -q
```

没有真实 LLM、OCR、embedding/reranker、PDF、Gold、GPU 或真实研究索引效果验证。
阶段 3 已补全新组合路径的模型计量与整图 deadline；阶段 4 已接入动态取证控制器。
后续阶段 5–6 接入独立答案尾链、运行入口与重放。
现有 CI 已补齐 Harness 安装/检查范围，触发条件仍只有 PR 与 main push；本分支 push 不触发。


## 阶段 3 模型执行边界

本阶段起点为 `e96cdd0d50b6ad3cc9829bc0daeef841cfe65626`。

- Harness 的 `model_contracts.py` 定义 ModelRequest/Message/Reply/Usage/Capabilities，
  原生工具提案包含 provider ID、名称和 JSON 参数，保留 finish_reason。
  工具结果须对应先前 assistant 调用；工具模式与 JSON schema 模式分开。
- `models.py::ModelExecutor` 对每次尝试预扣调用次数和 token 额度；timeout/retry
  使用 profile 的 model_timeout_seconds/retry_model，默认不重试。
  `execution.py` 负责协作取消和任务收敛，caller CancelledError 原样传播；取消不重试。
  能力不支持、预算不足在调用前失败；Recorder 故障不作为网络错误重试。
- usage 缺失字段保留 null，unknown_token_calls 单列。BudgetUsage 的 input/output_tokens
  是**已知实际值之和**，不是完整成本；estimated_input/output_tokens 独立占额。
  输入估算使用请求 UTF-8 字节长度与 framing allowance，未知输出按请求 cap 保守占额。
  返回后真实 usage 替换 reservation；未知失败同样占估算额度，不按免费处理。
  这是保守预算政策，不是真实 tokenizer/provider usage 验证；实际超额记录后停止。
- Agent 的 `integrations/models.py` 提供 LangChainModelPort 与 MeteredModelGateway。
  沿用已有 OpenAI 兼容/Anthropic 设置；新路径 SDK max_retries 必须为 0，由 Harness 重试。
  planner/judge/replan 首版复用 verifier 路由，角色独立记录。
  from_settings 的 capability 是路由声明，本轮未实测远端 provider 的实际支持程度。
- 新 `build_baseline` 第三个参数须满足 ModelPort，可使用 LangChainModelPort.from_settings。
  不再接受不可审计重试与 usage 的旧 gateway。旧 ModelGateway/DirectModelGateway/EvidenceGraph
  接口和行为保留，直接使用时没有新增预算保证；新组合通过 metered gateway 适配旧端口。
  query rewrite、answer、verify、一次 JSON repair 和可选答案修订均走同一 ModelExecutor。
- `BaselineRuntime.execute` 对整图施加共享 deadline/cancel，覆盖非模型阶段；
  超限、取消和异常不返回 verified 答案，不修改冻结基线的 prompt 或快照。
  进程内取消仍依赖 provider 协作，不保证硬停止不可取消的同步 CPU/GPU 工作。

本阶段新增一个小型 Harness 检查文件，在既有 Agent 检查中补 native response、repair
和整图 deadline 案例。核心 84 passed；五模块 240 passed、1 skipped；新增源码针对性
Ruff/mypy 检查通过。未请求真实模型服务，未安装新 provider 或下载模型资产。


## 阶段 4 动态证据需求控制器

起点 `a690eaa1972c409fa521c598aaf2e847b089a0c0`；只在云端分支实施。

- [agentic/decisions.py](../Agent/src/ped_research_agent/agentic/decisions.py) 定义
  ResearchPlan/RequirementSpec、Replan、SupportJudgment、DecisionPolicy 和 EvidenceActions。
  初始节点只能声明事实需求、依赖和候选查询，不能注入 satisfied 或生成答案。
- [agentic/controller.py](../Agent/src/ped_research_agent/agentic/controller.py) 使用普通 async
  循环，每轮只执行依赖已满足且尚有未试查询的需求层。保留 queries_tried；搜索或判断失败
  标 unknown/unsatisfiable，传播 blocked；替换查询后可恢复取证，上游满足后再执行下游。
  没有把需求图展平成固定流水线，也不回退到 EvidenceGraph。
- 初始计划拒绝重复 ID、悬空依赖、重复依赖、环及需求数超限，返回 plan_invalid。
  merge_plan 在深拷贝中验证整个候选图，拒绝超量追加、重复 ID、非法依赖与目标查询；
  只允许有限追加或替换未满足需求的查询，不能删除节点/改变既有事实与依赖。
  空补丁及无效尝试同样消耗 replan slot；无效补丁记录 replan_parse_failed 并计入无增益。
- [integrations/decisions.py](../Agent/src/ped_research_agent/integrations/decisions.py) 的
  MeteredDecisionPolicy 使用已计量 ModelExecutor 的 planner/judge/replan 角色与结构化响应，
  模型收到实际 AgentPolicy 上限。HarnessEvidenceActions 的 search 与首次 child read
  都经过 ToolExecutor；首轮读取核对 snapshot/child 身份，重复证据沿用首次读取与标签。
  组合调用者须给两执行器注入相同 run_id、meter、recorder 和 cancel_event，并将
  meter.remaining_seconds 传给控制器；本阶段没有通用运行入口。
- 以 evidence_id 去重，保留首次轮次及稳定标签（阶段 5 调整为来源前缀 L1/A2/W3）；同 ID 的身份/内容冲突被丢弃并记录。
  new_ids 表示新增取证，support_gain_ids 表示支持状态增强或已记录冲突解决。
  新引用 ID、重复检索或判断措辞变化本身不代表事实支持增益。判断必须引用已收集证据；
  satisfied/partial 须有支持，satisfied 不能有未解决冲突。其语义质量仍取决于注入的判断端口。
- quality_stop 要求所有需求都有证据、理由且无冲突。本阶段即使质量停止也只返回
  AgenticResult(state, outcome="stopped", answer=None)，供阶段 5 的尾链使用，未生成 verified。
  no_gain_stop、all_blocked、round_limit、replan_limit、budget_exhausted、cancelled、
  plan_invalid、execution_failed 都保留状态及缺口，不返回答案。
  轮数/无增益已触限不再重规划；已耗尽重规划仍可执行预先存在的未试查询，
  当失败需要替代或查询耗尽时返回 replan_limit。
  整体 deadline/协作取消复用 Harness helper；caller CancelledError 记录后继续传播。

复用既有集成检查及合成 SQLite/FTS fixture，增加 14 项状态/边界案例。
核心 98 passed；五模块 254 passed、1 skipped（可选 PedPy 未安装）。
覆盖非法初始图、原子拒绝、上游阻塞与失败替代、合法追加、重复证据/无增益、
无效重规划计数、轮数/重规划/工具上限、all_blocked、取消与 deadline 清理。
脚本化判断仅证明状态转移与计量，不证明真实模型规划或证据判断质量。
未调用收费模型、下载模型/PDF/完整 Gold 或修改冻结基线。
阶段 5 的 context cap/最终答案尾链及阶段 6 的 runner/manifest/replay 仍为 plan。


## 阶段 5 动态答案尾链

起点 `1866e8e2172387e8bb77e4b58737ce880fe1daf0`。
[agentic/answer.py](../Agent/src/ped_research_agent/agentic/answer.py) 的 DynamicAnswerChain
接收控制器结果；非质量停止直接形成结构化 gaps，无模型生成。质量状态才进入 context
选择与原有 AnswerChain 的 draft/validate/semantic_verify/revise/final_answer，默认只修订一次。
原验证逻辑和 EvidenceGraph/冻结 prompt/快照未修改。

动态标签采用来源前缀加首次出现的全局序号（L1/A2/W3），以兼容既有引用规则；
同一证据在后续轮次与 context 筛选中不重新编号。动态绑定校验额外拒绝标签偷换。
新增 max_context_items/max_context_tokens：保留完整 canonical 引文，以 UTF-8 字节数保守
占据 token 额度（不是 provider tokenizer）。需求声明的全部支持证据先于可选证据保留；
必要支持放不下返回 context_limit，记录 retained/dropped/missing_support_ids。
丢弃可选证据后，针对裁剪后的证据集合重新调用 DecisionPolicy.judge；未保持 satisfied
或引用了被丢弃的 ID 则 support_lost，不生成答案。这是保守策略，不尝试自动缩短原引文。
生成、一次 JSON repair、语义验证和至多一次修订共用 ModelExecutor/meter/deadline/cancel。
只有完整质量状态且最终规则和语义验证通过返回 verified；关闭 verifier 不能走 rules_only。
context/支持/预算/验证失败均返回 stop_reason、gaps 和无答案结果。

在既有集成文件增加 5 项检查：稳定 L7 标签经可选裁剪保留、context cap 停止、裁剪后
支持丢失停止，以及 JSON 修复/语义失败/一次修订在充足和不足共享预算下的行为。
核心 103 项；五模块 259 passed、1 skipped。仍只使用合成语料和脚本响应，无真实模型质量声明。
阶段 6 的运行入口、manifest 和状态重放随后接入。
