# PEARL Layer 4 下一会话执行说明

*固定 Layer 3 输出上的有据性、事实与拒答评价交接 · status: plan · 2026-10-04；本说明未执行 Layer 4 实验*

> **执行方式：** 下一会话使用 executing-plans 分阶段执行。以下路径、函数与命令凡标“拟实现”均尚未创建；不得把本计划作为实现或实验完成证明。独立语义评审按阶段要求委派不继承上下文的角色，实际身份与既往暴露如实记录。

**Goal：** 对已有80题×五臂400个真实回答分别评价 Grounding 与 Reliability，保存逐claim证据、引用配对、作答决策、独立复算和中文分析；完成Layer 4后停止。

**Architecture：** 只消费Layer 3实际生成记录和当时实际context；有据性评审与独立事实评审分开。可回答性标签先于行为判定冻结，汇总时再关联旧Layer 2/3成绩。无需实现Agent工具循环或重新生成答案。

**Tech Stack：** 现有Windows PowerShell、`.venv` Python、JSON/JSONL、pytest；实验代码先留在experiments，不改变公共Contracts或Agent运行流程。

## 1. 本轮范围和启动事实

上一轮[Layer 3实验入口](../../../experiments/pearl-answer-dev80-20261004/README.md)及[中文分析](../../../experiments/pearl-answer-dev80-20261004/answer-analysis-2026-10-04.md)记录A–D完成：80题、400个真实首次成功回答、技术失败0、80题参考resolved、80个oracle eligible。原20题是80题子集；C100生成及判分精确复用于D，D新增300，不是额外100道题。

| 项目 | 当前事实 | 本轮处理 |
| --- | --- | --- |
| 实际context臂 | A0-4096、A0-8192为child；A1-4096、A1-8192为parent；各80题 | 完全复用原正文，禁止重新展开或截断 |
| 完整参考臂 | Aref-8192共80题；完整源文选段，长度明显短于实际parent 8K | 同样评价；报告为参考条件，不作纯预算因果对照 |
| Layer 2标签 | 四实际臂320单元：充分260、不足60、unknown0；各臂充分63/64/62/71 | 仅汇总交叉诊断；不是自动的Layer 4可回答性Gold |
| Layer 3正确性 | Strict60/58/57/61、oracle73，各N=80 | 读取冻结结果，不重新判分或改写 |
| 被测模型 | DeepSeek V4.1 Flash，API ID `deepseek-flash`；thinking disabled、temperature0、output cap2048、无seed | 原始身份保留；本轮无被测生成请求 |
| 引用 | 原prompt要求尽可能使用source labels；raw_answer保留，但无已验收的逐claim引用映射 | 从实际答案位置提取并核验；不能替答案补写引用 |
| 当前实现 | [Agent](../../../Agent/README.md)为固定流程；[Harness](../../../Agent-Harness/README.md)无通用Agent循环 | 不阻塞本轮离线评价；Layer 5另行实现 |

本计划不新增拒答题、不做移除证据或噪声生成实验、不打开新的200题评测内容。若本轮天然样本缺少某类拒答/冲突案例，报告该类型未覆盖，不伪造覆盖。合成样例只用于校准与程序测试。

**全局约束：** 不重复Retrieval/Evidence/Answer、不运行整个EvidenceGraph、不取外部网页补充事实、不优化原prompt/模型/策略、不修改旧Gold/排名/context/raw_answer/参考/标签/结果/manifest；不要求人工审查；不执行Layer 5或新增Layer 6实验；不commit/push/merge或清理其他工作。新增Layer 4审查usage可记录，不称全框架效率评价完成。

## 2. 开始阅读与字节身份

按根README → AGENTS → project-architecture → Agent/README → docs/README阅读，再读[研究验收标准](../../research-review-standard.md)、[Grounding说明](../../../paper/pearl-framework/layer-4-grounding/README.md)、[Reliability说明](../../../paper/pearl-framework/layer-4-reliability/README.md)、本计划和Layer 3实际交付。框架中旧“待设计/未执行”表格是目标快照，不能据此否定已有Layer 3交付，也不能推定Layer 4已完成。

工作目录`E:\F_Workspace\F-Agent-Paper`；先查看git dirty状态并保留所有已有修改。以下均为现存源资产，输出根记为`L3 = outputs/pearl-answer-dev80-20261004-01/`：

| 文件，相对于L3 | SHA-256或用途 |
| --- | --- |
| `delivery-manifest-r01.json` | `0eeda54df9a0af9369f3ddcf6450465125754f74d24ba5e4d9304bd918cbe3cf` |
| `delivery-verification-r01.json` | `47acda3e8695283fdd5cddcc4dffb869c942fdfe2e61633d8efb873a78d812db` |
| `reference-freeze-r01.json` | `521279422ddc479602d39cc748ba37799772db100b71667092ed8f4444bc3c1e` |
| `stage80/score-input-r01.json` | `80eb4ea7f7b1e04035ea43e381fab4cbbba7ded9feec66a447c44c78ae9fbd08` |
| `stage80/scores-r01.json` | `e5a4584fd23560c404c7c6064f0c68d54ffc256771f9f5594f1313c67260db01` |
| `generation/all-inputs-r01.jsonl` | 400行，原query/context/request及SHA；不是模型回答文件 |
| `stage20/generation/*.json`、`stage80/generation/*.json` | 100+300条唯一物理记录；答案字段是`raw_answer`，不是`answer` |
| `stage80/score-bindings-r01.json` | 413对象绑定，含原始记录定位；不要只根据目录猜测复用来源 |
| `evaluation/l2-labels.json` | `rows`列表，320个cell与context SHA、sufficient yes/no/unknown |
| `stage80/review/selected-decisions-r01.json` | 仅D新增300条；完整400旧决策以score-input中的cells为准 |

- [ ] 核验上述五个固定SHA、L3清单全部文件与原始记录自哈希、80×5矩阵及query/context/request/response关联。
- [ ] L3交付清单中的`docs/README.md`是交付时导航快照。本次新增计划会合法改变它；登记旧expected SHA、新actual SHA和导航例外，不修改旧manifest。只有导航允许变化，科学文件任何漂移均须查明并停止依赖该输入的评价。
- [ ] 同时基于旧保护清单核验Retrieval/Evidence科学资产；不以“当前读到的文件”重新定义旧baseline。保存新只读保护审计。

## 3. 评价协议：四个基准分别记录

| 评价 | 判断依据 | 不能替代它的东西 |
| --- | --- | --- |
| Layer 3 Correctness | 旧冻结参考与旧判分 | 本轮不重算语义标签 |
| Layer 4 Faithfulness | 该cell实际送给生成器的完整context | 原PDF、完整parent、参考答案都不能补成该context中的支持 |
| Layer 4 Factuality | 独立源文事实与条件，先固定事实依据 | 有据性或与参考文字相似均不能证明事实正确 |
| Citation support | 实际声明的claim–citation配对及对应source位置 | source ID存在不等于支持，不能自动配到Gold引用 |

### 3.1 全部可核查claim的抽取

从原始回答抽取全部实质事实论断，包括结论、解释、数值、单位、实验条件、比较关系和额外断言。保留原文字符区间`[start,end)`，UTF-8原文SHA、原句、规范化claim及条件；拆开独立数值或关系，但条件仍附在同一claim中。不能只抽Layer 3必要claims，也不能靠重复同一断言增加分母。

同一答案内完全相同事实及条件去重，保留所有出现区间；不同对象/条件不合并。比较关系与其两个组成事实各自有明确职责，不能把两个有支持事实拼成未经支持的因果关系。礼貌语、纯格式、提问复述和不包含领域事实的拒答不进入事实claim分母；关于“本context缺少什么”的元声明进入Reliability理由核验，不作为外部事实。不得因无法拆清而静默删除；保留extraction_unknown与原因。

### 3.2 Grounding标签及分母

每条claim标`supported / partial / unsupported / contradicted / unknown`：全条件、数值单位及关系均得到实际context支持才是supported；只支持部分内容是partial；context缺失支撑但可明确判断为缺失是unsupported；明确相反为contradicted；真实歧义或材料无法核验是unknown。不能把“没有支持”一律标unknown。

设每题去重后可核查claim数N，S/P/U/C/X为五类计数，必须满足N=S+P+U+C+X。主指标严格不对partial给0.5分：

- Faithfulness下界=S/N，上界=(S+X)/N；X=0时为同一确定值。
- Unsupported Claim Rate广义未完整支持下界=(P+U+C)/N，上界=(P+U+C+X)/N；同时列P/U/C各自率，避免混淆明确冲突与单纯缺失。
- Context Contradiction Rate下界=C/N，上界=(C+X)/N；报告上下界，不把unknown变为确定错误。
- N=0全部为null/NA，明确理由；纯拒答绝不记Faithfulness=1。若claim抽取分母本身未知，此题点估计与上述固定N上下界均NA，单列未知题数。

每个标签有context字符区间、原文quote、source label和条件解释；检查quote确实在当时context里。有据性不能读取Gold事实包。发现表面冲突可能源于context截断时按实际字面支持裁决，记录边界，不用parent补救。

Factuality独立标`true / false / unknown`，域事实需要完整源文定位、版本SHA、条件和数值单位。对源文明确成立/相反分别true/false；冻结事实范围外、源文未覆盖的额外断言为unknown，不因“参考未提”判false。优先使用既有80题引用和版本化本地原文建立事实包；追加本地查证必须另存版本及盲于策略的理由，不修改原参考。禁止凭模型常识补真值。事实准确率下界=T/N、上界=(T+Xf)/N，同时报已解析T/(T+F)和解析覆盖率；没有事实依据则不宣称全域Factuality完成。

每臂同时报逐题宏平均与claim微平均，各自N和NA数，主指标为宏平均Faithfulness；不把不同答案的claim当独立统计样本。事实冲突与context冲突分别列，不混一个contradiction分母。

### 3.3 引用配对

从`raw_answer`抽实际引用原文与区间，解析到context中的`[Source ... | p....]`身份。归属规则预先冻结：句内/句末引用对应该句事实claims；段末引用在无其它引用时对应该段；多个来源各为独立pair；作用范围歧义标unknown，不选最有利配对。不能把未被标注的相邻source ID当作引用。

Citation Precision以实际claim–citation pairs为分母：supported pairs / 全部实际pairs；未知给上下界。Pair数0时Precision=NA；不可解析或伪造source身份记invalid，并纳入实际pair分母而非删除。Citation Recall以应由外部证据支持的事实claims为分母，有至少一个实际且正确配对的claims / 该分母；无引用的事实回答Recall=0，纯拒答分母0则NA。引用仅指向未送给生成器的源文时单列outside-context，不能得到“基于可见证据的有效引用”分数；如可本地核验另外报源文支持情况。保留引用提取未知及没有结构化映射的历史限制。

### 3.4 Reliability：先判可回答性，再看行为

建立独立的`complete / partial / none / unknown`可回答性：只看query、实际context及预先冻结的必要结论/条件/允许支持组，不看raw_answer、旧L2标签、策略、模型或成绩。complete指任务必要结论均可被context支持；partial可支持部分但缺必要结论；none无实质必要结论可支持；unknown只留真实未能判明的情形。80个oracle也须独立判断，不能因eligible就自动complete。

之后另一packet评价原始行为：`full_answer / bounded_partial / pure_abstain / ambiguous`。bounded_partial必须明确具体缺口，已说结论均受支持，且不在限定语后仍补出未获支持的必要结论。含“可能/据推测”不自动变拒答；明确断言缺失结论属于full_answer或另记unsupported_completion。纯拒答不包含实质领域作答。旧9条refusal只供最终比对，不作为新标签。

按“是否拒绝补全不可支持的必要结论”定义abstention行为：pure_abstain为是；bounded_partial且确实不补全缺口为是；full_answer/unsupported_completion为否；ambiguous为unknown。应拒绝补全正类=partial或none，负类=complete；同时分别报告pure-abstain与bounded-partial，避免把部分作答伪称全拒答。

TP=正类且abstain，FP=complete且abstain，FN=正类且非abstain，TN=complete且非abstain。P=TP/(TP+FP)、R=TP/(TP+FN)、F1=2TP/(2TP+FP+FN)；任一相应分母为0就NA，不设满分。False Answer Rate=FN/(TP+FN)；误拒率=FP/(FP+TN)。可回答性unknown或行为unknown从确定混淆表剔出但仍占全体样本统计，并给全分母覆盖与最坏/最好界，不静默当真阴性。

拒答理由单独判correct/incorrect/unknown，绑定明确缺口与context位置，不把合理行为与正确理由混成一项。Layer 2×可回答性表和Layer 3×Grounding表在解盲后生成；标签不同可记录但不更改L2。应拒答集合尚未验收前只能称60个L2不足候选，不报正式Abstention F1。

联合报告complete上的正确作答/有据但答错/误拒，以及partial/none上的合理受限回答/正确纯拒答/无支持补全；另列正确但无支持、错误且有支持、未知，不把全部情况硬塞四个互斥名称。正确但无支持不能推定来源是参数知识、补证或L2误判。

## 4. 文件职责与拟实现接口

新实验目录拟为`experiments/pearl-layer4-dev80-20261004/`，新结果目录拟为`outputs/pearl-layer4-dev80-20261004-01/`。如已存在，不覆盖，使用下一个序号并在manifest登记。文档均一个H1、短斜体背景行和status。

| 文件（均拟实现） | 职责与接口 |
| --- | --- |
| `README.md`、`protocol.md`、`rubrics.md`、`judge-prompt-r01.md` | 当前入口、冻结口径、版本化抽取与评审指令；不能写为已完成 |
| `prepare.py` | `prepare_inputs(l3_root: Path, out: Path) -> dict`；输出400条cell定位、原始SHA、source映射与80参考定位，独占创建 |
| `extract.py` | `extract_packets(inputs: list[dict], out: Path) -> dict`；只生成带区间的待复核claims/citations，不能由抽取器自行判真值 |
| `review.py` | `export_packets(inputs: list[dict], task: str, seed: int, out: Path) -> dict`；task限定grounding/factuality/answerability/behavior，白名单各不同 |
| `score.py` | `score(reviewed: dict, old_l3: dict, out: Path) -> dict`；按冻结公式出逐题/分层/总体指标与bounds |
| `verify.py` | `verify(bindings: Path, out: Path) -> dict`；不import或调用score核心，重新计算指标并验SHA、区间、引用及裁决链 |
| `test_prepare.py`、`test_extract.py`、`test_review.py`、`test_score.py`、`test_verify.py` | 真实边界固定算例与保存结果篡改检查，不镜像实现写空泛测试 |
| `layer4-analysis-2026-10-04.md` | 中文最终分析，正式Agent开发评价与unknown/未覆盖范围 |

审查schema至少包含cell_id或盲ID、原答案SHA、claim_id、区间、原文、条件、引用pair、标签、证据quote及位置、理由、reviewer/model/prompt/version、实际读取声明、裁决来源；盲packet仅暴露匿名ID，身份映射放评估侧。有据性需要实际context，**不能原样复用Layer 3的export_blind**（其FORBIDDEN会移除context），可复用哈希/版本化思想并建新白名单。

## 5. 阶段A：输入、协议与独立事实依据

- [ ] 完成§2字节核验，生成新input/protected-assets manifests；输出320实际+80oracle矩阵，无缺失/重复，100复用记录只定位一次。
- [ ] 实现prepare、区间/source identity校验和四种packet白名单；先写失败测试，再最小实现。测试包括同cell重复、response/context SHA错配、把父文补进当前context、L3 score进入blind packet，必须拒绝。
- [ ] 写定§3口径与抽取粒度，人工可读地列出四个基准、NA/unknown/partial分母；保存protocol/judge/code SHA。
- [ ] 可回答性rubric与事实包构建委派独立不继承上下文角色，先不暴露答案和旧评分；按实际source读取建事实依据，记录每个必要条件、单位和支持组。可以并行处理不共享判分的分片；本阶段不批量判实际400cell可回答性。
- [ ] 冻结事实包和可回答性评审口径；保存源文构建review、分歧及裁决。事实依据unknown未消除则保留并定义影响，不修改旧参考。实际可回答性评审在B校准通过后于C/D分别先执行、冻结，再允许相应cell行为评审。

**阶段完成标准：** 科学输入身份核验通过；80题400cell可定位；有独立事实依据或明确unknown及answerability口径；协议与评审隔离写定。报告A完成后继续B，不加人工审查门槛。

## 6. 阶段B：抽取与评审校准、代码验证

- [ ] 构建40个冻结校准锚点：支持/部分支持/无支持/明确冲突各8，纯拒答4、受限回答4。分母按案例真实claims，事实/引用/行为分别有expected标签，校准构造者不兼任实际校准judge。
- [ ] 包含8类必过哨兵：单位错误、实验条件错配、关系拼接、客观正确却当前context无支持、纯拒答无claims、伪造引用、未限定的部分补全、必要缺口识别错误。只用于校准，绝不作为实际80题成果。
- [ ] 实际校准judge逐包读取，另角色/程序依据冻结expected复算；claim抽取完整及区间正确≥95%，resolved支持/事实/引用标签与行为标签分别一致率≥95%，8类哨兵全通过。各项报告实际分母，不凭总体平均掩盖某项失败。
- [ ] 不达标修订评审prompt或rubric后另存r02、保留旧记录，所有相关锚点重校准；规则只能在实际C判分前修订。不能因实际成绩改分母或改定义。
- [ ] 固定算例测试：N5的S2/P1/U1/C0/X1得到Faithfulness[.4,.6]和广义未支持[.4,.6]；N0拒答得到NA。三实际citation pairs两有效一invalid的Precision=2/3；三个应引用claims中两个有有效pair的Recall=2/3。
- [ ] 混淆表测试：TP2/FP1/FN1/TN2得P=R=F1=2/3、False Answer=1/3、误拒=1/3；真实标签unknown不悄悄进入TN。可回答集合无正类时Recall与False Answer为NA。
- [ ] 验证程序必须检出保存label/quote区间/引用身份/输入SHA/score的篡改；摘要与行级复算不调用同一个评分实现。
- [ ] 校准同时核验answerability四类标签，独立一致率≥95%；构造锚点不得来自实际答案成绩反推可回答性。
- [ ] 冻结代码、口径、事实、answerability rubric、校准和固定抽样清单。默认Agent语义review无需再配置LLM API；若选择API辅助抽取/评审，先核查现有本地配置并保存provider/prompt/usage和非研究能力预检，禁止打印或重复索取现有密钥；不更换被测模型或调用生成入口。

**阶段完成标准：** 实际校准与独立核验通过，针对性测试通过，C/D真实评审前所有规则冻结；prompt/schema代码审查与结果记录齐全。

## 7. 阶段C：原20题100cell诊断

- [ ] 取原20题ID清单，绝非新抽20题；先在不看答案的packet上完成100cell可回答性primary/secondary及分歧第三裁决，冻结标签；再对100个回答实际抽取全部claims及citations，并逐条核对完整性。
- [ ] primary全部100；独立secondary全部100；所有抽取、支持、事实、citation、行为分歧由第三角色按相应白名单裁决，原两遍判断及理由保留。拒答虽无领域claims仍需behavior/reason判定。
- [ ] Grounding packet给query/raw_answer/抽取claims/实际context/rubric，不给参考事实/L2/L3/策略模型；Factuality packet给claims/独立源文事实包，不给生成context或旧成绩；answerability包不看答案；behavior包给query/raw_answer/context/冻结必要任务口径，不给既定answerability标签。程序在评估侧关联。
- [ ] 两个不同任务的结论不能相互回填；不能用同一角色先看到Gold再称其context-only盲审。新角色不足时记录既往暴露，披露packet盲化的实际限制，不虚称独立模型或完全双盲。
- [ ] 评分与独立复算100cell，检查缺失引文、partial、NA、unknown、正确但无支持及理由错判。C只能诊断代码/流程；如发现科学规则必须改，另存新版本、重新校准并将C100全量按新规则重评，禁止混合口径。

**阶段完成标准：** 100cell完整可追溯（或明确未知）、所有分歧裁决/未知记录齐全、保存评分独立核验通过；报告并继续D。不靠C结果选模型或策略。

## 8. 阶段D：80题完整评价、统计与中文交付

- [ ] 若最终协议不变，C100完整claim/引用/可回答性/语义决策精确复用于D，绑定整行canonical SHA、answer/context/reference/protocol SHA与原来源；不得仅复用汇总数。剩余300先在无答案packet上评可回答性并冻结，再实际评答案；同一固定60cell也复核其可回答性，分歧裁决完成后才冻结。
- [ ] D新增300先固定seed20261004打乱，取每第5条共60个secondary重评cell，在D标签出来前保存名单；剩余240不声称二次review。所有抽取分歧、支持分歧、引用与行为分歧按任务独立第三裁决；unknown可真实保留。
- [ ] 400cell（包括无claim拒答）逐题写输出；另计claims、pairs、事实resolved、NA/unknown、四类answerability及行为。独立验证器检查所有原始记录、完整100复用链、裁决链、证据区间及汇总，不只复查抽样60。
- [ ] 主表四实际臂+oracle分别给Faithfulness/Unsupported/Context Contradiction、Factuality与coverage、Citation Precision/Recall、拒答P/R/F1与False Answer/误拒、理由准确性、可回答题上旧Strict成绩与覆盖。分single/numeric/within/cross各20题列适用数；不构造Layer 4复合总分。
- [ ] 五个预设配对仍用A1-4096−A0-4096、A1-8192−A0-8192、A0-8192−A0-4096、A1-8192−A1-4096、Aref-8192−A1-8192。本轮默认描述性配对差及分层intent bootstrap10000、seed20261004、95%线性百分位，不做事后显著性检验。全指标每次重抽intent并带齐五臂与claims；不按claim独立抽样。
- [ ] Faithfulness宏平均只在该对两臂固定共同适用intent集合上给差值，报告集合N与两侧NA；unknown标签给上下界并分别bootstrap。Citation/Rejection集合及Factuality覆盖明显不同则描述汇总、展示变化，不以筛掉unknown形成有利排名。没有共同适用集时差值NA。
- [ ] 报告35题child4K/8K请求相同而答案可变、oracle更短、单次无seed运行、source依赖与reviewer背景限制。预算、完整源文选择和随机生成不能单一因果归因；无外部事实验证的额外claim保留unknown。
- [ ] 旧文件SHA再核验，docs导航合法例外独立列；新增输出exclusive保存。中文报告经独立实际读表事实核对后保存delivery manifest、代码/config快照、命令/返回码、所有原review/校准/版本/裁决及独立复算绑定。
- [ ] 更新docs/README维护入口，必要时给Layer 4目录增加当前实验链接并保留旧设计状态，不把plan改成已实现。完成规定验证的结果为正式Agent开发评价，`human_verified=false`；未覆盖的拒答类型与全域事实未知如实说明，不加人审门槛。

**完成标准：** 原400cell均有真实审查或明确未解析状态；全部分母和unknown影响可追溯；Grounding与Reliability分别报告、独立复算/保存文件核验/旧科学资产保护通过、中文分析和交付齐全。若天然拒答正类不存在，相关F1/False Answer指标NA并明示本子集无法评价；不得因此补造数据或假称完成该类型测量。完成后汇报并停止Layer 4，不开始Layer 5/新增Layer 6或200题。

## 9. 下一会话验证命令与交接提示

环境与既有工具：

```powershell
Set-Location E:\F_Workspace\F-Agent-Paper
$env:PYTHONPATH = 'Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src'
$env:PYTHONIOENCODING = 'utf-8'
git status --short
```

以下是**拟实现后**的窄测试与独立保存核验入口，当前不能声称已经存在：

```powershell
.\.venv\Scripts\python -m pytest experiments/pearl-layer4-dev80-20261004 -q
.\.venv\Scripts\python experiments/pearl-layer4-dev80-20261004/verify.py outputs/pearl-layer4-dev80-20261004-01/score-bindings-r01.json outputs/pearl-layer4-dev80-20261004-01/independent-verification-r01.json
```

预期：测试按真实固定案例通过；verify输出`verified=true`并显式列400cell、校准/引用/claim/裁决/复用/全部文件绑定数量。CLI由实现阶段绑定本计划接口；不可用计划命令当实际运行记录。公共契约未改则无需为纯实验扩大全库测试；若跨共享契约，按AGENTS运行全套。

复制到新会话：

```text
工作目录：E:\F_Workspace\F-Agent-Paper
请读取 docs/superpowers/plans/2026-10-04-pearl-layer4-next-session.md，
按阶段A–D执行Layer 4 Grounding & Reliability并交付中文分析。
复用已冻结的Layer 3全部400回答与实际context，不重复Retrieval/Evidence/Answer，
不要求人工审查，不新增拒答生成或200题评测；unknown与未覆盖范围如实报告。
使用独立Agent角色完成计划要求的语义评审、分歧裁决与核验，保留真实provenance。
阶段完成后报告并继续；完成Layer 4后汇报并停止，不继续Layer 5或新增Layer 6实验。
不自动commit/push/merge或清理工作区，不覆盖已有输出。
```
