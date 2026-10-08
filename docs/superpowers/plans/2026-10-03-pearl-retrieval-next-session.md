# PEARL Retrieval 后续任务与新 Session 交接计划

*从已完成的 80 题开发实验推进至完整发布与 200 题独立评估 · status: plan · 2026-10-03*

> **For agentic workers:** 按阶段执行并汇报；执行时使用 `executing-plans`，实际 child 语义复核使用独立子 Agent。采用 `subagent-driven-development` 时，语义复核必须另用 `fork_turns=none` 的隔离上下文，不能继承主执行者的排名、分数或旧决定。本文件是后续计划，不表示下列任务已执行。

**Goal:** 先完成三处开发 Gold 表述修订及四方法一致重算，再适配独立评估入口、登记完整发布版本，最后执行 200 题盲化评估。

**Architecture:** 沿用现有 PEARL、106 篇 Adobe-only 语料、6,433 child 和 R1–R4 方法配置。Gold 修订作为独立分析版本绑定原排名，不修改原检索运行记录；200 题入口在合成输入上开发和验证后才进入正式数据流程。

**Tech Stack:** Windows PowerShell；仓库 `.venv` Python；现有 PEARL 实验脚本；正式检索沿用已固定的 SQLite FTS5、BGE-M3、RRF 和 bge-reranker-v2-m3。

## 1. 新 Session 的工作范围

工作目录：`E:\F_Workspace\F-Agent-Paper`。研究框架：[paper/pearl-framework](../../../paper/pearl-framework/README.md)。

**新 Session 首项任务为阶段 A：Gold 三处表述修订、受影响支持路径盲审、80×4 统一重算和修订分析报告。** 完成后进行阶段汇报。阶段 B–D 是后续路线，不能在 A 的验收前读取封存评估内容、运行 200 题或宣称正式评估完成。

本交接整理不执行新实验、不建立新 chat、不更新个人记忆。不要因新文档中的计划目录和接口而假定相应脚本已经存在。

## 2. 已完成状态与权威入口

| 事项 | 当前实际状态 | 入口 |
| --- | --- | --- |
| 统一检索资产 | 106 篇 Adobe-only 英文来源、6,433 child；来源、canonical、索引、模型身份已核验 | [索引实验](../../../experiments/pearl-index-106-adobe-20260929/README.md) |
| 80 题开发闭环 | 四类各 20 题；四方法三遍真实运行；首遍 320 单元；实际 child 盲审、共同映射、计分和独立复算完成 | [开发实验](../../../experiments/pearl-retrieval-dev80-20261003/README.md)、[开发报告](../../../experiments/pearl-retrieval-dev80-20261003/development-analysis-2026-10-03.md) |
| 开发成绩 | 原 Gold／映射下 CEGR@10 为 R1 47/80、R2 48/80、R3 51/80、R4 58/80；三个预设 Holm p 均 >0.05 | 原开发报告；仅 `agent_reviewed_preliminary` |
| 开发难例复核 | 七题独立原文复核、三题重排退步追溯、39 页完整 PDF 视觉核对完成 | [难例与配置复核](../../../experiments/pearl-dev-review-freeze-20261003/README.md) |
| 方法配置 | 现行 R1–R4 单独冻结，未调参 | [method-freeze.json](../../../experiments/pearl-dev-review-freeze-20261003/method-freeze.json) |
| 开发 Gold 修订 | 012、050、080 的五字段修订建议已提出，**尚未采用**；没有新分数 | [gold-correction-proposal.json](../../../outputs/pearl-dev-review-freeze-20261003-01/gold-correction-proposal.json) |
| 200 题独立评估 | 题集及质控材料已封存；检索、支持盲审、评分、正式报告均未执行 | [题集记录](../../../experiments/pearl-dataset-80-200-20261003/README.md) |
| 完整评估发布 | 未冻结；Gold 修订、200 入口及显式发布门禁仍需完成 | [独立配置审计](../../../outputs/pearl-dev-review-freeze-20261003-01/reviews/configuration-audit.json) |

仍为 `human_verified=false`。人工审查可以后置；不能因此省略已经发现的 Gold 表述问题或入口校验。

## 3. 冻结边界

- 保留所有既有研究输出；不覆盖、改名、删除旧目录，不改旧 `run_manifest.json`、preflight、Gold、支持映射、排名、评分或审查草稿。
- 不读取 200 题 Gold、答案、证据标签、作者日志、QC 或混合材料来修订开发集和调试程序。阶段 A–B 对封存材料仅核验字节哈希和只读属性。
- 不引入旧 Gold-v5／Stage 的题目、标签、索引、排名、分母或成绩。此前旧资产仅为 historical。
- 阶段 A 保持全部 80 个 query、原 8 题、来源、child、索引和方法参数不变。若必要的事实修订涉及这些约束，先记录具体冲突；不能默默扩大实验或继续复用不再匹配的排名。
- 方法固定：R1 body-only SQLite FTS5 BM25；R2 归一化向量 float32 精确点积；R3 等权 RRF k=60；R4 固定 R3 Top-100 完整 child 的重排。D=100，K=1／5／10／20，主指标 CEGR@10，seed=20260929，同分按 chunk ID 升序。
- 不做参数搜索、模型替换、重新解析／切块、parent 扩展或 Agentic 比较。dev034 的单位提取损坏保留为处理失败，仍在评分分母。
- 来源／页命中不能替代实际 child 支持。所有正式 K≤20 判断必须无未决；21–100 未审关系保持未知，不能用于断言不存在证据或声称全深度 R3／R4 覆盖不变。
- 语义复核者与编写／执行者分离。使用独立 `fork_turns=none` 子 Agent，不设置未经用户要求的模型覆盖；只发中性包，不发方法、排名、分数、旧审查结论。PDF 原文不能借入 child 支持判断。
- 保留工作区已有及并行修改。不要自动 commit、push、清理或建新的工作树；如确需隔离，先核对已有附件和原 checkout 的未提交依赖。

## 4. 首先读取与核验

按仓库要求读取 [README](../../../README.md)、[AGENTS](../../../AGENTS.md)、[架构](../../project-architecture.md)、[Knowledge-Base README](../../../Knowledge-Base/README.md)、[文档导航](../../README.md)。随后读取 §2 的开发报告、最新复核报告和 Layer 1 的 [协议](../../../paper/pearl-framework/layer-1-retrieval/experiments.md)、[指标](../../../paper/pearl-framework/layer-1-retrieval/metrics.md)、[盲审规范](../../../experiments/pearl-retrieval-dev80-20261003/review-spec.md)。

### 身份基线

以下哈希已在交接准备时重新读取；新 Session 仍应重新验证，不仅信任文本：

| 文件／资产 | SHA-256 |
| --- | --- |
| 原 80 题开发交付 `outputs/pearl-retrieval-dev80-20261003-01/delivery-manifest.json` | `6539488c5ea10d6fa1b7737c6c24b7b75c1b5244b3aaa17ae7bc8ebc1ac343b0` |
| 最新难例交付 `outputs/pearl-dev-review-freeze-20261003-01/delivery-manifest.json` | `e981364b2bd9c2456e99bed00f800a8da800046afca51659b11fbfe5db1fd8a2` |
| 方法冻结 `experiments/pearl-dev-review-freeze-20261003/method-freeze.json` | `225306055aafe81baa7c260016b34a6cf947d6160ca780174a4785998c21f59f` |
| 原开发 Gold `outputs/pearl-retrieval-dev80-eval200-adobe106-20261003-01/pearl-retrieval-dev-80-adobe106-gold-20261003-r01.json` | `4b118700b2ec810dd57d342ab3d5447b7d313c11aea73535dff160bfaba2d56c` |
| 原首遍排名 `outputs/pearl-retrieval-dev80-20261003-01/rankings.jsonl` | `580c155d3e7075cc1aed5c2887f9f1924babf152e2dde91a9db8bf3f47b48222` |
| 原共同映射 `outputs/pearl-retrieval-dev80-20261003-01/pearl-retrieval-dev-80-adobe106-support-map-pearl-retrieval-dev80-20261003-01.json` | `b79f1d80a7d9246d6ba64911f60cc2fc919ad0a10f66f4b9722b2effdd63b9e1` |
| 原评分 `outputs/pearl-retrieval-dev80-20261003-01/score-details.json` | `a6b23167a6b0981a287322d1770cc4034d8c7cb7f83135b4c7faab7b34cb918e` |
| 修订提案 `outputs/pearl-dev-review-freeze-20261003-01/gold-correction-proposal.json` | `e3e20a44be281654a27091d962d309a98ee3e7ec54016a4782cb8e09b97032ab` |

原运行 checkpoint 的 `retrieval_complete_support_review_pending` 是保留的检索阶段状态；全链完成看独立 delivery manifest。不要为了更新进度而改旧 checkpoint。

下面是**现有可执行的只读起步命令**，不是新的修订入口：

```powershell
Set-Location -LiteralPath 'E:\F_Workspace\F-Agent-Paper'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONPATH = 'Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src'
git status --short --untracked-files=no
@'
import hashlib, json
from pathlib import Path

def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

roots = [
    ('outputs/pearl-retrieval-dev80-20261003-01', '6539488c5ea10d6fa1b7737c6c24b7b75c1b5244b3aaa17ae7bc8ebc1ac343b0'),
    ('outputs/pearl-dev-review-freeze-20261003-01', 'e981364b2bd9c2456e99bed00f800a8da800046afca51659b11fbfe5db1fd8a2'),
]
for folder, expected in roots:
    root = Path(folder)
    manifest_path = root / 'delivery-manifest.json'
    assert sha(manifest_path) == expected, manifest_path
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for name, digest in manifest['artifacts_sha256'].items():
        assert sha(root / name) == digest, name
    print(folder, 'immutable artifacts verified', len(manifest['artifacts_sha256']))

run = json.loads(Path('outputs/pearl-retrieval-dev80-20261003-01/run_manifest.json').read_text(encoding='utf-8'))
for name, digest in run['input_binding']['sealed_files_sha256'].items():
    path = Path(name)
    assert sha(path) == digest, name
    assert path.stat().st_file_attributes & 1, name
print('sealed files hash + readonly verified; no semantic parsing', len(run['input_binding']['sealed_files_sha256']))
'@ | .\.venv\Scripts\python -
.\.venv\Scripts\python -m pytest experiments/pearl-retrieval-dev80-20261003 -q
```

预期：原交付 538 项、最新交付 93 项身份一致，200 项封存文件通过，现有专项测试通过。测试实际数量以本次输出为准，不用旧运行的数量冒充新结果。

`workspace_files_sha256` 是交付时工作区快照，不等同永久不变的导航文件；本次新交接登记会继续更新 `docs/README.md`。应核对旧研究产物和保存的源码快照，并记录合理的文档变化，不能修改旧 manifest 来追平当前导航哈希。初始配置核验记录已由 `configuration-hash-verification-r02.json` 的明确 preflight 绑定核验接续，两份都保留。

## 5. 阶段 A：Gold 修订与开发共同重算

### A1. 保存新语义版本和差异

**输入：** 原开发 Gold、五字段提案、[源表述复核](../../../outputs/pearl-dev-review-freeze-20261003-01/reviews/source-scope-review.json)、[联合来源复核](../../../outputs/pearl-dev-review-freeze-20261003-01/reviews/source-joint-review.json)。

**计划文件边界：** 新建研究实验目录 `experiments/pearl-retrieval-gold-revision-r02/`，保存 README、修订 provenance 入口和必要的固定测试；新结果放入 `outputs/pearl-retrieval-dev80-gold-r02-20261003-01/`。这两个目录是计划路径，开始时先检查是否已存在；已有则使用另一个独立编号，禁止覆盖。

- [ ] 逐字段核对提案的 old_value 与原 Gold，重新核验原文出处，然后形成新 Gold r02、修订差异与基线哈希。
- [ ] 012：保留 zipper 机制答案，修正无例外的 universal scope；例外数字属于有效 selfish 比例、placid 条件，不能误写为 placid 比例。
- [ ] 050：参考答案改为中性的 head-sway 干扰表述；保留原文 children 锚点及其与成人参与者记录的矛盾，不修改来源引文。
- [ ] 080：明确尚缺经验验证／真实实验校准，同时区分已有数值验证。若采用 despite numerical verification 作为计分必需命题，必须提供明确的 atom／锚点及 actual child 路径；不能让旧 a2 的校准句自动支持新增命题。
- [ ] 030 保留作者报告阈值并记录源内矛盾；006 保留 f1(N) 分母；034 保留处理缺失与评分分母；079 保留建模子群范围。本轮不增加这些题的可选修订。
- [ ] 验证全部 80 个 query 和原 8 题全文不变，77 道未修订题的完整语义对象与原版一致；配额仍为四类各 20、无空组、来源／child 身份不变。

**验收：** 新版本明确 `agent_reviewed_preliminary`、`human_verified=false`；有准确修订内容与出处；原 Gold 未动。不能把提出提案或内存试应用当作已完成采用与评分。

### A2. 受影响实际 child 盲审与新映射选择

**输入：** 新版三题语义对象、原实际 child 池、原四方法 Top-20 ID 联集和所需同源补充 child。排名只由主执行者用于确定必审集合，不能出现在复核包中。

- [ ] 为 012、050、080 新建中性复核包，包含完整正文、来源／页／chunk ID／正文 SHA、新 Gold；清除 rank、score、method、channel、旧判断与路径结论。
- [ ] 独立子 Agent 逐题判定单 child 及联合 child 路径。作者／运行者不代替独立语义核验者；PDF 原文核对和 child 支持判定分开保存。
- [ ] 三题必审池所有 K≤20 关系和组合判断均审定。变动要求导致旧支持路径不再成立时，保留差异；不能为维持原分数而接受路径。
- [ ] 77 道未变题仅在 Gold 完整对象不变、原 packet／审查全文／正文哈希均验证后继承已选定决定。原最终选择来自 `outputs/pearl-retrieval-dev80-20261003-01/review/selected-review-files.json`，不能 glob 所有原稿／修订／复裁文件。
- [ ] 新选择清单覆盖 80 个唯一 intent，逐项绑定所选决定全文和适用 packet；新共同映射同时绑定原排名、新 Gold、冻结 child 和新选择清单。所有方法共享它。

**验收：** 80 个唯一最终决定、三题独立复核 provenance、K≤20 无未决；21–100 未审项仍为未知。新映射不能宣称源级原文复核本身就是 actual child 支持审定。

### A3. 实现显式修订分析绑定并共同重算

**现有接口：** `score.py` 的 `load_run`／`load_validated_inputs` 会核验原 preflight 和 run 的 Gold SHA；`build_details`、`aggregate` 可复用公式；`protocol.py` 的 `validate_gold`／`score_prefix` 提供结构与计分；`analyze.py` 的 `statistics`、`failures` 和来源分量分析已有实现；`verify.py` 的 `oracle` 是独立布尔参考。

**重要限制：** 直接执行原 `score.py --gold 新Gold` 会被原运行身份校验拒绝，这是正确行为。不得改旧运行的 Gold SHA、伪造新检索 manifest 或跳过全部绑定检查来绕过拒绝。

**计划新增接口：** 在新实验目录设计专用修订 loader，显式消费 `base_directory`、`base_gold_path`、`revised_gold_path`、`selected_review_manifest` 和 `revision_manifest`，验证后产出原评分函数所需的 `q_by`、`gold`、`children`、`ranks`、`decisions`、`run` 和 `preflight`。其中 run／preflight 仍是原检索事实；修订 Gold 与映射通过独立 revision manifest 绑定，不能将新 Gold 身份写回旧字段。后续 CLI 名称和参数在实际实现完成后登记，本交接不提供虚构的可运行新命令。

- [ ] 先写固定失败用例：Gold SHA 被偷换、query 改变、77 题语义漂移、重复／缺少 intent、所选决定全文不同、child 正文不同、未审关系进入 K20、revision manifest 指向错的原排名，均必须拒绝。
- [ ] 原开发入口保持原行为；新修订入口通过来源身份和 query 等价性证明后复用原首遍排名。不能重新挑选三遍中的最好一遍，也不需要因答案措辞修订重新运行 GPU 检索。
- [ ] 单独计算全部 80×4、K=1／5／10／20，共 1,280 个前缀；输出新评分 JSON／CSV、80 题完整矩阵、新来源与配对统计、失败诊断和与 r01 的逐题差异。
- [ ] 统计保持三项预设比较 R2–R1、R3–R2、R4–R3，精确 McNemar＋Holm；分层配对 bootstrap 10,000 次、seed=20260929；来源分量敏感性单列。即使修订前后分数完全相同，也应如实交付修订分析，不制造改善。
- [ ] 独立 oracle 复算 1,280 个前缀及 48 个总体指标；核对执行失败未被当作 0、分母不变、修订仅影响合理语义路径，重新生成代码和审查绑定。
- [ ] 新报告标题／状态明确“开发 Gold r02 修订分析”；保留 r01 主分析、原排名、既有损失及不确定性。同步导航并验证相对链接。

**现有针对性验证命令：**

```powershell
.\.venv\Scripts\python -m pytest experiments/pearl-retrieval-dev80-20261003/test_protocol.py experiments/pearl-retrieval-dev80-20261003/test_score_analysis.py experiments/pearl-retrieval-dev80-20261003/test_verify.py -q
```

新实验实现后，其自身测试命令为 `.\.venv\Scripts\python -m pytest experiments/pearl-retrieval-gold-revision-r02 -q`，执行前须确认目录和测试已创建。若采用其他独立目录编号，在报告中登记实际命令。没有跨稳定契约变更时无需为了文档交付运行全仓库 suite；若确实跨契约，则按 AGENTS 中四 src 环境执行全套。

**阶段 A 交付门槛：** 新 Gold、修订差异、独立三题审查、新唯一选择清单和共同映射、全部评分／统计、独立验证、完整 provenance 与修订报告全部存在且重算一致。完成后汇报实际改变、成绩是否变化、验证结果和下一阶段边界，不能只交新 Gold 或一个重算摘要。

## 6. 阶段 B：200 题入口适配，继续封存正式内容

**待适配范围：** 现有 `prepare.py` 固定开发 Gold／80 与原 8 题一致性；`run.py` 默认 80 和 development_80；`blind.py` 固定导入开发 Gold；`score.py` CLI／默认数量固定 80；`analyze.py`／`verify.py` 的计数、状态及验证分母仍依赖开发运行。具体源码定位以独立配置审计与新 Session 搜索为准。

- [ ] 先使用合成 80／200 query、Gold 与排名矩阵验证入口；不通过读取 sealed eval 检查程序“能否处理”200 题。
- [ ] 显式区分 split、expected_count、Gold／query-only 路径、四类配额、输出目录、原始运行与修订分析模式。检索器只接收 intent_id／query，不加载答案、要求或支持标签。
- [ ] 验证 200×4=800 个首遍单元、三遍共 600 个 timed query；仅在每题实际返回 100 候选时三遍 R4 为 60,000 对，短候选或合法空结果按真实记录计数，不能写死理想分母。
- [ ] 支持密封原始排名、盲化去线索、明确审查版本选择、共同映射、动态矩阵与独立公式验证。测试缺项、重复、跨 split 输入、输出已存在、截断、实际 token 输入、所选发布配置不符及模型／索引 hash 漂移的拒绝行为。
- [ ] 新入口在启动前验证所选 frozen release manifest；不能仅运行后记录当前参数。旧开发／原复现入口保持可核验。

**交付：** 实际可运行入口、完整合成验证、适配前后边界、登记命令与独立输出位置；200 Gold 及作者／QC 内容仍未读取，正式运行数仍为 0。

## 7. 阶段 C：完整发布与评估 Query 导出

- [ ] 登记协议版本、固定语料／child／模型身份、阶段 A 采用的开发 Gold 和评分代码、新入口版本、四方法配置、主指标与预设统计、执行硬件及输出目录。
- [ ] 明确完整冻结的范围，不能将 method-freeze 当作 Gold、程序和发布门禁均已冻结。记录替代完整组当前为 0、未达到原目标等已知协议限制；如接受限制，须显式登记，不能暗写达标。
- [ ] 分离数据保管／query 导出与检索执行：只有完整发布验证后，由隔离流程从既有评估封存包导出 query-only；检索执行者不获得答案或标签。记录封存时点、导出身份与访问范围，不提前开展“试运行几道评估题”。
- [ ] 正式命令引用实际已经验证的新入口和新输出目录；执行前核验所有依赖，不使用原 dev80 命令替换目录冒充 eval200。

**交付：** 完整 release manifest、实际执行命令、可审计 query-only 导出以及仍未运行的评估状态。若到此仍有真实阻塞，报告具体证据和可处理项，不能将未就绪登记为完成。

## 8. 阶段 D：200 题正式检索、支持盲审与评估报告

- [ ] 沿用冻结方法；5 次开发 query 预热；200 题固定随机顺序三遍，首遍排名用于评分并密封，其余用于确定性和时延核验。保存两通道 Top-100、完整 RRF union、R4 输入／输出、child 正文身份、forward 输入、设备、时延、失败与重试。
- [ ] 首遍 800 单元完整且无未解决执行错误；三遍差异如实记录。instrumented gross 时延与扣除显式审计开销的调整估计分开，不能将调整估计当作纯净无插桩延迟。
- [ ] 从四方法候选池生成独立中性包，实际 child 单片段与联合路径盲审；K≤20 全部审定后冻结共同映射。深层未知继续保留。
- [ ] 200×4、K=1／5／10／20 统一评分、预设配对统计、题型分析、来源依赖、失败与成本报告；独立公式复算 3,200 个前缀和 48 个总体指标。
- [ ] 核对来源／Gold／排名／映射／审查版本／代码／模型输入全部绑定，交付报告和 manifests。开发与独立评估分表，不能合并 N=280 或把四方法当作额外独立题。

**完成定义：** 正式排名、共同实际 child 支持映射、完整评分统计、独立复算、失败／成本报告和 provenance 全部完成。此后才可称 Retrieval 正式评估完成。若评估结果用于调参，后续分析标为探索性，不能保留“未见测试”的解释。

## 9. 可直接粘贴到新 Session 的启动指令

```text
工作目录：E:\F_Workspace\F-Agent-Paper
研究框架：paper/pearl-framework/
请先阅读 docs/superpowers/plans/2026-10-03-pearl-retrieval-next-session.md，按仓库 AGENTS 要求核对现有资产，继续阶段 A：开发 Gold 012/050/080 表述修订、受影响实际 child 独立盲审、80×4 全部 K 的共同重算及修订分析交付。
不要只给方案或只修改 Gold；完成阶段 A 全部验收后汇报。保持全部 query、原8题、106篇语料、6433 child、索引、R1–R4配置及原排名不变，原Gold/mapping/运行manifest/输出不得覆盖。语义复核使用 fork_turns=none 的独立子Agent，不提供方法/排名/分数/旧决定，且不借PDF补入child支持。
现有 score.py 的原Gold哈希约束必须保留；用单独修订provenance绑定新Gold、共同映射与原冻结排名，不能伪造新检索运行或跳过校验。200题和作者/QC/混合材料继续封存，仅核验字节hash和只读属性；阶段A不执行200、不调参、不重解析切块、不开展Agentic。人工审查后置，质量仍标 agent_reviewed_preliminary / human_verified=false。阶段B–D按计划后续推进。
```
