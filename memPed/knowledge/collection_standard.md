# PedRAGent 行人流与疏散交通 RAG 实验语料

_Agent/RAG 研究的语料范围、技术检查与评测输入 · status: current_

本项目用领域文献和规范研究检索、证据组织与问答。语料选择应服务于可检验的研究问题：
比较切块、BM25、BGE-M3 Dense、融合、重排及 Agent 证据编排在行人流与疏散交通问题上的效果。
资料可以进入明确命名的实验语料，实验启动以语料快照和技术检查为准。

## 语料范围

- 包含行人流基本理论、测量、设施通行、疏散行为、交通枢纽与人群安全相关文献；
  与研究问题直接相关的方法论文也可纳入。
- 法规和标准作为单独来源类型，保留发布机构、版本和效力状态；法规适用性结论只使用
  可追溯的当前版本。
- AI、RAG 和 Agent 方法论文属于算法研究资料，不混入领域证据库；原始轨迹数据与
  下载包进入相应数据实验，不作为 PDF 检索语料。
- 无可定位全文的资料可以保留元数据，但不参与需要原文页码或元素证据的评测。

## 从文献到 RAG 实验

1. **固定输入**：给每份 PDF 记录 `resource_id`、来源、版本和 SHA-256；记录实验语料成员。
2. **技术预检与解析**：验证文件存在、PDF 可读、哈希和重复项；解析为规范文档，保留
   解析器版本、页码、元素及空文本页告警。`preflight_manifest` 只执行技术检查。
3. **切块与索引**：按版本化策略构建 parent/child chunks、FTS5/BM25 和可选 BGE-M3/Chroma
   索引；记录 tokenizer、词法分析器、embedding 模型及索引指纹。
4. **检索与评测**：在同一冻结语料上比较 sparse、dense、融合和重排；使用与资源 ID、
   来源版本匹配的题集，分别报告中英文、题型和证据定位指标。
5. **保存结果**：在独立命名的 `outputs/` 目录记录命令、配置、代码版本、随机种子、
   输入哈希、逐题排名和聚合指标，不覆盖已有结果。

元数据缺项和旧期刊评分是语料描述变量，可用于分层或消融实验，不阻断探索性 RAG 实验。
PDF/DOI 身份冲突、撤稿或外部解析服务的来源使用限制应对受影响资料单独处理；选择
`ImportService(paths, parser_backend="pymupdf")` 可运行完全本地解析。技术导入中
`include=true` 推导的 `approved/official` 表示当前检索资格；证据质量由实验指标评价。

## 评测边界

Gold Questions 验收的是检索配置和索引，不决定单份文献能否导入。旧
[`pilot_gold.jsonl`](pilot_gold.jsonl) 的 31 个问题与当前 104 条 Catalog 的资源 ID 不匹配，
不能直接作为新语料的分数；[`gold/2026-09-23-rebuild/`](gold/2026-09-23-rebuild/README.md)
中的 Gold v2 候选题需要独立的指标实现。新实验应报告题集覆盖率、缺失证据和标签不确定性。
旧阈值保存在 [`pilot_config.json`](pilot_config.json) 与 [`core_config.json`](core_config.json)，
仅适用于其原有题集和指标口径。

既有 `literature_quality_rules.yaml`、`quotas.yaml`、筛选记录和准备表保留作历史语料
分层依据，不在这里重复期刊分区和配额审批流程。数据目录与本地资产边界见
[`../README.md`](../README.md)；算法与模型入口见 [`../../Knowledge-Base/README.md`](../../Knowledge-Base/README.md)。
