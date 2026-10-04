# Agent 与 Harness 配置设计

*面向可复现 Agentic 实验的配置开发目标 · status: target · 2026-10-04；本文件不是可执行配置*

## 分工与现有基础

Agent 配置决定研究策略，Harness 配置决定执行机制，模块配置决定底层算法。三者通过实验 profile 组合；不能让工具调用偷偷修改检索模型、索引或标定。

现有 [AgentSettings](../../Agent/src/ped_research_agent/config.py) 已有 answer/verify 模型结构、协议与继承规则。`load_settings()` 的 `.env + environment` 路径只读取其中部分字段，**不能假定 timeout、temperature、max_tokens 等结构字段都有环境变量映射**。DirectModelGateway 支持结构化生成/验证，目前没有面向 Harness 的工具循环模型协议。

配置开发先固定字段与解析规则，再实现 loader 与模型工具适配；不先创建大量空配置文件。下文数值是开发初始候选，不是已经实测的最佳超参数。

## 三层字段

| 配置归属 | 目标字段 | 开发要求 |
| --- | --- | --- |
| Agent | mode、planner、sufficiency_policy、query_strategy、evidence_selection、answer/verify、revision_limit、external_policy | 字段引用明确的策略/模型版本；领域判断可替换并保留输出依据 |
| Harness | backend、tool_allowlist、max_rounds、max_tool_calls、max_model_calls、max_input/output_tokens、context_limit、deadline、concurrency、retry、recording | 执行前/中/后检查，累计计量，禁止由模型覆盖上限 |
| 模块 | corpus/index IDs、policy/tokenizer/embedding/reranker 指纹；scene/analysis/tracker/model manifests | 引用既有模块配置，不复制算法默认值到 Harness |
| 实验 | profile ID、dataset split/hash、seed、重复次数、paired comparison、输出目录 | 冻结配置、实际解析值及环境；新目录防止覆盖 |

## 配置格式候选

下面是**目标 schema 的说明性 YAML**。当前 AgentSettings、旧 Harness Protocol 和 dsh 都不能直接加载此格式；模型名称用已有实验冻结别名映射，提交配置不携带 API key。

```yaml
schema_version: agentic-experiment-v1
profile_id: native-iterative-dev-v1
agent:
  mode: iterative_evidence
  planner: requirements-v1
  sufficiency_policy: requirements-support-v1
  query_strategy: missing-requirement-v1
  evidence_selection: frozen-layer2-policy
  answer_model_ref: frozen-answer-model
  verifier_model_ref: frozen-verifier-model
  revision_limit: 1
  external_policy: disabled
harness:
  backend: native_python
  tools: [knowledge.search, knowledge.read_evidence]
  budgets:
    max_rounds: 3
    max_tool_calls: 8
    max_model_calls: 12
    max_total_input_tokens: 60000
    max_total_output_tokens: 12000
    max_context_tokens: 8000
    deadline_seconds: 300
  executor:
    max_parallel: 1
    default_timeout_seconds: 60
    retry_readonly: 1
    retry_side_effects: 0
  recording:
    format: run-jsonl-v1
    save_canonical_results: true
    replay_model_calls: false
modules:
  knowledge_snapshot_ref: frozen-retrieval-manifest
  context_policy_ref: frozen-layer2-manifest
experiment:
  split: development
  dataset_ref: agentic-dev-v1
  seed: 42
  output_policy: create_new
```

`max_rounds` 计取证决策轮，不计草稿修订；max_tool_calls 计每个派发，包括并行子调用；max_model_calls 包括 planner、sufficiency、answer、verify、repair 及重试尝试。正常模型/工具失败仍消耗预算。token 实际值用 provider usage；不可得时保存估计方法和 unknown，不把它当零。

模型调用前用保守 token 预估与输出 cap 检查剩余额度，返回后累计实际 usage；不能保证 provider 的最终 usage 永不超过预估，允许有记录的超额并停止后续调用。请求重试同样计入总额度；模型 SDK 内部隐藏重试须显式配置并能追踪，避免多个层叠重试。

## 解析、校验与冻结

目标解析顺序：schema defaults → 被引用的基础研究 profile → 本实验覆盖 → 允许的显式命令行覆盖；凭据只在最后通过环境/本地 secret 注入。嵌套 object 递归合并，list 整体替换，null 只对 schema 允许字段有效，未知字段直接拒绝；这套规则属于目标 Python loader，和 dsh 配置树的 row replacement 不同。

每次启动先校验：预算必须为有限正值；revision_limit 可为零；allowlist 中工具存在；profile 不包含未实现工具；readonly/retry 与实际工具能力一致；引用 manifest 存在且哈希一致；output 尚不存在；证据 pack 的预留空间能容纳模型输出与工具 schema。失败在模型调用前结束。

落盘两份内容：原始配置文件和 `resolved-config.json`。解析结果保存 provider/model 精确身份、真实继承后的 verifier、工具/schema/算法版本、输入和 prompt 指纹，凭据替换为 secret_ref，不保存密钥。保存 parser/SDK/运行时版本和 git HEAD + dirty source hashes，避免只靠提交号遗漏本地修改。

## 工具配置与运行协议（target）

工具定义含输入 schema、输出 schema、version、side_effect_class、timeout 与 parallel_safe。Registry 只注册/查询定义与 provider，Executor 负责校验、预算、派发、异常归一化和结果校验；取消状态必须传给具体 provider。

ToolCall 至少有 run_id / call_id / tool_name / arguments / parent_call_id。ToolOutcome 返回 structured value、rendered content、status/error、artifact_refs、usage 与 provenance；旧 `ToolResult.content` 可作为渲染兼容字段，不能承担全部正式数值结果。

| 工具/操作 | 初始政策 | 原因 |
| --- | --- | --- |
| 冻结知识检索、按版本读证据 | readonly；可受限重试；串行先行 | 不改正式资产，便于记录逐轮增量 |
| 已存分析 bundle 读取 | readonly | 先验证数值证据与引用契约 |
| 新轨迹分析/视频推理 | 产生新产物；进程执行；不自动重试未知结果 | 需要输出身份、资源回收与固定数值样例 |
| 索引重建、入库与 corpus 变更 | 不在初始工具列表 | 冻结实验期间不改变取证基础 |
| 通用 shell/任意写文件 | 不在初始工具列表 | 研究任务可以通过结构化领域工具完成 |

进程内 async 超时只保证停止等待与协作取消，不是硬隔离。CPU/GPU 同步算法、子进程或外部写入不能靠 `asyncio.wait_for` 证明停止；选择独立进程时必须记录 kill/drain 的实际完成状态。

## dsh 对照的单独配置

固定 dsh commit、Python SDK 与 runtime wheel 同版本；profile/bundles、全部 patches、导出的有效插件树和独立 DSH_HOME 一并记录。provider/model 与原生路线一致才作 Harness 归因对照。

外部运行时返回 final_response 不足以完成答案契约：桥接 canonical evidence / answer 后，仍走相同 policy 与 verifier。sdk-minimal 不是默认安全研究 profile；不直接复制它的 shell 或 danger-full-access 配置。详见 [固定上游分析](deepseek-harness-design-study.md)。

## 验收样例

loader 应有固定的继承/覆盖样例：verify inherit 的最终值一致；未知字段报错；空 allowlist 或不存在工具不产生模型调用；预算在重试与子调用时确实递增；token unknown 不通过“零成本”门槛；resolved-config 不含 secret；dsh 与 Python 配置不混淆。

运行时样例：非法参数不调用 provider，非法结果进入显式错误；取消前未开始调用与已经开始但结果未知分别记录；输出目录冲突提前失败；离线 replay 恢复相同决策状态并且没有模型/工具外部调用。
