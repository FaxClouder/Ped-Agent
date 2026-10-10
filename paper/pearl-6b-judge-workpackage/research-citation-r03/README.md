# 引用重做 r03 研究主审：评审说明

*给 ChatGPT（外部裁判）的操作说明：704 个研究有据性包的引用部分，按已校准的新输入格式重做；含执行规则 F6 · status: current · 2026-10-08*

本目录共 704 个盲化包，只有一个任务：**引用**。每个包的 claims 已经固定，你只判断 raw_answer 中实际的 claim–citation pairs。

| 目录 | 包数 | 规则文件 |
| --- | --- | --- |
| 本目录 `research-citation-r03/` | 704 | `system-prompts/layer4-citation-r03.md` |

规则文件的判断规则部分（Layer 4 judge prompt、rubric、引用归属补充 r02、“本次任务”）与通过校准 cgpt-r02 时的有据性规则逐字相同。只有末尾不同：先是“输入格式说明 r03”，讲清新增字段怎么读；然后是只输出引用的 Output format。

## 你的角色

盲化评审员。每个包只依据包内内容和规则文件作出判断。

## 包里有什么

- `query`、`context`、`raw_answer`：与有据性包相同，原文没有任何改动。
- `source_fragments`：context 中每个来源块及其片段的位置，由程序从块头推算。读法见规则文件中的“输入格式说明 r03”。
- `claims`：已固定的 claims（`claim_id`、`text`、`occurrences`），不带任何标签。
- `instruction`：本任务的简短说明。

## 步骤

1. 打开本目录的 `manifest.json`，按 `index` 的顺序逐个处理分配给你的 `packets/<job_id>.json`。
2. 每个包含有：
   - `system_prompt`：指向 `system-prompts/layer4-citation-r03.md`。先完整读完这份规则，包括末尾的“输入格式说明 r03”和 Output format。
   - `user_message`：待评审的盲化包。
   - `identity_field` 和 `identity_value`：输出 JSON 中 `anchor_id` 必须原样填这个值。
3. 每个包只输出**一个 JSON 对象**，写入 `responses/<job_id>.json`（UTF-8，不附加其他文字）。
   - 只输出 `anchor_id`、`citation_pairs`、`citation_extraction_unknown`、`reason`，不要输出 `claims`。
   - `citation_pairs` 中的 `claim_id` 必须是包内 `claims` 的 `claim_id`（`claims` 为空时，`citation_pairs` 只能是 `[]`）。
   - `citation_text` 逐字复制自 raw_answer，不要写任何位置。
4. 写完后，在本工作包根目录（`paper/pearl-6b-judge-workpackage/`）运行：

   ```
   python validate_citation_responses.py research-citation-r03
   ```

   直到 `problems` 为 0。校验器只检查格式、身份字段、claim_id、逐字复制、片段编号和枚举值，不判断标签对错。
5. 写 `run-notes.md`（放在本目录，导入时必需），内容见下文“run-notes 必须包含”。

## 执行规则（F6）

允许使用子代理，但必须遵守以下规则。

1. **说明逐字相同。** 每个子代理拿到的说明只有本文件，派发时只能使用下面的模板，只替换尖括号里的 job_id 范围，不得增加、删减或解释任何文字：

   > 请阅读 paper/pearl-6b-judge-workpackage/research-citation-r03/README.md，并严格按其中的说明完成评审。你负责 `<第一个 job_id>` 至 `<最后一个 job_id>` 的包。

2. **协调者不得下发任何判断规则。** 协调者只负责派发、转达进度和汇总 run-notes。子代理提出关于判断的问题时，协调者只能回复：“按 README 的执行规则第 3 条处理。”不得给出例子、口径、倾向或解释，也不得把一个子代理的做法转告另一个子代理。
3. **规则没有覆盖的情况**：按冻结规则记为不确定（该字段可用的 unknown 类取值），在该回答的 `reason` 中写明原因，并在 run-notes 的“未覆盖情况”一节列出 job_id 和原因。由 Claude 统一处理，评审时不要自行裁定，也不要为此形成新的口径。
4. **机械修正要留记录。** 只允许不改变判断的修正（如 JSON 格式、身份字段、字段名、逐字复制错误）。每次修正都在 run-notes 的“修正记录”一节写明：时间、job_id、字段、修改前、修改后、原因。修改前先备份原文件内容到记录中。
5. **已写入的回答不得追加新判断。** 回答写入后，不得增加、删除或改变任何标签或判断。如果认为某个已写入的判断有误，只在 run-notes 中记录，不改文件。
6. **显示包内容时不得删改。** 读包时必须看到完整原文：不得去掉、合并、去重、重排或截断任何字段（包括 SHA、来源元数据、块头、`source_fragments`、重复引文）。输出被截断时，分段重新读完整，并在 run-notes 中记录。

## 必须遵守

- **只读写本目录**，外加本文件、根目录的 `README.md` 和 `validate_citation_responses.py`。
  - 不要打开 `calibration/`、`calibration-r02/`、`calibration-citation-r03/`，也不要打开本目录以外的任何 `research-*` 目录：这些目录含其他轮次的回答。
  - 不要打开 `outputs/`、`experiments/`、`memPed/`、`docs/` 等仓库其他位置，也不要读 `incidents-and-deviations.md`、`research-periods.md`、`6b-work-plan.md`、`scoring-pipeline-spec.md`。
  - 如果意外读到，在 run-notes 中如实写明。
- **每个标签都必须由阅读该包后作出的判断产生。** 不要用关键词匹配、启发式脚本或批量规则自动生成标签。脚本只能用来读写文件、按位置取出片段文字和运行校验。
- 包与包之间互相独立；不要参考其他包或先前的判断来调整当前包。
- 不联网，不用包外知识补足证据。
- 不修改 `packets/`、`system-prompts/`、`manifest.json`。只新建 `responses/*.json` 和 `run-notes.md`。

## run-notes 必须包含

- 实际使用的产品、模型名、推理强度（不知道就写 unknown）；
- 开始和结束时间；
- 用了几个上下文（协调者与每个子代理的标识），各自处理了哪些包（按 job_id 范围）；
- 协调者与子代理之间关于判断的全部往来（应当只有规则第 2 条的固定回复）；
- 除允许范围外读过的任何文件；
- 未覆盖情况（规则第 3 条）；
- 修正记录（规则第 4 条）；
- 中途出现的错误、重做、显示截断，或上下文压缩、中断后续做的情况。

## 之后（由 Claude 会话执行，不需要你做）

T3e 的 F5 门禁已通过（引用 36/36、8 个哨兵全过），本轮只完成 704 包评审与 run-notes 后停止，不导入、不评分、不导出次审。回收后由导入会话按已冻结的 F7 标准做上下文分段检查；标准不在评审时调整。

## 本轮与验收记录

每个上下文（包括协调者）负责的 job_id 范围必须在 run-notes 中逐一写明，恰好覆盖 704 包一次；同一上下文的多个范围合并为一段。主审、次审、裁决必须独立，本轮必须使用新的会话，不与 T4 共用会话。

本轮 claims 固定，保留原主审的 claim 层面有据性；仅重做引用。F5 的 40 个校准锚点都是单块、单来源，校准通过不证明合并块处理正确。F7 在导出记录中冻结：S1、S2、S3 按包置换 10,000 次、seed 20261005，p 均须 ≥ 0.01；S3 仅适用于包数 ≥ 30 的段。只有一个上下文时切为 4 个伪分段。范围覆盖不完整或重复时验收不达标；不达标不得改标签、删除分段或调整阈值，由导入会话登记并逐段排查。
