# Ped-Agent 证据问答链

## 运行边界

首版面向本机单用户，只监听 `127.0.0.1`。根发行包是 `ped-agent-core`，Python
模块仍为 `ped_agent`；`backend` 发行包是 `ped-agent-server`，Python 模块为
`ped_agent_server`，并提供仓库中唯一的 `ped-agent` CLI。

运行中的 `ped_agent_server` 和仓库脚本只把仓库根目录 `.env` 与进程环境
（process environment）作为配置来源，统一使用 `PED_AGENT_*__*` 双下划线嵌套字段。
旧 YAML 配置目录和无命名空间的 Key 别名已经移除。配置修改后必须重启；Embedding
模型、Base URL 或维度变化后，还必须显式重建 Chroma。

回答模型固定为 `deepseek-v4-flash`，语义复核模型固定为 `deepseek-v4-pro`。两者通过
LangChain 直接接入，DeepSeek 结构化输出使用 `json_mode`，而不是默认 JSON Schema。

## 请求与回答链

```mermaid
flowchart LR
    V["Vue 智能问答"] -->|"POST query"| A["FastAPI Run API"]
    A --> S["SQLite Run + Event log"]
    A --> G["Deterministic LangGraph"]
    G --> R["Deterministic preflight: FTS5 top 20"]
    G --> C["Deterministic preflight: Chroma top 20"]
    R --> F["RRF / dedupe / top 8"]
    C --> F
    F --> D{"Local evidence sufficient?"}
    D -->|"No, once at most"| X["Semantic Scholar + OpenAlex + Parallel"]
    D -->|"Yes"| N["Normalize evidence"]
    X --> N
    N --> E{"Any usable evidence?"}
    E -->|"No"| I["Deterministic insufficient_evidence"]
    E -->|"Yes"| W["Flash query rewrite"]
    W --> T["Refined local retrieval"]
    T --> P["Merge Evidence Pack"]
    P --> Q["Flash json_mode draft"]
    Q --> K["Claim/citation rules"]
    K --> M["Pro json_mode semantic verification"]
    M -->|"partial or unsupported"| U["One Flash revision using same Evidence Pack"]
    U --> K
    M -->|"supported"| Z["Persist verified answer"]
    Z -->|"SSE + conversation refresh"| V
```

固定节点为：加载会话、本地 preflight、证据判断、最多一次条件外搜、证据归一化、
零证据短路、Flash 独立问题改写、精检本地、草稿生成、规则校验、Pro 语义复核、
条件修订、最终持久化。Preflight 在任何 DeepSeek chat call 之前检查本地证据，并在必要时
补充外部证据；有可用证据后才调用 Flash 改写并精检本地。生成上下文只使用最近六条消息和
上一轮引用，完整历史仍保存在 SQLite。

若本地与外部合并后仍为零条可用证据，图直接生成确定性的 `insufficient_evidence`，
不调用 Flash 或 Pro。Preflight 中的 Chroma 向量检索仍可能调用配置的 Embedding service；
这不是 DeepSeek chat call。

## 证据与验证规则

- `[L]`：本地正式证据；只允许 Catalog 中 `retrieval_eligibility=official` 的片段。
- `[A]`：外部学术证据；必须获得可核验摘要。
- `[W]`：外部网页证据；必须成功抓取页面正文。
- `[I]`：单独展示的分析性推断，不伪造引用。
- 本地至少两个不同正式资源，或标题、DOI、文号精确命中时，不触发外搜。
- 每个事实 Claim 必须绑定存在的 Evidence；`partial` 必须收紧，`unsupported` 必须删除或修订。
- 只允许使用原 Evidence Pack 修订一次。二次校验仍失败时，Run 失败且草稿不展示。
- 语义复核默认失败关闭。只有 `.env` 显式设置 `PED_AGENT_VERIFY__ENABLED=false` 时，
  才允许 `rules_only`，前端会显示醒目提示。

## 本地存储

- `memPed/knowledge/`：分开保存文献与法规原文/治理记录，共享 Catalog、FTS5 和向量索引。
- `memPed/conversations/conversations.sqlite3`：会话、消息、Run、SSE 事件、证据快照和引用。
- `memPed/methods/`：Agent 生成的候选方法与人工审核通过的方法；候选方法不进入正式检索。
- `Video-Analysis/`：检测器 YAML、模型权重位置、视觉/分析函数和公共接口。
- `Video-Analysis/runtime/`：视频任务、轨迹、场景、SQLite 和导出产物，保持在 memPed 之外并忽略 Git。

SQLite 开启 WAL、外键与版本化迁移。每个会话只允许一个活动 Run，全局默认两个并发
Run。SSE 断开不取消运行；服务启动会把遗留的 `queued/running` Run 标为 `interrupted`。
Run 的 start、cancel、complete 和 fail 转换使用事务保护；complete 时最终回答、证据、
引用和 terminal events 一起提交，避免只保存部分可展示结果。

## LangSmith 可观测性与隐私

LangSmith 是可选能力，默认关闭；启用时只接受 `content_policy=redacted`。本地 Run UUID
作为 LangGraph 根运行的 `run_id`，因此等于 LangSmith root Trace UUID，反馈指标也写到
同一 UUID。启动配置成功后，可观测性是 non-blocking 的：trace/feedback 网络失败只记录
脱敏错误类型，不改变 Run 成功、失败或取消结果；关闭阶段的 flush/close 也有超时边界。

启用追踪后，允许上传当前 query、已经验证的 final answer、证据 identity（ID、来源、
标题、定位、内容哈希）、外部 candidate metadata（来源、标题、DOI、去敏 URL）以及
运行 metrics。不会上传 conversation history、evidence quote、abstract、未验证 draft、
raw model payload 或 API Key/token/cookie 等 secrets。URL 只保留 scheme、host、port 和
path，userinfo、query 与 fragment 会被移除。

## API 与 SSE

- `POST /api/conversations`
- `GET /api/conversations`
- `GET /api/conversations/{id}`
- `POST /api/conversations/{id}/runs`
- `GET /api/runs/{id}/events`，支持 `Last-Event-ID`
- `POST /api/runs/{id}/cancel`

SSE 事件为 `run.started`、`stage.started`、`stage.completed`、`evidence.summary`、
`answer.delta`、`run.completed`、`run.failed`、`run.cancelled` 和 `heartbeat`。
`stage.completed` 同时记录节点耗时、模型标识、证据 ID 或验证结果；异常只记录脱敏类型与
固定用户消息。

## 启动与索引

```powershell
Copy-Item .env.example .env
uv sync --project backend
uv run --project backend ped-agent agent doctor
uv run --project backend ped-agent library build-index
uv run --project backend ped-agent agent rebuild-vector-index
uv run --project backend ped-agent serve

cd frontend
npm ci
npm run dev
```

`.env` 修改后重启服务。Embedding 配置变化后执行 `rebuild-vector-index`。向量索引缺失、
过期或不可用时，Run 继续使用 FTS5，并通过 `evidence.summary` 标记降级。

## 故障排查

| 现象 | 检查 |
|---|---|
| `doctor` 配置无效 | 必填 model/API Key、协议拼写、Parallel/LangSmith 启用后是否有 Key |
| 本地检索报 FTS stale | 先运行 `ped-agent library build-index` |
| Run 显示向量降级 | 检查 Chroma 与 Catalog/Embedding fingerprint 后重建向量索引 |
| 浏览器断线 | EventSource 自动重连并携带 `Last-Event-ID`；Run 不会因断线取消 |
| 服务重启后旧 Run 失败 | 这是预期的 `interrupted` 恢复策略，重新提交问题 |
| Windows pytest 临时目录拒绝访问 | 使用仓库内 `--basetemp .pytest-tmp` |

CI 使用 Fake Model 和 Mock HTTP，不需要真实 Key。`doctor`、向量重建和真实端到端问答是
可选本地 Smoke Test；本文档不代表真实 DeepSeek 或 LangSmith Smoke 已执行。
