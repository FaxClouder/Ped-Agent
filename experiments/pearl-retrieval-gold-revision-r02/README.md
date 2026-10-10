# PEARL 开发 Gold r02 修订实验

*固定原排名的阶段 A 修订与共同重算 · status: current · agent_reviewed_preliminary · human_verified=false · 2026-10-03*

> 2026-10-07：`gold-r02.json` 与 `gold-diff.json` 已复制到规范位置 `memPed/knowledge/gold/pearl-adobe106/retrieval/dev80/r02/`（登记号 `qs-dev80-r02`，现行开发版本），SHA-256 不变；下文命令中的 `outputs/` 路径是冻结出处。

阶段 A 已完成：012、050、080 的五项表述修订；080 增加数值验证 atom a3，r2 要求 a2＋a3；三题独立实际 child 盲审；80 题四方法 K=1/5/10/20 统一重算及独立 oracle 验证。完整结果见 [开发 Gold r02 修订分析](development-gold-r02-analysis-2026-10-03.md)。

CEGR@10 为 R1 **47/80**、R2 **49/80**、R3 **51/80**、R4 **58/80**。原 r01 为 47/48/51/58。只有 dev012 的 R1/R2/R4 出现标量变化；R1/R4 的 @1 完成下降，R2 的 @10 完成增加。三项预设 Holm p 均 >0.05，来源分量差区间均跨零。200 题仍封存，完整评估发布尚未冻结。

## 冻结与身份

原 query、原 8 题、77 个未修订完整对象、106 篇来源、6,433 child、索引、方法配置和首遍排名不变。保留 [r01 实验](../pearl-retrieval-dev80-20261003/README.md)和[方法冻结](../pearl-dev-review-freeze-20261003/method-freeze.json)，原 run/preflight 的 Gold SHA 未改。

新产物在 [独立 r02 输出目录](../../outputs/pearl-retrieval-dev80-gold-r02-20261003-01/)，分析在其 `analysis-r02-01/`。原输出没有覆盖。两个语义子 Agent 均为 `fork_turns=none`、继承配置无模型覆盖；只读取中性实际 child 包。PDF 原文核对与支持决定分别保存。

| 文件 | 职责 |
| --- | --- |
| [prepare_revision.py](prepare_revision.py) | 核对提案 old_value、来源身份和原文；一次性创建新 Gold、精确 diff、中性包及原文页面核对资产；目标已存在即拒绝 |
| [finalize_inputs.py](finalize_inputs.py) | 显式选择 80 个最终文件并绑定全文／packet SHA；080 选择修复序列化后的 r02 文件，初稿保留 |
| [revision.py](revision.py) | 显式修订 loader、共同评分、配对统计、逐题差异、失败诊断及独立保存输出验证 |
| [test_revision.py](test_revision.py) | 21 个合成拒绝／固定参考测试；不读取封存评估内容 |
| [document_delivery.py](document_delivery.py) | 从完成的原始 JSON 生成报告并核对 r01、77 题全文评分和既有损失 |

Loader 消费 `base_directory`、`base_gold_path`、`revised_gold_path`、`selected_review_manifest` 和 `revision_manifest`。原加载器仍先验证原 Gold/run/preflight；独立修订 manifest 绑定原排名、共同映射、新 Gold、差异及选择清单。只允许三题的七个修订字段路径，保留既有 atom/source 身份，080 强制新 a3 与 `r2=[[a2,a3]]`。77 题继承原已选审查全文 SHA；K≤20 有未决则拒绝。

## 实际命令

在仓库根目录，以现有绑定输入只读核验已交付结果：

```powershell
$env:PYTHONIOENCODING = 'utf-8'
.\.venv\Scripts\python experiments/pearl-retrieval-gold-revision-r02/revision.py --base-directory outputs/pearl-retrieval-dev80-20261003-01 --base-gold outputs/pearl-retrieval-dev80-eval200-adobe106-20261003-01/pearl-retrieval-dev-80-adobe106-gold-20261003-r01.json --revised-gold outputs/pearl-retrieval-dev80-gold-r02-20261003-01/gold-r02.json --selected-review-manifest outputs/pearl-retrieval-dev80-gold-r02-20261003-01/selected-review-manifest.json --revision-manifest outputs/pearl-retrieval-dev80-gold-r02-20261003-01/revision-manifest.json --output-directory outputs/pearl-retrieval-dev80-gold-r02-20261003-01/analysis-r02-01 --verify-only
```

另存共同重算：移除 `--verify-only`，并将 `--output-directory` 改为尚不存在的独立目录，例如 `analysis-r02-02`。已有目录会拒绝，不重跑检索。复核全文与冻结资产必须可用；修改评分代码会使旧结果的代码绑定核验拒绝，应另行版本化分析。

```powershell
.\.venv\Scripts\python -m pytest experiments/pearl-retrieval-gold-revision-r02 experiments/pearl-retrieval-dev80-20261003/test_protocol.py experiments/pearl-retrieval-dev80-20261003/test_score_analysis.py experiments/pearl-retrieval-dev80-20261003/test_verify.py -q
```

本次最终 54 项通过（新 21＋原针对性 33）；原开发全部专项另有 47 项通过。没有跨稳定契约，未宣称全仓 suite。独立 oracle 核对 1,280 前缀、48 总体指标及 80 所选审查全文绑定一致。

## 后续检查点

本目录交付阶段 A。阶段 B 使用合成 80/200 输入适配入口并继续封存正式内容；阶段 C 完整发布和阶段 D 正式评估尚未执行。21–100 未审关系保持未知；来源／页命中不代替实际支持；dev034 处理缺失和三道既有 R4 退步保留。当前结果为 Agent 复核开发分析，非人工 Gold 或正式 200 题评价。
