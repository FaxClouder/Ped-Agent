# PEARL Retrieval 语料选择记录

*英文领域来源快照的选择依据与执行状态 · status: current · corpus: pearl-retrieval-corpus-2026-09-29-01 · 2026-09-29*

## 范围与选择规则

候选池为 `memPed/knowledge/` 下五个 `batch-1-incoming` 至 `batch-5-incoming` 目录的全部 PDF，另审计 `batch-1-held`。本轮直接扫描实际原文，不沿用旧评估题集、旧语料成员表、旧索引或既有检索结果。已有 `core_manifest.jsonl` 和批次 inventory 只提供可交叉核对的书目与哈希元数据；本次纳入依据是来源处于 incoming、标题和书目主题属于行人流／人群疏散领域、PDF 能打开并提取英文文本、来源字节可用 SHA-256 固定。

同一内容哈希只允许一个来源身份；每份 PDF 的 DOI 和标题保留作核对线索。英文检查使用来源语言元数据及前 3 页的英文常用词启发式，标题检查使用书目标题词与前 3 页文本的交集。这些是技术筛查，不能替代逐篇人工核实出版身份与全部正文。

## 本次扫描和选择

| 项目 | 结果 |
| --- | ---: |
| 扫描到的领域 PDF | 110 |
| 纳入来源快照 | 108（1956 页） |
| held，未纳入 | 2 |
| 纳入项唯一 SHA-256／唯一 DOI | 108／108 |
| 与既有 `derived/<resource>/<source-hash>/document.json` 可对照 | 104；仅作历史处理产物盘点 |
| 有低文本页告警的纳入文件 | 1 |

108 篇均已用 PyMuPDF 打开并有可提取文本；104 篇存在与历史书目表一致的来源哈希。另有 4 篇 incoming PDF 未列在历史 104 篇主清单中，本次按相同的原文技术规则纳入：`Alqahtani_2025`、`Aurell_2019`、`Li_2023_AppliedMathematicalModelling`、`Su_2024_TBS`。它们此前因旧内容评分门槛被暂缓；该旧门槛不作为 PEARL 的评估输入规则。四篇在本轮仍需和其他原文一样接受题目与证据适用性核验。

两份 held 文件 `Liddle_2009_arXiv_BottleneckWidthLengthCongestionExperiment.pdf` 与 `Vanumu_2017_ETRR_FundamentalDiagramsPedestrianFlowReview.pdf` 不在此次 incoming 来源范围内，逐份保留在审计文件中。前者是预印本候选，后者已有明确移出 incoming 的来源记录；若将来纳入，需要版本化修改语料选择并说明理由。

`Huang_2023_SafetyScience_MachineVisionCrowdDensityEstimation.pdf` 第 15 页只有 82 个可提取字符；其余页面可提取，故保留来源并在后续来源锚点核验时特别检查该页。审计文件中的低文本告警不得自动解释为 Gold 证据缺失。

书目主主题的来源分布为疏散行为建模 39、实验测量 19、设施场景与流动 21、流动基础 20、安全风险与干预 9。此分布只描述论文元数据，**不能证明** 80＋200 题、数值／表格、多证据与跨论文比较的证据配额已满足。

## 冻结边界与下一项核验

本版本固定**PDF 成员与字节**，依据为 [主清单](corpus-manifest.jsonl) 的逐份 SHA-256；主清单文件自身的 SHA-256 是 `f484cde3acf0d67c0982477679a24926a9544bb2bb7ec4803d2597ff8f8697ff`。每条记录的 `source_id` 从原文哈希派生，不继承旧 `resource_id` 作为 PEARL Gold 身份。

目前尚未完成逐篇出版身份人工审定、表格与跨页证据可用性检查，也未证明四类题型可以按预定数量构建。下一个准备步骤从这 108 篇中试标四类英文开发题，保存精确来源锚点、条件和替代证据路径。若核验发现某 PDF 不适用、需增删来源或文件变化，应先创建新语料版本，再冻结相应 Gold；不能在本版中静默更换来源。
