# PEARL Adobe 106：R4 八题开发补跑分析

*冻结 R3 Top-100 的本地重排、盲化支持核验与四方法统一重算 · status: current · 2026-09-29 · 仅开发初步结果*

本记录接续 [R1–R3 原始运行](../../outputs/pearl-retrieval-dev-pilot-8-adobe106-20260929-01/run_manifest.json)和[原分析](r1-r3-pilot-analysis-2026-09-29.md)。R4 使用相同的 106 篇 Adobe 文献、6,433 个 child、8 道英文开发题和[新 Gold](../../paper/pearl-framework/datasets/retrieval-pilot/pearl-retrieval-dev-pilot-8-adobe106-gold.json)；旧 PyMuPDF 资产与旧知识库 Gold v5 不参与。原 R1–R3 排名、Gold 和旧评分文件均未覆盖。

## 运行与核验

本地 `BAAI/bge-reranker-v2-m3` revision `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e` 经 Hugging Face 本地目录核验。权重 `model.safetensors` SHA-256 为 `d9e3e081faff1eefb84019509b2f5558fd74c1a05a2c7db22f74174fcedb5286`。固定 CUDA/FP16、batch=4、query_max_length=768、pair max_length=1024、原始 logit 不归一化、并列按 chunk ID 升序；完整配置见[配置文件](reranker-config.json)。实测 RTX 3080 上完成 8×100 个 query-child pair；800 个实际输入均未截断，实际 token IDs 和原始文本存于[模型输入审计](../../outputs/pearl-retrieval-dev-pilot-8-adobe106-r4-20260929-01/model-inputs-r4.jsonl)。

R4 的每题 Top-100 与 R3 的 child ID、原文及文本 SHA-256 逐条集合一致；只改变顺序。[R4 排名](../../outputs/pearl-retrieval-dev-pilot-8-adobe106-r4-20260929-01/rankings-r4.jsonl)、[运行清单](../../outputs/pearl-retrieval-dev-pilot-8-adobe106-r4-20260929-01/run_manifest.json)、[逐题耗时](../../outputs/pearl-retrieval-dev-pilot-8-adobe106-r4-20260929-01/query-timings-r4.jsonl)和[独立核验记录](../../outputs/pearl-retrieval-dev-pilot-8-adobe106-r4-20260929-01/verification-r4.json)位于独立输出目录。模型载入约 1.45 秒；首次重排约 2.70 秒，其余七题各 100 候选的重排中位数约 0.90 秒，另有每题约 0.12–0.17 秒的输入审计。这是单次开发运行，不是协议要求的多轮预热延迟测量。

R4 前 20 引入 36 条此前未审的题目与 child 关系。两组子 Agent 从[去方法、排名和分数的审查池](../../outputs/pearl-retrieval-dev-pilot-8-adobe106-r4-20260929-01/review_new_top20_blind.jsonl)逐条核验，并保存 [001–004](../../outputs/pearl-retrieval-dev-pilot-8-adobe106-r4-20260929-01/review-r4-001-004.json) 和 [005–008](../../outputs/pearl-retrieval-dev-pilot-8-adobe106-r4-20260929-01/review-r4-005-008.json) 的判定；36/36 已决，无 Gold 修订。新[统一支持映射](../../outputs/pearl-retrieval-dev-pilot-8-adobe106-r4-20260929-01/pearl-retrieval-dev-pilot-8-adobe106-support-map-pearl-retrieval-dev-pilot-8-adobe106-r4-20260929-01.json)吸收等价支持路径后，同一映射对 R1–R4 全部重算。R1–R3 在 K=1/5/10/20 的汇总值与原评分逐项相同；新[评分明细](../../outputs/pearl-retrieval-dev-pilot-8-adobe106-r4-20260929-01/preliminary-scores-r1-r4.json)保留各题的首次完整位置和组内覆盖。

## 八题开发初步对照

每格依次为 **CEGR / BestGroupCov / CompleteMRR**；一个题目的 CEGR 变动即 12.5 个百分点。主截断为 K=10，其他 K 用于诊断。

| K | R1 BM25 | R2 BGE-M3 dense | R3 RRF | R4 R3＋reranker |
| ---: | --- | --- | --- | --- |
| 1 | 0.125 / 0.1875 / 0.125 | 0.125 / 0.1875 / 0.125 | 0.250 / 0.3125 / 0.250 | 0.250 / 0.3125 / 0.250 |
| 5 | 0.375 / 0.500 / 0.250 | 0.375 / 0.500 / 0.1979 | 0.375 / 0.500 / 0.2917 | 0.375 / 0.500 / 0.2813 |
| 10 | 0.500 / 0.625 / 0.2625 | 0.375 / 0.500 / 0.1979 | 0.375 / 0.5625 / 0.2917 | **0.500 / 0.625 / 0.2938** |
| 20 | 0.625 / 0.6875 / 0.2699 | 0.500 / 0.625 / 0.2042 | 0.625 / 0.750 / 0.3066 | **0.750 / 0.8125 / 0.3121** |

R4 相对 R3：CEGR@10 从 3/8 到 4/8，@20 从 5/8 到 6/8。这是该八题样本的观察值，不能推断总体优劣或显著性。

| 题号 | R3 首次完整 | R4 首次完整 | 排序变化与必要证据 |
| --- | ---: | ---: | --- |
| 001 | 1 | 11 | 社会力定义的完整路径后移，R4 在 @10 失去此题 |
| 002 | 1 | 1 | 不稳定流、倒退及重叠条件保持首位完整 |
| 003 | 15 | 4 | 老年组均龄数值与表头两个 child 共同进入前 4；R4 在 @10 新完成 |
| 004 | 3 | 1 | 四个宽度及米单位、单双向实验条件更早齐备；新增审定 child 仅补部分 atom |
| 005 | — | — | running 条件仍未在前 20 与速度比较共同满足 |
| 006 | — | 18 | 平台速度与 `f1(N)` 比值趋势、无重叠基准定义在前 18 齐备 |
| 007 | 19 | 10 | Geoerg 与 Shi 两方及 Shi 年龄混合条件提前构成完整组 |
| 008 | — | — | 前 20 仍无 Pouw 年度 Eindhoven 追踪与 Shi 受控楼梯实验的完整跨论文组 |

第 008 题的一条已核验 Pouw 路径在 R3 完整 union 中排第 123，未进入 R3 Top-100，因此 R4 不可能恢复这条路径。对 21–100 的其他潜在等价支持尚未逐条审定，不能据此断言 R4 在 @100 完全失败。R3 与 R4 的 Top-100 候选集合一致，但本报告正式内容评分仅到 K=20。

## 复现与边界

从仓库根目录运行；补跑必须使用不存在的新目录，不能覆盖上述记录：

```powershell
$env:TRANSFORMERS_OFFLINE = "1"
$env:HF_HUB_OFFLINE = "1"
.\.venv\Scripts\python experiments/pearl-index-106-adobe-20260929/rerank_pilot.py --output-dir outputs/<new-unique-name>
```

生成新的盲池并完成内容审查后，才可用[统一评分脚本](score_r4_pilot.py)重算。它绑定当前指定的 R4 补跑目录和审查文件，不可直接用于新的目录；新运行应先更新该脚本的输入路径并重新生成独立支持映射。评分不是人工 Gold。80 道完整开发题与 200 道封存题尚未构建；流程确认后才扩展题集，封存题不参与调参。

本次 R4 清单、统一支持映射和评分文件 SHA-256 分别为 `762b3713bbb10c5d3126fc21fdf4fb07c725c11b1549d79e376e41fd4a3ef672`、`e5386ccd4306212fe4bbe7070e7777ccbb0e0ef573e4401a2f5531178168ec57`、`8b4e29ab5618aac881abb9765779234b217f4f4927ad6682e530758b907bc52d`。
