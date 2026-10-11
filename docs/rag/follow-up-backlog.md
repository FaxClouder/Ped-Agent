# 知识侧 RAG 后续整理与正文调整清单

*知识侧 RAG 组织整理 · status: plan · 2026-10-10*

本表用于下一轮讨论；本阶段全部未执行。当前原件、冻结题集、绑定输出、PDF、数据库、权重、索引及Past所指原件不搬迁。不新增默认人工验收门槛。future目标以文字表示，不伪装为现有链接。

## 正文修订候选

| ID | 源文件/定位与当前表述 | 证据 | 影响与建议 | 依赖/本阶段不执行原因 |
| --- | --- | --- | --- | --- |
| B01 | [rag-design-spec](../rag-design-spec.md)第4.2/7节（原165/286行）“6B评价进行中”；第9节D11依赖6B | [终止记录](../../Past/child-parent-Sum/README.md) | 拟说明2026-10-08终止、6B无最终评分；再讨论D11依赖 | 正文改写超出组织整理授权；不重启研究 |
| B02 | [docs总导航](../README.md)原87行及[旧索引实验](../../experiments/benchmark-index-20260924/README.md)“V1/V2索引目录已迁failed” | [V1原目录](../../outputs/knowledge-index-104-v1-20260924-01/)、[V2原目录](../../outputs/knowledge-index-104-v2-candidate-20260926-02/)、本轮基线 | 拟区分索引仍在outputs与评分进入failed，核对其他候选索引引用 | 需按目录逐项核定，当前只加主题入口 |
| B03 | [登记表](../../experiments/EVALUATION-REGISTRY.yaml) exp-chunking-dev80为in_progress_6B；[评测规范](../../experiments/EVALUATION-STANDARD.md)第7节Layer2–4独立评价以6B完成为前提 | [终止记录](../../Past/child-parent-Sum/README.md) | 拟更新执行状态/依赖叙述，保留冻结路径、哈希与既有使用史 | 不重写登记表、不替用户选择新评价方案 |
| B04 | [Layer3旧计划](../superpowers/plans/2026-10-04-pearl-answer-next-session.md)“未执行”；[V2实施记录](../superpowers/plans/2026-09-17-rag-tokenization-v2.md)与[总导航](../README.md)末部E0“未运行E1” | [Layer3实验](../../experiments/pearl-answer-dev80-20261004/README.md)、[E1收尾](../../experiments/pearl-chunking-dev80-20261005/session3-closeout-2026-10-06.md)、[V2历史目录](../../outputs/knowledge-index-104-v2-candidate-20260926-02/) | 拟在维护入口注明时点快照和后续交付；旧计划正文保留历史 | 不将旧计划整体“完成化”，需逐条比对 |
| B05 | [旧审计](../rag-asset-audit-2026-10-07.md)“唯一一份”冻结Gold与6B进行中；[memPed说明](../../memPed/README.md)提交Git通则列Gold | [规范位置](../../memPed/knowledge/gold/pearl-adobe106/README.md)、[规范](../../experiments/EVALUATION-STANDARD.md)第2节本地保存 | 拟标清审计快照时点、Gold本地规则覆盖通则 | 本轮不追改快照或提交Gold |
| B06 | [候选旧交接](../../outputs/pearl-question-redesign-pilot-20261008-01/phase2-evidence-review-20261009-01/next_session_single_agent.md)、[剩余工作记录](../../outputs/pearl-question-redesign-pilot-20261008-01/phase2-evidence-review-20261009-01/remaining_work.md)与后续交付关系 | [重跑交接](../../outputs/pearl-question-redesign-pilot-20261008-01/phase2-evidence-review-20261009-01/single-agent-rerun-01/handoff.md)、[集中交接](../../outputs/pearl-question-redesign-pilot-20261008-01/question-set-consolidation-20261010-01/handoff.md) | 拟加后续入口，保留v3问法与v2答案/QA，C-007/D-004未决独立登记 | 不改题、答案、QA；不补题或冻结Gold |
| B07 | [RAG个人汇总](../../outputs/RAG改进与实验计划汇总.md)被旧审计指出含/mnt/project-files外部路径 | [旧审计](../rag-asset-audit-2026-10-07.md)第3.3节 | 是否纳入维护文档及修订路径待讨论；目前unknown/reference | 未核定完整引用或正文权威，不直接复制成current |

## 重复、合并及迁移候选

| ID | 源布局/建议目标（仅候选文字） | 关系及证据 | 引用/保护状况 | 后续建议与依赖 |
| --- | --- | --- | --- | --- |
| O01 | Past/child-parent-Sum/copied 与 experiments/paper/outputs原件；保持原位 | [copy-manifest](../../Past/child-parent-Sum/copy-manifest.json)与[原件索引](../../Past/child-parent-Sum/index-all-files.jsonl)；本轮MD哈希相同者在CSV标明 | manifest/hash及脚本按原路径保护；摘要副本不等于完整冻结包 | 不合并删除；继续导航，若讨论冗余先逐文件范围/引用核定 |
| O02 | memPed/knowledge/gold/pearl-adobe106 与outputs/paper冻结来源；保持规范副本+来源原件 | [登记表](../../experiments/EVALUATION-REGISTRY.yaml)、[哈希核对](../../outputs/rag-asset-organization-20261010-01/validation/registry-hashes.csv) | 双路径均有来源绑定，封存题集不读取正文 | 不把字节相同当作可删；冻结副本不是迁移对象 |
| O03 | docs/rag-design-spec.md、rag-development-roadmap.md及专题spec；建议先保持原位，可能统一主题目录下导航 | 当前设计汇总/长期计划/target职责不同，只有内容相近，未证明重复 | 已知引用：docs/README.md、docs/project-architecture.md、rag-development-roadmap.md；完整引用检索未核定，受文档路径引用保护 | 如下一轮讨论迁移先生成完整链接图/兼容入口，再决定；本轮不合并正文 |
| O04 | outputs根部RAG笔记及e3/pearl命令日志；新运行的建议目标为各自run目录 | [基线](../../outputs/rag-asset-organization-20261010-01/baseline/files-before.csv)、[评测规范](../../experiments/EVALUATION-STANDARD.md)第4.2节 | 历史日志可能被manifest/hash绑定；完整脚本/manifest引用检索未核定 | 旧文件不搬；将建议用于未来新运行，不更改历史绑定 |
| O05 | docs历史入库/测试/批次报告；建议目标候选docs/rag/history（尚未创建） | 原文带historical；清单保留原状态和路径 | 完整引用图未核定；并非字节相同证据 | archive_candidate仅供讨论；先用主题导航解决查找，不执行移动 |

## 未决核查

| ID | 未决项 | 下一轮依据 | 当前边界 |
| --- | --- | --- | --- |
| U01 | CSV lifecycle/authority为unknown的说明及包 | 原README、handoff、manifest和来源链；优先[资产清单](asset-inventory.csv)筛选 | 不从目录名final/latest/编号推断完成或权威 |
| U02 | 历史索引与当前Catalog指纹 | [移除记录](../../memPed/knowledge/reports/pymupdf-two-papers-removal-2026-10-08.md)的检查命令 | 本轮只定位；需检索实验授权才建新索引，不覆盖 |
| U03 | C-007/D-004及50题缺额 | [集中交接](../../outputs/pearl-question-redesign-pilot-20261008-01/question-set-consolidation-20261010-01/handoff.md)、[补足计划](../../outputs/pearl-question-redesign-pilot-20261008-01/question-set-consolidation-20261010-01/dev50_completion_plan.md) | 不在组织任务中继续取证、出题、独立评审或系统测试 |

本表全部为后续候选；没有完成迁移、合并、删除、正文修订或新技术采纳。下一阶段由用户查看交付后另行决定。
