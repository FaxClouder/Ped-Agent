# Layer 4 执行记录

*冻结400回答的离线评价 · status: current · 2026-10-04*

## 边界

仅执行既定A–D；不重复Retrieval/Evidence/Answer，不访问外部网页，不新增200题，不进入Layer5/6，不覆盖旧输出，不commit/push/merge。

## 实际进度

- A完成：3656保护检查、400request/response绑定通过；80题149源段事实r03冻结及源文复核保留。
- B完成：r01引用scope分歧保留；r02实际重校准40全过、8哨兵全过。随后验证器/上下界修复已有25项测试通过；新增引用作用域候选程序2项测试通过。均为既定规则实现/核验修复，非科学口径变更。
- C完成：100可回答性全量双审、5需求支持分歧第三裁决；90/9/1冻结。最终1402声明、1297引用pairs、400任务链、2553文件绑定通过独立复算，独立工程审核及严格字段校验增强后再次通过。
- D进行中：剩余300可回答性主审及固定60次审完成、2初始分歧第三裁决；247complete/52partial/1none已冻结，552证据区间独立机械检查。原C100将整行精确复用，尚未汇编400分数。

### C第三裁决与源文重审补记

100条context两审已完成，第三裁决按实际重复Source/page全部窗口核读；保留r05、batch02-r03、r09、r11及r10和各补充版本的SHA。第三原子集合改变的条目重新source-only两审；仅六个语义字段逐字节结构相等的原子允许标明原审查的精确复用，不能按ID搬运。

新增独立facts_secondary_c以fork_turns=none实际读完100包1351原子，未读context/身份/旧分数/主审标签。源范围未覆盖者保留unknown。最终改变原子的35次source-only包重审两遍完成，其余精确语义原子保留原审查来源及SHA；根第三事实分歧按完整条件判定，C21不能将实质等式缩成纯source印字。

context_adjudicator_c实际第三裁决C21–50；calibration_builder实际第三裁决C51–100，既往C answerability/raw暴露披露；root第三C1–20及源侧分歧，root已知旧总体成绩/独立事实依据，不称全盲。所有full_answer额外局限与拒答理由分离，按冻结协议无拒答reason为na。

context_secondary_tail对自己新建、未冻结中间审查文件发生过QA覆盖与按生成规则重构；无首版字节SHA，不能声称已恢复原首版。最终r03及mutation audit单独冻结；未改旧Layer3科学资产。

实现核验修复记录至verification-code-revision-r07；窄测试54项通过（0.24s，exit0），冻结科学rubric未改变。列表引用和别名复用检查增强均有失败用例及修复后的通过输出。

### D当前实际分工

prepare_layer4实际D300可回答性主审，context_secondary_tail实际固定D60次审，根第三处理2初始分歧；完整标签冻结后才授权grounding/behavior。D300前150主审由prepare_layer4执行、后150由context_adjudicator_c执行；固定D60由context_secondary_tail独立次审。context主审此前工程读取过匿名映射及C成绩/事实alias核验的暴露均披露，不称全盲。第二次旧科学资产3656项核验零漂移。

## 角色与暴露

根角色执行编排、数值评分实现、source-only事实复核和第三context裁决；已读事实依据、L3总体分数及009真实答案，逐包披露暴露，不称context-only盲审。
prepare_layer4继承上下文，负责输入与包隔离，随后承担实际校准context judge、C可回答性及grounding/behavior主审；工程阶段见009部分旧score/定义与012部分generation。
calibration_builder使用fork_turns=none，先构造合成锚点，不兼任实际校准judge；随后承担C可回答性与grounding/behavior次审，未读真实facts/旧score/primary。
facts_builder使用fork_turns=none，读取80题源文、承担实际事实校准和C source-only factuality主审；009首次结构检查看到旧requirements/atoms，如实披露。未读生成context或旧分数。

早期第四角色创建因活动线程上限失败；facts主审完成一批后释放活动槽，后成功创建fork_turns=none的context_secondary_tail，负责C51–100独立次审。复用角色既往暴露仍保留；不声称不同独立模型或全程双盲。grounding次审完成数与全量raw读取记录分开统计，不以已读答案冒充已完成全部标签。

### D流水核验补充

D固定60 Grounding次审r03全部保存：792声明、849引用配对；behavior独立次审r02全部保存：58 full_answer、2 bounded_partial。次审behavior首次仅生成1包manifest的工程错误保留为r02历史，完整60包manifest另存r03，未覆盖科学review。根角色实际第三context首批10包已完成，不称盲审：根有C事实/成绩和评估侧身份暴露，但不读D事实结论作context判定。未知单位、引用页码差异、跨文献归属与重复声明逐项保留/裁决。

source-only事实包按最终选定声明exclusive分批导出，当前主审94包、固定60次审的规范声明包10包（尚未启动事实次审），所有导出均不赋标签、不含生成context/Grounding判定。专职facts_builder已开始独立D源文事实主审；生成context角色不兼任该源-only主审。机械context核验已对已导出各批及全60最新次审区间/Source/citation identity/原包SHA检查，已保存审计输出。工程白名单隔离测试3项通过；verification-code-revision-r08记录新增序列化工具而科学rubric/评分公式不变。当前尚未完成D300所有任务、400评分、bootstrap或最终交付。

### 阶段D继续执行记录（2026-10-05，未完成交付）

- 原冻结400回答及actual context继续只读；无被测生成请求。可回答性247/52/1已经冻结，本记录不重新定义。
- source-only secondary首16包140断言：71 true、69 unknown、0 false，72个证据区间逐包验证；具体读源和SHA见secondary-d-initial16-validation.json。未读context、primary、身份或旧score。
- Root完成19份D60 Grounding第三裁决，以及首12份行为第三裁决后，读取D源侧3/15/55以准备事实裁决；后续2份行为第三裁决显式披露该D源侧先前暴露。S55事实第三只读9原子和冻结摘要，0度由实验level walking蕴含；保留balanced条件和额外角度证据不足unknown。
- D195已声明final主审context机械核验195/195通过（原SHA、全文绑定、断言/occurrences、实际Source窗口和引用区间）；不把机械核验称语义二审。第三裁决处理相同0.6m对应不同物理量，保留S10独立五原子及一partial实际页引用。
- batch07追加43 primary、3 secondary源侧白包；batch08追加16 primary；全部context机械检查通过。未给导出的事实白包赋标签。D60 Grounding第三白包共38就绪；源侧175 primary白包中94已审、19 secondary中16已审，均为此时快照，不是最终覆盖。
- 实际命令 `.venv/Scripts/python -m pytest experiments/pearl-layer4-dev80-20261004 -q` exit0，57 passed in0.31s。评分/验算算法未改；analyze.py只修正C100复用表述和实际角色暴露说明。400评分、bootstrap、最终报告、完整交付尚未执行。

## 阶段D r02工程QA快照（2026-10-05）

最终r02完整400通过独立复算：400/5530/5676、6116绑定、1600审查链、C100精确整行复用100；校准160绑定。两角色实际核验结论一致。67项工程测试通过（1.23秒）；20项bootstrap及跨层400项独立核验通过。最终使用r02，两条拒答理由r04实际复核、六包实际映射修正保留旧版与审计。当时报告核查正在进行，随后发现受限回答一致性问题，见r03补充。保护3656项原科学输入进行只读哈希复查，docs导航是明确例外；不读封存200题内容。完成Layer4即停止。

## 最终r03一致性复核（2026-10-05）

实际3包重读与独立图注复核：080 A0-8192 c010 P→S，canon7/事实/引用对不变；067 A1-8192、074 A0-4096未补齐必要结论又含partial背景声明，类别未定ambiguous/abstain=null，不改必要补全标志或理由。可靠性确定覆盖398/400，保留上下界，不放宽bounded定义。新工程guard合成RED后GREEN，68 tests passed0.30s。最终r03独立复算400/5530/5676、6130绑定、1600链、C100精确复用100通过，配对bootstrap与跨层诊断同步r03。最终交付以r03为准，旧r01/r02结果与审计全部保留。
