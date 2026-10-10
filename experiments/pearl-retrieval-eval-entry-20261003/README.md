# PEARL Retrieval：独立评估入口的合成验证

*Stage B 运行与保管边界、动态评分和启动门禁 · status: current · 2026-10-03*

本目录适配固定 80/200 输入，复用 [原开发入口](../pearl-retrieval-dev80-20261003/README.md)的检索、正文验证、布尔评分、配对统计及独立 oracle。原入口及 [r02 修订入口](../pearl-retrieval-gold-revision-r02/README.md)保留。这里的 80/200 均为独立编写的合成题，真实 200 题内容未用于开发、模型推理或语义复核；Stage C 的完整真实 release 尚未登记。

## 访问角色和身份

| 文件／角色 | 允许输入 | 输出及约束 |
| --- | --- | --- |
| `runtime.py` 检索执行者 | 显式 raw-run contract、query-only、5 道独立开发预热 query、选定 release 与外部 SHA pin、索引和模型资产 | 三遍排名／union／query vector／forward 输入／时延／重试；仅首遍评分；不导入 Gold 保管模块 |
| `stub_backend.py` 合成模型 | query 与独立合成索引 | 真实 FTS5、float32 精确点积、RRF；模型 token／rerank 是明确 stub，无真实模型推理 |
| `custody.py` 保管与计分 | 显式 Gold、原始运行、逐题中性包、唯一选定审查清单 | query 导出、共同 mapping、全部 K 评分、分层、配对统计、来源敏感性及保存后独立复算 |
| `synthetic.py` 合成验证驱动 | 固定数量和新目录 | 从零编写题、Gold、child、来源、索引及 synthetic release；CLI 将检索放到独立 subprocess |

query-only 每行只含 `intent_id` 和 `query`。contract 明确 `split`、`expected_count`、四类配额、同 split 的完整 intent 清单、查询及预热 SHA、固定 policy、backend、模型 revision、实际索引／配置路径与 runtime 文件集合。四类为 `single_source`、`numeric_table`、`within_paper_multi`、`cross_paper`，开发各20、评估各50。`custody_binding` 只含 Gold／child 的不透明 SHA，不含 Gold 路径或内容。Gold 的正文、条件或 requirement 改动必须使用另存的 revision-analysis 身份；本 raw-run loader 不接受它。没有将 r02 loader 放宽为200题。

Gold 原生 schema 的 `development` 和 `sealed_independent_evaluation` 显式映射到 runtime 的 `development_80`／`evaluation_200`；可选的逐题 split 须一致。child 路径由实际 runtime index 推导，原生 Gold 无需额外 `child_path`。合成 Gold 使用同样的原生 split／无路径结构。该 schema 来自公开的冻结脚本，不来自封存评估内容。

release 必须带全部类别：protocol、statistics、code、method、model、index、child、source、view、dependencies。启动前先校验由调用者另行提供的 manifest SHA，再逐项读取实际所选文件，独立推导实际消费的代码、索引、模型、来源与输入视图，校验依赖版本和安装 metadata／入口字节。模型初始化发生在门禁通过后。仅 manifest 自比、遗漏评分代码或实际 index／model 文件均不能通过。真实 backend 复用原 `Models` 与 `retrieve`，包含 forward hook、无截断和 R3/R4 全正文身份核验；本次没有执行真实 GPU backend。

角色分离采用模块和 subprocess 的访问契约。正式 release 的操作系统权限／独立保管流程仍属于 Stage C；合成验证不声称拥有操作系统级隔离或真正独立语义评审。

## 可运行命令

在仓库根目录执行。所有新输出必须不存在；已有输出不得覆盖。完整合成 CLI 同时保存80/200及固定失败／成功重试参考，检索 subprocess 不获得 Gold 路径。

```powershell
$env:PYTHONPATH = 'Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src'
.\.venv\Scripts\python -m pytest experiments/pearl-retrieval-eval-entry-20261003 -q
.\.venv\Scripts\python experiments/pearl-retrieval-eval-entry-20261003/synthetic.py --output outputs/<new-synthetic-run>
```

单独准备合成200并运行 query-only CLI（外部 pin 从冻结的 pin 收据取值；实际文件门禁仍在启动前执行）：

```powershell
.\.venv\Scripts\python experiments/pearl-retrieval-eval-entry-20261003/synthetic.py --prepare-only --count 200 --output outputs/<new-synthetic-inputs>
$pin = (Get-Content outputs/<new-synthetic-inputs>/release-pin.json -Raw | ConvertFrom-Json).release_sha256
.\.venv\Scripts\python experiments/pearl-retrieval-eval-entry-20261003/runtime.py --contract outputs/<new-synthetic-inputs>/contract.json --release outputs/<new-synthetic-inputs>/release.json --release-sha256 $pin --output outputs/<new-query-only-run>
```

只执行门禁可添加 `--verify-release-only`，仍须使用另一个新输出目录。失败／未运行不转成质量0；合法空／短候选独立保存完成原因，R4 对数累加实际候选。恢复成功的重试保留 attempt 记录；最终失败阻止计分。600 timed queries 是200题三遍，同一题重复不增加统计分母，5次预热与对数另计。

每道已完成 query 的完整结果追加到 `completed-query-journal.jsonl` 并 flush／fsync，`checkpoint.json` 原子更新 pending／完成计数；该 live checkpoint 属于当前新目录，不改已冻结的最终 manifest。中断保留先前完成记录和当前 pending 身份，不自动续写或覆盖旧运行。terminal failure 的 CLI 退出码非0。

实际独立 child 判断只能由内容评审者在中性包上完成。合成驱动保存的决定是固定 fixture oracle，不是实际语义审查。唯一选择清单逐题绑定完整审查文件 SHA；暂稿不能 glob 合并。Top20 四方法 union 必审，正文池另含相同 Gold 来源的 child，深层未审保持 unknown。

```powershell
.\.venv\Scripts\python experiments/pearl-retrieval-eval-entry-20261003/custody.py packets --directory outputs/<raw-run> --gold outputs/<explicit-gold.json> --expected-count 200
.\.venv\Scripts\python experiments/pearl-retrieval-eval-entry-20261003/custody.py combine --directory outputs/<raw-run> --gold outputs/<explicit-gold.json> --expected-count 200 --selection outputs/<explicit-selection.json> --output outputs/<raw-run>/support-map.json
.\.venv\Scripts\python experiments/pearl-retrieval-eval-entry-20261003/custody.py score --directory outputs/<raw-run> --gold outputs/<explicit-gold.json> --expected-count 200 --mapping outputs/<raw-run>/support-map.json
.\.venv\Scripts\python experiments/pearl-retrieval-eval-entry-20261003/custody.py verify --directory outputs/<raw-run> --gold outputs/<explicit-gold.json> --expected-count 200 --mapping outputs/<raw-run>/support-map.json
```

`custody.py export` 提供独立保管端的 query-only 投影：额外指定 `--runtime-config` 与新 `--output`。它只生成输入 contract／query 及保管收据；实际完整 release 必须随后单独登记、外部 pin 固定并核验。这些是可用接口说明，不授权在 Stage B 导出真实评估内容。

## 验证与限制

合成80/200验证320/800首遍单元、240/600 timed queries、1,280/3,200个前缀、48总体指标、三项预设 exact McNemar＋Holm、10,000次固定 seed 的分层 paired bootstrap 和来源连通分量敏感性。保存后 `verify` 重新读入并独立计算原始排名和完整选择决定，拒绝评分标量、分母、审查全文、map 或 seal 漂移。固定参考涵盖空候选、短候选与100候选，以及条件、联合 child、AND／OR、跨来源路径。

合成模型时长不代表 BGE-M3 或 reranker 性能，stub 的 forward 记录不代表真实 GPU token hook 验证。正式运行仅复用已验证算法，真实 backend 本次为代码适配与审查，没有真实推理验收。依赖身份覆盖版本、安装 metadata 和入口文件，完整部署环境与硬件冻结属于 Stage C。合成审查结果不属于 Agent-reviewed Gold、不成为 PEARL 基线／分母或研究结论。

完整阶段范围见 [适配分析](adaptation-analysis-2026-10-03.md)与 [B–D 交接计划](../../docs/superpowers/plans/2026-10-03-pearl-retrieval-post-r02-next-session.md)。
