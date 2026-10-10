# PedRAGent 模块划分与功能设计

_项目模块边界、职责分工与功能清单 · 2026-09-15_

---

## 项目定位

PedRAGent 是面向行人流研究的**模块化科研工程仓库**，目标是构建可独立测试、可组合、可复现的知识检索、视频/轨迹分析和证据约束问答能力。当前**不是** Web 产品或长期运行服务，不维护 FastAPI、Vue、SSE、任务队列、会话数据库或多用户系统。

## 核心设计原则

1. **职责分离**：事实属于 Knowledge-Base，计算属于 Video-Analysis，编排和解释属于 Agent
2. **契约通信**：模块通过 Contracts 交互，不直接访问彼此的内部存储或代码
3. **可复现性**：研究数据、配置、模型版本、输入哈希、随机种子和 provenance 始终可见
4. **实验驱动**：新的跨模块行为先在 experiments 中验证，稳定后才进入模块公共 API

---

## 模块架构

```text
┌─────────────────────────────────────────────────────────────┐
│                        experiments/                          │
│                   可复现跨模块研究实验                         │
└────────┬──────────────────┬──────────────────┬──────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Knowledge-Base │ │ Video-Analysis  │ │     Agent       │
│                 │ │                 │ │                 │
│ 知识检索与证据   │ │ 视觉检测与分析  │ │ 证据编排与问答   │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┴───────────────────┘
                             │
                    ┌────────▼────────┐
                    │    Contracts    │
                    │  跨模块数据契约  │
                    └─────────────────┘
                             │
                    ┌────────▼────────┐
                    │     memPed/     │
                    │   研究数据根     │
                    └─────────────────┘
```

---

## 模块详细划分

### 1. Contracts — 跨模块数据契约

**路径**: `Contracts/`\
**包名**: `ped_contracts`\
**状态**: current

#### 职责范围
- 定义跨模块共享的**稳定数据结构**
- 提供证据、问答结果、轨迹的标准格式
- 不包含算法实现、数据库、HTTP 或前端语义

#### 核心数据契约

| 契约类型 | 文件 | 主要结构 |
|---------|------|---------|
| 证据与问答 | `evidence.py` | `EvidenceItem`, `EvidenceOrigin`, `AnswerDocument`, `AnswerDraft`, `RetrievalBatch`, `RuleValidation`, `SemanticReview`, `EvidenceRunMetrics` |
| 轨迹数据 | `trajectory.py` | 轨迹、检测框、坐标投影相关结构 |
| 运行状态 | `evidence.py` | `RunStatus` (queued/running/completed/failed/cancelled/interrupted) |

#### 证据来源分类
- `LOCAL_OFFICIAL`: 本地权威文献/法规
- `EXTERNAL_ACADEMIC`: 外部学术检索
- `EXTERNAL_WEB`: 外部网络搜索

---

### 2. Knowledge-Base — 知识与证据模块

**路径**: `Knowledge-Base/`\
**包名**: `ped_knowledge`\
**状态**: current

#### 职责范围
负责文献/法规的**技术导入**、**结构化存储**、**检索**与**评测**，不负责最终问答生成和视频推理。

#### 子模块结构

```text
ped_knowledge/
├── contracts/       # 内部导入契约 (IngestionManifest)
├── governance/      # 离线质量审计与历史兼容
│   ├── manifest.py
│   ├── audit.py
│   └── contracts.py
├── ingestion/       # 技术预检与导入服务
├── parsing/         # PDF/文档解析
├── chunking/        # 层次化 Chunking (Parent-child)
├── storage/         # Catalog、Vault 与 SHA-256 寻址
├── indexing/        # BM25 (FTS5)、Dense (Chroma)
├── retrieval/       # 检索与 RRF 融合
├── reranking/       # 可选 Rerank 协议
└── evaluation/      # Gold Questions 评测
```

#### 数据流

```text
人工筛选的 PDF
  → 技术预检 (文件存在性、可读性、SHA-256、重复项)
  → Vault (原文存储) + Catalog (metadata)
  → 解析 + Parent-child Chunking
  → derived/ (派生文档)
  → FTS5 索引 + Chroma 索引
  → Gold Questions 评测
  → 检索报告
```

#### 核心能力

| 能力 | 说明 | 状态 |
|-----|------|------|
| 技术预检 | 文件 SHA-256、元数据提取、重复检测 | current |
| 结构化解析 | PDF → 文本、表格、图像元素 | current |
| 层次化 Chunking | Parent-child 策略 | current |
| BM25 检索 | SQLite FTS5 全文索引 | current |
| Dense 检索 | BGE-M3 + Chroma | current |
| RRF 融合 | 多路检索融合 | current |
| Rerank | 可选协议或实验适配器 | target |
| 检索评测 | Gold Questions + 配置驱动 | current |

#### BGE-M3 本地配置
- **模型权重路径**: `memPed/knowledge/models/bge-m3/`
- **索引路径**: `memPed/knowledge/indexes/bge-m3-1024/`
- **向量维度**: 1024
- **目标设备**: CUDA/FP16
- **配置文档**: [`Knowledge-Base/config/embeddings/bge-m3/README.md`](../Knowledge-Base/config/embeddings/bge-m3/README.md)

#### 边界说明
- `governance/` 是**离线审计工具**，不是活动导入链的强制门禁
- Gold Questions 用于**检索配置验收**，不用于单份文档的入库准入
- Embedding、OCR、Rerank 通过**协议或适配器**提供，不硬编码实现

---

### 3. Video-Analysis — 检测追踪与流动分析模块

**路径**: `Video-Analysis/`\
**包名**: `ped_video_analysis`\
**状态**: current

#### 职责范围
负责把视频或轨迹数据转换为**可复查的轨迹、指标、图表和分析产物**，不负责文档准入和自然语言问答。

#### 研究链路

```text
视频或轨迹
  → 检测与跟踪 (YOLO + ByteTrack)
  → 人工复核
  → 标定与坐标投影
  → 轨迹后处理
  → 密度、速度、流量、OD 与交互分析
  → 图表和实验导出
```

#### 子模块结构

```text
ped_video_analysis/
├── vision/          # 检测与跟踪
├── analysis/        # 流动分析
│   ├── metrics.py         # 密度、速度、流量指标
│   ├── od_matrix.py       # OD 矩阵
│   ├── fundamental_diagram.py  # 基本图
│   ├── statistics.py      # 统计计算
│   ├── pedpy_adapter.py   # PedPy 集成
│   ├── visualizer.py      # 可视化
│   ├── vision_pipeline.py # 视觉分析流水线
│   ├── vision_schemas.py  # 视觉分析数据结构
│   └── vision_visualizer.py
├── configs/         # 模型配置
├── api.py           # 高层接口
├── registry.py      # 模型注册
├── pipeline.py      # 通用流水线
├── schemas.py       # 数据结构
└── paths.py         # 路径管理
```

#### 核心能力

| 能力 | 说明 | 状态 |
|-----|------|------|
| 目标检测 | YOLO 系列模型 | current |
| 多目标跟踪 | ByteTrack | current |
| 坐标标定 | 透视变换与真实坐标投影 | current |
| 密度分析 | Voronoi、网格密度计算 | current |
| 速度分析 | 瞬时速度、平均速度 | current |
| 流量分析 | 截面流量统计 | current |
| OD 矩阵 | 起终点分析 | current |
| 基本图 | 速度-密度关系 | current |
| PedPy 集成 | 复用 PedPy 分析能力 | current |
| 可视化 | 轨迹图、热力图、指标曲线 | current |

#### 模型与配置
- **检测模型**: `models/yolo26x/`
- **跟踪器**: `trackers/bytetrack/`
- **示例**: `examples/run_vision.py`

#### 边界说明
- 当前保留 `vision/` 与 `analysis/` 两套研究实现，待实验路线明确后收敛
- 模块不依赖后端服务、任务数据库、SSE 或前端页面
- 本地权重与运行产物受 `.gitignore` 管理

---

### 4. Agent — 证据编排与科研问答模块

**路径**: `Agent/`\
**包名**: `ped_research_agent`\
**状态**: current

#### 职责范围
负责**证据图编排**、**引用规则验证**、**模型适配**和**外部文献搜索**，面向实验调用，不提供 FastAPI、会话数据库、SSE、任务队列或多用户能力。

#### 核心组件

| 组件 | 文件 | 职责 |
|-----|------|------|
| 证据图 | `evidence_graph.py` | LangGraph 编排的证据收集-草稿-验证-修订流程 |
| 引用策略 | `policy.py` | 引用规则验证 (每断言需证据、引用格式检查) |
| 模型网关 | `model_gateway.py` | 统一模型调用接口 (LLM + Structured Output) |
| 外部搜索 | `external_search.py` | 学术数据库与 Web 检索适配 |
| 端口定义 | `ports.py` | `LocalEvidenceRetriever`, `ExternalEvidenceSearcher`, `ModelGateway` |
| 上下文 | `context.py` | `ResearchQuery` 查询结构 |
| 配置 | `config.py` | 运行参数与模型配置 |

#### 证据图流程

```text
用户查询
  → 预处理 (standalone query + preflight query)
  → 本地检索 (Knowledge-Base)
  → 判断是否需要外部搜索
  → 外部检索 (可选)
  → 证据打包
  → 生成草稿
  → 引用规则验证
  → 语义审查
  → 修订 (最多 N 轮)
  → 最终答案 (AnswerDocument)
```

#### 核心能力

| 能力 | 说明 | 状态 |
|-----|------|------|
| 证据编排 | LangGraph 状态机 | current |
| 引用约束 | 每断言需证据 + 引用格式检查 | current |
| 模型适配 | 统一 LLM 调用 (支持 Structured Output) | current |
| 外部搜索 | 学术检索 + Web 检索 | current |
| 语义审查 | 答案-证据一致性检查 | current |
| 多轮修订 | 基于验证结果自动修正 | current |
| 证据不足判断 | 当无可靠证据时返回标准消息 | current |

#### 运行指标

`EvidenceRunMetrics` 记录:
- 本地/学术/Web 证据数量
- 是否使用外部搜索
- 检索是否降级
- 引用规则是否通过
- 语义验证是否通过
- 修订次数
- 证据不足标记

---

### 5. experiments — 可复现研究实验

**路径**: `experiments/`\
**状态**: current

#### 职责范围
保存可复现的**跨模块科研实验定义**，不承载四个模块的核心实现。

#### 实验记录要求

每个实验建议使用独立子目录，并至少记录：

1. **研究问题与假设**
2. **输入数据引用或哈希**
3. **模块版本、模型版本和参数配置**
4. **随机种子与运行命令**
5. **指标定义、结果摘要和论文图表去向**

#### 资产边界
- **输入数据**: `memPed/`
- **模型权重**: 各模块本地模型目录
- **运行结果**: `outputs/` (Git 忽略)
- **跨模块代码**: 先在实验目录，稳定后下沉到模块公共 API

---

## 数据资产管理

### memPed/ — 研究数据根目录

**路径**: `memPed/`\
**状态**: current

#### 目录结构

```text
memPed/
├── knowledge/                    # 知识资产
│   ├── literature/
│   │   ├── files/                # 原文 Vault (不提交 Git)
│   │   └── records/              # 导入记录 (可提交 Git)
│   ├── regulations/
│   │   ├── files/
│   │   └── records/
│   ├── derived/<resource-id>/<sha>/  # 派生文档 (不提交 Git)
│   ├── models/bge-m3/            # 本地模型权重 (不提交 Git)
│   ├── indexes/bge-m3-1024/      # Chroma 索引 (不提交 Git)
│   ├── reports/                  # 本地报告 (不提交 Git)
│   ├── knowledge.sqlite3         # Catalog (不提交 Git)
│   ├── fts.sqlite3               # FTS5 索引 (不提交 Git)
│   ├── taxonomy.yaml             # 分类体系 (提交 Git)
│   ├── quotas.yaml               # 配额规则 (提交 Git)
│   ├── literature_quality_rules.yaml  # 质量规则 (提交 Git)
│   ├── pilot_gold.jsonl          # Gold Questions (提交 Git)
│   ├── pilot_config.json         # 评测配置 (提交 Git)
│   ├── core_gold.jsonl
│   └── core_config.json
├── conversations/                # 预留会话存储 (未实现)
└── methods/
    ├── candidates/               # 候选方法
    └── approved/                 # 批准方法
```

#### Git 管理边界

**提交 Git**:
- 分类、配额、质量规则
- 治理记录、Manifest
- Gold Questions 与评测配置
- 模型与索引的配置、版本和校验值

**不提交 Git**:
- 文献、法规原文
- SQLite、FTS、Chroma、派生文档
- 模型权重和缓存
- 会话内容、附件
- 本地运行报告

---

## 技术栈与依赖

### 通用依赖
- Python 3.12
- uv workspace 管理
- pytest + mypy + ruff

### Knowledge-Base 依赖
- Chroma (Dense 索引)
- SQLite FTS5 (BM25)
- BGE-M3 (本地 Embedding)
- pymupdf / pdfplumber (PDF 解析)

### Video-Analysis 依赖
- YOLO (检测)
- ByteTrack (跟踪)
- PedPy (行人流分析)
- OpenCV / matplotlib (可视化)
- pyarrow (导出)

### Agent 依赖
- LangGraph (证据图编排)
- Pydantic (数据验证)
- Anthropic / OpenAI SDK (LLM 调用)

---

## 验证与测试

### 模块级测试

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python -m pytest Contracts/tests Agent/tests Knowledge-Base/tests Video-Analysis/tests -q
```

### 测试边界
- 算法正确性
- 契约稳定性
- 实验结果不被无意改变
- **不追求**产品级高覆盖率

### 冒烟测试要求
- 视频推理需要本地权重
- Dense 检索需要 BGE-M3 模型
- Rerank 需要对应适配器

---

## 研究开发流程

1. **固定输入**：明确数据和实验问题
2. **单模块运行**：在模块内运行算法并保存中间产物
3. **记录 provenance**：配置、代码版本、模型版本、输入哈希
4. **生成产物**：指标、图表、实验报告
5. **跨模块组合**：接口稳定后开展组合实验

---

## 当前阶段边界

### 包含范围
✅ 独立模块开发与测试\
✅ 通过 Contracts 预留接口\
✅ 文件哈希、版本、配置、种子 provenance\
✅ 可复现实验定义\
✅ Python API 与测试

### 不包含范围
❌ FastAPI、Vue、SSE\
❌ 任务队列、会话数据库\
❌ 多用户、权限、加密、审计\
❌ 产品级高可用与高覆盖率测试\
❌ 稳定的命令行工具 (不使用旧的 `ped-agent library` 命令)

---

## 扩展规则

新的跨模块行为：

1. 先在 `experiments/` 中实现
2. 验证数据契约、可复现性和测试稳定性
3. 接口稳定后再移入模块公共 API

未来如需 Web/API 集成层，记录为**新架构决策**，而不是隐式复活已归档的产品集成树。

---

## 相关文档

- [项目架构](project-architecture.md)
- [模块 README](../README.md)
- [数据分析模块设计](data-analysis-module-design.md)
- [视觉模块设计](vision-module-design.md)
- [memPed 数据管理](../memPed/README.md)
- [BGE-M3 本地部署](../Knowledge-Base/config/embeddings/bge-m3/README.md)
