# Models

每个检测模型使用独立子目录，模型配置和权重放在一起：

```text
models/<model-name>/
├── model.yaml
└── weights/
```

`model.yaml` 提交 Git，实际权重默认不提交。新增模型时不要把追踪器参数写入模型配置。
