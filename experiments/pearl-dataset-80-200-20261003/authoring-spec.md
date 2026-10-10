# PEARL 80／200 初标与复核约定

*独立 Agent 工作包接口与来源支持要求 · status: plan · 2026-10-03*

## 必须执行

只使用分配工作包中的来源，从 Adobe canonical 全文和原始 PDF 获取证据。不要读取任何检索排名、评分、旧 Gold、旧题集或其他批次题目。查询和答案使用英文，题目明确研究、对象、场景和必要条件。每题有不同研究事实／机制／对比角度；同一答案换问法、同一实验只换数字或只换来源名不计为不同题族。

四层互斥，按以下顺序分类：`cross_paper`（完整答案必须至少两篇）→`numeric_table`（必要答案含数值或表格单元）→`within_paper_multi`（同一论文至少两个互补必要事实，证据来自不同位置／章节）→`single_source`（一个事实或机制）。单来源事实不得为了满足多证据配额拆成两个同义 requirement。

数值可以来自正文；如使用表格，记录原文表号、行、列、原值并渲染对应 PDF 页视觉核验。图形估计读数不用于凑数。正文数值保留单位、对象与条件；± 不自行解释成标准差等。不能把不同实验条件拼成一项答案。跨论文题应比较共同研究角度，至少两方各有必要 requirement，避免无关联论文的并列摘要。

替代支持只记录确实等价的来源路径。同一 requirement 的不同充分证据放在不同 support bundle；不复制 requirement 或制造逻辑重复 group 来凑替代组配额。真实等价证据不足时报告实际数量及原因。源原子不绑定 child ID，正文锚点须能在指定 PDF 页找到。原文存在而 Adobe 遗失的证据仍保留，并记录解析缺失。

## 输出格式

工作包输出为 JSONL，每行完整一题，采用已有试标相同结构：

```json
{
  "intent_id": "pearl-dev-009",
  "family_id": "study-id-specific-concept",
  "split": "dev_candidate",
  "main_stratum": "single_source",
  "query": "English question naming the study and necessary scope?",
  "reference_answer": "Complete bounded English answer.",
  "tags": ["mechanism"],
  "atoms": [{"atom_id": "a1", "source_id": "pearl-src-...", "page": 2, "locator_type": "text_anchor", "anchor_text": "Exact short text on the indicated PDF page", "supports": "Bounded fact supported by this anchor."}],
  "requirements": [{"requirement_id": "r1", "claim": "Necessary answer fact.", "scope": "Study, participants, scenario, condition and unit when needed.", "support_bundles": [["a1"]]}],
  "evidence_groups": [{"group_id": "g1", "requirements": ["r1"]}],
  "authoring_note": "Evidence pages/sections, why this is this stratum, and any visual check performed."
}
```

评估题用 `pearl-eval-001` 起的编号、`eval_candidate`；不同工作包按指定编号区间输出。table_cell 原子除上述字段外有 `table`, `row`, `column`, `value`；锚点可以分开记录数值与条件以形成联合 bundle。所有引用 ID 在该题内定义，无未使用 atom／requirement，无空 bundle／group，无冗余严格超集 group。

为节省手写字段可以用本地脚本生成结构，但每个 query、答案、claim、scope 与证据必须由阅读原文后逐题编写；不使用关键词或正则抽取批量伪造事实。写入 JSONL 之前先核对 PDF 页序（1 起）。作者完成时报告题型数量、使用来源、缺口／争议、替代 bundle 和替代完整组的实际数量，不宣称已经独立复核。

## 交叉复核

复核 Agent 独立阅读指定 PDF 页及必要上下文，逐题判定：`accept` 或 `revise`，记录事实、数值单位、条件、bundle/group 充分性、题型与家族唯一性。接受前必须逐条确认所有原子，并核验 query 的全部必要答案。对每个 intent 保存结构化意见与复核身份；作者据意见另存修订，复核者复查，未决题不封存。复核者不得自行扩大或降低原有要求来迎合检索。
