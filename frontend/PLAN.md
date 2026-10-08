# PedRAGent 前端初步规划

*本地研究控制台的页面与技术选型草案 · status: plan · 2026-10-08 · 设计方向已定为初版（v1），尚未开发*

---

## 1. 前提与边界冲突

[`AGENTS.md`](../AGENTS.md) 与 [`docs/project-architecture.md`](../docs/project-architecture.md) 目前明确把
FastAPI、Vue、SSE、任务队列、会话数据库列为范围外，并要求“如需 Web/API 集成层，先记录新的架构决策”。
因此本规划成立的前提是：**先补一份架构决策记录，把前端定位为本地、单用户、以只读为主的研究控制台**，
而不是产品或常驻服务。具体约束：

- 只监听 `127.0.0.1`，无登录、无会话库、无任务队列；
- 前端只读 `outputs/`、`memPed/knowledge/`、`events.jsonl` 等已有产物，不覆盖任何研究输出；
- 实时检索与问答只调用各模块公开 API（`RetrievalService` / `HybridRetriever`、`EvidenceGraph`、
  Harness `Executor` / `read_events`），不读其他模块内部存储；
- 封存的 200 题评估集不在界面中展示题面与 Gold，只展示已发布的汇总指标。

## 2. 页面清单

2026-10-08 按评审意见调整：页面以 Agent 为主线，RAG 与 PEARL 退为证据与评测参照；运行轨迹不单独成页，并入会话（每轮可展开完整事件）和总览的最近运行。

| # | 页面 | 依据的现有能力或设计 | 主要内容 |
| --- | --- | --- | --- |
| 1 | 总览 | resolved-config、Registry、run_start / run_end 事件 | 当前 profile 与关键上限、工具可用性、最近运行的停止原因与答案状态 |
| 2 | Agent 会话 | 控制器设计（DecisionState、plan / replan、停止规则）、events.jsonl、AnswerDocument | 多轮会话；每轮可折叠思考链（规划需求 → 逐轮工具调用 → 支持判断 → 停止 → 尾链）；需求状态与预算侧栏；可展开完整轨迹 |
| 3 | Agent 配置 | Agent-Harness/docs/configuration-design.md（target）、AgentSettings | 编辑 profile：Agent 策略、模型、Harness 预算与执行、停止与重规划、模块引用、YAML；启动前校验 |
| 4 | 工具 | ToolSpec、registry、首批 knowledge.search / read_evidence | 工具契约与 allowlist、不开放的操作、单工具试调用（检索试调用显示分阶段排名） |
| 5 | 知识库 | Catalog、CanonicalDocument、parent-child 切块 | 语料与索引版本、文献切块树、被哪些运行引用 |
| 6 | 评测 | PEARL Layer 5–6（待设计）与 Layer 1–3 已发布结果 | profile 成对对比（正确率、轮次、调用、成本、停止原因）、单题决策过程、RAG 四层参照 |

2026-10-08 第二次调整：整体布局参考 DeepSeek Harness Web 客户端（固定提交 5badb150）的三栏框架。左栏是工作区与会话列表，工作区对应实验 profile；中间是会话；右侧是可停靠的面板，分证据、需求、轨迹、预算四个标签。总览并入左栏与会话顶栏；Agent 配置和工具合并为“Agent 设置”，固定在左栏底部；知识库与评测是左栏顶部的入口。

**2026-10-08 用户确认：以上三栏布局作为初版设计方向固定下来，后续改动在此基础上迭代。**

静态设计稿见 [`prototype/index.html`](prototype/index.html)（纯 HTML，示例数据，无后端）。

Video-Analysis 的轨迹与流量可视化暂不纳入，等 Agent 侧稳定后再单独规划。

## 3. 技术选型建议

**推荐：React + TypeScript + Vite 的静态前端，加一个很薄的本地 Python 适配层。**

| 层 | 选择 | 理由 |
| --- | --- | --- |
| 前端 | React + TypeScript + Vite，组件用 shadcn/ui（Tailwind），表格用 TanStack Table，图表用 ECharts | 证据表格、逐题下钻和时间线是主要交互，这套组合成熟且类型安全；避开架构文档点名的 Vue |
| 数据获取 | TanStack Query | 缓存只读结果，支持轮询 |
| 后端适配 | 新增 `frontend/server/`，用 FastAPI（需在架构决策中显式放行）或 Starlette，进程内直接 import `ped_knowledge`、`ped_research_agent`、`ped_agent_harness` | 不复制业务逻辑，只做序列化；Pydantic 契约可直接导出 JSON Schema 生成前端类型 |
| 实时更新 | P1 先用轮询 `events.jsonl`（按 seq 增量读取） | 不引入 SSE/WebSocket，符合现有边界；确有需要再单独决策 |
| 类型同步 | `Contracts` 的 Pydantic 模型 → OpenAPI → `openapi-typescript` 生成 TS 类型 | 前后端字段口径与契约一致 |

后端接口草案（全部本地、P0 只读）：

- `GET /api/overview`、`GET /api/documents`、`GET /api/documents/{id}/chunks`
- `GET /api/pearl/experiments`、`GET /api/pearl/experiments/{id}/questions/{qid}`
- `POST /api/retrieve`（P1，调用检索服务，返回各阶段排名）
- `GET /api/runs`、`GET /api/runs/{run_id}/events?after_seq=N`（P1）
- `POST /api/ask`（P2，调用 EvidenceGraph，结果写入新的独立命名运行目录）

备选：若只想快速内部查看，可用 Streamlit 纯 Python 实现页面 1、3、6，无需单独 API 层，但交互深度和
后续扩展较弱。

## 4. 分阶段

| 阶段 | 内容 | 前置条件 |
| --- | --- | --- |
| P0 | 页面 1、3、6：只读浏览已有产物 | 架构决策记录；确认 PEARL 结果文件的稳定读取格式 |
| P1 | 页面 2、5：实时检索与运行轨迹 | 本地 BGE-M3 / reranker 权重与活动索引可用（注意活动 `fts.sqlite3` 缺 analyzer fingerprint 会直接报错） |
| P2 | 页面 4：研究问答 | Agent 模型端口与 Harness 控制器落地 |

## 5. 待决事项

1. 是否同意补架构决策，放行本地 FastAPI 适配层（或改用 Streamlit 方案）。
2. 前端代码放在仓库根目录 `frontend/`，还是作为 `experiments/` 下的工具。
3. PEARL 看板展示哪些实验为“当前”，历史 V1/V2、Gold v5 结果是否只作归档展示。
4. 本文档转为维护文档时，需登记到 [`docs/README.md`](../docs/README.md)。
