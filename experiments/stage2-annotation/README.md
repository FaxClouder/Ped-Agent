# Stage 2 开发集答案与证据复核

*20 个 Gold v5 候选开发意图的当前研究流程 · status: current*

`build_dev_scope.py` 物化 20 个可回答 intent、40 条中英查询，不包含 100 个 sealed test intent 或 20 个拒答 intent。原始 `memPed/knowledge/gold/2026-09-23-rebuild/answer_annotations_dev_v1.jsonl` 保持不变，其中参考答案为空、`human_verified=false`。已有 AI 草稿在 `outputs/stage2-answer-drafts-20260926-01/`；草稿不是独立复核结果。

## 当前使用口径

2026-09-27，用户批准由独立子 agent 执行开发集的来源、证据和双语答案复核，并明确**人工 Gold 审查不是本研究当前实验的前置门槛**。子 agent 查阅了 12 篇原始 PDF，覆盖 20/20 intent；逐题结论在 `outputs/stage2-agent-review-20260927-02/reviews.jsonl`。研究可使用这 20 题做探索性检索评测、失败分析和配置对照，但必须注明标签来源为 agent review，不写成 `human_verified=true` 或人工 Gold。

[`agent_review.py`](agent_review.py) 校验开发集与复核文件哈希、证据组及来源 PDF 哈希，在独立输出目录生成版本化答案包。当前最终产物是 `outputs/stage2-agent-adjudicated-20260927-03/`，其中 20/20 标为 `development_usable=true`：18 题有 `agent_reviewed_candidate` 双语候选答案及 36 条事实-证据组映射，可用于**探索性**答案分析；2 题保留 `agent_disputed`，仍可用于资源级检索及失败分析，但不作为无争议的答案正确性标签。`rgq-015` 的公式应定位至 PDF 第 4–6 页，旧页 1 标注不足以支持公式；`rgq-122` 的原文同时出现 58% 与 59%，不得强行选择单值。`rgq-048` 的约数 0.6 m 没有来源支持的绝对容差，不进行自动数值正确性判定。18 题的定位仍是页级，不称为元素级精确引用。

独立复核包同时记录必要原子事实、事实-证据组映射、数值单位与容差说明、允许的等价说法、禁止推断、争议和来源页。证据组间为 AND，组内替代来源为 OR。中英问法按一个 intent 统计，不把 40 条问法当作独立样本。后续若修订两个争议题，应新建来源和复核版本、保留旧结果、重算受影响的开发集指标；不覆盖现有研究输出，也不使用 sealed test 调参。

从仓库根目录复现（目标目录必须不存在）：

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
.\.venv\Scripts\python experiments/stage2-annotation/agent_review.py --reviews outputs/stage2-agent-review-20260927-02/reviews.jsonl --output-dir outputs/stage2-agent-adjudicated-新编号
.\.venv\Scripts\python -m pytest experiments/stage2-annotation -q
```

本流程不引入复杂人工审查门禁。将来如需发表一个明确声明“人工核验”的 Gold 版本，另按[可选人工 Gold 审查计划](../../docs/superpowers/plans/2026-09-27-optional-human-gold-review.md)执行；该计划不影响当前开发集结果的可用性。
