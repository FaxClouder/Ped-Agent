# PEARL Adobe 106：80／200 题集构建

*冻结语料上的英文开发题与独立封存评估题 · status: current · 2026-10-03*

本次执行 [Retrieval-v0.2](../../paper/pearl-framework/layer-1-retrieval/experiments.md)。现有 8 题保留其语义和身份，新增 72 题使开发集达到四层各 20 题；独立新建评估集四层各 50 题。题目、答案和来源原子由子 Agent 初标并交叉复核。旧知识库 Gold、题集、索引和结果不作为输入。

## 输入与隔离

- 语料：`outputs/pearl-index-106-adobe-20260929-01/sources.jsonl`，106 篇 Adobe 来源；其 PDF 和 canonical 哈希逐份复核。
- 现有开发题：`paper/pearl-framework/datasets/retrieval-pilot/pearl-retrieval-dev-pilot-8-adobe106-gold.json`。
- authoring seed：20260929。开发出题来源 32 篇（含原 8 题的 7 篇来源），评估出题来源 74 篇分成两个独立工作包。两集出题来源互斥；全部 106 篇仍属于同一检索语料，这不构成未见文献测试。
- 原文 PDF 阅读用于核验来源事实；当前检索资产仍为 Adobe child 快照。读 PDF 不重新切块或建索引。
- 每题记录 `family_id`、英文 query、完整参考答案、requirements、非空 AND/OR bundles、source atoms 和证据组。格式见 [authoring-spec.md](authoring-spec.md)。

## 执行任务

- [x] 核验 106 篇输入并生成三个无排名信息的原文工作包，冻结来源分配。
- [x] 初标新增开发 72 题、评估 200 题；数值题保留单位、条件和原文精度，多证据及跨论文题具备真实互补证据。
- [x] 另一子 Agent 逐题核验答案、条件、定位、组内充分性与题型；修复争议后再次复核。
- [x] 检查题族、近重复和仅替换数字的模板家族跨集泄漏；检查四层配额、来源／canonical 哈希、PDF 锚点与非空组。
- [x] 独立保存 80 题开发 Gold 与 200 题评估 Gold、复核记录和审计清单；最后对评估资产设置只读并冻结 SHA-256。评估排名尚不运行。

本地工作包与审查中间文件位于新的 `outputs/pearl-dataset-80-200-authoring-20261003-01/`；禁止覆盖旧研究输出。封存发生在全部内容核验及泄漏检查之后；封存题不参与开发调参。

## 当前质控

三位初标 Agent 各自完成开发 72、评估 A 100、评估 B 100 题；不同的三位复核 Agent 已逐题核对实际 PDF、条件和充分支持路径，覆盖新增题的 497 个 atom。另一全局复核 Agent 扫描全部 280 题，独立回读 11 道修订题原文并确认 70 道跨论文题的比较依据。作者与批次复核者调用配置为 `gpt-6.1-sol`，全局复核为 `gpt-6-astra`；均记录调用配置依据，未声称人工 Gold。

机器审计核对 PDF／Adobe 哈希、结构、配额和来源锚点；不能替代语义审查。表格空白正规化保留小数标点，`2 .41` 可定位 `2.41`，`241` 不能替代 `2.41`；表格另由页图核验。

出题及复核均不读取方法排名或得分。来源 Gold 保留原文可回答但 Adobe 遗失的证据；后续 child 支持映射必须明确记录这种处理缺失。原 8 题保持原文、答案、条件和证据结构，不沿用旧 child 映射到新增题。

独立复核接口见 [review-spec.md](review-spec.md)。封存门槛包括精确候选 SHA 上的逐题接受记录、全部 atom 复核、四层配额、来源哈希、原 8 题不变，以及另一 Agent 对全体 280 题的语义题族扫描。机器近似匹配为诊断，零标记不表示已经完成语义去重。

## 已发布资产

> 2026-10-07：下表文件已逐字节复制到规范位置 `memPed/knowledge/gold/pearl-adobe106/retrieval/`（登记号 `qs-dev80-r01`、`qs-eval200-r01`），SHA-256 不变；新实验从规范位置读取，下表原路径作为冻结出处保留。

状态为 `agent_reviewed_preliminary`，`gold_frozen=true`；独立评估未执行。原 8 题 JSON 内容与原 Gold SHA 保持不变。

| 资产 | 路径 | SHA-256 |
| --- | --- | --- |
| 开发 80 题 | [开发 Gold](../../outputs/pearl-retrieval-dev80-eval200-adobe106-20261003-01/pearl-retrieval-dev-80-adobe106-gold-20261003-r01.json) | `4b118700b2ec810dd57d342ab3d5447b7d313c11aea73535dff160bfaba2d56c` |
| 封存评估 200 题 | [评估 Gold](../../outputs/pearl-retrieval-dev80-eval200-adobe106-20261003-01/pearl-retrieval-eval-200-adobe106-gold-20261003-r01.json) | `25c0e5d1d493155f23fdee1ff1d6773e0ea74f7b013e5ad4a2805423f4fd9d70` |
| 冻结与封存清单 | [seal_manifest.json](../../outputs/pearl-retrieval-dev80-eval200-adobe106-20261003-01/seal_manifest.json) | `c3524b0095e610e4ce325166f357903d3319da6dd0de23adc63277381d4a656b` |

评估 Gold、198 份评估／混合质控资产及清单已设置只读；109 份原文工作包输入哈希重新通过核验。实际发布先在同父暂存目录写入完整资产、核验哈希与只读属性，再原子改名；缺少完整封存清单的暂存目录不能当作可用题集。只读属性不阻止读取，封存同时依赖禁止将评估题用于调参的操作规则。

## 内容分布与运行前协议登记

| 项目 | 开发 | 封存评估 |
| --- | ---: | ---: |
| intent | 80 | 200 |
| 四个互斥主层 | 各 20 | 各 50 |
| 使用来源 | 32 | 74 |
| source atom | 173 | 358 |
| requirement | 120 | 315 |
| table_cell atom | 8 | 22 |
| 具有替代 support bundle 的 intent | 8 | 19 |
| 额外 support bundle | 11 | 22 |
| 具有替代完整 evidence_group 的 intent | 0 | 0 |

**运行前修订登记（2026-10-03）**：[协议 §1](../../paper/pearl-framework/layer-1-retrieval/experiments.md#1-研究对象与样本)力争的 16／40 道替代完整组目标未达成。本轮仅保留实际核验的 bundle 与组，不制造等价组，也不据此断言 106 篇语料不存在其他等价路径。当前题集不支持报告替代完整组题型的实测效果；一般 AND／OR 评分逻辑保留。来源依赖分布与结构证据需求记录在封存清单中，不把它们当成实测难度。

批次复核修复实验条件遗漏、跨页联合支持、被引内容指代、预期与已验证能力及关联与因果等问题。全局扫描另发现并修复 dev046 的同义要求冗余、dev031／eval028 的群组比例题族重复、dev038／eval040 的引导改善百分比题族重复；实际更换研究角度，未靠改写掩盖重复。修订前后字段、原文页依据、首审和终审均保留；全局记录为 [family-review-final-r01.json](../../outputs/pearl-dataset-80-200-authoring-20261003-01/family-review-final-r01.json)。

开发题 dev034 的 Adobe 单位 glyph 损坏，dev035 的 Adobe 词序交错；原 PDF 支持完整命题，保留 source Gold。[80 题实际 child 盲审](../pearl-retrieval-dev80-20261003/development-analysis-2026-10-03.md)已独立核验：dev034 原单位要求在实际 child 中未完整满足，四方法 K≤20 不完整；dev035 有可接受的实际结论 child 路径，四方法 @10 均完整。来源存在或同页命中不代替支持，PDF 追溯不回填评分。

## 执行与验证

全部命令在仓库根目录执行；输出路径已存在时脚本拒绝覆盖。

```powershell
.\.venv\Scripts\python -m pytest experiments/pearl-dataset-80-200-20261003 -q
.\.venv\Scripts\python experiments/pearl-dataset-80-200-20261003/freeze_dataset.py --config outputs/pearl-dataset-80-200-authoring-20261003-01/freeze-input-config-r02.json --output-dir outputs/pearl-retrieval-dev80-eval200-adobe106-20261003-01
```

专项测试 11 项通过，覆盖来源分区、独立审查精确哈希与 atom 覆盖、全局 280 ID 覆盖、强题族碰撞拒绝、表格小数空白及封存路径预检。实际发布后独立复核两个 Gold 哈希、198 个封存资产的哈希和只读属性、清单只读、原 8 题内容及哈希、暂存目录不存在；全部通过。

发布后的独立核验保存为 [verification.json](../../outputs/pearl-retrieval-dev80-eval200-adobe106-20261003-01/verification.json)，仅对封存评估文件做哈希与属性检查，没有重新读取题目内容。维护文档 141 个本地链接无缺失；本阶段仅改实验代码及记录，不跨稳定合同。

[80 题同配置四方法开发对照](../pearl-retrieval-dev80-20261003/README.md)已完成三遍真实运行、实际 child 独立盲审、统一支持映射、320 单元评分和开发分析；原 Gold 与原 8 题不变。结果为 `agent_reviewed_preliminary`，不是人工 Gold 或 200 题正式评估。[原 8 题试标](../pearl-index-106-adobe-20260929/README.md)及输出保留；下一阶段复核开发难例与配置，200 题继续封存且未运行。
