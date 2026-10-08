# PEARL Retrieval 的方法来源与使用边界

*新 Retrieval 协议的文献与官方实现依据 · status: plan · 核验日期：2026-09-29*

本页说明各来源支持哪些设计，以及 PEARL 自行规定哪些规则。指标定义以
[Retrieval 指标](../layer-1-retrieval/metrics.md) 为准，比较配置以
[实验设计](../layer-1-retrieval/experiments.md) 为准，层间归因以
[主框架](../PEARL-framework.md) 为准。来源中的实验成绩不构成本项目结果。

## 1. 证据标注与指标

| 来源 | 已核验的方法内容 | PEARL 的采用范围与边界 |
| --- | --- | --- |
| [FEVER 2018 官方任务与计分规则](https://fever.ai/2018/task.html)，Task Definition／Scoring | 多个句子可共同构成证据，取得至少一套完整标注证据即可满足证据要求 | 支持完整替代证据集合的思路；PEARL 的 CEGR 只评价检索，不含 FEVER 的分类正确性条件，也不继承其句子粒度或 Top-5 设置 |
| [RARE，ACL 2026](https://aclanthology.org/2026.acl-long.923/)；[官方 PDF](https://aclanthology.org/2026.acl-long.923.pdf)，§3.6、§5.1，PDF 第 6–7 页 | required information 定义在 chunk 层级；Coverage@K 测量 Top-K 覆盖必要信息的比例，PerfRecall@K 测量全部必要信息是否齐备。Gold 包含原始段落和冗余追踪发现的语义等价替代 | 借鉴部分覆盖、完整证据及等价替代的区分。RARE 的文字定义没有规定 PEARL 的 source-span Gold、DNF 充分证据组及组间聚合公式 |
| [KILT，NAACL 2021](https://aclanthology.org/2021.naacl-main.200/)；[官方 PDF](https://aclanthology.org/2021.naacl-main.200.pdf)，§2、§5 | provenance 是知识源中的文本跨度；允许多个有效 provenance 集合。论文主检索评测采用 Wikipedia 页面级 R-precision 和 Recall@k，脚注说明脚本也支持更细粒度 | 借鉴来源锚定和替代证据集合。PEARL 将稳定 source span 与各切块配置的输出 ID 分开保存；切块映射与内容命中规则由 PEARL 定义。KILT 的页面级实验不支持“同页即内容命中”的推断 |

PEARL 的证据逻辑为**组内 AND、组间 OR**：一组列出共同充分的必要证据，完成任意一组即可满足该题的完整检索判定。Gold 锚定来源跨度，并按被比较配置重新核验到返回内容的映射。该设计采用独立名称，避免把更换了证据结构和分母的指标表述为 RARE 同口径复现：

| PEARL 名称 | 本协议测量的对象 | 文献关系 |
| --- | --- | --- |
| CEGR@K | Top-K 是否完成至少一个充分证据组，再按题汇总 | 受完整必要信息检索思想启发；不是直接复现 RARE PerfRecall@K |
| BestGroupCov@K | 对每个充分组计算覆盖比例，取单组内的最大覆盖 | PEARL 对替代充分组的聚合定义；不是 RARE Coverage@K 的原名或原公式 |
| CompleteMRR@K | 首次完成任意充分组的排名倒数，再按题汇总 | PEARL 的完整证据排序指标；不等于首个相关 chunk 的标准 MRR |

原始 Top-K child 内容与最终组装上下文分别观察、同页定位仅作诊断、parent 补证不追改原始检索命中，以及 Layer 1/2 四态归因，均为 PEARL 的操作规则。上述来源提供方法动机，不能替代本协议的明确定义。

## 2. 检索融合与模型候选

### RRF

[Cormack、Clarke 与 Büttcher，SIGIR 2009，作者公开原文](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf)
给出的融合分数为：

\[
\operatorname{RRFscore}(d)=\sum_{r\in R}\frac{1}{k+r(d)}.
\]

原文用从 1 开始的完整排列定义排名；参数 \(k=60\) 在先导实验中选定，随后验证保持不变，论文将其描述为该实验中的近优选择。它不是对所有语料成立的最优常数。PEARL 可将 `rrf_k=60` 设为预先声明的实验候选，并记录候选深度与并列排名规则。

对于截断检索列表，PEARL 明定只累加包含该候选的列表：候选在某路列表缺席时，该路贡献为 0。这是本协议的显式实现约定；[Elasticsearch 官方 RRF 文档](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion) 中的条件累加伪代码也采用该处理。不得给缺席候选填入一个有限的“末位排名”后额外加分。

### BAAI 模型

| 实验候选 | 官方来源 | 本轮使用范围 |
| --- | --- | --- |
| R2：`BAAI/bge-m3` | [BAAI 模型卡](https://huggingface.co/BAAI/bge-m3) | 只用 dense 输出。模型本身还支持 sparse 与 multi-vector；这些能力不自动纳入 R2。模型卡的多语言能力不构成本轮跨语言检索主张 |
| R4：`BAAI/bge-reranker-v2-m3` | [BAAI 模型卡](https://huggingface.co/BAAI/bge-reranker-v2-m3)；[BGE-M3 对 cross-encoder 重排的说明](https://huggingface.co/BAAI/bge-m3) | 对 query–passage 对联合编码并输出相关性分数，作为 cross-encoder 重排候选；实验须固定输入截断、候选池和模型版本 |

上述名称表示计划中的比较配置。本页仅核验官方说明，没有下载模型、执行 embedding 或 reranker 推理，也没有验证其领域效果。模型实际 revision、权重 SHA-256、精度与运行参数应由实验记录另行冻结。

## 3. Pooling 与未判定证据

[TREC 官方 Overview，§2.1.3](https://trec.nist.gov/pubs/trec33/papers/overview_33.pdf)
说明 pooling 将多个检索 run 的高位结果合并后交给评审；它是控制标注成本的抽样办法，并不保证穷尽相关证据。文中也指出，传统指标把未判定内容按不相关处理可能在浅池条件下产生偏差。

PEARL 据此记录 pool 来源、深度、判断状态和新增有效替代证据。`unjudged` 与明确的负例分开保存，未判定候选的计分及补审办法在实验前固定。采用 pooling 不能证明“未收入 Gold 的内容均不支持答案”，也不能证明替代证据已全部发现。这些处理是 PEARL 针对标注不完备性的协议选择。

## 4. 统计实现依据

| 官方实现文档 | 可核验的能力 | PEARL 需自行冻结的设计 |
| --- | --- | --- |
| [statsmodels `mcnemar`](https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html) | 配对二值结果可用精确二项版本检验边际同质性 | 主指标二值、intent 独立性、不一致方向假设及预设比较；未满足假设时不能仅凭库能运行就作推断 |
| [SciPy `bootstrap`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html) | `paired=True` 对各方法使用同一重采样索引；可指定区间方法、置信水平和随机数生成器 | 抽样单位、题族依赖、区间方法、重采样次数与种子；库默认值不自动成为协议 |
| [SciPy `permutation_test`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html) | 提供配对样本的置换方式及精确或随机置换检验 | 零假设、可交换单位、比较方向与置换次数；不能忽略同源题目的依赖 |
| [statsmodels `multipletests`](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html) | `method="holm"` 提供逐步 Bonferroni 多重检验校正 | 预先声明比较族；不能按结果选择纳入哪些比较 |

这些文档用于核验后续实现接口，不构成 PEARL 样本独立性、检验假设或统计功效的证明。

## 5. 其他相关方法

| 来源 | 方法关联 | 使用边界 |
| --- | --- | --- |
| [ARES，NAACL 2024](https://aclanthology.org/2024.naacl-long.20/) | 分别评价上下文相关性、答案忠实性与答案相关性 | 支持区分评价对象；不直接给出 PEARL 的 DNF 命中、parent 归因或四态规则 |
| [S2G-RAG，ACL 2026](https://aclanthology.org/2026.acl-long.1185/) | 显式判断当前证据是否充分，并将信息缺口用于下一轮检索 | 支持将充分性和缺口作为判断对象；其迭代控制器不是 PEARL 静态 Retrieval 主实验的一部分 |
| [OmniEval，EMNLP 2025](https://aclanthology.org/2025.emnlp-main.292.pdf) | 将领域场景、检索与生成分维度评价 | 提供领域评测的组织参考；不作为 CEGR、BestGroupCov 或 CompleteMRR 的原始定义来源 |

本地已收集的论文位于 [RAG-Paper/](RAG-Paper/)。该目录用于阅读，不是新实验所需数据、标签或结果的输入。
