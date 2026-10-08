# Layer 1: Retrieval

*PEARL 英文 Retrieval 协议入口 · status: current · protocol: retrieval-v0.2 · 2026-10-03*

Layer 1 评价预先固定的 Top-K child 文本是否包含问题所需证据，并将有序、可定位的结果交给 Layer 2。评价规则属于 PEARL；BM25、稠密检索、融合、重排及其他算法是具体实验中的候选配置，其改进不改变评价规则。

当前新主实验限定为**英文文献语料和英文查询**。对照实验使用同一批英文 intent 与查询，不把查询翻译或跨语言能力列为主比较；[原文来源快照](../datasets/retrieval-corpus/README.md)已固定，[80 题开发 Gold 与 200 题封存评估 Gold](../../../experiments/pearl-dataset-80-200-20261003/README.md)已完成逐题及全局子 Agent 复核，现有 8 题原样保留。

本轮已构建 **80 个开发 intent＋200 个独立评估 intent**。主指标 CEGR@10，次指标 BestGroupCov@10，排序诊断 CompleteMRR@10；四组为 BM25、dense、RRF、RRF＋reranker。方法配置均属于本次实验，模型选择不改变 PEARL 的指标定义。

## 当前边界

- PEARL 是后续评估工作的框架与方法底座。旧评估题集、标签、索引快照、排名和结果全部退出新实验；不得重算旧结果或直接沿用旧样本数、指标值与基线。
- 新 Retrieval 实验须先固定研究问题、语料和查询划分、证据标注、检索单元、命中定义、截断深度、统计单位与报告规则，再定义算法对照和运行配置。
- 仅改变算法配置时，使用同一版评价输入和指标；改变语料、解析或切块时，应明确哪些比较仍可归因于检索算法，并为受影响的定位标注建立新版本。
- 本层只评价进入 Top-K 的 child 文本。进入 Top-K 本身不算命中；同一资源或同一页上不含目标信息的片段也不算证据内容命中。parent 展开后的上下文充分性归 Layer 2；两层的命中与失败不得混算。

## 已明确的观察口径

| 观察量 | 判定对象 | 用途 |
| --- | --- | --- |
| 证据内容命中 | 原始 Top-K 中一个或多个 child 的文本，是否明确承载新标注的必要事实与适用条件 | CEGR 的组内 AND、组间 OR，及部分覆盖／完成排名，见 [metrics.md](metrics.md) |
| 资源／页定位 | 返回片段是否来自标注资源或覆盖标注页 | 定位诊断；不得代替证据内容命中 |
| 上下文充分性 | parent 展开、去重和预算截断后实际送入生成器的文本 | Layer 2 评价 |

新 Gold 应锚定版本化来源中的证据片段和事实，而非固定 chunk ID。不同解析或切块配置须各自记录可复核的来源到 child 映射。若 parent 补出 child 未含的必要证据，Layer 1 原始观察保持不完整，Layer 2 可记录上下文充分，并单列这一挽回情形。见 [主框架 §2.1](../PEARL-framework.md)；采用内容级而非宽松页级命中的研究依据见 [参考文献](../references/README.md)。

**判定示例**：标注证据在论文第 3 页，而 Top-K 返回该页另一个只谈背景的 child。资源／页定位诊断可记命中，Layer 1 证据内容不命中。若随后展开的 parent 含标注事实及条件，并实际进入生成器上下文，Layer 2 可记为上下文充分；报告中另记 parent 补证，不回填 Layer 1。

## 协议文档

以下五份文件已重写为新协议，替代旧资产草案。106 篇 Adobe-only 来源及统一 child 索引已冻结，[原 8 题 R1–R4 试标](../../../experiments/pearl-index-106-adobe-20260929/README.md#8-题-adobe-only-开发对照)保持可复现。[完整 80 题开发对照](../../../experiments/pearl-retrieval-dev80-20261003/README.md)已完成三遍真实运行、独立实际 child 盲审、统一映射、320 单元计分、开发分析与独立复算。200 题继续封存且未运行；结果质量仍为 Agent 复核初步，不是人工 Gold 或正式评估。早期[单组 R1 试标](../datasets/retrieval-pilot/preliminary-r1-2026-09-29.md)使用另一份 108 篇 PyMuPDF 资产，不能与新结果合表。

| 文件 | 定义内容 | 执行前需落实 |
| --- | --- | --- |
| [design.md](design.md) | 研究问题、证据单位、层间边界和执行顺序 | 新资产和运行准备 |
| [metrics.md](metrics.md) | 三项指标公式、支持组合、缺失规则和固定算例 | 实现评分器、核验支持映射 |
| [experiments.md](experiments.md) | 80/200 配额、四方法、K=10、D=100、manifest 与日志 | 冻结具体来源、版本和哈希并运行 |
| [statistical-methods.md](statistical-methods.md) | 三项预设比较、精确 McNemar＋Holm、配对 bootstrap | 核验样本依赖和实际分层 |
| [failure-taxonomy.md](failure-taxonomy.md) | 处理／索引／候选／排序失败及未决状态 | 保存各阶段文本和排名 |

## 实验准备现状（2026-10-03）

下表以已核验的 PEARL 文档、实验记录和本地输出为依据。方法参考 PDF 是研究依据，不自动构成本轮领域语料。

| 准备项 | 已有内容与入口 | 当前缺口 |
| --- | --- | --- |
| 评价协议 | [指标](metrics.md)、[设计](design.md)：固定 AND/OR、联合 child、空 Gold 与未知深度算例通过；80 题独立公式复算一致 | 正式评估前登记最终评分代码版本 |
| 实验与统计 | [80 题开发报告](../../../experiments/pearl-retrieval-dev80-20261003/development-analysis-2026-10-03.md)：R1–R4、K/D、固定比较、配对 bootstrap 与来源敏感性 | 仅开发诊断；正式统计待独立评估 |
| 英文语料 | [新来源快照](../datasets/retrieval-corpus/README.md)：106 份 Adobe-only 英文领域 PDF、逐份哈希与技术审计；80 题 K≤20 actual child 支持审定 | 21–100 尚有未知支持，处理缺失另行追溯，不声称全库无证据 |
| 新问题与 Gold | [80 开发＋200 封存评估](../../../experiments/pearl-dataset-80-200-20261003/README.md)，四类各 20／50；80 题检索开发对照已完成 | 质量为 agent_reviewed_preliminary；替代完整组 0，目标未达；200 题未运行 |
| 标注质量控制 | 来源锚点、支持组合、provenance、盲化和修订要求；[试标规范](../annotation/retrieval-guideline.md) | 当前由子 Agent 复核；人工审查后置，初步结果不得称为人工 Gold |
| 检索资产 | [106 篇 Adobe-only 统一索引](../../../experiments/pearl-index-106-adobe-20260929/README.md)：6,433 child、FTS 与 BGE-M3 向量；实际加载模型与零截断通过 | [现行 R1–R4 方法配置已单独冻结](../../../experiments/pearl-dev-review-freeze-20261003/README.md)；不扩展解析／切块，完整发布版本仍未冻结 |
| 运行与支持核验 | 80 题首遍 320 单元、三遍排名一致；3,116 条必审关系无未决，共同 mapping 与独立复算通过 | 200 题未运行；D100 未全审，不比较 R3／R4 全深度覆盖不变性 |
| 结果报告 | [80 题开发分析](../../../experiments/pearl-retrieval-dev80-20261003/development-analysis-2026-10-03.md)：主表、分层、预设比较、失败、成本与来源依赖 | 难例原文复核已完成；Gold 修订后需共同重算，正式独立评估未执行 |

按依赖排序的工作、交付物和验收条件见 [实验准备优先级](experiments.md#7-实验准备优先级与验收)。80 题完整开发链路已交付；[七道难例原文复核与现行四方法配置冻结](../../../experiments/pearl-dev-review-freeze-20261003/README.md)已完成。完整发布仍需三处 Gold 表述修订后的共同重算，以及 200 题运行入口适配；200 题保持封存，不参与调参。

## 六项检查的处理结果

| 原问题 | 新协议的处理 |
| --- | --- |
| 1 旧资产绑定 | 所有评估输入新建，manifest 不引用旧题集、索引或排名 |
| 2 页命中／内容命中冲突 | 来源锚定内容支持、DNF 完整组、child／parent 分别观察 |
| 3 实验组／统计单位错位 | 四组共用一个英文 query/intent；80/200 两集分别分析 |
| 4 语言归因过强 | 英文单语实验，归因限于预先定义的方法配置差异 |
| 5 日志不足以分类 | 保存各通道与最终 Top-100、融合 union 和重排映射；超出深度标未知 |
| 6 报告和比较冲突 | CEGR 唯一主指标，固定三项比较；页／资源诊断另表，次指标不替代主检验 |

协议层修复已在 80 题完整开发链路中核验。当前成绩来自 [80 题 Agent 复核开发对照](../../../experiments/pearl-retrieval-dev80-20261003/development-analysis-2026-10-03.md)，原 8 题试标另外保留；方法配置已登记冻结，Gold 修订、完整发布登记及 200 题独立评估仍是 [执行清单](experiments.md) 中后续工作。
