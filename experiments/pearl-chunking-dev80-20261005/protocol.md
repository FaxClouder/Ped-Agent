# PEARL 切片公共比较协议 r01

*Session 1 冻结科学规则，工程参数与映射待核定 · status: current · 2026-10-05*

## 身份和阶段门禁

科学规则 `protocol_ready` 与工程 `audit_ready_smoke_pending` 分开。[策略方案](../../docs/superpowers/specs/2026-10-05-pearl-chunking-research-design.md)的E1→E3→E2→E4→最终Layer1–2重跑→E5顺序固定。不新增默认人工审查门槛。参数不全时局部阻止正式比较；所有null、待审查与未运行均不可自动转换为成功。

H0为旧106 Adobe源/6433 child、历史检索和Layer2–4只读快照；B0为实际旧正文方法在本轮公共协议下重跑，保持正则长度及原overlap身份。B0不用旧排名或分数。12格才严格O0/M0。B0与任一格只有来源、正文、表格、前缀、索引、检索、恢复、预算及支持图完全相同时才别名复用。

## 来源、正文与公共表格

使用冻结Adobe CanonicalDocument，不重解析、不修复原文数字或单位。来源坐标为 `doc_id/source_version/element_id/[start,end)`，字符按Python Unicode code point，支持表格row/col坐标；PDF bbox只作为元素级定位，不宣称字符级PDF映射。多段正文用多个span，拼接分隔符无证据身份。

Session 2需冻结source_view与可逆normalization map。r01约定保留原文字符，不做大小写/空白/Unicode归一化；元素间显示用两个换行，单独登记为separator。image空正文排除；heading文本保留一次，heading_path另存为元数据，不重复注入正文。caption、公式等有实际text的元素保留。文献边界与table元素构成屏障；本轮不增加表格—正文专属恢复。C3另以真实heading_path变化构成小节边界，缺路径进入显式unsectioned段，禁止猜章节。

表格取现有table_data和table element的原始文本，建立所有配置共用的snapshot。超长表格的行组、重复表头与单个超长cell回退细则及SHA仍未解析，必须Session 2在看任何配置成绩前版本化冻结；表格无法可逆定位时阻止相关数值题的正式比较，不删掉该类分母。不得把表格切法随C1–C4改变。

## 边界与恢复

C1真实BGE offsets固定窗；C2段落→句子→token回退；C3同C2但小节内；C4连续相邻句1−cosine，仅无标签语料90分位阈值，分位数算法冻结为NumPy `method=linear`，有效样本为同文献/非表格连续正文句对，不跨屏障；空句/非有限/零范数排除并记录。数值阈值未执行，保持null。C4从floor(.5L)后遇距离严格大于阈值可切，下一句使core>L则先切，尾块保留。句子分割器版本尚待来源视图固定和反例测试，禁止用Gold校准。

L∈{256,384,512}为core上限。O∈{0,.1,.2}保留相同core，在屏障内附加≤floor(rL)连续前文，完整句优先，超长句允许offset可追溯后缀；C3不越小节。M1最多64 BGE tokens，只原文标题与章节路径，先标题/叶节，再祖先；具体配额和截取算法未解析，不臆填。overlap/prefix附加后完整模型输入须分别核验，不能声称最终输入等长。

P0命中来源正文；P1从core段落出发，两侧各一原文段且不越小节/表格；P2一次冻结公共小节父图，连续段落1536 BGE tokens上限，超长单元句/token回退，不继承child边界。跨父child保留多父，恢复后并入合法overlap来源并集。无标签父图先构建，再离线审查支持。

## 检索、面板和预算

复用实际固定英文FTS5/BM25、BGE-M3归一化dense、等权RRF k=60、BGE reranker；BM25/dense各Top100、RRF Top100重排。实际dense评分是保存unit向量float32点积的exact search；Chroma是索引构建/存储资产，不能未经改协议切换ANN作为研究评分。保存R1/R2/RRF全部union/R3/R4，ties按chunk_id；新索引真实运行，不跨配置套用旧排名。

| panel_id | 输入及计分 |
| --- | --- |
| `layer1_raw` | 原始child Top1/5/10/20，主CEGR@10；prefix不支持、parent不回填 |
| `fixed_budget_main` | R4 Top100依序组装4096/8192；主CGC，E5使用4K实际final |
| `seed10_diagnostic` | 同排名Top10，保存raw/expanded/deduplicated/final；不和主面板差量混算 |

来源去重以同文献同版本区间并集/表格cell位置，跨文献相同字符串保留；展开内部按来源顺序，跨种子按首次排名。首次溢出保留最大合法来源前缀后停止。截断同步更新span，序列化含统一来源头和标签，完整序列化后重新计BGE tokens，verify重开保存文件再计。旧assemble的字符二分不能默认保证BPE计数单调或最大合法前缀；Session 2需固定token-offset候选边界并核验最大前缀和Unicode尾部，不用正文token数替代预算。系统提示/query/输出预留不在context预算，完整请求另外核验provider上限。

## 支持图和三值计分

来源锚点的唯一字串定位只是机械候选，不是语义判定。共同support map必须脱离旧chunk_id，显式包含必要条件、事实及允许证据组。继承旧标签只限已核验完整支持范围、同source_version、实际保留全部span且条件未被截断的情况；partial quote或同论文不充分。新的联合证据需离线语义审查。盲包隐藏方法、排名、旧分数；本阶段没有独立盲审，不把作者自检写成独立审查。

组内AND：任一false→false，全true→true，否则unknown；组间OR：任一true→true，全false→false，否则unknown。跨块联合可组合，但原文关系和作用域必须成立。分别报确定下界、unknown可能上界和审查覆盖；上界不是成绩也不是置信区间。等价来源补充必须版本化共同映射，所有受影响配置重算。

旧Retrieval r02和Layer2 raw的支持视图已有差别，不能选较高旧标签作为B0支持。Layer3参考沿用独立resolved参考，但需与新Gold要求核对；Layer4必须读新答案/new context，NA/无实质claim不自动给Faithfulness满分。

## 候选、统计、缓存和失败

候选先按4K CGC确定完整率，再CEGR@10、实测检索延迟较低、config_id；unknown可能改变入选时先审查或保持pending。最多两个非重复候选，第二个可作不同家族机制对照，须标明目的。E3按相同4K完整性与成本规则冻结E2恢复；不因无提升扩展网格。

统计单位intent，三真实生成先intent内均值，分题型配对bootstrap10000、seed20261005、95%区间；确定二值面板才用精确McNemar/Holm。开发选择偏差保留，不称独立确认。所有失败保留分母并单列；空检索、接口故障、评分解析失败与unknown不同。F0–F7/FU按实际来源和前后文本证据归因，Top100 unknown不能证明索引无证据。

| 缓存 | 必须绑定的身份 |
| --- | --- |
| 来源/切块/父图 | 源SHA、Canonical SHA、view/normalize/表格/分句器/tokenizer/算法/参数/代码dirty SHA |
| 索引/排名 | chunk内容、core/O/M、lexical、权重/revision、模型完整输入、seed、retrieval参数、query/hash |
| context | ranking hash、panel、P、父图、source view、去重、预算、序列化版本 |
| 支持评价 | 实际可见正文、span、Gold/需求/共同map、量表、reviewer与审查记录，不进入运行时缓存 |
| 生成 | 完整messages字节/JSON规范hash、context/query、prompt、模型/API、参数、replicate_id、配置与run manifest；参考不进入messages |

完全相同请求可以共享同三次真实记录，单次不可复制；实际响应失败保留，technical retry最多两次（总attempt≤3）、SDK retry0、不可重试错误不重试，串行并发1，配置间轮转。沿用该上限不代表调用已授权。生成最多720个逻辑请求，理论含重试上限2160 attempts；裁判额度、当前模型可用性与费用为null，授权不足只暂停相应调用。Session1实际生成/裁判/API调用均0；旧Layer3授权不是本轮授权证据。

后续必须保存逐题/明细/上下文/SHA并独立复算，不依赖内存成功。Session 2先验证本交付manifest和输入SHA，完成适配、支持范围审查与5–8个固定分层真实模型冒烟；该完成证明以前E0不得写complete。
