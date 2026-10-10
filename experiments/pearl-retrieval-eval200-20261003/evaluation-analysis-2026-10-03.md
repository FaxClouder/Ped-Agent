# PEARL Retrieval：200 题固定评价分析

*阶段 C 完整发布之后的固定评价与共同计分 · status: current · 2026-10-03 · agent_reviewed_preliminary，human_verified=false*

本次以原封存 200 题完成固定 R1–R4 三遍检索、首遍共同支持映射、800 个题×方法单元与 3,200 个前缀评分，独立 Boolean oracle 复核全部前缀及 48 个总体指标。统计分母始终为 200 意图；600 次计时查询是重复测量，开发 80 题另表，不合并 N=280。实际内容判断仍由独立 Agent 完成，不能称人工 Gold。

CEGR@10 为 R1 116/200（58%）、R2 118/200（59%）、R3 126/200（63%）、R4 139/200（69.5%）。R4−R3 提高6.5个百分点，19题收益、6题退步，三项 Holm 调整 p=0.04390；配对意图区间为[2.00%, 11.50%]，来源分量敏感性区间为[0.94%, 11.10%]。这是冻结题集及当前 Agent 支持判断下的比较，来源敏感性不替代人工校验或新的独立数据。

R4@10 的单来源题50/50、数值／表格题48/50，同文多片段31/50，跨文献题10/50。总体提高没有消除多证据整组完成的不足；跨文献仍是这次题集的主要薄弱层，不能仅依据总平均宣称全部题型已解决。R4估计方法总时延约为R3的14.47倍；效果、退步和成本需要共同报告。未在本次执行层2或Agentic补证，也不由深层未知自动归因解析／召回损失。

## 固定方法与执行

106 篇 Adobe-only、6,433 child，R1 正文 FTS5 BM25；R2 归一化 float32 精确点积 BGE-M3；R3 两通道各 D=100、等权 RRF k=60；R4 固定 R3 Top-100 完整 child 重排。模型、分词、算法、索引、来源、统计和代码均绑定冻结 release；K=1/5/10/20、CEGR@10 主指标、seed=20260929。没有按评价结果调参、换模型、重新解析／切块、扩 parent 或进行 Agentic 比较。

阶段 C 导出前独立核验、隔离 query-only 导出与实际启动门禁见[发布记录](stage-C-public-report.md)及[固定预注册](preregistration.md)。首次准备的编码失败及第二次预热顺序拒绝保留于独立目录；第三次完整冻结后才运行真实评价。原预热为开发 query 按固定 seed 打乱取前5，三遍各200题。首遍800单元密封；后两遍共1,600单元的排序、分数、候选全文和 query 向量完全一致。执行失败、attempt failure 和重试均为0；原 run_manifest 的 quality_scores=null 是运行端隔离记录，质量结果保存于新文件，不追改运行清单。

## 完整 K 指标

| K | 方法 | CEGR | BestGroupCov | CompleteMRR |
| --- | --- | --- | --- | --- |
| 1 | R1 | 41/200 (20.50%) | 0.2575 | 0.2050 |
| 1 | R2 | 34/200 (17.00%) | 0.2050 | 0.1700 |
| 1 | R3 | 45/200 (22.50%) | 0.2650 | 0.2250 |
| 1 | R4 | 80/200 (40.00%) | 0.4900 | 0.4000 |
| 5 | R1 | 94/200 (47.00%) | 0.5575 | 0.3031 |
| 5 | R2 | 89/200 (44.50%) | 0.5475 | 0.2739 |
| 5 | R3 | 105/200 (52.50%) | 0.6200 | 0.3367 |
| 5 | R4 | 123/200 (61.50%) | 0.7300 | 0.4767 |
| 10 | R1 | 116/200 (58.00%) | 0.6750 | 0.3180 |
| 10 | R2 | 118/200 (59.00%) | 0.7075 | 0.2937 |
| 10 | R3 | 126/200 (63.00%) | 0.7525 | 0.3512 |
| 10 | R4 | 139/200 (69.50%) | 0.7975 | 0.4875 |
| 20 | R1 | 133/200 (66.50%) | 0.7625 | 0.3243 |
| 20 | R2 | 136/200 (68.00%) | 0.7900 | 0.2998 |
| 20 | R3 | 145/200 (72.50%) | 0.8250 | 0.3581 |
| 20 | R4 | 153/200 (76.50%) | 0.8650 | 0.4922 |

CEGR 是完整证据组是否在前 K 内完成；BestGroupCov 保留最佳组覆盖；CompleteMRR 按前 K 内首次完整组完成位置计算。全部方法使用同一份实际 child 支持映射。

## CEGR@10 分层与预设配对统计

| 题型（各50） | R1 | R2 | R3 | R4 |
| --- | --- | --- | --- | --- |
| cross_paper | 3/50 (6.00%) | 4/50 (8.00%) | 4/50 (8.00%) | 10/50 (20.00%) |
| numeric_table | 43/50 (86.00%) | 43/50 (86.00%) | 47/50 (94.00%) | 48/50 (96.00%) |
| single_source | 47/50 (94.00%) | 48/50 (96.00%) | 49/50 (98.00%) | 50/50 (100.00%) |
| within_paper_multi | 23/50 (46.00%) | 23/50 (46.00%) | 26/50 (52.00%) | 31/50 (62.00%) |

按原四层配对意图向量 bootstrap 10,000 次、seed=20260929、固定层权重各0.25，95% 区间采用 numpy linear 分位数。下表的区间是边际区间，不是 simultaneous 或 Holm 调整区间。

| 方法 | CEGR 95% CI | BestGroupCov 95% CI | CompleteMRR 95% CI |
| --- | --- | --- | --- |
| R1 | [53.00%, 63.00%] | [0.6300, 0.7175] | [0.2790, 0.3564] |
| R2 | [54.49%, 63.50%] | [0.6650, 0.7475] | [0.2555, 0.3317] |
| R3 | [58.50%, 67.50%] | [0.7175, 0.7875] | [0.3130, 0.3884] |
| R4 | [65.00%, 74.00%] | [0.7625, 0.8325] | [0.4571, 0.5180] |

| 预设比较 | 更优方法独有成功 b | 基线独有成功 c | CEGR差（百分点） | 差95% CI | exact McNemar p | 三项 Holm p |
| --- | --- | --- | --- | --- | --- | --- |
| R2-R1 | 14 | 12 | +1.00 | [-4.00%, 6.00%] | 0.84501898 | 0.84501898 |
| R3-R2 | 13 | 5 | +4.00 | [0.00%, 8.00%] | 0.096252441 | 0.19250488 |
| R4-R3 | 19 | 6 | +6.50 | [2.00%, 11.50%] | 0.014633298 | 0.043899894 |

b/c 是左侧方法成功而右侧失败／左侧失败而右侧成功的配对题数；正差只表示本题集上的差值。三项预设比较共同进行 Holm 调整；输出中的 R3−R1 是额外描述性诊断，不并入三项预设显著性家族。来源依赖和 Agent 标签限制推断，不将重复执行增加为统计样本。

## 来源依赖

Gold 来源图共有 25 个连通分量，最大分量 23 题；覆盖 74 个出题证据来源，单来源最多涉及 7 题，来源 incidence HHI=0.0151。整分量重采样保持原四层权重，有效重复 10000，缺层而不可估计重复 0。 满足冻结的分量区间报告门槛；来源敏感性区间如下。

| 比较 | 来源分量 CEGR 差 95% CI |
| --- | --- |
| R2-R1 | [-3.64%, 5.66%] |
| R3-R2 | [0.43%, 8.12%] |
| R4-R3 | [0.94%, 11.10%] |

开发和评估的出题来源互斥，但检索全集共同固定106篇，因此不能称未见文献泛化。来源关联传递连接跨层题，普通意图配对区间与来源分量敏感性必须分别理解。

## 内容复核、质量失败与深层未知

独立 fresh fork_turns=none 语义角色只读分配的中性实际 child 包与 review-spec，继承配置无模型覆盖；没有接收方法／排名／分数、作者／QC、原判断或 PDF 补文。K≤20 四方法 union 的 7,762 个必审 child–intent 关系全部纳入充分审读。最终200题选择由显式文件及完整 SHA 绑定，四方法共享；实际充分审定关系共 7,959，未充分审读的 supplementary 关系 32,578 保持 unresolved。

| 实际语义 reviewer | 本次最终选择题数 |
| --- | --- |
| /root/eval_child_review_a | 21 |
| /root/eval_child_review_a_next | 46 |
| /root/eval_child_review_c_extra | 21 |
| /root/eval_child_review_c_next | 12 |
| /root/eval_child_review_b | 60 |
| /root/eval_child_review_b_next | 30 |
| /root/eval_child_review_b_tail | 10 |

角色交接只移交未完成题的中性包；既有题采用原实际复核者显式选择，后继角色不重复审查。064、132 的 list 序列化初稿保留，原复核者另存 r02；机械校验确认仅列表包装变化、语义路径／证据／审读分区不变，最终显式选择修正版。机械门禁只核查 schema、字面摘录、必审覆盖、角色和 SHA，协调者不做语义裁决。

182 的路径内重复 child ID 由原复核者另存 r02 去重；独立机械核验确认语义 child 集合、literal evidence 和审读分区保持一致。156 是原独立内容复核者在冻结前补正自己的实际支持路径，初稿与 r02 同时保留；这属于语义复核修订，不能描述为仅格式改变。没有据此重新检索、调整方法或由协调者补造支持。最终使用的非初稿版本如下，完整逐文件 SHA 位于显式选择清单：

| 意图 | 实际选择文件 |
| --- | --- |
| pearl-eval-064 | pearl-eval-064-r02.json |
| pearl-eval-132 | pearl-eval-132-r02.json |
| pearl-eval-156 | pearl-eval-156-r02.json |
| pearl-eval-182 | pearl-eval-182-r02.json |
| pearl-eval-185 | pearl-eval-185-r02.json |
| pearl-eval-191 | pearl-eval-191-r02.json |

| 方法 | @10质量未完成题数 | @100已知完整 | @100充分审读仍不完整 | @100未决 |
| --- | --- | --- | --- | --- |
| R1 | 84 | 175 | 0 | 25 |
| R2 | 82 | 170 | 0 | 30 |
| R3 | 74 | 181 | 0 | 19 |
| R4 | 61 | 181 | 0 | 19 |

质量未完成与执行失败分别保存。21–100 处未审补充内容仍未知；已有肯定路径可证明存在，未知内容不能证明不存在，也不能据此断言 OCR／切块／索引丢失。精确首次完成位置只有此前所有候选充分审读时才可确认，其他保存上界。层2未执行。[失败与未知](../../outputs/pearl-retrieval-eval200-20261003-01/failures-and-unknown.json)保留逐题缺失 requirement 和四方法深层状态。

[证据约束失败诊断](../../outputs/pearl-retrieval-eval200-20261003-01/failure-diagnostics.json)复用冻结诊断公式，800单元中 @10 未完成 301 个；标签计数为 `{"R_RERANK_LOSS": 6, "R_TOPK": 208, "UNRESOLVED": 93}`，标签可重叠。R_TOPK 只在实际已知深层完整时登记；R_RERANK_LOSS 只在R3@10完成、R4@10未完成时登记。不能满足诊断证据条件的项保持 UNRESOLVED，不自动归因为候选召回／切块／解析损失。

## 实际模型输入与成本

| 计时项目（秒，N=600重复查询） | mean | p50 | p95 |
| --- | --- | --- | --- |
| R1 total | 0.04175 | 0.04066 | 0.05750 |
| R2 total（扣审计估计） | 0.03961 | 0.03821 | 0.05063 |
| R3 total（扣审计估计） | 0.08148 | 0.07963 | 0.10426 |
| R4 total（扣审计估计） | 1.17897 | 1.12048 | 1.76783 |
| R4 reranker gross（实际仪表） | 1.10210 | 1.04422 | 1.69458 |
| 完整 adapter wall（实际仪表） | 1.50657 | 1.44332 | 2.08190 |

实际 timed R4 输入 60,000 对，预热另500对；实际 dense token 最大60、reranker token 最大617，输入正文与 token identity 已核验，截断为0。gross 是实际同步仪表时延；扣除 CPU 输入核验与 forward hook 采集的 method total 是估计，不能等同于完整 adapter wall。完整 wall 累计约 903.94 秒；CLI 另含模型／索引加载、门禁和保存。硬件为 Windows 11、i7-12700K、RTX3080 10GB，Python3.12.7、torch2.14.0+cu130／CUDA13.0；实际版本、GPU UUID 与库文件以 release 为准。未宣称新 OCR 或视频模型验证。

## 解释边界、身份与复现

替代完整组实际0，未达原目标（开发16、评估40）；不能把多child支持路径说成多替代完整组达标。开发034处理损失／分母、030源内矛盾、pilot006分母、079建模子群及三个既有R4退步仍保留为开发限制，不改成评价结论。开发 r02 CEGR@10 47/49/51/58（N=80）见[原修订分析](../pearl-retrieval-gold-revision-r02/development-gold-r02-analysis-2026-10-03.md)，不与本表相加，Gold修订不解释为算法改善。标签质量始终 agent_reviewed_preliminary、human_verified=false；若后续据此调参，后续分析标探索性。

访问分离由独立 Agent 上下文、query-only 运行契约和输入白名单实施；共享Windows账号具有文件访问能力，不声称 OS ACL 隔离。封存原文件的只读属性、旧输出、原配置／入口／模型与冻结身份均保留；不修改旧manifest追平导航差异，不自动 commit／push／清理／创建工作树。

| 主要身份 | SHA-256／证据 |
| --- | --- |
| release | `f42c1c25dab4f7662a3b464fb519844feb4016ad26ff697591c336ef25ee7e2d`；16,986实际文件绑定 |
| 原 run_manifest | `1a251dc296017ec02137923b64d0ee42f37b3d6fa3c73ed640bb2d9f1780ac1c` |
| ranking seal | `858ec1db7a24fb7b2bb3ed9488e984fa51f9a571f4e89d04f2f6e04e308022c0` |
| 原 eval Gold | `25c0e5d1d493155f23fdee1ff1d6773e0ea74f7b013e5ad4a2805423f4fd9d70`；保管者内容访问，协调者仅不透明身份 |
| [实际支持映射](../../outputs/pearl-retrieval-eval200-20261003-01/support-map.json) | `dff24851e3aad793cdd18173e4979fe44bf92c9d16b698c5a73a78377d7f7937`；200实际完整裁决 |
| [唯一选择](../../outputs/pearl-retrieval-eval200-20261003-01/selected-review-manifest.json) | 每题单一最终文件、实际角色、完整原文SHA |
| [评分](../../outputs/pearl-retrieval-eval200-20261003-01/score-details.json)／[统计](../../outputs/pearl-retrieval-eval200-20261003-01/statistics.json) | 800单元、四层各50、全部K |
| [独立oracle](../../outputs/pearl-retrieval-eval200-20261003-01/independent-oracle.json) | 3,200前缀／48总体指标 |
| [模型输入与成本](../../outputs/pearl-retrieval-eval200-20261003-01/timing-and-inputs.json) | 600timed、60,000对、实际forward无截断 |

完整原始输出、源码快照和最终 completion／delivery manifest 位于[本次输出目录](../../outputs/pearl-retrieval-eval200-20261003-01/)；最终独立复核与保存证明位于[独立审计目录](../../outputs/pearl-retrieval-eval200-audit-20261003-01/)。原始 Gold／query／child／排名／逐题完整审查／共同 map／代码／release 的绑定由 custody 合并、保存后重开 verify 及最终独立交付核验共同验证。源代码快照按原仓库路径保存，实际模型／索引／source资产保持本地SHA绑定。

可复算命令（只读、不重跑模型，不覆盖输出）：

```powershell
Set-Location -LiteralPath 'E:\F_Workspace\F-Agent-Paper'
$env:PYTHONIOENCODING = 'utf-8'
.\.venv\Scripts\python experiments/pearl-retrieval-eval-entry-20261003/custody.py verify --directory outputs/pearl-retrieval-eval200-20261003-01 --gold outputs/pearl-retrieval-dev80-eval200-adobe106-20261003-01/pearl-retrieval-eval-200-adobe106-gold-20261003-r01.json --expected-count 200 --mapping outputs/pearl-retrieval-eval200-20261003-01/support-map.json
```

以上 custody 命令属于授权保管／验证角色，原 query-only 执行者不得运行。固定实际运行命令保留于预注册，已存在输出目录不能作为新运行输出；本次未重复阶段 A/B，也未因质量结果追加检索。
