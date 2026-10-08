# Agent core 开发进度与边界

*云端原生 Python 后端实施记录 · status: current · 2026-10-08；六阶段最小后端已交付；真实能力验证另行开展*

沿用 [dsh 工具契约与 AGI-Saber 有限重规划设计](../Agent-Harness/docs/contract-and-controller-design.md)，
保留 `EvidenceGraph` 为 `G-existing`；不是 HTTP 服务或完整外部 Harness 移植。
工作分支 `codex/agent-core`，本轮起点 `936bef8296295f42b2cb63315189f5b8aef6f527`。

## 分阶段交付

| 阶段 | 范围 | 状态与验收 |
| --- | --- | --- |
| 1 | 领域状态、停止原因、工具 IO、严格配置与快照引用 | 已实现；需求图拒绝环/悬空依赖；非质量停止无答案；JSON/TOML 继承、覆盖、哈希和路径校验 |
| 2 | 生产 KB 适配、只读工具、事件桥接、固定图接通 | 已实现；人工合成 SQLite 语料经真实 FTS/HybridRetriever、Harness 工具执行和原图生成脚本化答案 |
| 3 | 模型调用契约、工具调用、usage、预算与取消 | 已实现；新组合路径共享模型/工具预算，重试与 JSON repair 计量，整图 deadline 与协作取消 |
| 4 | 证据需求图控制器、支持判断、失败替代和有限重规划 | 已实现；依赖 ready、阻塞传播、原子重规划、ID/标签稳定、增益与硬界限离线验证；尾链见阶段 5 |
| 5 | 动态证据标签/context cap、独立答案尾链入口 | 已实现；稳定来源标签、必要支持优先、裁剪后确认、复用 AnswerChain；仅最终验证通过可 answered |
| 6 | 运行入口、manifest/trace、离线状态重放及交付 | 已实现；显式后端组合、离线 CLI、独立 run 归档、状态增量重建与损坏/版本拒绝 |

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
阶段 5–6 已接入独立答案尾链、运行入口与重放，见下文。
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
  meter.remaining_seconds 传给控制器；阶段 6 的 run_research 已统一组合这些依赖。
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
阶段 4 交付时尚未接入 context/尾链和 runner/replay；它们现已在阶段 5–6 实现。


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
阶段 6 已接入运行入口、manifest 和状态重放，见下文。


## 阶段 6 后端入口、离线运行与状态重放

起点 `bbefcd73285209e77d4f0bf5f3c410114bac644f`。可复用入口：

| 文件 | 当前能力 |
| --- | --- |
| [integrations/agentic_runtime.py](../Agent/src/ped_research_agent/integrations/agentic_runtime.py) | build_agentic 显式组合控制器与答案尾链，execute(question) 返回 AgenticResult；无文件持久化 |
| [integrations/research_run.py](../Agent/src/ped_research_agent/integrations/research_run.py) | run_research 统一共享工具/模型 meter、recorder、cancel、deadline，预检后持久化一次完整运行 |
| [integrations/run_records.py](../Agent/src/ped_research_agent/integrations/run_records.py) | RunArchive、凭据过滤、状态增量日志、完整性封存；replay_run 校验并重建结果和 usage |
| [cli.py](../Agent/src/ped_research_agent/cli.py) | demo 默认小型 SQLite/FTS fixture + OfflineModel；replay 仅读取归档 |

固定图与动态组合复用 runtime.py 的 build_execution，预算逻辑未另写一套。
底层端口、ModelPort 或规则 DecisionPolicy 由调用者显式注入；不自动读环境凭据，
不构造真实 provider，不开启外部搜索。生产代码不放 experiments；该 CLI 是开发 smoke
示例，不是 Gold 问题集、科研评估 runner 或真实规划质量证明。

在本云端已有轻量 `.venv` 中，从仓库根运行：

```bash
.venv/bin/python -m ped_research_agent.cli demo --output-root /tmp/ped-agent-runs
# 用上一条输出的 run_dir 运行；不需要临时 fixture 或任何模型/索引服务
.venv/bin/python -m ped_research_agent.cli replay /tmp/ped-agent-runs/<run-uuid>
```

新环境需要 Python 3.12、Contracts、Agent[integration]、Agent-Harness；demo 另需 Knowledge-Base
的 SQLite/FTS 路径，replay 无需 KB/模型资产。这里没有运行 root 的 Windows/CUDA uv sync。
库调用先 load_profile，再把新 KnowledgeAdapter 与已配置 ModelPort 传给
`await run_research(profile, knowledge, model_port, question)`；profile.output_dir 必须不存在。
`build_agentic(..., recorder, run_id=...)` 可用于无持久化调用，取消信号是 runtime.execution.cancel。
CLI 每次生成 UUID 子目录；库入口也默认生成 UUID，已有输出目录拒绝复用或覆盖。

每个 run 有四个小文件：

- manifest.json：无密钥 resolved config 及 SHA-256、run_id、问题、Git SHA/dirty、源码指纹、
  Python/包版本、KB snapshot/fixture 或 index 指纹、prompt 与工具/model schema 版本/指纹。
- events.jsonl：单调 seq，canonical 工具结果、原始模型回复的过滤视图、规划/支持/重规划、
  每轮状态和增量、新证据/重复/丢弃、答案验证及最终 usage。不是单纯渲染日志。
- result.json：最终 AgenticResult，包括 stop_reason、需求/证据/稳定标签、答案或结构化 gaps。
- completion.json：以上文件哈希、事件数、格式版本、run_id 和过滤计数。无 seal 的中断目录
  明确视为不完整；caller 取消会完成任务清理、归档 cancelled 缺口后继续传播 CancelledError。

Archive 对已识别 credential 字段/字符串（provider key、Bearer、私钥、URL 密码等）和调用者
显式 redact_values 递归过滤，字段名和字符串键也过滤。配置 schema 不接受凭据字段；
SDK 对象不进入 manifest。过滤后 tool arguments/value 的日志哈希重新计算，content_hash
保留原始来源身份；归档表示过滤后的可重放视图，不声称保留所有原始字节。
调用真实自定义 provider 时，调用者仍须传入需要过滤的不透明凭据值；未知形式的敏感研究
文本不是通用 DLP 的验证范围。过滤导致对象身份冲突会显式失败，不能悄悄合并对象。

replay_run 不创建 provider/ToolExecutor，不访问临时 SQLite、PDF、Gold 或真实索引。
它校验文件 seal、JSON/事件序号、run/profile/model 格式版本、调用和 canonical 值哈希；
从空 DecisionState 按 before/after 哈希和 patch 逐轮应用 state_delta，检查依赖图、
节点身份/查询历史、证据来自实际记录的工具结果、稳定标签、轮数和重规划上限，
再核对 result.json。模型尝试和已知/未知 token 占额重新汇总并核对 usage；工具完成结果
按 provenance.attempts 汇总。整图取消/超时时可能有已启动而未写 outcome 的工具，
此时明确保留最终 meter 的 charged count，下界由完成结果验证，不虚构缺失 outcome。
最后对 answered 结果重跑既有引用规则，检查精确标签、保留必要支持、语义判定记录与
最终已验证草稿一致；重放没有重跑模型，也不证明真实语义判断正确。

明确失败：missing（缺文件/不完整）、integrity（文件哈希变化）、incompatible（不支持的
run/profile/model 格式）、invalid（JSON、状态增量、身份、预算或答案记录不一致）。
哈希用于检测损坏和内部不一致，不提供外部签名或抵御可同时重写整份归档的真实性保证。

复用既有集成文件补 7 项高价值检查：完整后端/无调用重放/拒绝覆盖；四种坏归档；
已识别及不透明 credential 回显过滤；计划调用中断后可重放 cancelled 状态。
最终核心 110 项；五模块 266 passed、1 skipped。Ruff/格式、针对性 mypy、离线 lock 检查
通过；CLI demo 与单独 replay 已实际运行。冻结 EvidenceGraph、AnswerChain 验证逻辑、
prompt 与基线快照保持不变。

本次集成自审已修复重放对同 ID 多次 canonical 检索值的处理：读证据失败后重试时
检索时间/排名可变化，重建状态须匹配某次实际记录值，而不能误绑第一次未使用的召回。
也核对了裁剪支持、调用身份/output reservation、版本拒绝与最终验证记录的边界。
未验证真实 LLM、OCR、embedding/reranker、GPU、PDF/Gold 或真实研究索引质量；
进程内取消仍依赖工具/provider 协作，unknown usage 与 context token 都使用明确的保守估算。
现有 CI 仅 main push/PR 触发，本分支 push 无运行，不记为 CI 通过。
六阶段最小后端到此完成；新的算法、真实 provider 运行及科研评估须另行确定。
