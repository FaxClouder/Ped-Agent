# Ped-Agent 研究资料治理目录

`research/` 保存可提交 GitHub 的治理记录，不保存受版权保护的全文。

## GitHub 保存内容

- 入库标准、主题分类和数量配额；
- 检索式、候选清单、分区/JCI/引用量核验快照；
- 标题、摘要、全文筛选及例外审批记录；
- 可复现的 JSONL Manifest；
- Gold Questions、评测配置和可公开的摘要报告。

## 仅本地保存内容

PDF 原文、解析正文、切块、SQLite Catalog、检索索引和原始运行报告位于
`backend/storage/library/`。该目录已被 `.gitignore` 排除。

## 操作顺序

1. 在 `sources/` 记录检索和候选资料；
2. 在 `screening/` 完成质量评分与纳入决定；
3. 将通过审核且已取得合法全文的资料写入 `manifests/`；
4. 把 PDF 放入本地 `backend/storage/library/inbox/<type>/`；
5. 运行 `ped-agent library validate-manifest <path> --phase pilot|core`；
6. 按每批 5 篇文献或 2 份法规导入，并保留批次报告；
7. 重建索引；
8. 使用对应配置执行 Gold Set 评测，未达到阈值时命令返回失败。

试点候选池为 60—100 篇，稳定阶段累计候选池为 300—400 篇。完整的
pilot/core Manifest 负责校验总量和结构，导入批次负责隔离单份资料的解析失败。

CSV 多值字段统一使用英文分号 `;` 分隔，日期统一使用 ISO 8601 格式。
