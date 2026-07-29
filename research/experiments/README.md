# 检索评测资产

本目录保存可提交 GitHub 的 Gold Questions、评测配置和摘要报告。

原始索引、SQLite 数据库和包含大段原文的运行报告必须留在
`backend/storage/library/reports/`，不得提交。

试点评测命令：

```powershell
uv run --project backend ped-agent evaluate `
  research/experiments/pilot_gold.jsonl `
  backend/storage/library/reports/pilot-evaluation.json `
  --config research/experiments/pilot_config.json
```

配置门禁会校验问题数、Recall@5、MRR、页码/条款命中率和非正式资料泄漏率；
任一指标未达标时命令退出码为 1。
