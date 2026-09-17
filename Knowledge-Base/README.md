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
│   ├── tokenization/
│   ├── storage/
│   ├── indexing/
│   ├── retrieval/
│   ├── reranking/
│   └── evaluation/
├── config/
│   ├── embeddings/
│   └── retrieval/
├── examples/
└── tests/
```

## RAG 分词与切块状态

| 能力 | 当前基线 | V2 候选 |
|---|---|---|
| Chunk policy | `parent-child-v1`，兼容原正则计数 | `parent-child-v2`，BGE-M3 tokenizer 计数 |
| 边界 | 固定 token 窗口 | 元素、段落、双语句子、超长原子单元 token 回退 |
| Child 预算 | target 320、max 450、overlap 48 | 同一预算，强制 `token_count <= 450` |
| 词法召回 | jieba 基础切词 | 固定领域词表与停用词、OR 召回、指纹校验 |
| 发布状态 | 默认行为 | candidate，尚未替换当前基线 |

V2 策略保存在
[`config/retrieval/chunking-v2.yaml`](config/retrieval/chunking-v2.yaml)，词法策略保存在
[`config/retrieval/lexical-v1.yaml`](config/retrieval/lexical-v1.yaml)。Chunk 记录包含 tokenizer
指纹、token 数、父文本字符偏移和 `hard_split` 标记。Catalog 按 `policy_version` 并存 V1/V2，
索引构建记录 policy、tokenizer、词法分析器、模型和实验来源指纹，读取时拒绝不匹配的候选。

`memPed/knowledge/pilot_gold.jsonl` 目前包含 31 条已规范化问题；配置使用最小问题数门槛，
避免新增 Gold 后因精确计数而使评测失效。V2 只有在新建独立索引、完成真实 BGE-M3 与 Gold
评测，并通过现有发布门禁后才可激活。现有 `memPed/knowledge/` 数据库和索引不会由代码变更
自动重建或覆盖。

## BGE-M3 本地配置

BGE-M3 的固定参数和复现命令见
[`config/embeddings/bge-m3/README.md`](config/embeddings/bge-m3/README.md)。模型权重保存在
`memPed/knowledge/models/bge-m3/`，后续独立 Chroma 索引保存在
`memPed/knowledge/indexes/bge-m3-1024/`；两者均不提交 Git。
