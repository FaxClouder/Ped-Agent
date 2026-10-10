# 研究主审第 1 期：评审说明

*给 ChatGPT（外部裁判）的操作说明：Layer 3、可回答性、有据性与引用三个任务的主审 · status: current · 2026-10-07*

本期共 1,648 个盲化包，分成三个任务目录。**每个任务必须在一个独立的新对话中完成**，不要沿用校准时的对话，也不要在同一个对话里做两个任务。三个任务互不依赖，可以并行。

| 对话 | 目录 | 包数 | 规则文件 |
| --- | --- | --- | --- |
| A | `layer3/` | 704 | `layer3/system-prompts/layer3.md` |
| B | `answerability/` | 240 | `answerability/system-prompts/layer4-answerability.md` |
| C | `grounding/` | 704 | `grounding/system-prompts/layer4-grounding.md` |

评审规则与你通过校准 cgpt-r02 时使用的规则逐字相同。

## 你的角色

盲化评审员。每个包只依据包内内容和对应规则作出判断。

## 每个对话的步骤（以 `<task>` 代表本对话负责的目录）

1. 打开 `<task>/manifest.json`，按 `index` 的顺序逐个处理 `<task>/packets/<job_id>.json`。
2. 每个包含有：
   - `system_prompt`：指向本目录 `system-prompts/` 里的评审规则。末尾的 “Output format” 规定输出 JSON。
   - `user_message`：待评审的盲化包。
   - `identity_field` 和 `identity_value`：输出 JSON 中对应字段必须原样填这个值。
3. 每个包只输出**一个 JSON 对象**，写入 `<task>/responses/<job_id>.json`（UTF-8，不附加其他文字）。
   - 有据性（C）：每个 `text`、`other_occurrence_texts`、`citation_text` 必须从 `raw_answer` 逐字符复制，每个 `context_evidence.quote` 必须从 `context` 逐字符复制。不要输出字符偏移。
   - Layer 3（A）：参考中列出的每个 target、condition、claim ID 都要给标签，数值目标按规则写 `numeric`。
4. 全部写完后，在本工作包根目录（`paper/pearl-6b-judge-workpackage/`）运行：

   ```
   python validate_responses.py research-primary-1/<task>
   ```

   直到 `problems` 为 0。校验器只检查格式、身份字段、枚举值和逐字复制，不判断标签对错。
5. 写 `<task>/run-notes.md`（导入时必需），至少包含：
   - 实际使用的产品、模型名、推理强度；
   - 开始和结束时间；
   - 本任务用了几个对话或线程，各自处理了哪些包（按 job_id 范围）；
   - 除允许范围外读过的任何文件；
   - 中途出现的错误、重做，或上下文压缩、中断后续做的情况。

包很多，一个对话做不完可以分到先后几个新对话里，但每个对话只做这一个任务，并在 run-notes 里写清楚分工。中断后续做时，已经通过校验的回答不要重写。

## 必须遵守

- **每个对话只读写自己的任务目录**，外加 `research-primary-1/README.md`、根目录的 `README.md` 和 `validate_responses.py`。
  - 不要打开本期其他任务的目录。同一个回答在不同任务里的编号相同（例如 `answer-0042` 与 `grounding-0042`），看到别的任务的包或回答会破坏独立性。
  - 不要打开 `calibration/`、`calibration-r02/`、`outputs/`、`experiments/`、`memPed/`、`docs/` 等仓库其他位置，也不要读 `incidents-and-deviations.md`、`research-periods.md`、`6b-work-plan.md`。
  - 如果意外读到，在 run-notes 中如实写明。
- **每个标签都必须由阅读该包后作出的判断产生。** 不要用关键词匹配、启发式脚本或批量规则自动生成标签。脚本只能用来读写文件和运行校验。
- 包与包之间互相独立。很多包会是同一问题的不同回答，或同一回答在不同 context 下的版本；不要参考其他包或先前的判断来调整当前包。
- 不联网，不用包外知识补足证据。证据不足时，按规则使用 unknown、partial 等。
- 不修改 `packets/`、`system-prompts/`、`manifest.json`。只新建 `responses/*.json` 和 `run-notes.md`。

## 之后（由 Claude 会话执行，不需要你做）

Claude 会导入三个目录的回答，核验格式和绑定，然后导出第 2 期（行为、事实性）。第 2 期同样要求每个任务在新的独立对话中完成。
