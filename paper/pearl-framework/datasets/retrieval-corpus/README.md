# PEARL Retrieval 英文语料快照

*Layer 1 原文来源快照与技术核验入口 · status: current · corpus: pearl-retrieval-corpus-2026-09-29-02*

本目录记录本轮英文领域 PDF 的**来源成员**。实际 PDF 位于 `memPed/knowledge/`，这里仅保存可复核的元数据与审计记录。当前语料版本为 106 篇；题目和证据覆盖、解析／切块质量仍须在后续阶段核验。协议 `retrieval-v0.2` 与本语料版本分别管理。

| 文件 | 内容 |
| --- | --- |
| [corpus-selection.md](corpus-selection.md) | 前一版本 `-01` 的选择记录；当前 Adobe-only 选择以本页为准 |
| [adobe-membership-verification-v02.json](adobe-membership-verification-v02.json) | 只读核验：106 篇与活动 Adobe 版本按原文哈希一一对应，记录规范文档路径与哈希 |
| [corpus-manifest-v02.jsonl](corpus-manifest-v02.jsonl) | **当前版本**：106 篇纳入 PDF 的路径、内容哈希、身份和来源元数据 |
| [corpus-audit-v02.jsonl](corpus-audit-v02.jsonl) | 110 份原文的逐份技术检查及选择状态（106 included / 4 excluded） |
| [corpus-manifest.jsonl](corpus-manifest.jsonl) | 前一版本 `-01` 的 108 篇清单，保留作沿革 |
| [corpus-audit.jsonl](corpus-audit.jsonl) | 前一版本 `-01` 的审计记录 |
| [audit_corpus.py](audit_corpus.py) | 只读原文与书目信息、可重建 `-01` 两份 JSONL 的脚本 |

## 版本 -02：排除 2 篇仅有 PyMuPDF 解析的文献

`-01` 的 108 篇中有 2 篇无法取得 Adobe PDF Extract 解析，已在 `-02` 中排除：

| source_id | 文献 | 页 | 排除理由 |
| --- | --- | ---: | --- |
| pearl-src-744e08488fd68857 | Haghani 2024 TRC Part 2 (Physical Movement) | 31 | Adobe Extract 上传写超时；仅有 `pymupdf-structured-v2` 解析 |
| pearl-src-8545ec8c9dc6e8ff | Haghani 2024 TRC Part 1 (Decision Making) | 25 | 同上 |

本轮按用户指定的 **Adobe-only** 范围选择：只纳入已有活动 `adobe-pdf-extract-v1` 解析的 106 篇，另 2 篇 PyMuPDF 文献暂不加入，不删除其 PDF 或主库产物。排除依据是本轮解析器范围，不据此认定两篇原文或所有数值证据不可用。

排除后语料的解析器口径统一为 `adobe-pdf-extract-v1`。8 题开发试标 Gold v4 的全部来源均保留；v4 仍绑定 `-01`，已另存绑定 `-02` 的[新 Gold](../retrieval-pilot/pearl-retrieval-dev-pilot-8-adobe106-gold.json)并对 Adobe child 重新盲化核验支持。两篇仍保留在 `-01` 清单和 `-02` 的审计记录中；若后续重新纳入，须生成新语料版本，不在 `-02` 下追加。

活动 Catalog 的 106 篇 Adobe 资产盘点为 6,433 个 child、2,830 个 parent（`parent-child-v1`）。这是现有资产核对，不等于 PEARL 检索资产已冻结或质量已审定。后续四组方法必须使用同一份经核验并记录哈希的 Adobe child 库，另建实验索引。此前 108 篇全 PyMuPDF、9,491 child 的 R1 输出仅保留为历史流程试标，不代表此版本的实验成绩。

上述资产现已完成[独立 child 快照与英文 FTS／BGE-M3 Chroma 索引构建](../../../../experiments/pearl-index-106-adobe-20260929/README.md)：6,433 条成员、文本及向量一致性通过独立重开核验。新资产 8 题 R1–R4 已完成语义支持映射和开发初步评分；完整 80/200 题集尚未完成。

重建命令（从仓库根目录运行；需要已安装 PyMuPDF 的本地 Python 环境）：

```powershell
.\.venv\Scripts\python paper/pearl-framework/datasets/retrieval-corpus/audit_corpus.py
```

脚本扫描五个 `batch-*-incoming` PDF 目录和 `batch-1-held`；引用旧书目／筛选目录以读取题名、DOI 和语言元数据及核对既有哈希，不读取旧 Gold、排名或分数，也不把既有 `derived/` 文件作为本轮解析资产。来源 ID 按实际 PDF SHA-256 派生；新解析、child 和索引需另行构建。该脚本重建的是 `-01` 版本；`-02` 由 `-01` 排除 2 篇派生，逐份技术字段未重算。

## 清单哈希

| 语料版本 | 篇数 | 页数 | 主清单 SHA-256 |
| --- | ---: | ---: | --- |
| `-02`（当前） | 106 | 1900 | `50daa8469adf6cda5c68f7ad84197eedd93f639a54278ccc47174d916b22630a` |
| `-01` | 108 | 1956 | `f484cde3acf0d67c0982477679a24926a9544bb2bb7ec4803d2597ff8f8697ff` |

`-02` 的审计文件 SHA-256 为 `4254f5e4f8b65417d82104416d6d1694abdfe459e125b1d276b7e1d3c5fa86e8`。以上按现存文件字节重新核验，未改写清单。若来源成员或文件字节变化，须生成新语料版本并重新核对受影响的 Gold 与检索资产；不得在此版本下静默改写。
