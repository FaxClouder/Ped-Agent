# memPed 数据目录

`memPed/` 是 Ped-Agent 的统一数据根目录，只保存数据资产，不包含 Python、前端或脚本业务代码。

## 三个数据组件

```text
memPed/
├─ knowledge/
│  ├─ literature/
│  │  ├─ files/       # 本地文献原文；不提交 Git
│  │  └─ records/     # 候选、筛选、质量快照和 Manifest
│  ├─ regulations/
│  │  ├─ files/       # 本地法规、标准和规范原文；不提交 Git
│  │  └─ records/     # 来源、版本、筛选和 Manifest
│  ├─ knowledge.sqlite3
│  ├─ fts.sqlite3
│  ├─ vectors/
│  └─ reports/
├─ conversations/
│  ├─ conversations.sqlite3
│  └─ files/<session-id>/
└─ methods/
   ├─ candidates/
   ├─ approved/
   └─ methods.sqlite3
```

## `knowledge/`

知识库只保存能够回查来源的外部领域知识。当前正式资源类型为文献、法规和标准；数据集名称、版本和链接只作为文献元数据，不建立独立数据集目录。

- `literature/files/`：合法取得的文献 PDF。文件名使用稳定 `resource_id`；正式导入后允许在该目录下生成按 SHA-256 寻址的副本。
- `literature/records/`：候选清单、检索日志、期刊与引用快照、筛选记录、例外审批和 pilot/core Manifest。
- `regulations/files/`：法规、标准和规范原文。
- `regulations/records/`：官方来源核验、版本历史、筛选记录和 pilot/core Manifest。
- `knowledge.sqlite3`：正式资源、版本、正文切块和资源关系的权威 Catalog。
- `fts.sqlite3`、`vectors/`：从 Catalog 派生、可以重建的检索索引。
- `reports/`：本地导入、解析、检索和评测报告。
- 根目录 YAML/JSONL：分类、配额、质量规则、Gold Questions 和评测配置。

正式治理顺序保持为：候选记录 → 人工筛选 → Manifest → 预检 → 导入 Catalog → 构建索引 → Gold 评测。候选资料、外部搜索结果和 LLM 回答不能绕过该流程进入正式知识库。

## `conversations/`

会话与任务记忆以 `session_id` 为基本分区：

- `conversations.sqlite3`：会话、消息、Run、事件、证据引用、摘要和用户反馈。
- `files/<session-id>/`：会话关联的小型附件；大型视频和轨迹只保存路径、哈希与摘要。

所有 Session 共用一个 SQLite 数据库，不为每个 Session 创建独立数据库。

## `methods/`

方法记忆保存从场景分析中提炼的通用分析与评估方法：

- `candidates/`：Agent 自动提炼的候选方法，不能用于正式检索。
- `approved/`：人工审核通过的方法，可进入后续正式检索。
- `methods.sqlite3`：方法检索与版本索引的预留位置；当前尚未定义正式方法表结构。

候选方法必须保留来源 `session_id`、`run_id` 和知识证据引用。未经人工审核，不得升级为正式方法。

## Git 边界

提交 Git：

- 本文件；
- `knowledge/` 下的治理记录、规则、Manifest、Gold Questions 和配置；
- `methods/approved/` 下通过审核且不含隐私的正式方法。

不提交 Git：

- 文献、法规和标准原文；
- SQLite、FTS、Chroma 等运行数据；
- 会话内容和附件；
- 候选方法；
- 本地原始报告。

## 常用命令

```powershell
uv run --project backend ped-agent library validate-manifest `
  memPed/knowledge/literature/records/pilot_manifest.jsonl `
  --phase pilot

uv run --project backend ped-agent library build-index

uv run --project backend ped-agent evaluate `
  memPed/knowledge/pilot_gold.jsonl `
  memPed/knowledge/reports/pilot-evaluation.json `
  --config memPed/knowledge/pilot_config.json
```

业务代码仍位于 `backend/src/ped_agent_server/` 和 `src/ped_agent/`；`memPed/` 只回答“数据放在哪里”。
