# DeepSeek Harness 调研 - 文档导航

> **status: historical** · 2026-10-07 审计标注：本文是写作当日的快照，其中“当前”“完成”等表述只指当时状态。当前 RAG 状态见 [RAG 资产与一致性审计](rag-asset-audit-2026-10-07.md)。

**调研完成**: 2026-09-15\
**总文档量**: 2500+ 行\

---

## 📖 阅读指南

### 🌟 快速开始（推荐）

如果你是第一次了解这次调研，从这里开始：

**[`dsh-research-complete-summary.md`](dsh-research-complete-summary.md)** (450行)
- ✅ 任务完成情况
- ✅ 核心发现与建议
- ✅ 最终技术决策
- ✅ 行动计划
- ✅ 文档导航

---

## 📚 完整文档体系

### 1. 综合报告

**[`dsh-research-final-report.md`](dsh-research-final-report.md)** (570行)
- 文档调研 + 源码分析综合
- 深度技术分析
- 集成方案对比
- 可借鉴的设计模式
- 详细行动计划

### 2. 文档调研

**[`../Agent-Harness/docs/dsh-research-and-integration.md`](../Agent-Harness/docs/dsh-research-and-integration.md)** (829行)
- dsh 架构深度分析
- 4种集成方案详细评估
- Python 集成方式探讨
- 完整的参考资源

### 3. 源码分析

**[`dsh-source-code-notes.md`](dsh-source-code-notes.md)** (169行)
- 项目结构分析
- Python SDK 验证
- 关键组件识别
- 实验计划

### 4. 快速参考

**[`dsh-research-summary.md`](dsh-research-summary.md)** (104行)
- 执行摘要
- 核心发现
- 推荐路径（简洁版）

**[`task-summary-dsh-research.md`](task-summary-dsh-research.md)** (269行)
- Phase 1 任务总结
- 完成内容清单
- 价值评估

---

## 🎯 核心结论

### ✅ 推荐路径

**借鉴 dsh 设计 + 纯 Python 实现 Agent-Harness**

**理由**:
- 技术栈统一（纯 Python）
- 可控性高（源码透明）
- 维护简单（无外部运行时）
- 适合科研（可复现性强）
- 设计成熟（dsh 已验证）

### ❌ 不推荐

**直接依赖 dsh 框架**

**理由**:
- 开发者预览状态（破坏性变更）
- 双栈复杂（Python + TypeScript）
- 过度设计（UI/沙箱非必需）
- 黑盒调试困难
- 安装复杂

---

## 🔍 关键发现

### dsh 技术特点

**优势**:
- ✅ 成熟的插件系统（Cordis）
- ✅ Python SDK 真实存在且完整
- ✅ 官方维护与社区支持
- ✅ 完整的工具链（CLI + Web + Desktop）

**劣势**:
- ⚠️ 开发者预览（官方警告破坏性变更）
- ⚠️ TypeScript 核心（Python 只是客户端）
- ⚠️ 需要 Node.js ≥22.19 运行时
- ⚠️ 安装复杂（pnpm monorepo）

### Python SDK 验证

**通信机制**:
```
Python SDK (deepseek_harness)
    ↓ JSON-RPC over stdio
TypeScript Runtime (dsh --profile sdk)
    ↓
DeepSeek API
```

**核心组件**:
- `HarnessClient` - JSON-RPC 客户端
- `DeepSeekHarness` - 高层 API
- 支持同步调用：`harness.run(prompt)`

---

## 📊 可借鉴的设计

### 1. Tool 注册机制
```python
class ToolRegistry:
    def register(name, description, parameters, handler)
    def execute(tool_call) -> ToolResult
```

### 2. Profile 配置系统
```python
@dataclass
class Profile:
    name: str
    model_config: ModelConfig
    enabled_tools: list[str]
    execution_policy: ExecutionPolicy
```

### 3. 执行追踪
```python
class ExecutionTracer:
    def record(tool_call, result, timing)
    def replay(record_id) -> ToolResult
```

---

## 🚀 行动计划

### Phase 1: 核心模块稳定（当前）✅
- 继续完成 Knowledge-Base、Video-Analysis、Agent 核心功能

### Phase 2: POC 实验验证（核心稳定后）📋
- 创建 `experiments/dsh-evaluation/`
- 创建 `experiments/deepseek-tool-calling/`
- 实际测试 dsh 与 DeepSeek API
- 数据驱动决策

### Phase 3: Agent-Harness 实现（实验后）📋
- 实现 ToolRegistry（借鉴 dsh）
- 实现 Profile 系统（借鉴 dsh）
- 实现 ExecutionTracer（借鉴 dsh）

### Phase 4: DeepSeek 集成（未来）📋
- 直接 API 调用（无需 dsh 框架）
- 在 Agent 模块添加 DeepSeekAdapter

---

## 📁 源码位置

**dsh 源码**: `E:\F_Workspace\Paper-Sum-Ped\deepseek-harness-master\`

**关键目录**:
```
deepseek-harness-master/
├── python/sdk/                 # Python SDK
│   └── src/deepseek_harness/   # 核心实现
├── packages/                   # TypeScript 核心
└── apps/                       # 应用层
```

---

## 🔗 外部资源

### DeepSeek Harness
- [官方主页](https://deepseek.com/harness/en/)
- [GitHub 仓库](https://github.com/deepseek-ai/deepseek-harness)
- [Python SDK](https://github.com/deepseek-ai/deepseek-harness/tree/main/python/sdk)

### DeepSeek API
- [工具调用文档](https://api-docs.deepseek.com/guides/tool_calls/)

### 社区
- [hello-dsh](https://github.com/pingfanfan/hello-dsh) - 22个技能实例
- [dsh-crew](https://github.com/ZSeven-W/dsh-crew) - Agent 编排
- [dsh-eval](https://github.com/hccccc01333/dsh-eval) - 评估平台

---

## ✨ 调研成果

✅ **文档总量**: 2500+ 行\
✅ **调研深度**: 文档 + 源码双重验证\
✅ **技术决策**: 明确清晰\
✅ **设计参考**: 可直接借鉴\
✅ **行动计划**: 分阶段实施\
✅ **风险控制**: POC 验证先行

**项目现在有了成熟的 Agent 框架设计参考！** 🎉

---

**任务状态**: ✅ 完成\
**创建时间**: 2026-09-15\
**最后更新**: 2026-09-15
