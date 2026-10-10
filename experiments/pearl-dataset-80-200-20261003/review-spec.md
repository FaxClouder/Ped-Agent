# PEARL 全量题集独立复核接口

*来源事实、充分证据路径、题型与家族审查 · status: plan · 2026-10-03*

复核者与作者必须是不同子 Agent。读取候选文件、分配来源原文及原文页，逐题核验，不参考检索排名和成绩。所有 atom 都要独立核对 source/page/anchor 与事实解释；table_cell 要视觉核对表号、行列、数值和单位。判断每个 requirement 必要、每个 bundle 充分、每个 evidence_group 可独立支持整个 query 的完整答案。单篇多证据判断是否真的需要互补不同位置，跨论文判断至少两方是否不可缺，确认数字仅身份/背景时不误分数值层。

输出独立 JSON 审查文件：

```json
{
  "review_type": "independent_subagent_source_semantics",
  "reviewer_id": "/root/reviewer-name",
  "model_id": "actual model when known",
  "candidate_sha256": "SHA-256 of exact candidate JSONL reviewed",
  "intents": [
    {"intent_id": "pearl-dev-009", "decision": "accept", "checked_atom_ids": ["a1"], "stratum_confirmed": true, "all_complete_paths_sufficient": true, "family_distinct_within_batch": true, "findings": [], "reason": "What the original text establishes, and why the answer and conditions are supported."}
  ],
  "unresolved": []
}
```

发现错误用 `revise`，指出具体原文、字段和修正依据。不要自动降低必要条件。作者另存修订文件；复核者对最终修订的候选 SHA 再输出完整覆盖的接受记录，保留初审。若作者原子从正文获取、机器 PDF 正规化定位通过，无须渲染全部页；表格/图/歧义关系需要看 PDF 页图。不能用“锚点有相同词”代替事实和条件审查。

完成三批审查后，另一 Agent 汇总检查跨集及集内题族、近重复、仅换数字/来源的模板，以及看似数值实为机制等分层问题。对机器标记的所有 pair 分别记录 `distinct` 或 `revise` 和具体理由；对未标记问题仍做全体 query/answer/family 的语义扫描。封存前所有修订必须再次核验。

全局记录包含 `reviewer_id`、`model_id`、三个候选的 `candidate_sha256`、`pilot_gold_sha256`、`all_intents_semantically_scanned: true`、覆盖全部 280 题且无重复的 `reviewed_intent_ids`、`adjudications` 与 `unresolved`。全局复核者与三位作者、三位批次复核者都不同；机器无 pair 标记时仍须覆盖所有题目，并具体解释容易混淆的题族及修订事实的最终核验。
