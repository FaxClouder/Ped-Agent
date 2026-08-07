# Ped-Agent Knowledge Base

`Knowledge-Base/` 是 Ped-Agent 的独立知识程序模块。它负责准备入库资料的技术预检、
结构化解析、层次化 Chunking、Catalog/Vault、稀疏与稠密索引、混合检索、Rerank
和 Gold 评测；运行数据仍写入仓库根目录的 `memPed/knowledge/`。

## 边界

- `ped_knowledge` 不导入 `ped_agent_server`。
- 后端负责 HTTP、CLI、设置和供应商装配。
- 文献价值、JCI、CAS、引用量和人工评分属于上传前或离线治理，不是运行时导入门禁。
- OCR、Embedding 和 Rerank 通过协议注入；依赖不可用时保留可观测降级。

## 目录

```text
Knowledge-Base/
├─ src/ped_knowledge/
│  ├─ contracts/
│  ├─ ingestion/
│  ├─ parsing/
│  ├─ chunking/
│  ├─ storage/
│  ├─ indexing/
│  ├─ retrieval/
│  ├─ reranking/
│  └─ evaluation/
└─ tests/
```

## 验证

```powershell
uv run --no-sync pytest Knowledge-Base/tests -q -p no:cacheprovider
uv run --no-sync ruff check Knowledge-Base/src Knowledge-Base/tests
uv run --no-sync mypy -p ped_knowledge
```

后端兼容回归仍从 `backend/` 运行。正式资料、数据库、派生文件和索引不提交 Git。
