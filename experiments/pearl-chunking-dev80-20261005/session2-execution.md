# PEARL 切片 Session 2 E0 执行记录

*最小适配、公共来源与真实开发冒烟 · status: current · 2026-10-05*

本阶段仅执行 Session 2。最终状态与逐文件身份以[交接](../../outputs/pearl-chunking-dev80-20261005-03/handoff.md)、[交付清单](../../outputs/pearl-chunking-dev80-20261005-03/delivery-manifest.json)及打包后重开核验为准。已完成8个预先固定开发意图的真实检索、组装与评分，停止于 E0；没有执行 E1，也没有根据冒烟成绩选择策略。

## 实际实现与复用边界

| 能力 | 实际交付与验证 |
| --- | --- |
| 公共来源 | 106个冻结Adobe CanonicalDocument，26,324个非空元素；原文identity normalization，Unicode半开区间，跨元素分隔符没有证据身份 |
| 表格 | 502张表格全部定位，公共row/cell快照、256 tokens行单位；不合成重复表头，表头原文和所有cell可逆 |
| 公共parent | 3,734个section parent，最大1,536 tokens；与child边界独立，来源与文本可重建 |
| 切片 | C1–C4及B0实验局部适配；core/overlap/prefix分开；真实tokenizer边界、尾块、Unicode、超长句、节边界与来源守恒反例 |
| C4校准 | 实际BGE-M3/CUDA，63,735句、63,137合法相邻对；源句总体与每对、实际输入、向量与0.9 linear分位数独立复核；阈值0.6305798393562411 |
| 索引与检索 | 单个预声明C1-L384-O0-M0索引，5,388个child；真实FTS5/BM25、dense、RRF、reranker，完整中间排名及实际forward IDs |
| 两种面板 | Top100预算主面板与Top10种子诊断；P0/P1/P2×4096/8192，96记录；raw/expanded/deduplicated/final、来源去重、序列化计数与截断offset |
| 支持映射与评分 | 共同来源区间图80题，8题有独立语义证书、72题pending/unknown；不继承旧chunk labels，不进入运行时；复用原Evidence AND/OR评分器 |

C1实际全语料守恒通过。C1–C4/B0的其他策略只完成必要契约测试与15个实际来源结构样例，没有运行其他策略的全语料模型索引。B0保留历史regex320/48及trim空白约定，不伪称原文空白完全分区。M1仅使用原始title/heading元素，最多64 tokens；O1按floor(r×L)附加前文且不改变core。真实模型输入与预算token counter使用同一冻结模型资产的不同明确入口：模型AutoTokenizer与tokenizer.json计数器分别核验，没有混用。

## 固定冒烟与验收证据

按seed20261005、排序strata/IDs每层抽2题，在评分前固定：071、080、036、039、013、012、062、061（完整ID见[抽样记录](../../outputs/pearl-chunking-dev80-20261005-03/smoke-selection.json)）。实际查询执行次序为012、013、036、039、061、062、071、080；各意图使用同一预声明索引。

- 实际8/8检索成功，R1/R2/R3/R4共32方法单元，800个重排pair；8个query dense forward与全部reranker forward逐批核对无截断。
- 96个上下文保存成功；416条评分明细由288条上下文raw/expanded/final与128条Layer1 raw构成，52单元每个分母8，不能当作416个独立问题。
- [保存结果核验](../../outputs/pearl-chunking-dev80-20261005-03/verification-r01.json)独立复算排名/RRF、源区间/可见文本、序列化预算、映射/Gold组、AND/OR、上下界及分母。
- [资产核验r03](../../outputs/pearl-chunking-dev80-20261005-03/assets-verification-r03.json)检查全来源、表格、parent、C1守恒、校准总体/实际输入/向量和阈值。
- 必要测试179 passed：实验72、现有chunk/tokenizer13、原Evidence94；同名测试模块需`--import-mode=importlib`。固定反例不计研究成绩，不替代模型执行。
- [代码与契约审查r05](../../outputs/pearl-chunking-dev80-20261005-03/code-review-r05.md)及[交付审查r06](../../outputs/pearl-chunking-dev80-20261005-03/code-review-r06.md)均通过；真实来源证书与盲化实际final文本诊断保存在独立review文件。

## 身份保全、偏差与限制

初次及最终导航维护前，36个Session1交付、10,335个历史保护文件、1,683个资产、194个旧代码SHA全部无漂移。Session1 manifest SHA为`d90df1326c95c0098bedc7a96a1d758ad76fb23a39e90d76c9a31ab11f703341`。仅当前`docs/README.md`在新交付注册时追加导航：原始bytes另存本次run，并记录before/after SHA；不重写原交付manifest、实验协议或旧输出。

保留全部失败及主动中止记录。修复校准FP16转float32后归一化、模型AutoTokenizer与JSON计数入口差异、pytest同名导入冲突。建库和P2展开的全语料重复扫描改为来源过滤：212个真实child parent-ID列表及40个真实R4 child展开区间完全等价；lazy source hash与原值一致。索引/排名保留旧阶段code SHA，组装记录新阶段SHA和等价证据，不改旧manifest绕过缓存门控。逐字符最大合法前缀截断成本较高，真实组装延迟已保存；未来优化必须保持非单调token计数语义。

支持证书使用独立审查过的保守必要原文区间。完整保留才记yes；不完整或缺证书记unknown，不能机械记no。实际final诊断不升级这些保守分数，也不用于选择方法。8题来源审查披露了启动导航引入的历史汇总元数据曝光，未用于判断；不宣称比原review更严格的隔离。新final诊断仅用提供的query/requirements/真实可见text。72题仍pending，不构成完整80题语义覆盖或正式比较结论。

本阶段generation、远程judge及远程模型API调用均0；未找到本轮既有调用授权。实际运行本地BGE-M3及bge-reranker-v2-m3，不声称新OCR/PDF解析或其他策略模型验证。未改变稳定跨模块契约，未新增产品架构，未运行E1，未提交/合并/推送。

## 交接入口

真实命令、help、返回码和重现范围见[重现命令](reproduction_commands.md)，解析参数见[Session2 manifest](resolved_manifest_session2.yaml)。下一阶段唯一入口是用户另行授权的Session3；先核对本次delivery所有hash，保留pending/unknown，影响正式结论时先补语义证据。不自动执行12格/B0、候选选择、答案生成或旧200题评价。
