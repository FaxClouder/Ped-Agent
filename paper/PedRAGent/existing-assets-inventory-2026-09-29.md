# PedRAGent 既有产物盘点与复用边界

*2026-09-29 仓库现状核查 · status: current；这是资产盘点，不是新系统设计或实验结果发布。*

## 1. 范围与结论

本次围绕已确认主线盘点：固定文献库内的领域文献 Agentic RAG，重点是跨文献综合与条件比较；视频联合分析和研究方法建议属于后续扩展。

核查现存代码、模块 README、目标设计、实验脚本及已保存输出；未运行模型、重建索引或重新执行实验，未读取 sealed test 题目。代码存在不等于真实端到端效果已验证，旧报告中的成绩也不等于本次复测。

结论：检索、来源追溯、断言引用、核验和实验基础可复用；证据槽位、条件缺口和比较问答已有明确目标设计，不能再作为全新方案从头设计。当前需要补齐的是这些目标的实现与适配主线的评价数据。

## 2. 已实现代码

| 能力 | 现存入口 | 核查结果与复用边界 |
| --- | --- | --- |
| 文献检索底座 | [Knowledge-Base README](../../Knowledge-Base/README.md)、[检索实现](../../Knowledge-Base/src/ped_knowledge/retrieval/__init__.py) | 已有 BM25、Dense、RRF、可选 rerank、每文献片段上限、索引兼容与降级检查。继续复用；V1 是默认，V2 是候选，不能把候选当成更优基线。 |
| 父上下文 | [HybridRetriever](../../Knowledge-Base/src/ped_knowledge/retrieval/__init__.py) | 已返回 `parent_contexts`，无需重新实现父文本取回。但 Agent 的 `RetrievalBatch` 未包含该字段，证据打包也未原生消费此映射；跨模块接入仍需明确。 |
| 证据与回答契约 | [evidence.py](../../Contracts/src/ped_contracts/evidence.py) | 已有 EvidenceItem、AnswerClaim、CitationRef、InferenceItem、AnswerDraft、AnswerDocument、SemanticReview。来源 ID、版本、chunk、定位、内容哈希和引用绑定已有基础；内容哈希不应未经核查当作源 PDF 哈希。 |
| 固定证据工作流 | [evidence_graph.py](../../Agent/src/ped_research_agent/evidence_graph.py) | 已有初次检索、按需外部搜索、查询改写、再次检索、合并、草稿、规则核验、语义核验、一次修订及失败出口。适合作为既有工作流对照的起点。 |
| 引用与推断约束 | [policy.py](../../Agent/src/ped_research_agent/policy.py)、[工作流提示词](../../Agent/src/ped_research_agent/evidence_graph.py) | 已检查断言与引用双向绑定、证据 ID、正文引用标记；推断单列并绑定依据。无需另起一套引用格式。 |
| 模型端口与结构化输出 | [ports.py](../../Agent/src/ped_research_agent/ports.py)、[model_gateway.py](../../Agent/src/ped_research_agent/model_gateway.py) | 已有生成/核验端口，工作流支持结构化响应及 JSON 修复。可复用适配层；本次未执行外部模型。 |
| 工作流追踪 | [evidence_graph.py](../../Agent/src/ped_research_agent/evidence_graph.py)、[运行指标契约](../../Contracts/src/ped_contracts/evidence.py) | 已有阶段事件、耗时及证据/核验/修订指标；不等同于完整的逐轮需求、增量覆盖、停止原因和 token 成本账本。 |
| 检索评价 | [gold_v2.py](../../Knowledge-Base/src/ped_knowledge/evaluation/gold_v2.py)、[开发集实验](../../experiments/benchmark-gold-20260923/README.md) | 已有旧口径的证据组、定位评价及双语开发集入口；其版本与定位校验经验可供参考。PEARL 须使用新 Gold 和新评分器，不能沿用旧标签、评分逻辑或结果。 |

### 当前工作流的实际限制

- KB 的 `retrieval_is_sufficient` 用“两种资源”或精确匹配标题/DOI/文号判断充分性；它不是比较条件的覆盖判断。Agent 读取检索端口返回的布尔值，本次未确认端到端适配如何生成该值。
- 查询改写当前是将问题转换为独立检索问题，未输入结构化证据缺口；不能描述成按缺口定向改写。
- 当前修订使用原证据修改答案，不会再次检索；一次修订不是多轮补证。
- 无证据时返回不足说明；核验失败且一次修订无效时抛出 `VerificationFailed`。不能统称为成熟的限定回答与拒答策略。
- 固定文献库实验需要显式隔离外部搜索。既有图按 `sufficient` 分支进入外部搜索，不可直接把原流程称为封闭语料实验。

## 3. 已有设计，不应重复提出

| 设计资产 | 已经明确的内容 | 当前边界 |
| --- | --- | --- |
| [2026-09-22 知识库设计](../../docs/superpowers/specs/2026-09-22-memped-knowledge-update-design.md) | P7 按问题证据槽位及引用支持度判断充分性；ResearchCard 包含 conditions、evidence_refs、依赖和版本；冲突 finding 保留来源与条件；原文外推导放入 inference。 | target；ResearchCard 完整实现未在本次检索的业务代码中发现。 |
| [同日实施计划 §11 P7](../../docs/superpowers/plans/2026-09-22-memped-knowledge-update.md) | 比较题缺条件/单位时明确缺口；上下文去重与 token 预算；parent 补证；外部检索不得改变冻结本地 benchmark；支持度、条件错误及拒答评价。 | plan；列出的 `Agent/.../coverage.py` 和对应测试尚不存在，不能认为 P7 已完成。 |
| [PEARL 主框架](../pearl-framework/PEARL-framework.md) | 检索→充分性→答案→忠实/拒答，Agent 控制器和成本维度；领域条件与单位；多轮公平比较；逐轮 query、增量证据和停止理由。 | target；是现有评价总框架，应继续沿用。 |
| [Layer 2](../pearl-framework/layer-2-evidence/README.md) | 父上下文展开、Evidence Coverage、Sufficiency Accuracy、噪声及层间归因。 | 细则和上下文充分性标签待补；固定展开与 Agent 动态动作需在不同实验配置中明确区分。 |
| [Layer 5](../pearl-framework/layer-5-agentic/README.md) | 需求覆盖、逐跳成功、过早停止、过度检索、改写增益；A0–A4 消融梯度。 | 逐轮记录、分母、观测时点及多证据子集仍待定义。 |
| [Harness](../../Agent-Harness/README.md)、[协议](../../Agent-Harness/src/ped_agent_harness/protocols.py) | 已有工具 schema、调用/结果、注册与执行等协议设计。 | 实现主要是协议与包骨架；不应按 README 中的规划目录推断已有 registry/executor/runtime。 |

此前讨论的“证据表”与既有 ResearchCard/证据槽位设计重合；“停止条件”与 PEARL Layer 5 重合；“引用核验与推断分离”已有实现。后续应做字段和行为差异对照，避免平行维护第二套概念。

## 4. 仍在本地的实验和标注产物

| 资产 | 入口 | 可复用内容及限制 |
| --- | --- | --- |
| 104 篇索引实验 | [索引实验](../../experiments/benchmark-index-20260924/README.md)、~~V1 目录~~、~~V2 目录~~ | 索引构建脚本可复用；V1/V2 索引目录已迁至 `../../failed/outputs-void-scores/`（PEARL 退出该评测口径；见 `../../failed/README.md`）。 |
| ~~P1 检索候选对照~~ | ~~`outputs/gold-v5-dev-p1-synthesis-20260926-03/README.md`~~ | **已作废** — 迁至 `../../failed/outputs-void-scores/`；评分语义与 PEARL 相反。 |
| Stage 2 开发标注 | [说明](../../experiments/stage2-annotation/README.md)、[标注](../../outputs/stage2-agent-adjudicated-20260927-03/annotations.jsonl)、[manifest](../../outputs/stage2-agent-adjudicated-20260927-03/manifest.json) | 实读 20 条：18 条 agent 候选、2 条争议；18 条包含 36 条必要事实。字段组织可供新标注设计参考，但旧题目和标签不进入 PEARL。`answer_type`、`requires_multi_hop` 均为 0/20 已填，`numeric_constraints` 为 4/20；全部不是人工 Gold。 |
| P2 解析敏感性 | [交付清单](../../experiments/benchmark-parser-sensitivity-20260927/DELIVERABLES.md)、[综合 summary](../../outputs/parser-sensitivity-p2-synthesis-20260927-01/summary.json) | 解析、检索、综合三个产物目录仍在；已保存资源/页/文本/parent 定位指标。可复用诊断和脚本，本次没有重新执行 Adobe、BGE-M3 或 GPU。 |
| 解析证据锚点 | [开发集锚点](../../experiments/benchmark-parser-sensitivity-20260927/evidence_anchors_dev.json) | 已有比资源级召回更细的文本定位实验输入，后续充分性研究应先检查这些产物。 |
| ~~Stage 1 分析代码~~ | ~~`experiments/stage1-analysis/analyze_stage1.py`~~ | **已作废** — 迁至 `../../failed/stage1-analysis/`；输入路径缺失。 |

### 开发集与当前主线的差距

对 Stage 2 的 18 条 `agent_reviewed_candidate` 实际统计：每题都只有一个候选证据组；必要事实每题来自一个文献、一个页码。36 条事实不等于 36 个跨文献问题。`requires_multi_hop` 等预留字段不能当作已经完成的多跳标注。

因此现有题目仅可用于旧口径的探索性基础问答、检索和引用对照，不能直接证明跨论文比较或动态补证收益，也不构成 PEARL 新题集。应保留现有数据版本，按新协议另行设计和版本化题目；不动旧 sealed test 来迎合当前方案。`rgq-015` 的多页公式定位争议保留在旧数据记录中，不作为新 PEARL 的已验证多页样本。

## 5. 已核实的文档偏差

1. **论文导航含失效目标。** `paper/README.md` 引用的 `evaluation-reports/`、`F-Report/`、`latex/`、`llm-pedestrian-literature/` 和 `memped-rag-design-summary.md` 在本次检查时均不存在。它们不是已确认可复用的现存资产；本次不推断丢失原因，也不把现有 outputs 当作原文件的完整恢复。**已完成修复：`paper/README.md` 和 `docs/README.md` 已标记失效路径并指向 `failed/` 目录。**
2. **旧首页定位说法已退出现行协议。** 此前的 15/18 不再出现在现行 PEARL Layer 1 文档。按 Stage 2 `required_facts[].source_locator.pdf_page_1based` 复核，18 条 `agent_reviewed_candidate` 中有 14 条的必要事实均定位在 PDF 第 1 页，其余四条分别定位在第 5、12、13、15 页。该数字仅描述旧开发标注，不是新 PEARL 的题型分层或成绩。
3. **证据组与定位结构不同。** 既有 Gold 评分是组间 AND、组内替代 OR；其评分器读取 `alternatives[].locator.page_index`，Stage 2 则记录 `required_facts[].source_locator.pdf_page_1based`。PEARL 使用完整组内 AND、可替代组间 OR，并另建来源锚点和支持映射；旧字段不能直接交给旧评分器，也不能靠字段转换把旧数据变成 PEARL 评估输入。**已迁移：41 个 Gold v* 评分目录迁至 `failed/outputs-void-scores/`。**
4. **截断和样本范围不同。** 旧开发实验主要按前 5 个去重资源评分，覆盖 20 个开发 intent；新 PEARL Layer 1 计划按原始前 10 个 child 的内容评分，新建 80 个开发 intent 与 200 个独立评估 intent。新题集尚未构建，不能把旧 18 条无争议候选当作 PEARL 分母或将旧汇总分数转成新成绩。
5. **旧查询数量的分母不同。** Stage 2 的 40 条中英查询来自 20 个 intent 各两种语言；18 条无争议候选若只统计其双语问法则为 36 条，另有 36 条必要事实／证据组映射。三种计数须分别标明对象。新 PEARL Retrieval 每个新 intent 使用一条英文主查询，不沿用这两个旧查询数。
6. **旧人工审核表述不一致。** P1 输出 README 写”下一轮人工核验后”，较新的 Stage 2 说明允许 agent 复核标签用于探索性研究。人工 Gold 是独立质量声明，不应重新成为当前开发研究的默认门槛。
7. **完成报告不能替代状态核查。** P2 交付文档称代码已纳入版本控制，但本次 `git status` 显示该实验目录仍为 untracked。文件存在、测试记录、Git 归档和真实实验完成是不同事实。

## 6. 后续复用顺序

1. 以当前 Contracts、HybridRetriever、EvidenceGraph 为实现基础，沿用其测试与端口。
2. 以 9 月 22 日 P7 为功能起点，逐项核对条件槽位、上下文预算、补证和封闭语料适配的缺口。
3. 以 PEARL Layer 2/5 和 A0–A4 为评价起点；原固定工作流可作为补充对照，不替代既有消融体系。
4. 参考 Stage 2 的事实映射结构与 P2 的定位方法，为 PEARL 新建证据标注；新增跨文献比较题时保留来源、条件和不支持的推断。
5. 当前盘点不决定引入新运行框架或多 Agent，也不启动新的实现或实验。

## 7. 核查记录

- 只读检索代码/文档/实验目录，检查指定路径存在性，并统计开发标注。
- Stage 2 `annotations.jsonl` 的 SHA-256 与同目录 manifest 记录一致。
- 新增盘点文档的相对链接单独检查；第 5 节缺失资产仅作文本记录，不构造失效链接。
- 本次未运行测试套件或任何真实模型实验，因此不作“当前测试全通过”或“结果已复现”的声明。
