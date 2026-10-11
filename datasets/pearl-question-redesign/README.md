# PEARL 新版开发候选题版本管理

*Git 管理的候选、答案证据与 QA；status: current · 2026-10-10；不是正式冻结测试集*

用户授权在公开的 `codex/question-set` 分支管理这批 40 道开发候选。该例外仅适用于此目录；旧封存题集、PDF、完整解析文本、数据库、索引、模型、凭据和其他 outputs 仍不提交。分支不是访问权限或测试封存机制。

## 当前发布

[pilot40-cloud-20261010-r01](releases/pilot40-cloud-20261010-r01/README.md)：40 题、39 ACCEPT、D-004 未决，非盲、非人工、未冻结。当前版本入口同时登记在 [CURRENT.json](CURRENT.json)。

| 文件 | 职责 |
| --- | --- |
| candidates.jsonl | ID、英文题文、分类、question_revision 与出题来源 |
| answers.jsonl | 参考答案、atoms、requirements、支持路径与条件 |
| qa.jsonl | 对应版本审查、裁决、核验范围及 provenance |
| changes.jsonl | 云端逐题修改说明及原记录哈希 |
| bindings.jsonl | 本地导出记录的确定绑定，不修改历史 QA 字段 |
| metadata/source_catalog/source_graph/D004_classification.json | 统计、106 来源清单、来源关系及 D-004 调查依据 |
| transformations.json | 原输入哈希、拆分/序列化过程、没有改动的字段与未交付依赖 |
| manifest.json / validation.json | 内容哈希、接收合同、结构核验范围与结果 |

候选/答案/QA 对象来自用户提供的 revision_integrated.json，字段无修改，仅作规范化 JSONL 序列化。云端独立 contract 未交付；[本地接收合同](contracts/intake-v1.json)只说明 Git 包装规则，不冒充云端合同或完整 Gold schema。新增题集遵循 [Gold v1.2](../../docs/rag/gold-question-standard-v1.2.md)，本发布没有追改既有记录以假装满足全部新字段。

## 拉取和使用

在本分支的独立工作区中执行，先确认 `git status --short` 没有需要保存的修改：

```powershell
git switch codex/question-set
git pull --ff-only origin codex/question-set
python datasets/pearl-question-redesign/validate_release.py datasets/pearl-question-redesign/releases/pilot40-cloud-20261010-r01
```

读取 CURRENT.json 的 release 字段选择最新接收版本；实验必须记录实际 commit SHA 和 manifest SHA-256，不能仅绑定“最新”。不在含 main 未提交研究工作的目录强行切分支，不使用 reset/clean 清理它。

全新云端环境可直接 clone 分支，无本地 PDF 也能运行结构核验；无 PDF 不能声称完成原文核验。运行实验需要另行满足语料、索引和评测授权要求，本次发布不授权实验。

## 后续发布

1. 不修改已发布 release；新建独立版本目录，manifest 的 parent_release 指向父版。
2. 保留题目/答案/QA 各自 revision 和完整修改原因；不按系统得分改题，不覆盖未决记录。
3. 新 schema/contract 使用新版本。处理缺失云端原合同应补原件并核哈希，不能用同名自造文件代替。
4. 更新 manifest；运行只读 validator，将结果另存 validation.json；结果绑定 manifest 与 validator 哈希。manifest 不包含自身及 validation，避免循环哈希。
5. 更新 CURRENT.json，提交明确的数据路径；检查 diff 后推送本分支。不要 git add 整个研究 outputs。

不承诺自动同步到 main。main 合并应另行执行；在合并前，直接读取此分支的独立工作区或固定提交。
