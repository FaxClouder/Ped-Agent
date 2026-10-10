# 研究主审第 2 期：评审说明

*给 ChatGPT（外部裁判）的操作说明：行为、事实性两个任务的主审；含执行规则 F6 · status: current · 2026-10-08*

本期共 1,402 个盲化包，分成两个任务目录。两个任务互不依赖，可以并行，但**必须在相互独立的上下文中完成**：负责行为的上下文不得接触事实性目录，反之亦然。

| 对话 | 目录 | 包数 | 规则文件 |
| --- | --- | --- | --- |
| D | `behavior/` | 704 | `behavior/system-prompts/layer4-behavior.md` |
| E | `factuality/` | 698 | `factuality/system-prompts/layer4-factuality.md` |

评审规则与你通过校准 cgpt-r02 时使用的规则逐字相同（行为规则末尾带 r02 澄清条款）。

## 你的角色

盲化评审员。每个包只依据包内内容和对应规则作出判断。

## 包里有什么

- 行为包（D）：`query`、`raw_answer`、`context`、`requirements`（必要结论）、`instruction`，以及两个 SHA 字段。
- 事实性包（E）：`claims`（每条有 `claim_id`、`text`、`occurrences`）、`fact_packet`（独立事实源：`sources` 中每条有原文 `quote` 与来源信息，`supplementary_facts` 可能为空，`scope` 说明事实范围）、`instruction`。包内没有 context，也没有原回答；`occurrences` 是该 claim 在原回答中的字符位置，只作标识。

## 每个上下文的步骤（以 `<task>` 代表本上下文负责的目录）

1. 打开 `<task>/manifest.json`，按 `index` 的顺序逐个处理分配给你的 `<task>/packets/<job_id>.json`。
2. 每个包含有：
   - `system_prompt`：指向本目录 `system-prompts/` 里的评审规则。末尾的 “Output format” 规定输出 JSON。
   - `user_message`：待评审的盲化包。
   - `identity_field` 和 `identity_value`：输出 JSON 中对应字段必须原样填这个值。
3. 每个包只输出**一个 JSON 对象**，写入 `<task>/responses/<job_id>.json`（UTF-8，不附加其他文字）。
   - 事实性（E）：包里的每个 `claim_id` 都要恰好给一个标签（true / false / unknown）。
4. 写完后，在本工作包根目录（`paper/pearl-6b-judge-workpackage/`）运行：

   ```
   python validate_responses.py research-primary-2/<task>
   ```

   直到 `problems` 为 0。校验器只检查格式、身份字段、枚举值和事实性的 claim 覆盖，不判断标签对错。
5. 写 `<task>/run-notes.md`（导入时必需），内容见下文“run-notes 必须包含”。

## 执行规则（F6）

本期允许使用子代理，但必须遵守以下规则。

1. **说明逐字相同。** 每个子代理拿到的说明只有本文件，派发时只能使用下面的模板，只替换尖括号里的任务目录和 job_id 范围，不得增加、删减或解释任何文字：

   > 请阅读 paper/pearl-6b-judge-workpackage/research-primary-2/README.md，并严格按其中的说明完成评审。你负责 `<task>` 目录中 `<第一个 job_id>` 至 `<最后一个 job_id>` 的包。

2. **协调者不得下发任何判断规则。** 协调者只负责派发、转达进度和汇总 run-notes。子代理提出关于判断的问题时，协调者只能回复：“按 README 的执行规则第 3 条处理。”不得给出例子、口径、倾向或解释，也不得把一个子代理的做法转告另一个子代理。
3. **规则没有覆盖的情况**：按冻结规则记为不确定（规则中该字段可用的 unknown 类取值），在该回答的 `reason` 中写明原因，并在 run-notes 的“未覆盖情况”一节列出 job_id 和原因。由 Claude 统一处理，评审时不要自行裁定，也不要为此形成新的口径。
4. **机械修正要留记录。** 只允许不改变判断的修正（如 JSON 格式、身份字段、字段名、逐字复制错误）。每次修正都在 run-notes 的“修正记录”一节写明：时间、job_id、字段、修改前、修改后、原因。修改前先备份原文件内容到记录中。
5. **已写入的回答不得追加新判断。** 回答写入后，不得增加、删除或改变任何标签或判断。如果认为某个已写入的判断有误，只在 run-notes 中记录，不改文件。
6. **显示包内容时不得删改。** 读包时必须看到完整原文：不得去掉、合并、去重、重排或截断任何字段（包括 SHA、来源元数据、重复引文）。输出被截断时，分段重新读完整，并在 run-notes 中记录。

## 必须遵守

- **每个上下文只读写自己的任务目录**，外加本文件、根目录的 `README.md` 和 `validate_responses.py`。
  - 不要打开本期另一个任务的目录，也不要打开 `research-primary-1/`。同一个回答在不同任务里的编号相同（例如 `behavior-0042`、`factuality-0042` 与第 1 期的 `grounding-0042`），看到别的任务的包或回答会破坏独立性。
  - 不要打开 `calibration/`、`calibration-r02/`、`outputs/`、`experiments/`、`memPed/`、`docs/` 等仓库其他位置，也不要读 `incidents-and-deviations.md`、`research-periods.md`、`6b-work-plan.md`。
  - 如果意外读到，在 run-notes 中如实写明。
- **每个标签都必须由阅读该包后作出的判断产生。** 不要用关键词匹配、启发式脚本或批量规则自动生成标签。脚本只能用来读写文件和运行校验。
- 包与包之间互相独立。很多包会是同一问题的不同回答；不要参考其他包或先前的判断来调整当前包。
- 不联网，不用包外知识补足证据。事实性只依据 `fact_packet`，范围外按规则记 unknown。
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

Claude 会导入两个目录的回答，核验格式和绑定。之后是引用重做、固定次审和分歧裁决，各有自己的目录和说明。
