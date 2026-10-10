# PEARL Layer 1：80 题开发四方法对照

*冻结 Adobe-only child 上的检索、独立盲审与统一评分 · status: current · 2026-10-03*

本实验执行 [Retrieval-v0.2](../../paper/pearl-framework/layer-1-retrieval/experiments.md)。共同输入为已冻结的 106 篇 Adobe-only 英文来源、6,433 个 child，以及 [80 题开发 Gold](../pearl-dataset-80-200-20261003/README.md)。四个主层各 20 题；原 8 道试标题未变。200 题独立评估及其质控材料继续封存，仅核验文件哈希和只读属性。

## 执行与边界

| 环节 | 当前已核验内容 |
| --- | --- |
| 冻结输入 | PDF、Adobe canonical、child 正文、FTS 正文及成员、dense IDs／向量、两套模型实际资产哈希通过；200 个封存文件仅作哈希及属性检查 |
| 方法 | R1 英文正文 SQLite FTS5 BM25；R2 BGE-M3 精确余弦；R3 等权 RRF k=60；R4 固定 R3 Top-100 的 bge-reranker-v2-m3 重排 |
| 实际运行 | RTX 3080 CUDA/FP16；固定 seed=20260929；5 次完整预热、3 遍相同固定随机顺序；每遍 80 题，首遍 320 个计分单元 |
| 重复性 | 三遍所有候选顺序、分数和 query 向量字节完全一致；最大分数差 0 |
| 实际输入 | 首遍 R4 8,000 对，最长 628 tokens；dense query 最长 64 tokens；三遍全部实际 forward 输入核对通过，零截断 |
| 候选身份 | 每题 R3／R4 的 ID、完整正文与正文哈希完全一致 |
| 内容复核 | 80 题最终决定全部审定；3,116 条必审关系无未决；另审定 441 条补充关系，12,397 条补充关系明确保持未知；三题采用独立复裁 |
| 统一评分 | 首遍 320 单元、K=1／5／10／20；独立布尔公式复算 1,280 个前缀与 48 个总体指标一致；选定原审查文件全文绑定 80/80 |

完整结果见 [80 题开发分析报告](development-analysis-2026-10-03.md)。CEGR@10：R1 47/80（58.75%）、R2 48/80（60.00%）、R3 51/80（63.75%）、R4 58/80（72.50%）。三个预设比较的 Holm p 均大于 0.05，Gold 来源分量敏感性差区间均跨零；仍为 Agent 复核的开发初步结果。200 题未运行。

实际专项测试 [60 项通过](../../outputs/pearl-retrieval-dev80-20261003-01/test-verification.json)；运行后 [244 项冻结输入哈希](../../outputs/pearl-retrieval-dev80-20261003-01/frozen-input-post-run-verification.json)、[269 项 runtime 哈希及 200 个封存文件哈希／只读属性](../../outputs/pearl-retrieval-dev80-20261003-01/verification.json)通过。原运行 checkpoint 保留不变，全链完成记录另见 [delivery-manifest.json](../../outputs/pearl-retrieval-dev80-20261003-01/delivery-manifest.json)。

仅读取 query 的检索入口见 [run.py](run.py)；答案、requirements 和支持标签只用于运行之外的 [prepare.py](prepare.py)、[blind.py](blind.py) 与 [score.py](score.py)。实际 child 复核接口见 [review-spec.md](review-spec.md)。来源或同页命中不替代内容支持，parent 不参与 Layer 1。21–100 的未决支持保持未知，不据此断言全库不存在证据或比较 R3／R4 @100 覆盖不变性。

沿用原方法配置，没有参数搜索、模型替换、解析／切块扩展或 Agentic 实验。原试标脚本与输出保持不变。新实验源码在本目录，本地输出在 [outputs/pearl-retrieval-dev80-20261003-01](../../outputs/pearl-retrieval-dev80-20261003-01/)。首遍排名和 runtime manifest 已冻结；后续评分和交付记录分别保存，不修改原始运行记录。

## 复现入口

所有命令在仓库根目录运行。已有输出必须保留；完整重跑使用新的目录名。`prepare.py` 拒绝已存在目录；runner 仅接受同一次准备写入的 query-only 输入与 preflight。评分及修订另存新文件。

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python -m pytest experiments/pearl-retrieval-dev80-20261003 -q
.\.venv\Scripts\python experiments/pearl-retrieval-dev80-20261003/prepare.py --output-dir outputs/<new-run-id>
.\.venv\Scripts\python experiments/pearl-retrieval-dev80-20261003/run.py --output-dir outputs/<new-run-id> --preflight outputs/<new-run-id>/preflight.json --queries outputs/<new-run-id>/queries.jsonl
.\.venv\Scripts\python experiments/pearl-retrieval-dev80-20261003/blind.py --directory outputs/<new-run-id>
```

独立语义复核完成后，用明确选定的最终审查版本生成统一 mapping，再由冻结排名计算 K=1／5／10／20。临时原稿和修订稿都保留，不能同时作为同一 intent 的最终决定输入。选定清单见 [selected-review-files.json](../../outputs/pearl-retrieval-dev80-20261003-01/review/selected-review-files.json)。评分和分析入口见 [score.py](score.py)、[analyze.py](analyze.py)，固定算例见 [test_protocol.py](test_protocol.py)。

在本次冻结排名与原 mapping 上独立重算（以下新文件名若已存在，先另选名字）：

```powershell
$run = "outputs/pearl-retrieval-dev80-20261003-01"
$map = "$run/pearl-retrieval-dev-80-adobe106-support-map-pearl-retrieval-dev80-20261003-01.json"
.\.venv\Scripts\python experiments/pearl-retrieval-dev80-20261003/score.py recompute --directory $run --mapping $map --reference "$run/score-details.json" --output outputs/pearl-dev80-scores-recomputed-r01.json
.\.venv\Scripts\python experiments/pearl-retrieval-dev80-20261003/analyze.py --directory $run --mapping $map --scores "$run/score-details.json" --output outputs/pearl-dev80-analysis-recomputed-r01.json --failures-output outputs/pearl-dev80-failures-recomputed-r01.json
.\.venv\Scripts\python experiments/pearl-retrieval-dev80-20261003/verify.py --directory $run --mapping $map --scores "$run/score-details.json" --output outputs/pearl-dev80-verification-recomputed-r01.json
```

若要重新合并同一批审查，使用明确清单另存 map；其创建时间和哈希会改变，应由它生成新评分，不能假称原 map 字节未变：

```powershell
$decisionPaths = (Get-Content "$run/review/selected-review-files.json" -Raw | ConvertFrom-Json).files.path
.\.venv\Scripts\python experiments/pearl-retrieval-dev80-20261003/score.py combine --directory $run --decisions $decisionPaths --output outputs/pearl-dev80-map-recombined-r01.json
.\.venv\Scripts\python experiments/pearl-retrieval-dev80-20261003/score.py score --directory $run --mapping outputs/pearl-dev80-map-recombined-r01.json --output outputs/pearl-dev80-scores-recombined-r01.json --csv-output outputs/pearl-dev80-scores-recombined-r01.csv
```

## 当前限制

题集和支持复核均为 `agent_reviewed_preliminary`，不是人工 Gold。替代完整 evidence_group 为 0，既定期望目标未达；替代 bundle 不能充当替代完整组。开发出题来源 32 篇、评估出题来源 74 篇互斥，全部 106 篇仍是共同检索语料，所以这不是未见文献测试。来源重用及跨篇连接须随开发结果分析，不把 80 行等同于 80 个完全独立研究证据。原文可回答但 Adobe 内容损坏的题保留原条件与共同分母。

来源图有 12 个连通分量，最大 33 题。D100 的正向充分路径可证明存在；未充分审阅的深层支持不作负例，全部 80 题尚不满足 R3／R4 全深度覆盖不变性核验条件。真实延迟同时保留带核验开销的 gross 与审计扣除估计，后者不是无 instrumentation 的干净时延。后续先复核开发难例和配置，版本变动后所有方法一致另存重算；正式配置冻结与 200 题独立评估另行登记，不自动进入。
