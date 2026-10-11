# 知识侧 RAG 文档与资产整理执行计划

*供新 session 执行的组织整理计划；仅统一清单、导航与存放关系，文档内部调整另行进行 · status: plan · 2026-10-10*

> 执行方式：使用 executing-plans 技能逐项执行；用户已选择交给新 session。本计划不要求子 Agent，不创建新会话，不启动研究实验。

**Goal:** 建立可核对的知识侧 RAG 总入口和资产清单，让当前设计、实现、候选题集、实验与历史资料有明确归属。

**Architecture:** 保留代码、数据、实验定义和运行产物的现有顶层职责，通过主题导航与资产关系连接。第一阶段不移动既有文件、不合并正文；对迁移和正文修订只形成候选与问题清单，交回用户后再安排。

**Tech Stack:** Markdown、UTF-8 CSV、PowerShell、现有本地 Python；只读文件枚举、链接检查与 SHA-256 核验，不增加依赖。

## 1. 授权范围和停止边界

用户要求先制定计划并交付新 session 实现，完成整理后再进行文档内部调整。新 session 收到用户执行指令后，按本计划完成组织层整理；不要因发现正文错误自行扩大范围。

| 纳入主题 | 范围 |
| --- | --- |
| 主线与规范 | RAG 开发路线、知识侧设计、数据边界、来源与版本规则 |
| 语料建设 | 文献筛选、来源登记、预检、去重、Adobe 解析、结构化资产 |
| 切块与检索 | 父子切块、BM25、BGE-M3、融合、重排、上下文恢复 |
| 题集 | 历史 Gold、现行登记集、新候选、取证和审查记录、补题计划 |
| RAG 评价 | 检索、上下文、答案和引用质量的协议及既有运行资料 |
| 调研与历史 | 方法调研、专项方案、终止研究、作废评分与来源链 |

排除 Agent-Core、Agent 编排实现、整个 `Agent/`、`Agent-Harness/`、动态控制器、工具调度与接入设计、视频分析。综合文档中的相关章节保持原样；若一份文档同时含知识侧 RAG 与排除主题，登记为 mixed，只导航 RAG 相关用途。PEARL Layer 5 Agentic 不作专项整理；Layer 6 仅保留与知识侧成本评价有关的入口。`Contracts/` 只读引用，不重组。

### 允许和禁止的操作

- 允许：只读盘点；创建第 3 节规定的清单和导航；在 `docs/README.md` 新增一个组织整理入口；记录问题和迁移候选；创建独立核验记录。
- 禁止：改动既有设计、计划、实验报告正文及其中的状态文字；移动、删除、重命名、合并既有资料；覆盖研究产物；重写登记表；修改问题、答案或审查标签；冻结 Gold；重建索引；运行实验或调用外部 API。
- 发现旧正文过期时，在新导航中注明“原文为某时点快照”，附证据；原文修订列入后续清单。不得把推测写为已完成或正式采用。
- 不读封存评估题目的题干、答案、证据内容；目录、文件元数据、登记信息和文件哈希足以支持本次盘点。
- 不读取凭据文件，不输出密钥。模型、PDF、数据库、向量和逐题记录不复制入 Git 文档。
- 保留已有 tracked、untracked、ignored 文件，不执行 `git clean`、reset、批量 add 或自动提交。用户说“交付说明”不等于要求 Git commit/push。
- 第一阶段无须人工逐项确认才能完成清单与导航；迁移和正文改写超出本阶段，交付后停止，不自行进入第二阶段。

## 2. 必读材料与复查种子

按顺序阅读：

1. [仓库 README](../../../README.md)、[AGENTS](../../../AGENTS.md)。
2. [架构](../../project-architecture.md)和 [Knowledge-Base README](../../../Knowledge-Base/README.md)。
3. [文档导航](../../README.md)、[数据根说明](../../../memPed/README.md)。
4. [评测规范](../../../experiments/EVALUATION-STANDARD.md)、[登记表](../../../experiments/EVALUATION-REGISTRY.yaml)和 [研究验收标准](../../research-review-standard.md)。
5. [RAG 路线](../../rag-development-roadmap.md)、[设计规范](../../rag-design-spec.md)、[资产审计快照](../../rag-asset-audit-2026-10-07.md)。
6. [切块研究归档](../../../Past/child-parent-Sum/README.md)、[方法调研入口](../../../paper/RAG_Report/README.md)。

以下是 2026-10-10 本地盘点的复查种子，不代替执行时检查：

- `outputs/pearl-question-redesign-pilot-20261008-01/` 已有 Phase 2 和 `question-set-consolidation-20261010-01/`。后者 `handoff.md` 记录 38 道可用开发候选、C-007/D-004 未决，50 题补足仍是计划；不得提升为已冻结 Gold。
- 旧切块及 6B 于 2026-10-08 终止；原件保留，`Past/child-parent-Sum/` 是副本与索引归档，不是唯一原件。
- `docs/rag-design-spec.md` 尚有“6B 评价进行中”；`docs/README.md` 尚有旧 V1/V2 索引已迁至 failed 的描述，但本次实际发现索引仍在 outputs。仅登记差异。
- 仓库存在很多既有未跟踪脚本、调研与归档资料；未跟踪不等于无用，也不等于可删除。
- 本地 outputs 和研究资产未必在远端或新 worktree 中。应在完整的 `E:\F_Workspace\F-Agent-Paper` 本地 checkout 执行；若环境缺失，记录缺失并交付可完成部分，不把“当前环境不可见”写成“资产不存在”。

## 3. 文件职责与交付位置

下列是执行阶段创建的目标文件，本计划编写阶段不提前创建。

| 文件 | 职责 |
| --- | --- |
| `docs/rag/README.md` | 唯一知识侧 RAG 主题导航，分别列设计、实现、语料、题集、评价和调研/历史 |
| `docs/rag/asset-inventory.csv` | 逐文档/逐资产包的结构化清单 |
| `docs/rag/organization-report.md` | 范围、方法、覆盖统计、权威关系与未覆盖项 |
| `docs/rag/follow-up-backlog.md` | 后续正文修订、重复合并、归档/迁移候选；本阶段不执行 |
| `docs/README.md` | 仅新增或更新指向 `rag/README.md` 的一个入口，不重排旧条目 |
| `outputs/rag-asset-organization-<YYYYMMDD>-<NN>/` | 新建且不覆盖的本地核验包，含 baseline、validation、handoff 和 delivery-manifest |

如果 `docs/rag/` 已有资料，先逐文件读取并复用相同职责文件，不覆盖未知成果；若职责冲突，保留现有文件并在核验包记录替代文件名与理由。运行目录日期使用用户时区，NN 选不存在的下一个编号，不复用旧失败编号。

每个新 Markdown 文档一个 H1，紧随斜体背景行和状态。整理完成的清单/导航/报告用 current，后续工作表用 plan。所有文档链接使用仓库相对链接，不写本机绝对路径。

CSV 固定列：

```text
asset_id,topic,path,asset_type,scope,lifecycle,declared_status,observed_state,authority_role,canonical_or_source_path,related_assets,evidence_paths,proposed_action,notes
```

- `path`：仓库相对路径，统一 `/`；同一路径原则上一行，多个主题用分号。
- `asset_type`：document/code/config/source/catalog/derived/model/question_set/protocol/experiment/run/archive。
- `scope`：included/mixed/reference；排除项只在报告写边界，不逐个展开。
- `lifecycle`：current/target/plan/historical/unknown；这是盘点分类，不覆写原文件标签。
- `declared_status`：原文状态原样记录；`observed_state` 写执行时证据支持的状态。目录存在不等于执行完成。
- `authority_role`：entrypoint/original/canonical_copy/summary_copy/snapshot/reference/unknown；权威未知就保留 unknown。
- `related_assets`：关联 asset_id，分号分隔；`evidence_paths` 指向判断依据。
- `proposed_action`：keep/index_only/body_revision_later/merge_candidate/archive_candidate/move_candidate/needs_verification。
- 不根据文件名中的 latest、final 或日期自动选权威；有冲突时记录来源链和未决项。

## 4. 执行任务

### Task 1：建立只读基线与文件覆盖范围

**输入：**第 2 节入口与当前完整本地目录。**输出：**运行目录内 `baseline/git-status.txt`、`baseline/files-before.csv`、`baseline/scope.md`。

- [ ] 阅读入口与规则，记录实际工作目录和 Git 状态。
- [ ] 创建独立运行目录；保存待改文件 `docs/README.md` 的原始副本、字节数与 SHA-256。
- [ ] 按纳入范围枚举文档、代码/配置目录和数据包；明确包含 Git ignored 的 outputs、gold、调研和历史目录。
- [ ] 既有纳入范围的 Markdown、配置/脚本和清单文件保存路径、长度、SHA-256；大型数据仅记录包级路径、文件数/大小和已有 manifest 位置，本阶段不宣称逐字节验证全部数据。
- [ ] 对混合文档仅登记 RAG 用途；不读取封存题集正文和凭据。

基础命令（输出重定向到新运行包，不写源目录）：

```powershell
Get-Location
git status --short
rg --files docs Knowledge-Base experiments paper memPed Past failed -g '*.md'
Get-ChildItem -LiteralPath outputs -Directory | Select-Object -ExpandProperty FullName
rg --files --hidden --no-ignore outputs -g '*.md' -g '*manifest*.json' -g '*manifest*.yaml'
Get-FileHash -LiteralPath docs/README.md -Algorithm SHA256
```

**验收：**范围、排除项、可见性限制明确；现有未跟踪资产有记录；未改变任何原件。禁止对整个仓库无差别抓取环境文件和凭据。

### Task 2：建立资产清单与来源关系

**输入：**Task 1 枚举结果和只读说明。**输出：**`docs/rag/asset-inventory.csv`、`docs/rag/organization-report.md`。

- [ ] 文档逐文件登记：纳入 `docs/` RAG 专项、Knowledge-Base README/配置说明、语料说明、PEARL 知识侧协议、RAG_Report、相关实验报告及归档说明。
- [ ] 大型资料按包登记：原文 Vault、derived、模型、Catalog、题集版本、每个相关实验目录和每个相关运行目录；不为几千个 chunk/packet 创建几千行。
- [ ] 每个实验关联其协议、输入身份、运行目录和报告；仅使用已存在的登记/交接证据，不补造登记号。
- [ ] 新题集关联最初候选、Phase 2、单 Agent 重跑、集中整理和补题计划；区分候选问法版本与答案/QA 版本，不按文件日期替换身份。
- [ ] 旧 Gold、终止切块研究、6B 工作包和 failed 评分分别保留历史角色。对归档副本记录原件位置。
- [ ] 报告写出枚举总数、纳入文档数、资产包数、mixed/unknown 数与遗漏原因；无法确定关系的项留在清单。

**验收：**CSV 无重复 asset_id；所有关联 ID 存在；纳入路径存在或明确标为不可见/缺失；扫描范围内每份文档有纳入或排除依据。状态判断可追溯，不能用目录存在证明研究完成。

### Task 3：建立统一主题导航

**输入：**Task 2 已核对的清单。**输出：**`docs/rag/README.md` 与 `docs/README.md` 的单个新增入口。

- [ ] 导航开头说明整理边界、更新时间和“原件保留”的原则。
- [ ] 按主线设计、实现配置、语料资产、题集、评价实验、方法调研/历史六类列出首选入口，列用途、状态、来源位置。
- [ ] 分开“当前设计”“实际实现”“既有实验采用配置”；不把 roadmap、V2 或历史实验配置写成默认实现。
- [ ] 问题集入口同时标明登记题集和最新候选工作包，两者不能相互替代。最新候选状态以本次读取的交接为准。
- [ ] 对旧报告使用带时点的说明；正文冲突在新入口链接至后续清单，不改旧正文。
- [ ] 在 `docs/README.md` 的当前入口区域新增一个指向 `rag/README.md` 的条目，其余原文保留。

**验收：**用户能从一个入口分别找到知识实现、数据、题集、实验和历史；新入口无 Agent/Harness 专项扩展；新增链接可解析。

### Task 4：形成后续整理与正文调整清单

**输入：**盘点差异和当前引用关系。**输出：**`docs/rag/follow-up-backlog.md`。

- [ ] 每项写明问题 ID、源文件及定位、当前表述/布局、证据、影响、建议、依赖和当前阶段不执行的原因。
- [ ] 正文修订单列：如 6B 状态、历史索引位置、旧计划阶段与当前交付冲突；不在本阶段替用户决定技术方案。
- [ ] 重复资料区分摘要/原件、冻结副本、字节相同副本、内容相似文档；相似内容不自动认定可删。
- [ ] 迁移候选写源路径、建议目标、已知引用、是否受 manifest/hash/脚本路径保护；未检索完整引用就标未核定。
- [ ] 明确冻结题集、绑定清单的输出、数据库、PDF、权重、索引及 Past 来源原件不是本轮搬迁对象。优先通过导航解决。

**验收：**问题列表能直接支撑下一轮讨论；没有执行迁移、合并、删除或正文修订；不新增默认人工验收门槛。

### Task 5：验证与交付，然后停止

**输入：**四份新组织文件、docs 入口变更及基线。**输出：**运行包内 `validation/report.md`、`handoff.md`、`delivery-manifest.json`。

- [ ] 核对每份新 Markdown 恰好一个 H1、有斜体背景和状态。
- [ ] 检查新文档所有本地链接、CSV 路径与关联 ID；未来候选目标作为文字字段而非伪装成现有链接。
- [ ] 比较基线文件哈希：除允许新增的导航条目外，既有源文件应无变更。若存在并发修改，记录具体路径与差异，不能归因不明地宣称全部保全。
- [ ] 检查 `docs/README.md` diff 只有新增导航条目；检查新文件没有凭据、题目正文、受限内容或本机绝对链接。
- [ ] 执行 `git diff --check`，并对新文件补查尾随空格和冲突标记；未跟踪文件不能只靠 git diff 验证。
- [ ] 交付清单记录四份组织文件与核验文件的路径、字节数和 SHA-256；不包含自身哈希；引用大型数据原件而不复制。
- [ ] 最终交接写出覆盖数量、实际修改文件、未解决项、验证范围和下一轮正文修订入口。明确“未运行模型/索引/实验测试，未验证检索效果”。

**最终验收：**仅新增清单/导航/报告/后续工作表和运行核验包，只对 docs 总导航增加入口；没有移动删除原件、改变技术结论或题集身份。文档型变更只做结构、链接、清单和保全验证，不运行全套算法测试。

完成上述交付即停止。下一阶段由用户查看整理结果后，另行决定正文修改、文档合并或具体迁移；不得连续推进。
