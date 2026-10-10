# Session 2 最小适配任务

*逐文件接口与验收建议；以下新接口均未实现 · status: plan · 2026-10-05*

Session 2先校验 [handoff](../../outputs/pearl-chunking-dev80-20261005-02/handoff.md) 与交付manifest及当前资产SHA。再补接口级实施计划，不直接调用旧CLI构建本轮。保持新实验目录和唯一新output，不改旧实验/模块/契约以替代历史行为。

## 文件与依赖顺序

| 拟建文件 | 复用入口及限制 | 拟建函数接口与输出 | 最小固定验收 |
| --- | --- | --- | --- |
| `source_view.py` | CanonicalDocument/DocumentElement；Adobe现有table_data | `build_source_view(doc, view_config) -> SourceView`，多span、段落/小节/屏障、文本hash、separator map；`resolve_legacy_span(child,parent,view)`仅定位 | Unicode、最后短尾、两元素拼接、heading注入区与同文重复字串，roundtrip保持原文；数组字段先解JSON字符串 |
| `table_snapshot.py` | Adobe表格element与table_data，不重新OCR | `freeze_tables(views, tokenizer, table_config)`，row/cell mapping、必要重复表头身份、内容与配置SHA | 重复表头能回到原cell；超长行/cell仍守恒；所有chunker使用同表格SHA；在成绩前冻结未解析行组规则 |
| `parent_graph.py` | 现有parent仅作历史审计，不作公共图 | `build_parent_graph(view, counter, max_tokens=1536)`；`parents_for_spans(core_spans)`允许多父 | 两个child策略读同一图hash，短小节不跨，长段fallback，多父完整覆盖 |
| `chunkers.py` | HierarchicalChunker及HuggingFaceTokenCounter offsets；V2只复用句边界实现线索，不直接当C2/C3 | `chunk(view, C, L, semantic_manifest=None) -> list[SourceChunk]`；`attach_overlap(core,r,L)`；`render_prefix(chunk, prefix_config)` | C1尾块；C2长句；C3短小节；C4不跳句/不合并非连续；O不改变core SHA；前缀不能成为支持正文 |
| `semantic_threshold.py` | 固定BGE-M3现有encode适配器，不注入Gold/query | `freeze_threshold(views, sentence_splitter, model, quantile=.9, method='linear')`，sentence/距离文件与排除计数 | 固定向量参考距离/分位数；跨屏障不入样本；零范数、空句、非有限明确排除；真实句模型执行证据另存 |
| `index.py` | 旧build.py的build_fts、encode/input audit、向量校验；其read_snapshot绑定旧Catalog/POLICY/6433，不能直接用 | `build_index(chunks, resolved_manifest, output)`；独立FTS/向量/IDs与可选Chroma保存，所有资产SHA | 独立目录exists拒绝；新数量动态；体长/完整模型输入守门，M1词法/dense/rerank相同表示；无labels字段 |
| `retrieve.py` | run.py Models/retrieve/capture_forward_inputs、compare_pilot.rrf_union、rerank_pilot.audit_inputs；eval-entry已有动态规模适配可先检查 | `retrieve_all(query_only,index,config,output)`，中间R1/R2/union/R3/R4、full model inputs、返回数、延迟 | 5–8题实际CUDA dense/BM25/reranker成功，无mock；改变config/query/index失效；R4候选集合与R3相同 |
| `assemble.py` | 旧assemble.serialize/snapshot/verify_saved已计完整头标签；旧assemble强制Top10、unit_id去重、历史parent | `assemble(ranking,view,parents,P,B,panel) -> ContextRecord`；`union_spans`/`truncate_with_offsets` | 不同文献同文本保留，同文重叠合并；头标签计入；首次溢出停止；截断更新span、token数最大前缀非单调反例；Top100与Top10不同panel_id |
| `support.py` / `review.py` | r02 path_evidence以及Evidence实际文本盲包；旧support map用旧chunk_id不能直接绑定新chunk | `export_source_support(gold,registry,legacy_review)`只评估侧；`export_visible_packets(context,requirements)`；显式选择真实review | AND/OR、跨块联合、少必要条件unknown；旧锚点遗漏上下文时不直接赋true；新map所有配置共享版本 |
| `score.py` / `verify.py` | Retrieval protocol.score_prefix、Evidence三值评分及独立verify；保留量表语义 | 新adapter把来源支持图转换为相同AND/OR输入；独立核验不调用score核心 | 真/假/未知参考例、截尾失去条件、空排名/API失败保持分母；保存后复算主表和SHA，不用关键词赋标签 |
| `preflight.py` | 现有hash gates、独占创建及strict query-only | `preflight(manifest, expected_stage, output)`核验null/blockers/身份/授权 | null参数或map待审查阻止正式单元；source/chunker/model/prefix/P/B/prompt漂移准确失效；Gold无运行字段 |
| `reproduction_commands.md` | Session 1只读audit helper是真实入口；本表均是待建接口 | 每个实现CLI的`--help`、成功命令、返回码、日志、输出SHA | 不提前把文件名写成可用命令；新CLI先合成契约再真实冒烟 |

SourceChunk最小字段：`chunk_id,doc_id,source_version,core_spans,overlap_spans,prefix_spans,source_text,retrieval_text,core_sha256,text_sha256,tokenizer_sha256,table_snapshot_sha256,parent_ids,policy/config_id`。ContextRecord至少包含panel/ranking hash、实际raw/expanded/dedup/final、多来源span、截断记录、完整serialized_context/hash/tokens及assembly耗时。它们是实验内target契约，不修改Contracts。

## 现有计分能力不能复制成新语义

先读 [动态评价适配入口](../pearl-retrieval-eval-entry-20261003/README.md)，找已实现的动态count、query-only、独立核验；reuse需按新source map绑定，不修改其旧release身份。Layer3 prepare/generate目前固定旧四臂与oracle及旧output，后续以adapter绑定新final context和独立reference；现有完整请求hash与exact_reuse可复用，但加入replicate_id与三真实记录账本。Layer4 prepare绑定400旧回答，后续要动态adapter与新source packets，评分/rubrics保持一致。Session2生成冒烟只在本轮已有明确授权时运行，授权缺失可完成本地E0检索/组装验证并登记生成未验证。

## 冒烟样本与真实命令确认

在解析80题分层元数据后，固定每类2题（最多8题）；先按intent_id排序，固定种子20261005抽样并保存抽样文件及SHA，再看模型成绩。来源映射有问题的题不静默替换，先完成该题审查或登记受影响范围。包含数值表格、同篇多证据、跨文献、单源。合成反例仅验证契约，不计真实研究分数，冒烟成绩不选C/L/O/M/P。

已有命令只作Session2验证入口，从仓库根运行：

```powershell
$env:PYTHONPATH = "Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src"
$env:PYTHONIOENCODING = "utf-8"
.\.venv\Scripts\python -m pytest Knowledge-Base/tests/test_parsing_and_chunking.py Knowledge-Base/tests/test_tokenization.py -q
.\.venv\Scripts\python -m pytest experiments/pearl-evidence-dev80-20261004 -q
```

Session1未执行上述模型/算法测试，也未创建新chunker/index/run CLI。Session2须对实际实现补必要参考测试、运行上述窄检查；只有稳定跨模块契约变化才加规定全仓检查。实际CLI/模型执行日志及保存后验证全部登记后，才能宣称E0_complete；然后停止，不运行E1。
