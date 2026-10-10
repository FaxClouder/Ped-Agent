# Ped-Agent：RAG 与 Agentic RAG 评价框架

*PEARL 原始评价设计记录 · status: historical · 2026-09-27*

> 本文件保留旧项目名称与早期评估方案，仅供追溯。后续评估以 [PEARL-framework.md](PEARL-framework.md) 为框架入口；旧评估资产全部退出新实验。

> 版本：2026-09-27。研究范围为行人交通流与疏散科学文献的检索、证据整合及有依据的问答。本文件根据项目 Notion 的[文献整理](https://app.notion.com/p/3e891a0ae63c81929fc2daba56858add)、[统一指标体系](https://app.notion.com/p/3e891a0ae63c8135bc1cf6cc62435339)、[实验安排](https://app.notion.com/p/3e891a0ae63c81198b69d864e396b298)和[研究定位](https://app.notion.com/p/3e791a0ae63c816ea3cfee9a8a93b65b)整理。它是本项目的评估设计，具体阈值和标注细则需在开发集上冻结。

**项目定位：**Ped-Agent 是面向 RAG 与 Agentic RAG 的研究项目和系统主线。PEARL 是为评价 Ped-Agent 制定的流程和指标体系，不是独立系统，也不替代 Ped-Agent 的系统设计。以下六层规定如何检验其证据获取、回答、Agent 决策与代价；本文状态为目标设计，已实现范围须以代码和实验记录为准。

## 1. 评价目标与基本原则

评价链条为 **检索 → 证据充分性 → 答案正确性 → 证据忠实与可靠性 → Agent 决策过程 → 成本**。每一层对应一种可定位的失败：漏检、证据不够、读错证据、无依据推断、错误停止或过度检索、代价过高。

研究问题：

- **RQ1 检索：**解析、切块、稀疏/稠密检索、融合及重排如何影响完整证据的获取？
- **RQ2 回答：**检索改进能否转化为正确、完整且有引用支持的科学回答？
- **RQ3 Agent：**证据需求规划、迭代检索、充分性判断和逐项验证能否改善复杂问题，并控制额外开销？

固定语料、问题划分、生成模型和提示约束。先在开发集选定 **Best Static RAG**，再固定其底层检索器进行 Agent 消融；封存测试集不参与选择模型、阈值或提示。统计单位是 underlying intent，中英问法与改写必须同组划分。

## 2. 数据与 Gold 标注

每个 underlying intent 至少记录：`intent_id`、题型、推理深度、答案类型、语言变体、参考答案及必要 atomic claims、可回答性、条件依赖、冲突状态、Gold evidence groups、等价证据、来源文档及页码。数值题另记单位、合理容差和实验条件；拒答题注明缺失的证据以及为何不足。

一个 **evidence group** 是足以独立支持答案的一组必要证据；组内为 AND，多个可替代组之间为 OR。例如“宽度变化是否影响 specific flow”可能同时要求宽度设置、specific flow 数据及实验条件，而另一篇独立研究可构成替代组。标注应允许不同论文提供同一 atomic fact，不能把唯一指定的页当作唯一正确证据。

建立 claim ↔ evidence 对应：每条参考 claim 标记直接支持页/片段、可接受替代证据、适用条件、可能反例。抽样建立人工精标集，用于校准自动 claim 判断和 LLM judge；人工仲裁应在不知道系统身份的情况下进行。

## 3. 六层指标定义

| 层次 | 指标 | 计算口径和用途 |
| --- | --- | --- |
| Retrieval | **Complete Evidence Group Recall@k** | 对可回答题，若 top-k 检索单元及其按预设规则展开的上下文完整覆盖至少一个 Gold 证据组，记 1，否则记 0；按题平均。主报 @10，辅报 @1/3/5/20。 |
| Retrieval | Recall@k、Equivalent Evidence Recall@k | 前者衡量 Gold 证据单元命中；后者把事先标注的等价文献/事实也视为命中。须写清分母是页、片段还是 atomic requirement。 |
| Retrieval | MRR、nDCG@k | MRR 为首个相关结果排名倒数的题目均值；nDCG 使用固定的相关性等级评价整张排序列表。 |
| Evidence | Evidence Coverage | 已由输入上下文满足的必要 evidence requirements / 全部必要 requirements。可按 atomic requirement 微平均，另报题目宏平均。 |
| Evidence | Sufficiency Accuracy | 系统预测“现有上下文充分/不足”与人工 Gold 一致的比例；同时报告两类混淆矩阵，尤其是把不足误判为充分的次数。 |
| Evidence | Context Relevance、Noise Ratio | 分别评估上下文的相关性，以及进入生成器的无帮助片段或 token 占比；标注单位须固定。 |
| Answer | **Answer Correctness** | 按题型评分：事实题归一化匹配；数值题单位归一化后按容差判对并报 MAE/相对误差；比较和综合题按必要 claims；机制题按预先制定的 rubric。总体宏平均前先把各题型映射到统一 0–1 量表。 |
| Answer | Claim Coverage、Integration Success | 前者为正确覆盖的参考必要 claims / 参考必要 claims；后者专门判断多证据题是否完成跨来源整合。 |
| Grounding | **Faithfulness**、**Unsupported Claim Rate** | Faithfulness：实际回答中获所给检索证据支持的可核查 claims / 全部可核查 claims。Unsupported Claim Rate：未获支持的可核查 claims / 全部可核查 claims。若采用“部分支持”标签，须预先固定其计分规则。 |
| Grounding | Factuality、Contradicted Claim Rate | Factuality 对照 Gold/事实判断结论是否成立；Contradicted Claim Rate 统计与检索证据或 Gold 明确冲突的 claims。事实正确但未被当前证据支持，仍属于不忠实。 |
| Grounding | Citation Precision / Recall | Precision：实际引文中确实支持其对应 claim 的比例；Recall：应由外部证据支持的回答 claims 中，具有有效引文支持的比例。按 claim–citation 配对核验，不能只检验引文是否存在。 |
| Reliability | **Abstention F1**、False Answer Rate | 将“应拒答”设为正类，报告拒答 Precision/Recall/F1。False Answer Rate = 应拒答问题中仍给出确定性结论的题数 / 应拒答题数；同时报告可回答题上的正确率，防止一律拒答。 |
| Agentic | Requirement Coverage、Hop Retrieval Success | 比较 Agent 计划的证据需求与 Gold requirements；逐轮判断所需 hop 是否取得对应证据，仅在有多跳/多证据 Gold 的子集上报告。 |
| Agentic | Premature Stop、Over-retrieval、Query Rewrite Gain | 分别统计证据不足却停止、证据已充分仍无必要继续、改写查询相对于原查询带来的完整证据组召回变化。分母、判定时点须事先固定。 |
| Efficiency | Latency、Tokens、Calls、Rounds | 记录端到端及各阶段延迟、输入/输出 token、上下文 token、LLM 调用与检索轮数；按题型与复杂度报告分布及均值。 |

**重要区分：**Answer Correctness 对照参考答案；Factuality 对照事实/Gold；Faithfulness 对照系统本次看到的证据；Citation Precision 判断所标的来源是否真正支持对应 claim。这四项不能互相替代。对于没有实质性回答 claim 的拒答输出，不把 Faithfulness 人为记为满分；拒答单独评分，回答 claim 指标报告其适用样本数。

### 主表与诊断表

论文主表限定六项：**Complete Evidence Group Recall@10 ↑、Answer Correctness ↑、Faithfulness ↑、Unsupported Claim Rate ↓、Abstention F1 ↑、Latency ↓**。也可以在资源受限场景用 Tokens 替换 Latency，但须保持所有方法口径一致。MRR、nDCG、Citation P/R、hop 指标、数值误差与题型细分放诊断表或附录；不要用 BLEU/ROUGE 或单一 LLM 总评分替代上述指标。

## 4. 实验设计

| 阶段 | 对比与控制 | 主要目的及指标 |
| --- | --- | --- |
| 0. Gold 冻结 | 完成参考答案、证据组、等价证据和 claim 标注；按 intent 分割开发/封存测试 | 保证后续测量有效，校准自动评审 |
| 1. Static RAG | PyMuPDF vs 增强解析；fixed vs parent-child v1/v2；BM25 vs BGE-M3 vs RRF；有/无 Cross-Encoder | 表格/数值定位、Complete Group Recall、MRR、nDCG、延迟。选定并冻结 Best Static RAG |
| 2. 端到端 | No-RAG、Long-Context、Dense/Naive RAG、Best Static RAG、Agentic RAG | 正确性、忠实度、引用质量、拒答与成本；分题型报告 |
| 3. Agent 消融 | A0 No-RAG；A1 Static；A2 +需求规划/分解与迭代检索；A3 +充分性判断及停止；A4 +claim 验证、修订/拒答 | 在同一底层检索器和生成模型下，定位每一步带来的收益与成本 |
| 4. Hop 诊断 | 对多证据、跨论文和冲突题逐轮记需求、query、结果、新覆盖证据、充分性判断及停止原因 | Hop Success、Requirement Coverage、Premature Stop、Over-retrieval、Rewrite Gain |
| 5. 压力测试 | 逐级加入干扰；移除关键证据；加入条件错配/冲突；允许等价证据 | 噪声下性能跌幅、错误拒答/虚假作答、条件感知、冗余证据鲁棒性 |
| 6. 专项与成本 | 表格/数值子集；中文/英文/改写配对；按复杂度画质量–token、质量–延迟曲线 | 单位归一化误差、成对一致性、额外 Agent 成本是否值得 |

建议题型：单来源事实、数值/表格、多证据综合、跨论文比较、机制解释、条件推理、冲突证据、证据不足。行人交通领域特别要核对 density、speed、specific flow、evacuation time、瓶颈宽度、样本规模、测量方法与场景条件；条件不一致时不得直接合并结论。

## 5. 运行与报告规范

1. 固定 corpus/index 版本、解析器、chunk 配置、嵌入模型、reranker、生成模型、提示、top-k、token 预算及随机种子；静态与 Agent 方法使用相同基础检索配置。
2. 每题保存检索排序及页级 provenance、送入模型的上下文、生成答案及 claim–citation 对应。Agent 另存逐轮 query、覆盖变化、充分性结论和停止理由。
3. 报告总体均值及每题型结果、样本数、置信区间；成对比较和 bootstrap 以 **underlying intent** 聚类，不能把同一问题的中英/改写版本当独立样本。
4. 同时报告 answerable 与 insufficient-evidence 子集，区分“正确回答”“正确拒答”“有证据但答错”“证据不足却编造”。对数值、冲突和条件问题提供错误案例审计。
5. 先用开发集校准自动 judge，再抽样人工复核；报告一致性与争议案例。所有阈值、rubric 和缺失值规则在封存测试前写定。

## 6. 当前执行优先级

- **P0：**补全参考答案、atomic claims、claim–evidence 对应、等价证据、充分/不足标签；封存测试集。
- **P1：**跑完解析、切块、BM25/BGE-M3/RRF/重排，冻结 Best Static RAG。
- **P2：**完成端到端回答正确性、Faithfulness、Citation P/R、Unsupported Claim Rate 和拒答评测。
- **P3：**实现 Agent 的需求规划、迭代检索、充分性判断、claim 验证与逐轮日志；做消融、压力测试和质量–成本分析。

**验收问题：**Agent 相较强 Static RAG，在什么类型的复杂科学问题上稳定提高完整证据获取、正确回答与引用支持？这些收益分别来自哪一模块，增加了多少 token、调用与延迟？
