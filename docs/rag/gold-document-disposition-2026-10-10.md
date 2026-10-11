# PEARL 出题相关文档核对与整理建议

*v1.2 修订后的文档职责、合并与删除候选；status: current · 2026-10-10；未执行文件删除或历史原件迁移*

## 维护分工

后续规则入口为 [Gold v1.2](gold-question-standard-v1.2.md)，管理题型、数量目标、出题、证据与 QA；[评测总规范](../../experiments/EVALUATION-STANDARD.md)负责资产与实验治理；[登记表](../../experiments/EVALUATION-REGISTRY.yaml)记录已登记身份；[验收标准](../research-review-standard.md)负责验收来源。四者不复制整套条款。

## 文档清单与处置

| 文档或组 | 用途 | 建议处置/本次情况 |
| --- | --- | --- |
| [Gold v1.2](gold-question-standard-v1.2.md) | 新版统一规则 | 新建，持续维护；不是已冻结题集 |
| [评测总规范](../../experiments/EVALUATION-STANDARD.md) | 存放、冻结、访问和实验管理 | 本次补新版适用范围与出题链接；旧登记资产身份保留。第 7 节依赖 6B 的后续评价计划需另行审定，不自行重启 |
| [登记表](../../experiments/EVALUATION-REGISTRY.yaml) | 题集/实验身份及哈希 | 保留；新题集冻结时再登记。旧切块状态 in_progress_6B 应据终止记录另行更正，不在本次冒充已处理 |
| [研究验收标准](../research-review-standard.md) | Agent/人工与验收边界 | 保留，其他文档引用，不另造人工门槛 |
| [外部 v1.1 原稿快照](../../outputs/gold-standard-revision-20261010-01/PedRAGent_PEARL_Gold_v1.1.original.md) | 本次修订来源 | 保留历史快照，不再作为后续执行入口 |
| [新版原构建计划 v1.1](../../outputs/pearl-question-redesign-pilot-20261008-01/plan_v1.1_corpus106.md) | 最初分工与试标执行计划 | 通用规则已收敛到 v1.2；原文件保留计划身份，不移动/删改 |
| [Solver](../../outputs/pearl-question-redesign-pilot-20261008-01/phase2-evidence-review-20261009-01/work/protocol/solver_spec_v1.md)、[Auditor](../../outputs/pearl-question-redesign-pilot-20261008-01/phase2-evidence-review-20261009-01/work/protocol/auditor_spec_v1.md)、[补充协议](../../outputs/pearl-question-redesign-pilot-20261008-01/phase2-evidence-review-20261009-01/work/protocol/protocol_addendum_v1.1.md) | 历史执行与质量依据 | 可合并的是未来通用规则，已纳入 v1.2；批次权限和历史提示原件必须保留。新批次另生成绑定 v1.2 的角色包 |
| [旧 authoring](../../experiments/pearl-dataset-80-200-20261003/authoring-spec.md)、[旧 review](../../experiments/pearl-dataset-80-200-20261003/review-spec.md)、[冻结记录](../../experiments/pearl-dataset-80-200-20261003/README.md) | 旧 80/200 题生成与复核的复现依据 | 保留，不能用 v1.2 覆盖旧实验规则；可在导航说明旧版本范围 |
| [检索标注操作规范](../../paper/pearl-framework/annotation/retrieval-guideline.md)、[标注入口](../../paper/pearl-framework/annotation/README.md) | 旧试标说明及指标接口 | 通用出题条款可改为引用 v1.2；试标历史、PEARL 指标定义保留。此项尚未修改 |
| [Gold 规范副本入口](../../memPed/knowledge/gold/pearl-adobe106/README.md) | 已冻结题集位置 | 保留；新候选尚未冻结，不能写成正式替代或搬入 Gold |
| [旧集中整理](../../outputs/pearl-question-redesign-pilot-20261008-01/question-set-consolidation-20261010-01/handoff.md)、[旧补足计划](../../outputs/pearl-question-redesign-pilot-20261008-01/question-set-consolidation-20261010-01/dev50_completion_plan.md) | 当时 38 题状态和补题依据 | 原件保留；新入口说明后续云端为 39。新补题执行计划需另建，不直接改旧计数 |
| [云端接收包](../../outputs/pearl-question-redesign-pilot-20261008-01/cloud-revision-import-20261010-01/README.md) | 最新候选、QA、修订和哈希 | 保留最新接收入口；Excel 是阅读版，完整 JSON 是接收原件，不能因信息相似删掉任一唯一交付 |
| [旧 Gold 准备指南](../gold-questions-guide.md) | PEARL 前示例 | 可退出当前导航或改为仅历史链接；开头指向 Gold v5 的“当前”说明需更新。旧例仍有历史用途，尚不建议物理删除 |
| [RAG 资产清单](asset-inventory.csv)、[组织报告](organization-report.md)、[后续清单](follow-up-backlog.md) | 另一整理 session 的交付快照 | 保留原交付哈希；本次新增规范与新状态由导航说明，后续清单刷新应形成新快照，不静默改旧清单 |

## 哪些可以合并

新计划、Solver/Auditor 与 addendum 中通用出题/证据/审核规则统一维护到 v1.2；原执行包仍保留。旧 authoring/review 不与新数据身份合并。评测总规范不复制全部题型/字段，引用 v1.2；登记表和验收标准不并入长篇出题文档。

## 哪些可以删除

本次没有发现可直接删除的权威原件。优先删除或替换的是维护文档中的重复现行规则段落，而非历史文件。

物理删除候选仅限后续确认的字节相同临时副本、过期导出缓存、重复下载件；需同时证明已有可恢复原件、哈希相同、无脚本/链接/manifest 依赖，并获得具体删除授权。当前未完成这类逐文件依赖核验，故不列任何“已批准可删”的路径。

不得删除：题集原件、云端接收原件、旧 QA/provenance、冻结/交付 manifest、历史提示规范、输出目录与 Past 索引绑定文件。合并阅读入口不等于可以删除来源。

## 本次已完成与后续

已完成：新规范 v1.2、本文清单、总规范的新版适用条款、docs 与 RAG 导航入口更新。未改任何题目、答案、QA、登记身份或实验数据，未删文件。

后续按本文“尚未修改/需另行”事项分批处理；不把文档维护当作补题、审核完成或 Gold 冻结。修订来源、备份及验证记录见[本次交付](../../outputs/gold-standard-revision-20261010-01/handoff.md)。
