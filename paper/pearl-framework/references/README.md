# 参考文献与相关框架

*PEARL 指标来源与对比框架 · 2026-09-28*

## 目录

| 项目 | 内容 |
| --- | --- |
| [RAG-Paper/](RAG-Paper/) | RAG 评测相关论文 PDF |
| `related-frameworks.md` | 与其他 RAG 评测框架的对比（待撰写） |

## 已引用文献

### RARE (ACL 2026)

`RAG-Paper/2026.acl-long.923.pdf` — *RARE: Redundancy-Aware Retrieval Evaluation Framework for High-Similarity Corpora*，ACL 2026 长文，pp. 20160–20185。

| 引用位置 | 内容 |
| --- | --- |
| §5.1 Evaluation Metrics（PDF 第 6 页） | Coverage@10 与 PerfRecall@10 为主指标；required information 定义在 chunk 层级；使用 redundancy-aware gold labels |
| §5.1 续（PDF 第 7 页） | Coverage@K：Top-K 中检索到的必要信息比例，度量部分成功。PerfRecall@K：全部必要信息进入 Top-K 则记 1，度量上下文是否足以回答 |
| §3.6 Benchmark Construction（PDF 第 6 页） | gold set 含原始段落及通过冗余追踪识别的全部语义等价替代，减少对返回正确但非原始证据的惩罚 |
| 附录 D（PDF 第 17–18 页） | 全指标结果表（Coverage@10、PerfRecall@10、NDCG@10、MRR） |

**被本项目用于口径判断的实测细节**：附录 D 各域的 1-hop 列中，Coverage@10 与 PerfRecall@10 数值完全相同（如 Finance BM25 82.9/82.9、OpenAI-Large 90.1/90.1；Legal BM25 68.8/68.8）。两者仅在 2-hop 及以上分离。这说明单证据单元场景下两指标恒等——当前开发集全为单组单页，等同该场景，见 [layer-1-retrieval/metrics.md](../layer-1-retrieval/metrics.md) §6.1。

RARE 以文字定义两个指标，未给出编号公式。本项目的形式化表达是自行操作化的结果，不声称逐字引自原文。

### OmniEval (EMNLP 2025)

`RAG-Paper/2025.emnlp-main.292.pdf` — *OmniEval: An Omnidirectional and Automatic RAG Evaluation Benchmark in Financial Domain*，EMNLP 2025，pp. 5726–5751。

| 引用位置 | 内容 |
| --- | --- |
| §3.3 Evaluation of RAG Models（PDF 第 5 页） | 采用 MAP 与 MRR 评价 RAG 系统的检索器 |
| 附录 B，式（9）—（10）（PDF 第 12 页） | $\mathrm{MRR} = \sum_{q=1}^{Q} \mathrm{RR}_q$，$\mathrm{RR} = 1/\mathrm{FRP}$，FRP 为首个相关文档的排名位置 |

**口径差异**：OmniEval 的 MRR 未标注截断深度，$\mathrm{RR} = 1/\mathrm{FRP}$ 是不截断形式。本项目采用截断到 10 的 MRR@10，且按必要信息单元分解，因此不声称与其同口径。见 [layer-1-retrieval/metrics.md](../layer-1-retrieval/metrics.md) §4.5。

## 待归类文献

以下 PDF 已收入但尚未在设计文档中引用，需确认其定位后写入 `related-frameworks.md`：

| 文件 | 状态 |
| --- | --- |
| `RAG-Paper/2025.emnlp-main.1267.pdf` | 待确认 |
| `RAG-Paper/2026.acl-long.1151.pdf` | 待确认 |
| `RAG-Paper/2026.eacl-long.391.pdf` | 待确认 |

## `related-frameworks.md` 规划内容

对比维度：

| 维度 | 说明 |
| --- | --- |
| 领域与语料特性 | 通用 vs. 专业领域；冗余度与相似度 |
| 标注策略 | LLM 生成 / 自动+人工验证 / Agent 复核 / 多标注员 |
| 评测粒度 | 文档级 / 页级 / chunk 级 / atomic fact 级 |
| 覆盖层级 | 仅检索 / 检索+生成 / 含 Agent 决策 |
| 等价证据处理 | 是否考虑语义等价的替代来源 |

PEARL 的差异化定位（待在对比中论证）：跨语言检索不对称、科学证据的条件与单位约束、分层渐进的评测粒度、透明的标注来源声明。
