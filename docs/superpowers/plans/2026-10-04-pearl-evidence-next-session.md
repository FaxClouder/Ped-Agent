# PEARL Layer 2 Evidence 下一会话任务说明

*Retrieval 正式交付后的上下文充分性实验交接 · status: plan · 2026-10-04*

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task. 按阶段执行并报告；本说明不是已经实现的入口或完成的实验。

**Goal:** 复用冻结的 PEARL Retrieval 输入，在开发集上实施并正式交付 Layer 2 Evidence 的上下文组装、证据充分性评价与失败归因。

**Architecture:** 固定 R4 原始 Top-10 child，比较无展开与直接 parent 展开，再进行去重、排序和预算截断。评价保存下来的最终上下文文本；组装器只接收查询、排名和语料，不接收 Gold、答案或支持标签。

**Tech Stack:** 当前仓库 Python 环境、既有 parent-child 资产、冻结检索排名、可复现 tokenizer、独立 Agent 语义评审与程序评分核验。先盘点已有接口再补最小缺口，不另建一套系统。

## 1. 用户指令与验收规则

- 工作目录：`E:\F_Workspace\F-Agent-Paper`。
- 当前任务是 Layer 2 Evidence；不重复执行 Retrieval 阶段 A–D，不进行新的 Retrieval 模型或排名优化。
- 执行[研究评估与审查验收标准](../../research-review-standard.md)：完成规定验证的 Agent 评估就是正式内容。仅用户明确指定的环节需要人工审查；本任务没有额外人工审查门槛。
- 保留原查询、Gold、语料、child、parent、索引、方法配置、排名、输出及历史报告。所有新结果使用独立目录和版本，禁止覆盖。
- 本会话不执行 Layer 3、Layer 4 或 Agentic 实验；为其保存可消费的上下文和评价结果，并交付后续任务建议。
- 不自动提交、推送、合并或清理工作区，不引入 Web 服务或产品基础设施。

## 2. 当前已确认的状态

Retrieval 阶段 A–D 已完成，按当前标准属于正式 Agent 评估。旧字段 `agent_reviewed_preliminary`、`human_verified=false` 如实保留，不表示还需人工核验才能继续。

| 项目 | 当前事实 |
| --- | --- |
| 活跃语料 | 106 篇 Adobe-only 文献，6,433 child；不用历史 108 篇临时资产 |
| 开发集 | 80 个 intent，四类各 20；使用 Gold r02 及其绑定的原排名 |
| 独立 Retrieval 评估 | 200 个 intent，四类各 50；已经运行并交付，不再描述为尚未解封 |
| 开发 CEGR@10 | R1/R2/R3/R4 = 47/49/51/58，分母 80 |
| 200 题 CEGR@10 | R1/R2/R3/R4 = 116/118/126/139，分母 200 |
| R4 题型差异 | 单来源 50/50；数值表格 48/50；同文多片段 31/50；跨文献 10/50 |
| 深层诊断 | R4 Top-100 已知完整 181 题，Top-10 完整 139 题；其余深层未知不能判为没有证据 |
| 后续层状态 | 有方法草案和部分系统接口，不等于已有真实 Layer 2–4 实验结果 |

上述 42 题差距只说明已知证据在较深候选中，不能据此保证 parent 展开有效。本轮仍固定 Top-10；扩展到 Top-100 属于另一项输入深度实验，不能混入展开主对照。

## 3. 开始前按顺序读取

1. [项目 README](../../../README.md)、[AGENTS](../../../AGENTS.md)、[当前架构](../../project-architecture.md)。
2. [Knowledge-Base README](../../../Knowledge-Base/README.md)、[Agent README](../../../Agent/README.md)、[文档导航](../../README.md)、[审查标准](../../research-review-standard.md)。
3. [PEARL 主框架](../../../paper/pearl-framework/PEARL-framework.md)。
4. Layer 2 的 [README](../../../paper/pearl-framework/layer-2-evidence/README.md)、[设计](../../../paper/pearl-framework/layer-2-evidence/design.md)、[指标](../../../paper/pearl-framework/layer-2-evidence/metrics.md)、[展开策略](../../../paper/pearl-framework/layer-2-evidence/expansion-strategies.md)、[标注指南](../../../paper/pearl-framework/layer-2-evidence/annotation-guidelines.md)、[实验草案](../../../paper/pearl-framework/layer-2-evidence/experiments.md)。
5. [开发 Retrieval 入口](../../../experiments/pearl-retrieval-dev80-20261003/README.md)、[Gold r02](../../../experiments/pearl-retrieval-gold-revision-r02/README.md)、[200 题正式分析](../../../experiments/pearl-retrieval-eval200-20261003/evaluation-analysis-2026-10-03.md)。

**旧草案不能直接充当执行配置。** 其中 100/100 划分、parent-child-v2、融合权重和示例 reranker 不代表当前冻结资产；本轮以真实运行清单和 r02 provenance 为准。旧指标中的 Coverage 单调性也不是截断后保证：parent 替换、去重和预算截断均可能造成证据损失。

## 4. 既有输入与新增文件边界

### 既有资产

- 原开发排名：`outputs/pearl-retrieval-dev80-20261003-01/rankings.jsonl`。
- 原开发配置及运行身份：同目录 `run_manifest.json`、`method-R4-manifest.json`、`queries.jsonl`。
- 开发 Gold r02 与绑定记录：`outputs/pearl-retrieval-dev80-gold-r02-20261003-01/`；从实际 revision/delivery manifest 解析选定文件，不靠猜测文件名或选“最新文件”。
- 原 200 题报告与交付清单：`experiments/pearl-retrieval-eval200-20261003/`、`outputs/pearl-retrieval-eval200-20261003-01/`；本輪仅作既有基线，不用于本轮组装策略调优。
- child/parent 正文路径、版本、映射和哈希：从原运行清单追溯核对。不得从当前默认索引悄悄读取不同版本。
- 复用盘点起点：`Knowledge-Base/src/` 中 parent-child 与检索上下文相关实现；`Agent/src/ped_research_agent/evidence_graph.py` 中证据组织；`Agent/src/ped_research_agent/policy.py` 中引用规则。结构核验不等于语义充分性评价。

### 拟新增资产（尚未创建）

| 位置 | 职责 |
| --- | --- |
| `experiments/pearl-evidence-dev80-20261004/README.md` | 实际范围、已实现命令和运行方式 |
| 同目录 `protocol.md` | 指标、组装规则、标注规则、实验矩阵、统计与来源边界 |
| 同目录 `assemble.py` | 最终上下文生成与各步骤追踪；优先调用既有实现 |
| 同目录 `review.py` | 盲化审查材料导出、审查版本选择和导入验证 |
| 同目录 `score.py`、`verify.py` | 指标与配对分析、独立复算、保存产物和 provenance 核验 |
| 同目录 `test_assembly.py`、`test_scoring.py` | 固定算例和关键失败路径 |
| `outputs/pearl-evidence-dev80-20261004-01/` | 新实验结果；若已存在则采用新序号，不覆盖 |
| 实验目录中的 `evidence-analysis-2026-10-04.md` | 实际效果、失败归因、限制与 Layer 3 交接 |

实际执行日期改变时调整新目录日期并记录。本表是任务文件分工，不是声称现有 CLI 已实现；最终 README 只写实际可执行的命令。

## 5. 分阶段任务

### 阶段 A：复用盘点、输入核验与协议冻结

- [ ] 检查工作区状态；列明已有实现、可复用接口和最小缺口，避免重复造轮子。
- [ ] 核对 r02 Gold、原排名、R4 配置、child/parent 与查询身份；保存本轮输入清单与 SHA-256。
- [ ] 固定 R4 Top-10，按既有顺序消费，不重排、不新检索、不用 Gold 控制展开。
- [ ] 冻结下列最小矩阵：C0 无展开、C1 直接 parent 展开；各使用 4,096 和 8,192 token 预算，共四组。C0 与 C1 使用同一查询、排名、tokenizer、排序和预算口径；先比较同预算下的展开，再比较同策略下的预算。
- [ ] 直接 parent 使用冻结正文，缺失时保留 child 并记录；重复 parent 合并一次，按关联 child 的最早排名排序。验证 parent 是否包含关联 child 的关键内容，不能假定替换无损；发现问题保留实际证据并按统一规则处理，不按 Gold 逐题特调。
- [ ] 固定完整序列化格式和 tokenizer 版本，计入标题、来源标签、分隔符；预算按最终字符串实测。优先保留完整单元，超长单元按统一规则截断并记录丢弃部分。
- [ ] 预先冻结充分性、组内 AND/组间 OR、未知与不适用的计分规则；不能观察结果后选更有利口径。

**阶段交付：** 盘点、输入清单和可执行协议。报告后继续阶段 B，无需等待人工批准。

### 阶段 B：合成入口与固定算例验证

- [ ] 先用合成数据验证组装和评分入口，不先消耗真实开发样本做接口调试。
- [ ] 测试同 parent 多 child、无 parent、缺失或漂移正文、空结果、重复 ID、预算边界、长表格和标头/单位被截断；拒绝跨版本混用和已有输出目录覆盖。
- [ ] 保存展开前、去重后及最终上下文，记录源 ID、来源定位、文本哈希、顺序、token 数和截断追踪。
- [ ] 使用人工构造的确定性算例验证：两个必需条件只满足一个时整组不完整；一个完整替代组即可充分；未裁决支持关系保持未知；截断后重新按最终文本判断。
- [ ] 核查输出重新读取后的预算与哈希，不只检验内存结果。这里的“人工构造”指编写固定测试数据，不构成人工语义审查门槛。

**阶段交付：** 合成结果、实际测试命令及通过/失败证据；入口通过后继续阶段 C。

### 阶段 C：20 题真实开发验证

- [ ] 按四类各 5 题选取，共 20 题；在各类内按稳定 intent ID 排序，使用 seed `20261004` 抽样，预先保存选定清单，不按成绩挑题。
- [ ] 用四组配置保存共 80 份最终上下文，保持 Gold 与组装执行隔离。
- [ ] 独立语义审查使用 `fork_turns=none` Agent：只提供查询、必要需求/证据组和匿名化后的实际最终上下文，不提供策略名称、排名、分数、旧判断或未送入上下文的 PDF/parent 补充内容。保留可解释事实所必需的正文和来源关联。
- [ ] Reviewer 直接判断最终文本的支持，不把旧 child 支持标签复制到 parent 或截断后的片段；组装过程中获得但最终未保留的证据不计分。
- [ ] 固定算例与独立评审校验评分口径；分歧保存双方依据并明确选定裁决版本，未知项不强制转为否定或成功。
- [ ] 排除实现、序列化和计分错误；改动影响结果时另存版本、重跑受影响配置，并披露 20 题属于开发诊断。

**阶段交付：** 20 题分析和实际入口。修正明确错误后继续阶段 D；不借此启动 Retrieval 参数搜索。

### 阶段 D：80 题 Evidence 评估与交付

- [ ] 在冻结的最终规则下运行完整 80 题、四组配置，共 320 个上下文单元；20 题诊断样本计入开发集，不声称是另一个独立测试集。
- [ ] 完成最终上下文的独立 Agent 支持裁决与选定清单，保存模型、提示、输入、审查记录及内容哈希。
- [ ] 独立评分实现复算逐题、总体和四个题型结果；核对保存文件、样本分母、未知数量和适用数量。
- [ ] 报告同预算 C1−C0、同策略 8K−4K 的配对差异；预先规定统计和多重比较口径，开发结果不包装为新的确认性独立评估。
- [ ] 报告展开新增的证据、去重/截断丢失的证据、噪声与成本；如称为某一步的损失，必须有该步前后文本的支持依据。
- [ ] 保存输入与输出 manifest、代码/配置版本、独立复算、测试证据、旧资产保存核验和中文适配分析；更新维护文档导航。
- [ ] 最终报告明确“正式 Agent 评估”，说明开发集用途；交付后停止本轮，不直接推进 Layer 3/4。

## 6. 指标和归因要求

| 指标/记录 | 本轮用途 |
| --- | --- |
| Complete Group Coverage | 主指标：最终上下文至少完整支持一个允许证据组的 intent 比例 |
| Evidence Coverage | 辅助：按冻结的证据组规则报告必要需求覆盖，避免混合不同替代组制造完整性 |
| Context Relevance / Noise Ratio | 辅助：提前固定文本单元、标签及分母；不能将 token 占用率冒充语义噪声，不默认两者互为补集 |
| Sufficiency 判断性能 | 只有实现了独立系统预测才报告准确率等；不能把参考裁决本身当预测，或直接令预测等于 Gold |
| 成本 | 实际上下文 token、组装时延、评审调用和 token；模型不可用时如实记录，不伪造模型实验 |
| 失败归因 | 原始 child 不充分、parent 新增支持、替换/去重/截断损失、最终仍不足、尚未裁决分别报告 |

未知项的指标范围、上下界或有效样本口径须在阶段 A 写定，并同时展示总样本数；不能通过删除困难未知样本只报告乐观成绩。引用来源正确也不能替代“该文本支持这个条件、数值或结论”的判断。

如父正文能补证，只提高 Layer 2 指标，不追改 Layer 1 CEGR。组装器不得读取评分标签，也不得针对每题利用参考答案选 parent 或裁剪正文。

## 7. 200 题及后续层边界

本轮先交付完整开发 Evidence 实验。原 200 题 Retrieval 结果已被查看；若后续针对这些弱点调优后在相同题集评价，应明确探索性用途。新的确认性结论另行冻结新留出集和配置，正式 Agent 评估标准不改变数据独立性。

本轮不新运行 200 题 Evidence、不创建新题集，也不启动生成器实验。交付时说明 Layer 3 如何消费固定上下文及其充分性标签；后续将实际上下文与独立复核的完整参考上下文分组对照，区分证据不足与读错证据，但该对照尚未执行。

## 8. 完成标准与验证命令

完成须具备：80 题 × 四组最终上下文、实际审查与未知记录、独立评分复算、总体及分题型表、证据增损归因、成本、完整 provenance 和旧输出未改动的证据。仍无法裁决的项目如实报告，不因缺少人工审查而停止交付。

先运行新增实验的定向测试；若变更跨 Contracts/Agent/Knowledge-Base 契约，再运行仓库全套：

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python -m pytest Contracts/tests Agent/tests Knowledge-Base/tests Video-Analysis/tests -q
```

不为不存在的 CLI 预写“已通过”结论。最终 README 列实际命令、实测输出和限制；计划条目完成情况与运行结果分开记录。

## 9. 可直接复制到新会话的启动消息

```text
工作目录：E:\F_Workspace\F-Agent-Paper
请读取 docs/superpowers/plans/2026-10-04-pearl-evidence-next-session.md，按阶段执行 PEARL Layer 2 Evidence 任务。
Retrieval 阶段 A–D 已完成，不重复执行；保留原 Gold、配置、排名、语料和旧输出。
按 docs/research-review-standard.md，完成规定验证的 Agent 评估就是正式内容，本任务不要求人工审查。
先盘点现有实现和协议偏差，固定 R4 Top-10，验证无展开/直接 parent 展开与 4K/8K 预算；合成入口通过后做 20 题开发验证，再交付完整 80 题 Evidence 评估和中文分析。
各阶段完成时报告并继续下一阶段；本轮不运行新的200题评估，不调优Retrieval，不执行Layer 3/4。完成Evidence后汇报并停止。
```
