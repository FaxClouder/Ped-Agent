# memPed 数据目录

_Ped-Agent 的纯数据根目录与治理资产边界 · 2026-08-11_

---

`memPed/` 是 Ped-Agent 的统一数据根目录，只保存数据资产，不包含 Python、前端或脚本业务代码。

## 📦 三个数据组件

```text
memPed/
├─ knowledge/
│  ├─ literature/
│  │  ├─ files/       # 本地文献原文；不提交 Git
│  │  ├─ records/     # 跨批次主表、质量快照和 Manifest
│  │  └─ reviews/     # 按 review_id 保存 PRISMA 阶段产物与选择冻结包
│  ├─ regulations/
│  │  ├─ files/       # 本地法规、标准和规范原文；不提交 Git
│  │  └─ records/     # 来源、版本、筛选和 Manifest
│  ├─ knowledge.sqlite3
│  ├─ fts.sqlite3
│  ├─ vectors/
│  ├─ derived/      # Canonical Document、结构元素、表格/图片、Chunk 和解析报告
│  └─ reports/
├─ conversations/
│  ├─ conversations.sqlite3
│  └─ files/<session-id>/
└─ methods/
   ├─ candidates/
   ├─ approved/
   └─ methods.sqlite3
```

## 📚 `knowledge/`

知识库只保存能够回查来源的外部领域知识。当前正式资源类型为文献、法规和标准；数据集名称、版本和链接只作为文献元数据，不建立独立数据集目录。

- `literature/files/`：合法取得的文献 PDF。文件名使用稳定 `resource_id`；正式导入后允许在该目录下生成按 SHA-256 寻址的副本。
- `literature/records/`：候选清单、检索日志、期刊与引用快照、筛选记录、例外审批和 pilot/core Manifest。
- `literature/reviews/<review_id>/`：方案、检索快照、去重、逐级筛选、全文获取、PRISMA 计数、选择冻结和发布决定。
- `regulations/files/`：法规、标准和规范原文。
- `regulations/records/`：官方来源核验、版本历史、筛选记录和 pilot/core Manifest。
- `knowledge.sqlite3`：正式资源、版本、正文切块和资源关系的权威 Catalog。
- `fts.sqlite3`、`vectors/`：从 Catalog 派生、可以重建的检索索引。
- `derived/`：按 `resource_id/version_id` 保存规范文档、结构元素、表格、图片、
  Parent-child Chunk 和解析报告；可从原文与配置重建，不提交 Git。
- `reports/`：本地导入、解析、检索和评测报告。
- 根目录 YAML/JSONL：分类、配额、质量规则、Gold Questions 和评测配置。

资料选择按照 [`prisma_governance.yaml`](knowledge/prisma_governance.yaml) 分阶段完成。
只有获批的选择冻结包才能生成 Manifest。`memPed` 的活动导入链从准备入库的 Manifest
开始，只承接技术预检、版本登记、解析、Chunking、Catalog、索引和评测数据。技术预检
检查文件、哈希、重复、元数据、版本关系和可解析性，不重复执行论文价值、主题相关性、
JCI、CAS 或引用量判断。

现有筛选表、质量规则和指标快照继续作为上游资料与历史兼容资产保存。活动导入链使用
`ped_knowledge.ingestion.IngestionManifest` 与技术预检；`ResourceManifest`、`manifest.py`
和 `governance.py` 的内容质量门禁只保留给历史兼容和离线审计。Gold Questions 用于
检索配置和索引的发布验收，不用于单份文档的入库准入。

## 💬 `conversations/`

会话与任务记忆以 `session_id` 为基本分区：

- `conversations.sqlite3`：会话、消息、Run、事件、证据引用、摘要和用户反馈。
- `files/<session-id>/`：会话关联的小型附件；大型视频和轨迹只保存路径、哈希与摘要。

所有 Session 共用一个 SQLite 数据库，不为每个 Session 创建独立数据库。

## 🔍 `methods/`

方法记忆保存从场景分析中提炼的通用分析与评估方法：

- `candidates/`：Agent 自动提炼的候选方法，不能用于正式检索。
- `approved/`：人工审核通过的方法，可进入后续正式检索。
- `methods.sqlite3`：方法检索与版本索引的预留位置；当前尚未定义正式方法表结构。

候选方法必须保留来源 `session_id`、`run_id` 和知识证据引用。未经人工审核，不得升级为正式方法。

## 🔐 Git 边界

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

## ⚙️ 常用命令

评审初始化、冻结、Manifest 发布与正式导入：

```powershell
uv run --project backend ped-agent research init <review_id>

uv run --project backend ped-agent research freeze-selection <review_id> `
  --approved-by <content_owner>

uv run --project backend ped-agent research release-manifest <review_id> `
  memPed/knowledge/literature/records/import_manifest.jsonl `
  --approved-by <manifest_owner>

uv run --project backend ped-agent library preflight `
  memPed/knowledge/literature/records/import_manifest.jsonl

uv run --project backend ped-agent library import-manifest `
  memPed/knowledge/literature/records/import_manifest.jsonl `
  --release memPed/knowledge/literature/reviews/<review_id>/08-manifest/manifest_release.json

uv run --project backend ped-agent library build-index

uv run --project backend ped-agent evaluate `
  memPed/knowledge/pilot_gold.jsonl `
  memPed/knowledge/reports/pilot-evaluation.json `
  --config memPed/knowledge/pilot_config.json `
  --pipeline hybrid
```

文献 Manifest 默认必须绑定有效的 `manifest_release.json`。`--technical-only` 仅用于受控的
底层解析或导入 Smoke Test，不表示内容已通过选择冻结，也不得作为正式文献入库方式。法规
与标准 Manifest 暂不要求 PRISMA Release，但必须与文献分开导入。

历史质量与配额规则可继续通过 `library validate-manifest` 做离线审计，但该命令不在
活动导入链中。

知识业务代码位于 `Knowledge-Base/src/ped_knowledge/`。后端的同名旧模块只提供兼容导出，
`src/ped_agent/knowledge/` 仍是冻结的早期占位代码；新实现不应写入 `memPed/`，也不应
继续扩展旧目录。详细方案见
[`docs/modules/knowledge-and-evidence.md`](../docs/modules/knowledge-and-evidence.md)。
