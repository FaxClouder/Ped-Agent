# PEARL 开发 Gold r02 修订分析

*固定原首遍排名的阶段 A 交付 · status: current · agent_reviewed_preliminary · human_verified=false · 2026-10-03*

三处开发 Gold 修订、独立实际 child 复核、80×4 共同重算与独立验证已完成。CEGR@10 为 **47／49／51／58**，原 r01 为 47／48／51／58。数值变化仅涉及 dev012；三项预设 Holm p 均 >0.05。结果属于开发修订分析，200 题继续封存，完整评估发布尚未冻结。

## 输入与修订边界

沿用 106 篇 Adobe-only 来源、6,433 child、原索引、方法冻结和原首遍 320 条排名。全部 80 query、原 8 题全文、其余 77 题完整语义对象及四类各 20 的配额不变。D=100，K=1/5/10/20，seed=20260929，同分按 chunk ID 升序。R1 body-only FTS5 BM25；R2 归一化 float32 精确点积；R3 等权 RRF k=60；R4 原 R3 Top-100 完整 child 重排。本次没有新检索、GPU 推理、时延实验或参数搜索。

新 loader 先验证原运行与原 Gold，再通过独立 revision manifest 绑定新 Gold、差异和审查。原 run/preflight 的 Gold SHA 保留，原 score.py 对新 Gold 的身份拒绝行为保留。原 r01 分析及全部旧输出保留。

| 题目 | 实际采用修订 | 出处／限制 |
| --- | --- | --- |
| 012 | 保留 zipper 机制答案；r1.scope 改为近乎全部实验，并注明例外 | Nicolas PDF p1/6/8/13；45%/47% 为 placid 条件的有效 selfish 比例。数字限定研究范围；query 仍问机制。独立 child 复核不再把摘要的无例外句单独当作完整修订范围支持 |
| 050 | reference_answer 改为中性的 head-sway 干扰及均值滤波 | Li PDF p1/2/3/4；children 原锚点不改，成人大学生记录的矛盾保留；49/50 帧文字差异另记，不改变原 query/要求 |
| 080 | r2.claim/scope 和答案区分经验验证与数值验证；增加 a3，r2 必需 bundle=[a2,a3] | Twarogowska PDF p14 明确数值验证；a3 独立原文锚点和实际 child 路径，旧 a2 校准句不自动支持 a3 |

030 保留作者约 1.31 m 阈值及源内方向矛盾；pilot006 保留 f1(N) 分母；034 保留单位损坏、处理缺失及评分分母；079 保留建模子群范围。上述题没有可选语义修订。

## 独立支持复核与版本选择

两个独立子 Agent 使用 fork_turns=none、继承配置且无模型覆盖。只提供中性实际 child 包及 review-spec，未提供排名、方法、分数、旧结论或 PDF。主执行者的原文核对另存，不进入 child 支持标签。

| 题目 | Top-20 联集必审关系 | 充分审定关系 | 补充未知关系 | 接受 atom 路径 |
| --- | ---: | ---: | ---: | --- |
| 012 | 37 | 44 | 165 | a1:4 |
| 050 | 34 | 34 | 120 | a1:1，a2:3 |
| 080 | 54 | 60 | 202 | a1:2，a2:1，a3:2 |

共 125 个必审关系全部审定；三题共审定 138 个关系，487 个补充关系保持未知。77 题只继承原 selected-review-files.json 的唯一已选版本，Gold 全对象、packet、正文和审查全文 SHA 均验证。新选择清单恰含 80 个唯一 intent。080 的首份序列化草稿保留，最终显式选择 pearl-dev-080-r02.json；修订仅修复单元素嵌套数组序列化，未改语义判断。

## 主表与全部 K

95% CI 使用四层各 0.25 权重的配对 intent bootstrap，10,000 次，seed=20260929，NumPy linear 分位数。以下为边际区间，未作同时区间或 Holm 区间解释。

| 方法 | CEGR@10（95% CI） | BestGroupCov@10（95% CI） | CompleteMRR@10（95% CI） | r01→r02 完整题数 |
| --- | --- | --- | --- | --- |
| R1 | 47/80=0.5875 [0.5125, 0.6625] | 0.7125 [0.6500, 0.7750] | 0.3927 [0.3267, 0.4619] | 47→47 |
| R2 | 49/80=0.6125 [0.5250, 0.7000] | 0.7375 [0.6625, 0.8062] | 0.3794 [0.3098, 0.4496] | 48→49 |
| R3 | 51/80=0.6375 [0.5625, 0.7125] | 0.7562 [0.6875, 0.8187] | 0.4192 [0.3531, 0.4870] | 51→51 |
| R4 | 58/80=0.7250 [0.6500, 0.8000] | 0.8313 [0.7750, 0.8813] | 0.5162 [0.4544, 0.5746] | 58→58 |

每格依次为 CEGR／BestGroupCov／CompleteMRR；均 N=80。

| K | R1 | R2 | R3 | R4 |
| ---: | --- | --- | --- | --- |
| 1 | 0.3000 / 0.3812 / 0.3000 | 0.2750 / 0.3500 / 0.2750 | 0.3250 / 0.4375 / 0.3250 | 0.4125 / 0.5250 / 0.4125 |
| 5 | 0.5250 / 0.6438 / 0.3837 | 0.5000 / 0.6125 / 0.3650 | 0.5500 / 0.6625 / 0.4071 | 0.6375 / 0.7438 / 0.5046 |
| 10 | 0.5875 / 0.7125 / 0.3927 | 0.6125 / 0.7375 / 0.3794 | 0.6375 / 0.7562 / 0.4192 | 0.7250 / 0.8313 / 0.5162 |
| 20 | 0.6875 / 0.8000 / 0.3996 | 0.7250 / 0.8187 / 0.3857 | 0.7375 / 0.8375 / 0.4258 | 0.8250 / 0.8938 / 0.5233 |

## 逐题差异及分层

全部 308 个未修订题方法单元的完整评分对象与 r01 一致。三题的 12 个单元保留完整路径结构差异；其中只有 dev012 的 R1/R2/R4 产生标量指标变化，共 10 个 K 前缀。050、080 所有 K 的指标不变；080 即使不改变当前分数，新增必需命题仍由独立 a3 路径验证。

| dev012 方法 | r01 首次完成位置（≤20） | r02 首次完成位置 | 实际变化 |
| --- | ---: | ---: | --- |
| R1 | 1 | 3 | @1 完整→不完整；@5/10/20 仍完整，CompleteMRR 下降 |
| R2 | 11 | 10 | @10 不完整→完整，新联合路径于第10位齐备；@20 原本完整 |
| R3 | 5 | 5 | 标量指标不变 |
| R4 | 1 | 2 | @1 完整→不完整；@5/10/20 仍完整，CompleteMRR 下降 |

R2 增加的一题来自修订后的独立联合支持映射；原 query、child 和顺序不变。该变化应与范围修订和重新盲审一起解释，不能归因于检索算法或调参改善。

四层 @10 完整题数（每层 N=20）：

| 层 | R1 | R2 | R3 | R4 |
| --- | ---: | ---: | ---: | ---: |
| cross_paper | 0/20 | 3/20 | 3/20 | 5/20 |
| numeric_table | 16/20 | 16/20 | 17/20 | 19/20 |
| single_source | 20/20 | 19/20 | 19/20 | 19/20 |
| within_paper_multi | 11/20 | 11/20 | 12/20 | 15/20 |

## 配对统计与来源依赖

| 预设差 | 胜/负 | CEGR 差（百分点） | intent CI（百分点） | 精确 McNemar p | Holm p | 来源分量 CI（百分点） |
| --- | --- | ---: | --- | ---: | ---: | --- |
| R2-R1 | 6/4 | 2.50 | [-5.0000, 10.0000] | 0.753906 | 1.000000 | [-5.0000, 7.9281] |
| R3-R2 | 3/1 | 2.50 | [-2.5000, 7.5000] | 0.625000 | 1.000000 | [-1.7857, 13.5470] |
| R4-R3 | 10/3 | 8.75 | [0.0000, 17.5000] | 0.092285 | 0.276855 | [-8.4428, 19.9303] |

R4−R3 的 intent 区间下端浮点值约 1.1e−16，显示为 0；不以舍入或该边际区间替代 Holm 判断。三项 Holm p 均 >0.05。来源图仍为 32 篇出题来源、12 个连通分量，最大 33 题；来源分量 bootstrap 10,000 次均可估计，但三项差区间均跨零。来源复用、题族及额外等价支持限制独立性解释；这不是正式独立评估结论。

## 失败、未知深度与既有损失

@10 不完整单元 115/320，其中已知深层充分路径 R_TOPK=88，未足够归因 UNRESOLVED=27。R_RERANK_LOSS=3 与前述标签重叠，不能相加当互斥总数。

pilot001、dev070、dev071 的 R4 @10 退步全部保留。dev034 四方法所有正式 K 均不完整，处理缺失仍在分母。来源／页命中只作诊断。21–100 未审关系仍为未知；深层正向路径仅证明已知支持存在，不能证明不存在更早证据或声称全深度 R3/R4 覆盖不变。此次没有新增时延测量，原 instrumented／审计扣除估计及其限制继续对应 r01 原运行。

## 验证与交付入口

本次原开发全实验测试 47 项通过；最终新实验 21 项＋原针对性 33 项，共 54 项通过。拒绝测试覆盖偷换 Gold SHA、query/77 题漂移、重复/缺题、所选全文变化、child 正文变化、K20 未审、错原排名，以及重新绑定后的越界字段、原 atom/source 漂移、缺 a3、弱化 bundle、provenance 漂移及同语义异字节审查。独立布尔 oracle 重开保存的输出，1,280 个前缀及 48 个总体指标一致。原评分从原排名/映射重算与 r01 保存全文一致。未跨稳定契约，不宣称运行全仓 suite。

旧开发 538 项、难例复核 93 项，244 项冻结 source/canonical/index/model 输入，以及 200 项封存 byte hash/只读属性均核验一致。200 内容未解析，正式运行数仍为 0。代码审查的两项绑定缺口已修复并再次批准；初次发现及复查记录均保留。

| 交付 | 入口 |
| --- | --- |
| 新Gold | [gold-r02.json](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/gold-r02.json) |
| 精确字段差异 | [gold-diff.json](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/gold-diff.json) |
| 独立修订绑定 | [revision-manifest.json](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/revision-manifest.json) |
| 80唯一版本选择 | [selected-review-manifest.json](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/selected-review-manifest.json) |
| 盲审独立性 | [review/reviewer-provenance.json](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/review/reviewer-provenance.json) |
| 原文核对 | [source-check/factual-review.json](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/source-check/factual-review.json) |
| 共同支持映射 | [analysis-r02-01/support-map.json](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/analysis-r02-01/support-map.json) |
| 1,280前缀完整评分 | [analysis-r02-01/score-details.json](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/analysis-r02-01/score-details.json) |
| 320行矩阵 | [analysis-r02-01/scores.csv](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/analysis-r02-01/scores.csv) |
| 配对/来源统计 | [analysis-r02-01/statistics.json](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/analysis-r02-01/statistics.json) |
| 320单元逐题差异 | [analysis-r02-01/delta-vs-r01.json](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/analysis-r02-01/delta-vs-r01.json) |
| 失败及未知深度 | [analysis-r02-01/per-intent-failures.json](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/analysis-r02-01/per-intent-failures.json) |
| 独立公式及保存绑定验证 | [analysis-r02-01/verification.json](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/analysis-r02-01/verification.json) |
| 原成绩与未变题验证 | [baseline-and-delta-verification.json](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/baseline-and-delta-verification.json) |
| 最终测试 | [test-verification-r02.json](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/test-verification-r02.json) |
| 代码复查 | [code-review-r02.json](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/code-review-r02.json) |
| 冻结输入验证 | [immutable-input-verification.json](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/immutable-input-verification.json) |
| 交付哈希 | [delivery-manifest.json](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/delivery-manifest.json) |

阶段 A 达到交付门槛。下一检查点为阶段 B：使用合成 80/200 输入适配 split、expected_count、query-only 和 frozen-release 门禁，继续封存正式评估内容。阶段 C 完整发布与阶段 D 200 题评估尚未执行；本报告不替代后续阶段验收。
