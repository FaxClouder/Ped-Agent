# Manifest 说明

每个 JSONL 文件一行对应一个 `ResourceManifest`。Manifest 可以提交 GitHub，PDF 不提交。

正式文献记录至少包含：

- 资源身份：`resource_id`、`doi`、标题、作者、期刊和日期；
- 本地全文：仓库相对 `source_path` 与 SHA-256；
- 正式状态：`publication_status`、`integrity_status`、`include`；
- 影响指标：引用量及来源、JCI、中科院分区和核验年份；
- 指标时效：`metrics_checked_at` 记录 JCI/中科院分区快照的核验日期；
- 治理结论：质量等级、正文评分、主主题及附加主题；
- X级资料额外包含 `exception_reason` 和 `approved_by`。

法规记录不使用 JCI 或引用量字段，但必须包含官方来源、文号、发布机构、辖区、
效力状态、日期、`accessed_date`、`source_verified_by` 和受控主题。

Manifest 中不得写用户专属绝对路径、密钥、Cookie 或受限下载令牌。
