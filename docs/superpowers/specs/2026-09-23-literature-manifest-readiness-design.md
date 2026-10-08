# 文献 Manifest 准备表与正式生成设计

_五批 PDF 文献从内容初筛转入逐篇准入核查的设计 · status: plan_

## 目标与安全边界

为五批文献建立可复核、可重建的 Manifest 准备表。当前
[`screening.csv`](../../../memPed/knowledge/literature/records/screening.csv) 中 108 篇
有 104 篇高于 65 分，4 篇已标记为 `temporarily_not_used`。准备表只覆盖前 104 篇；
4 篇只保留在现有候选与筛选记录中，不生成准备表行或任何 Manifest 条目，
不删除 PDF。构建核对仅统计排除数量，不为这 4 篇另建逐篇清单。

准备表不是 `ped_knowledge.contracts.IngestionManifest` JSONL，不含 `include` 字段，
不得交给 `ImportService.import_manifest`。当前活动导入程序即使遇到 `include=false`
也仍会处理文件，因此不能把该字段当作“草稿安全开关”。本设计不执行导入、解析、
建索引或发布。

## 数据流与文件职责

在 `Knowledge-Base/` 中提供可重复执行的离线构建逻辑；它只读取五批 inventory、
`candidates.csv`、`screening.csv`、`citation_snapshots.csv` 和已核验的期刊指标表，
以及本地 PDF 的只读属性。代码不得写入 `memPed/`。输出为新命名的
`memPed/knowledge/literature/records/manifest_readiness_2026-09-23.csv`，和单独命名
的本地构建/缺项报告，不覆盖现有 `pilot_manifest.jsonl`、`core_manifest.jsonl`
或历史评判报告。

每行以规范化 DOI 与 `resource_id` 唯一对应，至少保存批次、题名、原文件相对路径、
inventory SHA-256、实测 SHA-256 是否一致、PDF 技术检查结果、内容总分和筛选决策、
正式版本状态、引用快照来源/数值/日期、期刊指标匹配状态、完整性状态、使用权限
状态、A/B/X 等级、人工复核状态和明确的 `blocker_codes`。来源缺失时保持空值或
`pending`，不能猜测 `clear`、引用次数、授权或等级。相同 DOI、重复 SHA、缺 PDF、
哈希不符、无法解析等必须出现在报告中，不能静默跳过或改写 inventory。

## 准入状态

- 104 篇是“内容分数满足”的准备对象，不是 104 篇已批准论文。
- 已标记人工证据局限复核的 18 篇继续待复核；领域范围和 PDF/DOI 身份两项独立
  阻断继续保留。68 篇 `publication_status=unverified`、2 篇缺引用数值，以及尚未
  分配的 A/B/X 等级均按当前记录呈现，不能自动转为通过。
- 期刊来源核查的既有结果可引用，但必须逐篇匹配其 venue 与来源年份；匹配不明
  时标记待核实，不把来源级核查等同于文章级准入。
- 只有在正式版本、PDF 身份/合法性、完整性、内容复核、期刊分区、引用、受控
  主题和等级/配额全部留有证据并获人工确认后，才能从准备表选择批准记录生成
  技术 `IngestionManifest` JSONL。正式 JSONL 在生成后仅运行只读
  `preflight_manifest`；导入及索引发布属于后续单独授权步骤。

## 验证

构建器以固定输入文件和 SHA-256 记录 provenance。测试覆盖 108 篇输入中仅为
104 篇生成准备表行、4 篇只计数不输出条目、
DOI/`resource_id` 唯一性、五批 inventory 与候选表一对一匹配、原评分不变、
缺项不被伪装成通过、路径与哈希验证、技术 Manifest 不会在准备阶段生成。
构建后核对 104 行和每类阻断数量；再运行知识模块测试，若触及共享契约则运行
仓库全套测试。任何输入冲突进入报告并阻断正式 JSONL 生成，不覆盖原记录。
