# Session 2 E0 重现命令

*仓库根 PowerShell、本地冻结模型与只读历史输入 · status: current · 2026-10-05*

本文件记录 Session 2 的真实入口；仅单个预声明 C1-L384-O0-M0 冒烟索引。当前运行位于 `outputs/pearl-chunking-dev80-20261005-03/`。所有命令返回码和完整日志由该目录的 `command-*.json` 及其绑定日志保存。失败、主动中止与成功记录全部保留。正式 E1 网格未执行，也未根据冒烟分数选策略。

## 环境与保存结果复核

```powershell
$env:PYTHONPATH = 'Contracts/src;Agent/src;Knowledge-Base/src;Video-Analysis/src'
$env:PYTHONIOENCODING = 'utf-8'
$exp = 'experiments/pearl-chunking-dev80-20261005'
$out = 'outputs/pearl-chunking-dev80-20261005-03'
.\.venv\Scripts\python "$exp/smoke.py" --help
.\.venv\Scripts\python "$exp/evaluate.py" --help
.\.venv\Scripts\python "$exp/verify.py" --help
.\.venv\Scripts\python "$exp/audit_assets.py" --help
```

下面两个复核命令不执行模型推理。必须使用不存在的新 receipt 名称；程序以 exclusive create 写入，防止覆盖研究结果。

```powershell
.\.venv\Scripts\python "$exp/audit_assets.py" --output $out --receipt "$out/assets-verification-new.json"
.\.venv\Scripts\python "$exp/verify.py" --output $out --scores "$out/score-smoke-r01.json" --receipt "$out/verification-new.json"
```

## 真实执行链

来源输入 `source-views.json` 从冻结 `source_registry.json` 的106个 CanonicalDocument 构建：逐项先核对 canonical SHA，再载入 JSON，注入 registry 的 `doc_id/source_version`，调用 `source_view.build_source_view`，保持 registry 顺序。查询输入为严格 `{intent_id,query}` 两字段的 JSONL。固定8个 ID 见 `smoke-selection.json`，随机种子20261005，sorted strata/IDs 每层 random.sample 两题；抽样在任何分数产生前完成。语义支持映射只能在离线评价侧准备，不进入建库、检索和组装请求。

在一个不存在的新输出目录准备上述两个输入，以及冻结选择的副本后，以下命令依次执行；实际本次参数为 `$out`，成功的校准 revision 为 r02。CLI不会自动运行后一阶段。

保留缓存的重现方式：先核对原运行的 delivery manifest 与上述保存结果，然后给 `$out` 指定一个**不存在**的新 run 名称；将原运行的 `source-views.json`、`queries.jsonl`、`smoke-selection.json` 和评价侧 `common-support-map-r03.json` 逐字节复制到新目录并核对 SHA。这是显式使用冻结输入；检索模型、索引、排名、上下文和分数仍由下列真实命令重新计算。不得复制一次模型输出冒充新执行。来源彻底重建的函数路径已在上一段列出，原 registry canonical 全部本地保留。

```powershell
.\.venv\Scripts\python "$exp/smoke.py" prepare --output $out
.\.venv\Scripts\python "$exp/smoke.py" calibrate --output $out --attempt-id r02
.\.venv\Scripts\python "$exp/smoke.py" build --output $out
.\.venv\Scripts\python "$exp/smoke.py" retrieve --output $out
.\.venv\Scripts\python "$exp/smoke.py" contexts --output $out
.\.venv\Scripts\python "$exp/evaluate.py" --output $out --mapping "$out/common-support-map-r03.json" --receipt "$out/score-smoke-r01.json"
.\.venv\Scripts\python "$exp/verify.py" --output $out --scores "$out/score-smoke-r01.json" --receipt "$out/verification-r01.json"
```

校准使用实际 BGE-M3、CUDA、batch8、最大输入2048；检索 dense 和重排最大输入1024。每批保存实际 forward input IDs 并核对无截断。校准句子最长1927模型tokens，2048参数在评价前固定。完整句子总体63735，相邻合法对63137；分位数为0.9、linear，实际阈值0.6305798393562411。模型权重与配置由 `runtime.model_assets()` 对 Session 1 SHA 门控。

恢复现有缓存时先运行 saved-output verifier，不重新写同目录。任何来源、模型、切片、前缀或运行代码漂移均需新索引与新排名。预算只影响组装；support map 只影响评价。当前 index manifest 内保留建库/检索时的代码 SHA，后续 assembly 性能优化的阶段 SHA 与实际等价反例记录见交接；不能静默改旧 manifest 来绕过 retrieve 的代码门控。

## 必要测试与日志

```powershell
.\.venv\Scripts\python -m pytest experiments/pearl-chunking-dev80-20261005 Knowledge-Base/tests/test_parsing_and_chunking.py Knowledge-Base/tests/test_tokenization.py experiments/pearl-evidence-dev80-20261004 --import-mode=importlib -q
```

实际结果179 passed；`--import-mode=importlib` 避免两个实验同名 `test_verify.py` 的 collect 冲突。实验目录72项包含来源、长度、表格、C1–C4/B0、支持AND/OR、预算尾部条件、未知传播、缓存身份和篡改反例；另13项现有chunk/tokenizer与94项原Evidence测试。不改变稳定模块契约，未要求全仓跨模块测试。

`capture_command.py --receipt <new.json> -- <executable> <args...>` 为可重用日志包装器。实际重排800对，8个dense查询；完整R1/R2/R3/R4排名与RRFunion保存在 `rankings.jsonl`，真实输入与延迟在 `retrieval-audits.jsonl`。两种面板为 Top100预算主面板和Top10种子诊断，P0/P1/P2×4096/8192，合计96上下文；raw/expanded/deduplicated/final和截断offset全部保存。

打包是上述文件日志包装器的唯一例外：`package_e0.py package --output $out` 必须用 `subprocess.run(..., capture_output=True, text=True)` 在内存捕获 stdout/stderr，返回后再 exclusive 保存 `command-package-final-r01.json`。该回执是明确排除自哈希的外层命令信封，不应通过 `capture_command.py` 或目录内文件重定向执行打包，否则活动日志会在冻结后追加并导致 SHA 漂移。`package_e0.py preservation --output $out` 可以使用普通包装器。

## 偏差、范围与停点

失败记录保留：校准r01向量归一化检查失败；建库r01与组装r01因全语料重复扫描主动中止；audit r01混用了JSON token counter与真实模型AutoTokenizer；合并测试r01同名模块导入冲突。修复均先验证契约与受影响范围，成功revision对应命令日志可查。B0仅重建历史trim约定，不声称守恒原文空白；表格固定不合成重复表头，原始表头仍可定位。共同支持图80题中8题来源语义独立审查，其余72题显式pending/unknown；覆盖不完整仍unknown，不机械记no。

生成与远程judge调用均0：未找到本轮既有调用授权。停止于E0工程交付，后续只允许另行授权 Session 3。冒烟评分不构成方法推荐、完整80题语义覆盖或E1结果。
