# PEARL Retrieval：200 题固定评价预注册

*完整发布、固定评价与解释边界 · status: current · 2026-10-03*

本次独立评价使用原封存200题、四类各50，检索全集仍为106篇 Adobe-only 文献、6,433 child。出题来源与开发来源互斥，检索全集共同固定，因此不称未见文献泛化。开发和评价不合并 N=280。质量状态为 `agent_reviewed_preliminary`，`human_verified=false`。

## 固定方法与统计

| 内容 | 预设 |
| --- | --- |
| R1 | 正文 FTS5 BM25；已冻结 analyzer／fields／ordering |
| R2 | 归一化 float32 1024维精确点积；固定 BGE-M3 revision／所有实际模型 SHA |
| R3 | 等权 RRF k=60；两通道 D=100；同分 chunk_id 升序 |
| R4 | 固定 R3 Top-100 完整 child、本地 bge-reranker-v2-m3；不扩 parent、不截断、不调参 |
| 评价 | 仅首遍评分；K=1/5/10/20，主指标 CEGR@10；共同实际支持映射 |
| 比较 | R2−R1、R3−R2、R4−R3，exact McNemar＋三项 Holm |
| 区间 | 四层 paired bootstrap 10,000次，seed=20260929；Gold 来源连通分量敏感性另列 |
| 重复 | 5道开发 query-only 预热；固定随机顺序200题三遍；后两遍确定性与时延；600 timed queries 的分母仍为200意图 |

协议、指标和统计分别见[experiments](../../paper/pearl-framework/layer-1-retrieval/experiments.md)、[metrics](../../paper/pearl-framework/layer-1-retrieval/metrics.md)、[statistical methods](../../paper/pearl-framework/layer-1-retrieval/statistical-methods.md)。固定方法直接绑定[method-freeze](../pearl-dev-review-freeze-20261003/method-freeze.json)，开发 r02 Gold、revision、选择清单、映射、评分、delivery 及实现仅 byte hash 绑定。

## 正式运行命令

仓库根目录 PowerShell 执行，外部 pin 使用预先冻结的 `release-pin.json`；禁止在执行时从 release 重新计算可变 pin。该命令已由现有 runtime CLI 接口核验；真实检索只有 C 验收后由独立执行者运行。输出 `outputs/pearl-retrieval-eval200-20261003-01` 必须不存在。

```powershell
Set-Location -LiteralPath 'E:\F_Workspace\F-Agent-Paper'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONPATH = 'Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:HF_DATASETS_OFFLINE = '1'
$pin = (Get-Content -LiteralPath 'outputs/pearl-retrieval-eval200-release-20261003-03/release-pin.json' -Raw | ConvertFrom-Json).release_sha256
.\.venv\Scripts\python experiments/pearl-retrieval-eval-entry-20261003/runtime.py --contract outputs/pearl-retrieval-eval200-release-20261003-03/query-only/contract.json --release outputs/pearl-retrieval-eval200-release-20261003-03/release.json --release-sha256 $pin --output outputs/pearl-retrieval-eval200-20261003-01 --retries 0
```

完整 release 门禁结果保存在 `outputs/pearl-retrieval-eval200-release-20261003-03/gate-verification/release-gate.json`；它只执行核验，不初始化检索 backend、不运行真实 query、不做模型 forward。运行后保管者使用既有 custody 制作中性包，独立 child 评审者只获得中性包；唯一审查清单绑定逐题完整决定 SHA，不 glob 草稿。

## 解释与失败规则

替代完整组实际为0，原协议目标未达，不把额外 support bundle 说成替代完整组达标。保留 dev034 处理损失与分母、dev030 源内矛盾、pilot006 分母、dev079 建模子群和三处既有 R4 退步限制。以上是开发边界，不把旧开发标量当评估结果。

K≤20 四方法 union 必须全部审定；单 child、联合 child 路径只凭实际 child，不能从PDF补正文。21–100未审保持 unknown，不能由未找到支持推断不支持。合法空／短候选单独登记；失败／未运行不按质量0计。固定主比较不按结果改口径，若后续用于调参，后续分析改标探索性。

保存全量 RRF union、两通道候选、R3/R4正文与SHA、实际 forward token 输入、随机顺序、checkpoint、失败／重试和三遍审计。gross 同步推理／pipeline 是实际仪表时延；扣除输入核验及 forward hook CPU 成本的 method totals 是估计，分别报告。预热与 R4 实际对数另计，只有所有候选均100时600 timed query才有60,000 R4对。
