# Knowledge-Base

知识与证据科研模块，负责文献技术预检、结构化解析、层次化 Chunking、Catalog/Vault、
BM25、Dense、RRF、可选 Rerank 和检索实验评测。

## 边界

- 只依赖 `ped_contracts` 的共享证据契约，不依赖 Agent 或产品后端。
- `governance/` 是离线科研资料筛选与语料统计，不是在线强制门禁。
- 正式数据、数据库、索引、模型缓存和报告写入 `memPed/knowledge/`，不提交 Git。
- Embedding、OCR 和 Rerank 通过协议或实验适配器提供。

## 目录

```text
Knowledge-Base/
├── src/ped_knowledge/
│   ├── contracts/
│   ├── governance/
│   ├── ingestion/
│   ├── parsing/
│   ├── chunking/
│   ├── storage/
│   ├── indexing/
│   ├── retrieval/
│   ├── reranking/
│   └── evaluation/
├── examples/
└── tests/
```
