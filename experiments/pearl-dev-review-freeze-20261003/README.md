# PEARL Layer 1：开发难例复核与方法配置冻结

*80 题开发闭环之后的独立原文复核与发布边界登记 · status: current · 2026-10-03*

本阶段完成七道开发难例的独立原文复核、三道重排退步的排序追溯，以及现行 R1–R4 方法配置核对。四方法沿用已执行的配置，登记为 [method-freeze.json](method-freeze.json)，未进行参数搜索。**方法配置已冻结；完整评估发布版本尚未冻结。** 原开发 Gold 的三处表述需要版本化修订，现有脚本也尚未适配独立评估的 200 题。

本次没有修改原 Gold、支持映射、child、索引或既有研究输出。原 [80 题开发报告](../pearl-retrieval-dev80-20261003/development-analysis-2026-10-03.md)继续对应其原始 Gold 与映射，不把本阶段的修订建议混入原成绩。200 题及封存质控材料仅核验字节哈希和只读属性，没有解析内容或运行检索。

## 复核输入与独立性

两位语义复核子 Agent 使用 `fork_turns=none`，仅接收题目、Gold 要求、原始 PDF／canonical 身份和同源实际 child；不提供方法名、排名、分数或既有复核决定。原文事实核对与 child 支持观察分开记录。第三位子 Agent 独立检查方法配置和评估入口，不能以配置核对替代语义复核。实际调用配置与文件绑定见 [stage-preflight.json](../../outputs/pearl-dev-review-freeze-20261003-01/stage-preflight.json)。质量仍为 `agent_reviewed_preliminary`，`human_verified=false`。

原文复核使用 PDF 逐页读取和完整页面视觉核对；材料覆盖八份不同 PDF。七份包共有 512 条同源 child 实例，其中重复来源跨题复用，不能当作 512 份独立证据。新包与冻结库的正文哈希、来源成员及来源文件身份均另行核对。它们是源级复核材料，不是新支持映射。

## 难例决定

| intent | 原文复核与限制 | 本阶段决定 |
| --- | --- | --- |
| dev012 | Nicolas 摘要使用所有比例的表述；正文在 placid 条件下对有效 selfish 比例 45% 及较弱的 47% 情形给出例外，结论称几乎所有实验。广义 zipper 机制归因有依据 | 保留机制答案；提出修订 r1.scope，避免把摘要的普遍表述当作无例外的经验规律 |
| dev030 | Li 摘要和结论报告 funnel 在宽度低于约 1.31 m 时流量更高；正文另有高于阈值的矛盾句 | 保留作者报告的阈值答案；记录源内矛盾与近似阈值，不把它推广成独立确证的普遍阈值 |
| dev050 | 均值滤波与等宽条件下较低密度有原文依据；轨迹段落写 children，但参与者记录是成人 | 提出参考答案改为中性的 head sway，保留矛盾原句作为原文锚点；不声称实验参与者为儿童 |
| pilot006 | landing 速度较高，occupied-area／f1(N) 比值随占用增加而下降；分母的无重叠／无整体几何边界假设可由原文和 child 文字追溯 | 语义 Gold 保留；不把正文／结论的最大／最小措辞分歧引入当前未要求的命题 |
| dev034 | 原文明确使用线密度 m⁻¹ 与 1.25／3 的分段；canonical 和实际 child 把单位提取成 mŁ 1 | Gold 保留，题目留在分母；继续记录处理缺失，不能修补冻结 child 或借用 PDF 判定 child 支持 |
| dev079 | 来源明确选择慢行凝视、无方向改变的注意力子群；另一来源明确给出吸引势 | 保留现有建模子群范围；不能推成所有零售行人、绝无转向或模型新颖性的证明 |
| dev080 | 论文报告第二阶模型的数值行为验证，同时称其远未获得验证、需要真实实验校准 | 提出 r2.claim／scope 和参考答案明确经验验证，区分已经做过的数值验证；不降低原有真实性要求 |

完整逐页出处、哈希与建议见 [源表述复核](../../outputs/pearl-dev-review-freeze-20261003-01/reviews/source-scope-review.json)和 [联合来源复核](../../outputs/pearl-dev-review-freeze-20261003-01/reviews/source-joint-review.json)。可直接审阅的字段修订见 [gold-correction-proposal.json](../../outputs/pearl-dev-review-freeze-20261003-01/gold-correction-proposal.json)：这是尚未采用的建议，不能作为已冻结 Gold 或新成绩的依据。

## 重排退步与方法决定

使用原 Gold、最终共同映射和首遍冻结排名，另以独立布尔逻辑核对三题 R3／R4 的 K=1／5／10／20，共 24 个计分单元，全部与原成绩一致。每题候选 ID 和正文哈希完全相同。

| intent | R3 首次已知完整排名 | R4 首次已知完整排名 | 边界 |
| --- | ---: | ---: | --- |
| pilot001 | 1 | 11 | 前序关系均已审定，首次排名可确定 |
| dev070 | 9 | 37 | R4 21–36 有未决关系，37 只是已知完整路径的排名上界 |
| dev071 | 9 | 80 | R4 深层有未决关系，80 只是已知完整路径的排名上界 |

这三题的 @10 退步可归于排序变化；不能由深层未决项推断最早真实完成排名或全库缺失。详见 [rerank-loss-audit.json](../../outputs/pearl-dev-review-freeze-20261003-01/rerank-loss-audit.json)。本阶段保留默认 reranker，保留三个预设配对比较，不修改 query、候选深度、评分阈值或不利样本。

## 已登记的配置与发布缺口

| 内容 | 冻结状态 |
| --- | --- |
| 共同语料与检索输入 | 106 篇 Adobe-only 来源，6,433 child，D=100，parent 不参与检索；资产身份不变 |
| R1 | SQLite FTS5 body-only BM25；k1=1.2、b=0.75，ln-IDF 非正值 floor 1e-6；现行英文词法分析器 |
| R2 | BGE-M3 pinned revision／权重；归一化向量的 float32 精确点积 Top-100；HNSW 元数据仅保留来源说明，不是实际检索路径 |
| R3 | 两通道各 Top-100，等权 RRF k=60，保存 union 后截取 Top-100 |
| R4 | 固定同一 R3 Top-100 的完整正文，bge-reranker-v2-m3 pinned revision／权重，raw logit 排序，batch=4、query_max_length=768、pair max_length=1024 |
| 执行与评分策略 | seed=20260929，5 次开发 query 完整预热、3 遍固定顺序，首遍计分；K=1／5／10／20，主指标 CEGR@10；同分按 chunk ID 升序 |
| 版本与哈希 | [method-freeze.json](method-freeze.json)登记运行配置、资产、源码与协议／评分代码快照；[最终配置哈希核对](../../outputs/pearl-dev-review-freeze-20261003-01/configuration-hash-verification-r02.json)记录新鲜验证；初始记录单独保留 |
| 完整评估发布 | **未就绪**：三处 Gold 表述需修订并一致重算；200 题入口、split 标签、配额、输出矩阵及验证分母仍需适配 |

独立 [configuration-audit.json](../../outputs/pearl-dev-review-freeze-20261003-01/reviews/configuration-audit.json)指出 `prepare.py`、`run.py`、`blind.py`、`score.py`、`analyze.py` 和 `verify.py` 中的开发集绑定。不能把开发运行命令换一个输出目录便宣称可运行 200 题。方法参数冻结与完整发布冻结分别登记，原运行 checkpoint 保留。

## 下一项工作及验收

下一项为**Gold 表述修订和共同重算**：创建独立 Gold 修订版本，保留原版及本报告；保持 query、来源、child、四方法配置和排名不变，独立核验三道受影响题的语义／支持路径。修订后统一计算全部 80×4 的 K=1／5／10／20，重新输出主表、配对统计、修订前后差异及独立公式校验，显式绑定新旧 Gold、原排名与选定映射。不能把新 Gold 直接代入旧 manifest 伪装成原冻结分析。

随后才适配 200 题运行入口：使用合成输入验证 80／200 数量、四类配额、query-only 边界、首遍矩阵和三遍日志，不解析封存 Gold 或质控材料来开发程序。Gold、协议、方法和实际评分入口都完成版本登记后，按隔离流程导出评估 query、执行并密封排名，再做盲化支持核验。人工审查可后置，当前语义修订与程序缺口不能以人工后置为由跳过。

## 本阶段交付

本地只读复核和输出位于 [outputs/pearl-dev-review-freeze-20261003-01](../../outputs/pearl-dev-review-freeze-20261003-01/)。最终 [delivery-manifest.json](../../outputs/pearl-dev-review-freeze-20261003-01/delivery-manifest.json)绑定新材料、方法登记及文档；[verification.json](../../outputs/pearl-dev-review-freeze-20261003-01/verification.json)核对原 538 项交付文件、新包与审查记录、配置快照和 200 项封存文件的哈希／只读属性。旧文档导航的更新与旧研究输出的不可变性分别核验。本阶段未改算法、运行入口或稳定契约；没有重新执行模型，也不报告新的检索成绩。
