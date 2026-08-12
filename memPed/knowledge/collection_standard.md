# Ped-Agent 文献与法规入库标准

_内容选择、质量准入与工程入库的统一边界 · 2026-08-11_

---

## 📋 治理结论

文献采用 PRISMA-informed 分阶段治理。PRISMA 负责方案、检索、去重、筛选、全文获取、
排除理由和纳入集合的透明留痕；Ped-Agent 继续负责质量、语料结构、Manifest、技术预检、
解析、索引和 Gold 发布门禁。

完整阶段、产物和门禁见：

- [`prisma_governance.yaml`](prisma_governance.yaml)：机器可读阶段契约
- [`PRISMA 文献治理与入库方案`](../../docs/modules/prisma-literature-governance.md)：执行说明

PRISMA 纳入不等于正式入库。只有通过选择冻结、Manifest 技术预检和 Gold 发布门禁的
资源才允许进入正式检索。

## 🎯 资料范围

- 学术文献仅覆盖行人流、拥堵、疏散与安全；
- 法规类包含法规、规范和标准；
- AI、RAG、LLM Agent 技术论文不进入领域知识库；
- 原始轨迹数据、数据下载包不进入 RAG；
- 与实验方法、轨迹测量或指标解释直接相关的正式论文可按质量标准纳入。

## 🔍 PRISMA 选择链

文献必须依次完成：

1. 冻结范围、纳排标准和检索策略
2. 执行检索并保存完整检索日志与原始响应
3. 规范化记录并保留去重映射
4. 完成标题摘要筛选和冲突裁决
5. 记录全文 sought、retrieved 和 unavailable 状态
6. 完成全文资格筛选并保存主要排除理由
7. 建立 report、study 和 `resource_id` 映射
8. 冻结纳入集合并生成 PRISMA 计数、流程图和清单

AI 只能辅助排序、标记和提出建议，不能作为最终排除者。全文排除必须由第二人确认或由
裁决人批准。任何阶段未完成时不得自动进入下一阶段。

## ✅ 文献质量门槛

普通期刊论文必须同时满足：

1. DOI、作者、期刊和正式发表版本核验通过；
2. 具有合法可用、能够解析和定位页码的 PDF 全文；
3. 中科院分区为一区或二区；
4. Clarivate JCR 官方 JCI 不低于 1.0；
5. 引用量来自 Web of Science，无法使用时允许 Scopus；
6. 完整性状态为 `clear`，不存在撤稿或关注声明；
7. 全文质量评分不低于 80；
8. 使用受控主题标签，并指定唯一 `primary_topic`。

预印本、学位论文、会议摘要、无全文资料以及无法核验分区/JCI的论文只进入候选池。

这些条件属于 Ped-Agent 内容质量治理，不属于 PRISMA 本身。

## 📊 质量等级

- A：中科院一区、JCI 不低于 1.5，并满足分年龄引用标准；
- B：中科院二区及以上、JCI 不低于 1.0，且为高引用文献或近三年高质量新作；
- X：不可替代的经典或缺口证据，必须记录原因和审批人，正式库占比不得超过 10%。

18 个月以内的论文必须为 A 级，且不得超过正式库 10%。19—36 个月内未达到
20 次引用但满足其他要求的 B 级论文计入“高质量新作”，该通道不得超过正式库 20%。

## 📚 全文评分

- 主题相关性：30；
- 方法严谨性：30；
- RAG 证据价值：20；
- 主题覆盖贡献：10；
- 页码与引用可追溯性：10。

## ⚖️ 法规正式入库门槛

- 仅接受政府、发布机构或标准组织的官方来源；
- 必须记录文号、发布机构、辖区、层级、发布日期、生效日期和效力状态；
- 只有当前有效版本可以进入默认检索；
- 历史版本保留追溯，但标记为废止或被替代并排除在正式检索之外。

## 💾 工程入库门槛

通过内容准入的文献先生成 `selection_freeze.json`，再由冻结包生成 Manifest。活动导入链只
执行文件、哈希、重复、版本、元数据和可解析性等技术预检，不在导入时重复判断论文价值、
JCI、CAS 或引用量。

正式发布顺序为：

`selection freeze → Manifest → technical preflight → import → parse → index → Gold evaluation → release`

## 🔐 GitHub 边界

GitHub 只保存治理记录、元数据、Manifest 和评测摘要。PDF、解析正文、SQLite、索引、
密钥和 Cookie 不得提交。

## 🧪 批次与验收

- 每批导入 5 篇文献或 2 份法规；
- 试点候选池保持 60—100 篇，稳定阶段累计候选池保持 300—400 篇；
- 完整 Manifest 先通过数量、主题、等级和引用结构校验，再分批导入；
- 导入后重建索引，并使用对应评测配置执行 Gold Questions 门禁；
- 试点评测必须满足 30 个问题、Recall@5 ≥0.80、MRR ≥0.70、页码/条款命中率
  ≥0.75，且非正式资料泄漏率为 0。

## 📦 必须保留的产物

| 阶段 | 关键产物 |
| --- | --- |
| 方案 | protocol、eligibility criteria、search strategy、amendments |
| 识别 | search log、candidate snapshot、原始响应 |
| 去重 | deduplication、record aliases、canonical records |
| 筛选 | reviewer decisions、consensus、automation log、exclusions |
| 全文 | retrieval log、inventory、study-report map |
| 质量 | journal metrics、citation snapshots、integrity checks、corpus audit |
| 冻结 | included studies、PRISMA counts、flow、checklist、selection freeze |
| 入库 | Manifest、preflight、import、parse 与 index 报告 |
| 发布 | Gold Set、evaluation report、retrieval release decision |
