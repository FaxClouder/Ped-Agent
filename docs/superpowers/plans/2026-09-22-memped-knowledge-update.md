# memPed 与知识库更新实施计划

_分阶段更新、迁移与验收计划 · status: plan · 2026-09-22；本次仅制定计划，任务均未执行_

> **执行方式：** 后续采用 executing-plans 逐任务实施；若另行选择并行代理，再使用 subagent-driven-development。本文是跨阶段总计划，不要求一次完成所有阶段或部署外部记忆系统。

**Goal:** 建立可恢复、可发布、可回查的知识证据库，并增量增加研究卡与主题导航。

**Architecture:** 保留 Vault/Catalog/双索引；先修复治理、构建与评测闭环，再通过最小共享契约连接 Agent。研究记忆是有依赖的派生内容，外部框架仅作可选旁路。

**Tech Stack:** 现有 Python、Pydantic、SQLite/FTS5、PyMuPDF、BGE-M3/Chroma、JSON/JSONL、Markdown；基础阶段不新增框架依赖。

## 1. 全局约束与阅读入口

- 遵循仓库 [AGENTS.md](../../../AGENTS.md) 与[目标设计](../specs/2026-09-22-memped-knowledge-update-design.md)。
- 不覆盖已有原文、derived、索引、报告；不直接迁移活动数据库。
- memPed data-only；跨模块试验在 experiments；所有新实验产物在 outputs 的独立 run id。
- 不引入 Web 服务、会话数据库、任务队列、图数据库或自动桌面记忆采集。
- 新字段先兼容旧读取，旧证据身份保留；来源不能解析时显式失败，不猜测最新版本。
- 修改一个模块或一个稳定契约形成独立提交/审查单元；不捎带整理现有工作区修改。
- 源哈希、模型/配置/代码指纹、seed、实际降级状态、指标口径必须进入报告。
- 单元测试不能替代真实模型验收；资料 unknown 状态不能自动转 approved。

本计划给出模块任务、接口责任、文件清单、行为样例和退出门槛。后续单个阶段实施前依据当时源码展开局部代码补丁；这里不预写数千行跨阶段实现以免冻结未经测试的代码。

## 2. 阶段依赖与交付包

```mermaid
flowchart LR
    P0[P0 盘点与恢复副本] --> P1[P1 治理闭环]
    P1 --> P2[P2 不可覆盖构建]
    P2 --> P3[P3 评测与发布基线]
    P3 --> P4[P4 稳定证据契约]
    P4 --> P5[P5 修订与附件]
    P5 --> P6[P6 研究卡及主题视图]
    P6 --> P7[P7 Agent 问答实验]
    P7 --> P8[P8 可选 memU 旁路]
```

| 交付包 | 内容 | 可独立完成的结果 |
| --- | --- | --- |
| A：可信基线 | P0—P3 | 当前批准语料可构建、检索、评测、发布与恢复 |
| B：研究资料管理 | P4—P6 | 精确证据契约、多附件/修订、版本化研究卡与导航 |
| C：科研问答增强 | P7 | 比较/条件问题有证据槽位、引用约束与拒答评测 |
| D：外部复用评估 | P8，可选 | 有依据地决定采用或停止 memU 旁路 |

A 不依赖 B/C/D。完成 A 就有可用科研基线，无需等待所有扩展。复杂版面解析器和检索模型替换另做消融，不加入 A 的同时改造。

## 3. 文件变更总表

所有下列路径相对仓库根目录；“新增”路径是计划内容，当前可能不存在。已有大 __init__.py 只保留兼容导出和必要调用改动，不做无关全量拆分。

| 区域 | 修改已有文件 | 新增文件/目录 | 边界 |
| --- | --- | --- | --- |
| 治理 | Knowledge-Base/src/ped_knowledge/governance/contracts.py；governance/audit.py；storage/__init__.py；contracts/__init__.py；memPed/knowledge/literature_quality_rules.yaml | Knowledge-Base/src/ped_knowledge/governance/approvals.py | 批准凭据，不在线计算期刊评分 |
| 构建/存储 | Knowledge-Base/src/ped_knowledge/ingestion/__init__.py；parsing/__init__.py；storage/__init__.py；indexing/__init__.py | Knowledge-Base/src/ped_knowledge/storage/migrations.py；storage/builds.py；ingestion/derive.py | 独立构建与恢复，不扩展后台服务 |
| 评测/发布 | Knowledge-Base/src/ped_knowledge/evaluation/__init__.py；retrieval/__init__.py | Knowledge-Base/src/ped_knowledge/evaluation/gold_v2.py；evaluation/metrics_v2.py；storage/releases.py | 口径版本化；整套资产发布 |
| 共享证据 | Contracts/src/ped_contracts/evidence.py；Contracts/src/ped_contracts/__init__.py | Contracts/tests/test_evidence_provenance.py | 只共享 locator/provenance，不共享 Catalog schema |
| 附件/修订 | Knowledge-Base/src/ped_knowledge/storage/migrations.py；storage/__init__.py；contracts/__init__.py；ingestion/__init__.py | Knowledge-Base/src/ped_knowledge/storage/assets.py | 多附件字节及版本关系，不执行附件脚本 |
| 研究卡 | Knowledge-Base/src/ped_knowledge/retrieval/__init__.py | Knowledge-Base/src/ped_knowledge/research/__init__.py；research/contracts.py；research/store.py；research/views.py | 规范卡/依赖/视图；生成实验外置 |
| Agent | Agent/src/ped_research_agent/ports.py；context.py；policy.py；evidence_graph.py | Agent/src/ped_research_agent/coverage.py | 消费稳定证据端口，不读数据库 |
| 试验 | experiments/README.md | experiments/benchmark-knowledge-rebuild-20260922/；integration-research-cards-20260922/；exploration-memory-sidecar-20260922/ | 最后一个仅在 P8 创建 |
| 文档与忽略 | .gitignore；Knowledge-Base/README.md；memPed/README.md；Contracts/README.md；Agent/README.md；docs/project-architecture.md；docs/README.md | 各实验 README 与版本化配置 | current 随验收更新 |

每项新代码所属目录保留已有 import 边界；共享 EvidenceItem 字段以可选字段开始迁移，严格发布门禁另行要求其完整性。

## 4. P0：建立真实资产清单与可恢复副本

**文件：** 新建 experiments/benchmark-knowledge-rebuild-20260922/README.md、inventory.py、config.yaml；修改 .gitignore、experiments/README.md；新增 Knowledge-Base/tests/test_workspace_inventory.py。

**输入/输出：** 只读 Catalog、治理记录、Vault/derived/索引目录 → inventory.json、missing-assets.json、source-manifest.json、backup-manifest.json；全部写 outputs/memped-upgrade/<run-id>/。

- [ ] 先写临时目录样例：缺失源、错误哈希、无 chunks 表、孤立 derived，盘点应分类报告且不改输入文件。
- [ ] 实现只读盘点与一致性 SQLite 备份；记录 Git revision、dirty diff/源码指纹、模型配置和输入哈希。
- [ ] 增加 assets、catalogs、research、indexes、releases 和新副本 SQLite 的忽略规则，保留明确可提交的公开 schema/config。
- [ ] 在新目录恢复备份，比较源文件哈希、数据库表计数和清单；写 restore-report.json。
- [ ] 对账现有 Gold 与批准记录；未知批准只标 unknown，不修改原 Catalog eligibility。
- [ ] 审查并提交本阶段代码/文档，排除所有运行数据和既有无关修改。

**退出门槛：** 输入哈希前后一致；恢复成功；现有断点有清单；git check-ignore 确认新增运行资产被忽略。

## 5. P1：治理批准与正式资格闭环

**文件：** 新建 governance/approvals.py；修改治理/导入内部契约与 storage；更新 literature_quality_rules.yaml 和 collection_standard.md；新增 Knowledge-Base/tests/test_approval_binding.py。

**接口责任：** validate_approval(record, resource_id, source_sha256, rules_version) 校验绑定并输出明确错误；批准事实由离线人工记录提供。legacy include 不再能独立授予正式发布资格。

- [ ] 固定样例：缺批准、批准旧哈希、规则版本不匹配、withdrawn 均不能正式发布；可明确作为实验资料归档。
- [ ] 增加 ApprovalRecord 解析及规范内容哈希；未知 reviewer/time 不自动补造。
- [ ] 用一套当前规则配置消除 YAML 与代码漂移；保留期刊/引用阈值的现有政策，本阶段不擅自降低门槛。
- [ ] 在 P0 副本登记批准映射；保留 legacy 状态字段用于历史读取，生成差异清单。
- [ ] 验证治理变化不会触发重新解析 PDF；官方资格检查只校验记录而不在线查期刊数据。
- [ ] 更新模块/资料说明并独立提交。

**退出门槛：** 正式发布候选成员均有可核验批准；unknown 不泄漏；历史 50 篇若未全审核，只报告已审核范围，不声称完整库验收。

## 6. P2：拆分源导入与派生构建

**文件：** 新建 storage/migrations.py、storage/builds.py、ingestion/derive.py；修改 ingestion/parsing/storage/indexing 的现有入口；新增 Knowledge-Base/tests/test_build_lifecycle.py、test_catalog_migration.py。

**接口责任：** ensure_parse_build(source_ref, parse_config, output_root) 与 ensure_chunk_build(parse_manifest, chunk_policy, output_root) 返回完整 BuildManifest；名称为本阶段计划新增接口。source_ref 明确 resource_id/version_id/source hash/path，不传隐式全局活动版本。

- [ ] 固定样例：相同源 SHA 已导入但无 Chunk，显式 derive 可补建；再次导入仍 unchanged，不承担修复职责。
- [ ] 固定样例：同源 V1/V2 各有独立 chunks 路径；新增构建前后旧文件哈希相同。
- [ ] 增量 schema migration 记录版本，在副本上建立 parse/chunk build 登记；重复 migration 幂等。
- [ ] 仅通过结构/哈希/抽检合格的旧 canonical 可复用；其余重新解析到新 build。
- [ ] 构建使用 staged → complete/failed；模拟文件写入和登记间失败，失败产物不可被检索或发布。
- [ ] 索引目录/collection 以 index build 显式配置；禁止默认落回共用目录。
- [ ] 先对 5—10 篇代表资料运行，再扩大到冻结语料；分别保存真实模型可用与不可用状态。
- [ ] 更新构建说明并独立提交。

**退出门槛：** 原文和旧 derived 零覆盖；同策略确定性 Chunk id 一致；父子引用完整；失败构建零发布。此阶段不将 V2 自动设为默认。

## 7. P3：可信评测与整套发布

**文件：** 新建 evaluation/gold_v2.py、evaluation/metrics_v2.py、storage/releases.py；修改 evaluation/__init__.py、retrieval/__init__.py；新增 test_gold_v2.py、test_release_snapshot.py；新建实验 run.py、evaluate.py、publish.py 与 schema 配置。

**接口责任：** Gold v1 reader 保持旧语义；Gold v2 表达 answerable 与证据组。build_release_manifest 将语料、Catalog、索引和验收绑定；activate_release 只在所有前置条件通过时切换登记引用。

- [ ] 建立指标固定样例：预期 A/B/C、仅命中 A 时 Hit=1、Resource Recall=1/3、Complete Evidence=0；A 的 p.2 不能匹配 B 的 p.2 或 A 的 p.20。
- [ ] 为不可回答题、重复 resource chunk、替代证据组、缺定位标注定义固定输出；新旧 report 标注 metric schema。
- [ ] 原 pilot_gold.jsonl 保留；新建 Gold v2 文件，人工校验 source/version/page 标注；保存开发/锁定集成员与哈希。
- [ ] 在固定解析/语料上运行 BM25、Dense、Hybrid V1、Hybrid V2；只有切块变化时才归因到 V2 整包效果。
- [ ] 构建期间冻结 Catalog 快照；分别核对 FTS/Dense 指纹、成员数量和真实检索模式。
- [ ] 门禁失败、模型缺失、未声明降级、Gold 不完整时保留 candidate；不可发布 official。
- [ ] 验证活动引用切换及整套回滚；模拟一个索引缺失，旧完整 release 仍可解析。
- [ ] 新目录恢复发布资产并复跑固定查询，写恢复报告；更新基线文档并独立提交。

**退出门槛：** Pilot v1 全量门槛按现有配置通过；v2 使用预先冻结开发阶段阈值和逐题对比，不事后调低。正式发布的失败构建/非批准泄漏/跨策略混用均为 0。

完成此阶段交付 A，可以暂时停止扩展并开展科研检索实验。

## 8. P4：共享精确证据契约

**文件：** 修改 Contracts/src/ped_contracts/evidence.py、__init__.py、Knowledge-Base 检索转换；新增 Contracts/tests/test_evidence_provenance.py；扩展 Agent/tests/test_contracts.py。

**接口责任：** 可选 EvidenceLocator 与 EvidenceProvenance 附加到 EvidenceItem；旧 locator 保留展示用途。原文版本、parse/chunk build、page/element/span 在新数据中明确。

- [ ] 固定样例：旧 EvidenceItem payload 仍能加载；新字段能 round-trip；span 越界、源版本不匹配必须被源回查拒绝。
- [ ] 文献收录资格与 publication_type/authority 分开，停止将所有本地论文等同于官方法规权威。
- [ ] parent 中新增事实若不在 child quote 内，必须解析并补发对应证据，而非仅引用原 child。
- [ ] 先跑 Contracts 与 Knowledge-Base/Agent 契约测试，再跑四模块全套。
- [ ] 同步 Contracts README 与引用说明，独立提交稳定契约。

**退出门槛：** 旧消费者兼容；新证据可定位到保存原文；共享契约不含存储路径访问逻辑。

## 9. P5：修订与附件身份扩展

**文件：** 新建 storage/assets.py；修改内部 contracts、migration、Catalog/ingestion；新增 test_resource_assets.py、test_legacy_version_resolution.py。

**输入/输出：** 在副本中从旧单 PDF version 映射出 revision_id、asset_id、revision_assets 与 legacy alias；原字节路径保留，新增补充附件写新资产目录。

- [ ] 样例覆盖相同 DOI 的不同 PDF、两条书目引用同字节、正文+补充 PDF+CSV；各自关系不得丢失。
- [ ] 旧 SHA version alias 在原 release 下保持可解析；新 revision 不覆盖旧版本。
- [ ] 附件按 MIME、角色、哈希登记；ZIP/代码附件只登记保存，不执行或自动解包。
- [ ] 迁移完成后比较资源/附件映射、文件哈希、引用可解析率；失败则弃用新副本，保留原库。
- [ ] 在独立快照重建检索；正文检索范围与附件能力显式声明，不因保存 CSV 就声称支持表格问答。
- [ ] 更新数据 README 和迁移报告后独立提交。

**退出门槛：** 旧引用零丢失；文件身份与书目身份分开；修改策略只影响新增产物。

## 10. P6：研究卡与主题视图

**文件：** 新建 research/__init__.py、contracts.py、store.py、views.py；新增 test_research_cards.py、test_research_invalidation.py；新增 experiments/integration-research-cards-20260922/README.md、config.yaml、run.py。

**接口责任：** ingest_card 校验证据依赖并保存新 revision；resolve_card_evidence 返回原文 EvidenceItem；build_topic_view 使用明确卡版本；invalidate_dependents 根据源/build 变更标记受影响内容。

- [ ] 先用人工撰写的 reading/method/finding 样例贯通，避免初次验证同时依赖 LLM 抽取正确性。
- [ ] 规范 JSON、人工 Markdown、自动 Markdown 各有独立权威；旧 card revision 与人工笔记不可覆盖。
- [ ] 证据 ref 校验资源/版本/build/span/hash；无依据卡保持 candidate，不能输出为正式原文证据。
- [ ] 源变更使相关卡和主题 stale；无关卡不变；冲突 finding 并存并保存条件与单位。
- [ ] 同资料多主题只增加关联，PDF 不复制；主题视图固定成员及生成指纹。
- [ ] 实验层可调用现有 Agent 模型适配生成候选卡，保存实际结果；Knowledge-Base 不反向依赖 Agent。
- [ ] 比较纯原文召回与主题导航+直接召回并行两方案；记录低频研究漏检、证据完整性与 token。
- [ ] 验收后更新研究卡文档，独立提交。

**退出门槛：** 固定样例的来源回查与失效定位均为 100%；不把模型总结作为 quote；原文直接召回仍可使用。

## 11. P7：Agent 证据充分性与比较问答

**文件：** 新建 Agent/src/ped_research_agent/coverage.py；修改 ports.py、context.py、policy.py、evidence_graph.py；新增 Agent/tests/test_evidence_coverage.py；扩展研究卡集成实验。

**接口责任：** coverage 接收问题所需证据槽位与 EvidenceItem，不读取 memPed；检索适配在 experiments 组合 KB 与 Agent。先以确定性规则实现方法/比较/精确资料题型。

- [ ] 固定样例：单篇精确条款可足够；两篇无关论文仍不足；比较题缺条件或单位时明确缺口。
- [ ] 上下文按 evidence/parent 去重及 token 预算组织，截断不能移除引用需要的条件说明。
- [ ] 检查断言引用支持与 parent 补证；外部检索不能隐式改变冻结本地 benchmark 的语料。
- [ ] 评测答案支持度、条件/单位错误、正确拒答和误拒答，人工抽检校准模型判定。
- [ ] 运行跨模块完整测试；保存真实端到端运行配置和成本，更新 Agent README 并独立提交。

**退出门槛：** 科研问答收益可以归因于证据组织；测试中的已知单位冲突、无依据断言不被标记为 verified。

## 12. P8：可选 memU 旁路验证

**文件：** 仅新增 experiments/exploration-memory-sidecar-20260922/README.md、config.yaml、adapter.py、run.py、test_mapping.py；使用隔离依赖环境。

- [ ] 固定 memU commit、依赖和存储配置；先决定使用已调研旧三层或当前 RecallFile 模型，不能混用。
- [ ] 只输入公开/授权的小语料或研究卡；保存外部 ID → memPed 证据映射。
- [ ] 旁路返回导航候选后，回查 memPed 再生成 EvidenceItem；禁止旁路直接授予 official。
- [ ] 测量来源回查成功率、源删除/修订后残留记忆、token/延迟、接入维护成本；与 P6 自建视图比较。
- [ ] 有稳定净收益才形成后续采用决策；无收益保留报告，不修改主链。

**退出门槛：** 输出可追溯、生命周期可控且收益优于维护成本；未满足时停止采用属于有效实验结论。

## 13. 验证命令与数据运行入口

以下测试命令可用于后续代码阶段；本次计划编写不声称已经运行它们。新增单测文件在相应阶段创建后才存在。

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python -m pytest Knowledge-Base/tests -q
.\.venv\Scripts\python -m pytest Contracts/tests Agent/tests Knowledge-Base/tests Video-Analysis/tests -q
```

各任务的新增测试先以目标行为失败，再实现最小变更，最后运行所属模块；跨契约任务运行全套。验证数值采用本文固定样例，避免仅验证函数存在。

计划新增实验入口约定如下，当前不可直接运行：

```powershell
.\.venv\Scripts\python experiments/benchmark-knowledge-rebuild-20260922/inventory.py --config experiments/benchmark-knowledge-rebuild-20260922/config.yaml --run-id inventory-001
.\.venv\Scripts\python experiments/benchmark-knowledge-rebuild-20260922/run.py --config experiments/benchmark-knowledge-rebuild-20260922/config.yaml --run-id baseline-001
.\.venv\Scripts\python experiments/benchmark-knowledge-rebuild-20260922/evaluate.py --run-id baseline-001 --gold-version pilot-v1
```

所有入口拒绝复用已存在 run-id；无参数时不自动发布、迁移或覆盖。配置记录 source_catalog、source_manifest、approval_manifest、source_scope、output_root、chunk_policy、lexical_config、embedding_config、gold_path、seed 和 strict_retrieval_mode。publish.py 接收验收通过的 release manifest，不自动搜索“最新”结果。

## 14. 文档同步、风险和完成定义

| 风险 | 控制措施 | 拒绝进入下一阶段的条件 |
| --- | --- | --- |
| 工作区已有修改被混入 | 开始阶段记录状态；隔离实现、只提交本阶段文件/hunk | 无法解释代码快照或输入来源 |
| 历史资产被覆盖 | 副本迁移、新 build/run、promote-copy | 原文件哈希变化 |
| 治理历史缺失 | unknown + 明确实验 scope | 官方候选无批准绑定 |
| 小 Gold 误导优化 | 固定开发/锁定集、按题型报告、逐题分析 | 用测试标签调参或隐藏不可评题 |
| 多格式/多版本扩展破坏引用 | legacy alias + old release resolver | 任一既有引用无法定位 |
| 自动摘要污染证据 | 类型隔离、依赖回查、候选审核 | 摘要被直接标成原文 quote |
| 运行能力被夸大 | 实际设备/模型/失败模式单列 | 仅有替身测试却标记 GPU/OCR 已验证 |

阶段完成同时要求：功能与固定例子成立、必要测试通过、真实运行范围有证据、旧资产未覆盖、恢复方法验证、current 文档只更新已完成部分。新 maintained 文档进入 docs/README.md；不把本计划复选框勾选当作验收依据。

当前仅完成设计与计划文档；P0—P8 均未执行。推荐后续先执行交付包 A，再根据真实结果决定 B/C 的细节和 D 的必要性。
