# PEARL 切片变量的研究依据

*Session 1 原始来源核验与可证伪操作定义 · status: current · 2026-10-05；无本轮效果结果*

## 来源与已读范围

从 [既有调研包](../../paper/RAG_Report/README.md)的 literature.jsonl 与 reading_text 定位，未刷新或覆盖旧包。网络核验日期为2026-10-05；本地全文的版本、SHA及实际阅读范围见 [source registry](source_registry.json)。没有执行论文代码或模型复现。

| 来源 | 本次已读 | 本轮用途与差异 |
| --- | --- | --- |
| [Qu等，NAACL 2025](https://aclanthology.org/2025.findings-naacl.114/)；R098 | 原始出版页摘要、全文§2–3开头，PDF pp.1–3 | 比较固定、相邻断点及聚类；支持将成本和不同评价层分开。C4仅保留连续句子，使用BGE-M3、全语料90分位及长度约束；不复现其SpaCy分句、模型、多阈值或聚类实验。 |
| [Dense X v3](https://arxiv.org/abs/2312.06648v3)；调研包Dense-X | 本地PDF pp.1–3，§2及§3开头；原始页面核验 | 粒度影响检索与问答，但命题抽取会生成自包含内容。本轮不抽取命题，不将其效果外推为父恢复效果。 |
| [复杂切片 v1](https://arxiv.org/abs/2608.16586v1)；R089 | 本地PDF pp.1–3，Table 1、§2、§3.1–3.3开头；原始页面 | 提供token、sentence、标题丰富、语义及成本对照线索。论文的文档相关性和模型不同，不能当CEGR或CGC证据；未来会议页眉不当作已召开。 |
| [LangChain recursive splitter](https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter) | 官方介绍与示例参数 | 段落→句子→细粒度回退的工程依据；官方默认以字符计量，本轮用BGE tokens和可逆offset，C2不是原类的逐字复现。文档未固定release，登记访问日期，不假设已安装。 |
| [LangChain ParentDocumentRetriever](https://reference.langchain.com/python/langchain-classic/retrievers/parent_document_retriever/ParentDocumentRetriever) | 官方API说明 | 小单元检索、大单元返回的模式依据；本轮父图独立于child、允许多父、加入来源去重和固定预算，不照搬默认splitter。 |
| [LlamaIndex sentence window源码](https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/node_parser/text/sentence_window.py) | 官方main文件快照的类说明、默认window_size和window metadata构造；文件SHA固定，未获取上游commit | 区分检索单元与恢复窗口。P1是原文段落前后各一段且限小节，不是默认±3句。旧版本示例URL失效，旧API页重定向到概览，未把它们当有效正文。 |
| [Anthropic contextual retrieval](https://www.anthropic.com/engineering/contextual-retrieval) | 2024-09-19官方文章§Introducing/Implementing、方法与rerank部分 | 说明上下文同时影响词法与dense表示；原文以LLM生成说明，本轮M1只使用原文标题/路径，不称复现Contextual Retrieval，也不使用厂商收益数字预测本轮成绩。 |
| [Late Chunking v3](https://arxiv.org/abs/2409.04701v3)；R079 | 本地PDF pp.1–2摘要、引言、Figure 1；原始页面 | 长文编码后池化属于表示阶段。本轮固定独立chunk编码，因此列为后续，不能混入边界网格。 |

## 操作定义、机制与反例

所有数值是预注册选择或实际资产参数，均不是文献证明的最优值。统一来源、表格屏障、标题规则和检索链后再比較。

| 变量 | 操作定义 | 预期机制 | 反例/可证伪结果 | 额外成本与方法差异 |
| --- | --- | --- | --- | --- |
| C1 | 连续规范化正文按BGE tokenizer offsets，core≤256/384/512，尾块保留 | 直接控制粒度，减少无关语义压缩 | 句中切断必要条件、块数增多而CEGR下降 | tokenizer/offset；不是H0正则320窗口 |
| C2 | 完整段落贪心组合，超长段拆句，超长句token回退；允许跨小节 | 保留句内条件与自然段 | 章节换题被混合，短段导致长尾/召回下降 | 边界识别；与字符recursive及V2父内句组合不同 |
| C3 | C2规则限定小节；短小节独立 | 减少跨小节主题干扰 | 条件或定义位于上节，过多短块 | 结构可信度与更多块；不使用新解析器 |
| C4 | 同一分句器+BGE句向量，1−cosine相邻距离，90分位，min=floor(.5L)，max=L | 在自然主题转换处分割 | 指代连续但向量距离高；同主题长句必要条件仍被切 | 句编码一次性成本；项目自定义，无聚类跳句、摘要或阈值搜索 |
| L | 256/384/512为core上限，统计实际分布 | 小块易排序、大块条件更完整 | 完整率不升或推理/建库成本增加 | 同K不等计算量；表格单列 |
| P0 | 实际命中source_text的来源区间并集 | 保持检索证据原样 | 找到主题却缺必要条件 | 基础组装与预算成本 |
| P1 | core命中段落加两侧各一段，限小节/表格屏障，再并入合法overlap | 找回附近条件 | 条件跨小节，重复挤出另一文献 | 组装放大与预算截断；不是相邻chunk |
| P2 | 公共小节父图，连续段落≤1536 BGE tokens，长段句/token回退，多父映射 | 稳定大上下文、不随child策略改变恢复来源 | 父中噪声和放大挤出后置条件 | 公共图一次性成本及逐题放大；不复用H0私有parent |
| O | 固定core，追加≤floor(rL)的连续前文，r=0/.1/.2，整句优先，长句token后缀 | 边界事实能落入一个检索单元 | 恢复已补足且重复增加无收益 | 重建索引及更长模型输入；不重新切core |
| M | M0原文；M1原文标题/路径≤64 BGE tokens，标题和叶节优先 | 词法及向量消歧 | 泛标题压过正文、额外tokens导致模型限长 | BM25+dense+rerank表示共同变化；不宣称单一检索器因果 |

## 五个问题与停点

| RQ | 可证伪比较 | 结论所需证据 |
| --- | --- | --- |
| 1 | C1–C4×L，O0/M0，B0单列 | 新索引真实排名、原始child CEGR@10、分布与成本；无提升也有效 |
| 2 | 同排名P0/P1/P2×4096/8192 | 同面板raw/expanded/final实际支持；找回与截断损失分别计 |
| 3 | 固定core 0/10/20%，P0和预先冻结恢复 | 重检索、新实际来源并集、重复度和CGC；不可拼接旧指标 |
| 4 | 固定core/O的M0/M1 | 新检索表示、正文支持隔离；整体表示效应 |
| 5 | 最多B0/A/B三完整配置，4K主面板，三次真实生成 | 意图内聚合、Layer3/4、新context与答案绑定；上游提升不保证Strict提升 |

LLM切片、命题、摘要前缀、Late Chunking、RAPTOR摘要树、query改写、Agent修订与表格专项仅列后续。Session 1不估计效果、不筛选候选；E0真实模型冒烟仍待Session 2。
