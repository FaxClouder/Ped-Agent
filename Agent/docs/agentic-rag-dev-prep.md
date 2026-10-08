# Agentic RAG 开发准备

*Agent 模块现有代码的复用分级、缺口与开发前置 · status: plan · 2026-10-05；2026-10-07 已核定基线组件抽取，其余为后续计划*

## 本次实现核定

2026-10-07 收回原 Agent 工作树的 `answer_chain.py`、`evidence_pack.py`、
`prompts.py`、`structured.py` 及 `evidence_graph.py` 的委托调用；34 项 Agent
测试与冻结行为快照通过，快照未重新生成。源码以代码地图和模块 README 为准。

下文的抽取任务、旧函数名与行号描述开发前状态；这四个组件的抽取现已完成。
稳定跨轮标签、丢弃记录、检索适配器、迭代控制器和真实 Agentic 评价仍未完成，
不因本次合并而升级为已实现。本次没有调用真实模型或外部网络服务。

## 范围与关系

阶段划分、消融编号和指标口径以 [Agentic 研究开发计划](../../Agent-Harness/docs/agentic-research-plan.md) 为准；模块断点见 [接入评估](harness-integration-assessment.md)。本文只把计划中 **P1（连接现有图）** 与 **P4（领域控制器）** 落到 `Agent/` 的具体代码上，不涉及 Harness 执行器（P2）和模型工具协议（P3）。

原则：现有 `EvidenceGraph` 冻结为基线 `G-existing`，只做保持行为的抽取；迭代取证是新增路径，不在原图上加分支。

## 现有代码复用分级

| 组件 | 位置 | 处理 | 理由 |
| --- | --- | --- | --- |
| 固定图整体 | `evidence_graph.py` `EvidenceGraph` | **冻结为基线** | 消融需要原行为作对照；不改名为 A1 |
| 引用规则 | `policy.py` `validate_draft` | **直接复用** | 与取证策略无关，已有 3 个测试 |
| 结构化生成/修复 | `_structured_generate`、`_structured_verify`、`_repair_structured`、`_parse_structured` | **抽出为 `structured.py`** | 控制器的 planner / judge 也需要结构化输出 |
| 验证尾链 | `generate_draft → validate_rules → semantic_verify → revise_once → final` | **抽出为可单独调用的答案链** | A4 复用同一验证，保证对照只改变取证 |
| 证据选择与打包 | `_normalize`、`_evidence_pack` | **抽出为 `evidence_pack.py` 并改造** | 上限、合并顺序与标签需要配置化（见下节） |
| Prompt | `_draft_prompt`、`_verify_prompt`、`_revision_prompt`、改写 prompt | **抽出为 `prompts.py` 并标版本** | manifest 要记录 prompt hash |
| 端口协议 | `ports.py` | **保留，只新增端口** | 已有测试与适配器依赖；不改签名 |
| 模型网关 | `model_gateway.py` | 保留 | usage 与工具调用属于 P3 |
| 模型配置 | `config.py` | 保留 | Agentic 策略配置另立，不塞进 `AgentSettings` |
| 外部搜索 | `external_search.py` | 暂不动 | 主消融关闭外部检索 |

## 代码级缺口

| # | 位置 | 现状 | 对迭代取证的影响 |
| --- | --- | --- | --- |
| 1 | `evidence_graph.py:547` | 每次打包都按出现顺序重新编号 `L1/A1/W1` | 跨轮标签不稳定，逐轮 trace 与引用无法对齐 |
| 2 | `policy.py:5` / `evidence_graph.py:550` | 来源前缀映射写了两份 | 新增来源（如分析证据）时容易不一致 |
| 3 | `evidence_graph.py:530` | 来源上限写死 8/5/5 | 动态取证要求可配置 final context cap |
| 4 | `evidence_graph.py:288` | 二次检索结果排在前面再截断 | 本地结果满 8 条时，预检证据被静默挤出且无记录 |
| 5 | `evidence_graph.py:225` | 外部搜索使用原始问题，不用改写后的查询 | 外部开启实验时查询口径不一致 |
| 6 | `ped_contracts.evidence.ModelOutput` | 只有 `content` 与 `model` | 无 token usage，Efficiency 指标无法计算 |
| 7 | `evidence_graph.py:409` | trace 只经 `emit` 回调，`__trace__` 字段随意 | 没有 seq / run / call 身份，不能离线复算 |
| 8 | `evidence_graph.py:415` | 取消只在阶段开始检查 | 长检索或模型调用不能中断 |
| 9 | `evidence_graph.py:59,137` | `previous_evidence_ids` 写入但未使用 | 多轮会话不能重新载入证据 |
| 10 | `external_search.py:199` | 网页 evidence_id 只由 URL 生成，正文截断 12000 字 | 同一 URL 内容变化后 ID 不变而 hash 变化 |
| 11 | `Knowledge-Base/.../retrieval/__init__.py:232` | `retrieval_is_sufficient`：两份不同资源或标题/DOI/文号完全匹配 | 只能作对照策略，不能作充分性判断 |
| 12 | `VerificationSummary.status` | 只有 verified / rules_only / insufficient_evidence | 没有 budget_exhausted / no_gain；先放在 Agent 本地结果中，不改契约 |

## 拟定结构

```text
Agent/src/ped_research_agent/
  evidence_graph.py        # 基线 G-existing，行为冻结
  policy.py                # 唯一来源前缀映射
  structured.py            # 抽出：结构化生成/验证/修复
  evidence_pack.py         # 抽出：选择、稳定标签、打包、丢弃记录
  prompts.py               # 抽出：prompt 文本 + 版本 ID
  answer_chain.py          # 抽出：草稿 → 规则 → 语义 → 修订
  agentic/
    state.py               # RequirementPlan、DecisionState、RoundRecord、StopReason
    policies.py            # Planner / SufficiencyJudge / QueryStrategy 协议
    controller.py          # 有预算的迭代取证循环
experiments/agentic-baseline/adapters/
  knowledge.py             # HybridRetriever → LocalEvidenceRetriever（P1）
```

适配器先放在 `experiments/`，Agent 不导入 Knowledge-Base。控制器建议用**普通 async 循环 + 显式状态**，不复用 LangGraph：状态需要逐轮记录和离线 replay，图编译的状态合并会让这些更难核对。基线继续用 LangGraph。

## 接口草案

以下为说明性签名，字段以实现时的固定案例为准。

```python
class StopReason(StrEnum):
    QUALITY_SUFFICIENT = "quality_sufficient"   # 必要事实均有支持
    NO_GAIN = "no_gain"                         # 连续无新增支持
    BUDGET_EXHAUSTED = "budget_exhausted"       # 硬上限
    TOOL_FAILURE = "tool_failure"
    CANCELLED = "cancelled"

class Requirement(BaseModel):
    requirement_id: str
    text: str

class RequirementSupport(BaseModel):
    requirement_id: str
    status: Literal["supported", "partial", "missing", "unknown"]
    evidence_ids: list[str]
    rationale: str

class RoundRecord(BaseModel):
    round_index: int
    queries: list[str]
    returned_ids: list[str]
    new_ids: list[str]
    duplicate_ids: list[str]
    dropped_ids: list[str]          # 被 context cap 挤出的证据
    support: list[RequirementSupport]
    degraded: bool

class Planner(Protocol):
    async def plan(self, question: str) -> list[Requirement]: ...   # 不接收 Gold

class SufficiencyJudge(Protocol):
    async def judge(
        self, requirements: list[Requirement], evidence: list[EvidenceItem]
    ) -> list[RequirementSupport]: ...

class QueryStrategy(Protocol):
    async def next_queries(self, state: DecisionState) -> list[str]: ...
```

Planner、Judge、QueryStrategy 都提供规则版与模型版，规则版用于测试和对照。`AgenticResult` 包含 `answer: AnswerDocument | None`、`state: DecisionState`、`stop_reason` 与 `outcome`；只有质量停止后答案链通过才可标 verified。

## 先写的固定案例

全部用伪造 retriever / gateway，不调用真实模型。

| 案例 | 期望 |
| --- | --- |
| 基线快照 | 抽取前后，同一伪造输入的阶段序列、证据 ID 与答案完全一致 |
| 重复 chunk | 第二轮只返回已有 ID → 记为 duplicate，coverage 不变 |
| 无关的两份资源 | 规则版 judge 不判充分；作为与 `retrieval_is_sufficient` 的对照 |
| 连续两轮无增益 | `stop_reason=no_gain`，不生成 verified 答案 |
| 预算耗尽 | `budget_exhausted`，即使已有证据也不标 verified |
| 跨轮标签 | 同一 evidence_id 在各轮保持同一标签 |
| 证据挤出 | 超出 cap 的 ID 进入 `dropped_ids`，不静默消失 |
| 检索降级 | `degraded` 逐轮保留；所有索引失效抛错，不当作零命中 |
| Gold 隔离 | planner 输入只含问题文本 |

## 开发顺序

1. 补基线快照测试，锁定 `G-existing` 行为。
2. 抽出 `structured.py`、`prompts.py`、`evidence_pack.py`、`answer_chain.py`，`EvidenceGraph` 改为调用它们；Agent 测试保持全部通过。
3. P1：`experiments/agentic-baseline/adapters/knowledge.py`，固定查询跑通基线（依赖 P0 冻结的索引快照）。
4. `agentic/state.py` 与规则版策略，先完成上表案例。
5. 模型版 planner / judge / query strategy，复用 `structured.py`。
6. 控制器接入答案链，产出 `AgenticResult` 和逐轮记录。

每步先运行 `pytest Agent/tests -q`；步骤 3 改动跨模块，再运行全套测试。

## 待决问题与 P0 风险

- **planner / judge 模型**：与答案模型同一路由，还是单独配置？影响成本归因。建议首版与 verify 模型共用，单独计量。
- **usage 记录位置**：扩展 `ModelOutput` 会改变共享契约。建议先在 Agent 内包装，稳定后再下沉。
- **跨语言查询**：104 篇活动语料 `language` 全为 `en`；Gold v5（`questions_full_candidate_v5.jsonl`）每个意图都有 en / zh 成对问题，各 140 条。中文变体对英文语料的词法检索基本无效，主要依赖多语言稠密向量（旧 31 问 Pilot 全为中文，曾测得 FTS-only recall@5 仅 0.48）。迭代控制器的 QueryStrategy 可把“中文问题 → 英文检索查询”作为一种改写策略，但必须按语言分开报告，并与原始查询做配对对照，不能把语言改写的收益算成迭代取证的收益。
- **活动索引与代码版本**：较早的活动 FTS 索引缺少 analyzer fingerprint，会被当前代码拒绝加载，而 source fingerprint 检查仍然通过。P0 选择快照时要先实际加载一次，不能只看 source fingerprint。
