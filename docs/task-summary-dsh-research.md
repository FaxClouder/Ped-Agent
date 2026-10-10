# Agent-Harness 与 DeepSeek Harness 调研总结

> **status: historical** · 2026-10-07 审计标注：本文是写作当日的快照，其中“当前”“完成”等表述只指当时状态。当前 RAG 状态见 [RAG 资产与一致性审计](rag-asset-audit-2026-10-07.md)。

**完成时间**: 2026-09-15

---

## ✅ 完成内容

### 1. **Agent-Harness 模块创建** (Phase 1)

创建了独立的 Agent-Harness 模块作为通用工具调用与编排框架：

```
Agent-Harness/
├── src/ped_agent_harness/
│   ├── protocols.py          # ✅ 核心协议 (Tool, ToolCall, ToolResult)
│   ├── tools/                # 📋 工具注册 (待实现)
│   ├── agents/               # 📋 Agent抽象 (规划中)
│   ├── runtime/              # 📋 运行时 (规划中)
│   └── orchestration/        # 📋 多Agent编排 (未来)
├── tests/
│   └── test_protocols.py     # ✅ 8个测试全部通过
├── docs/
│   ├── design-notes.md       # ✅ 详细设计决策
│   └── dsh-research-and-integration.md  # ✅ dsh调研报告 (829行)
├── README.md                 # ✅ 模块文档
└── SETUP_SUMMARY.md          # ✅ 创建总结
```

**核心协议定义**:
- `Tool` - 工具定义
- `ToolCall` - 工具调用请求
- `ToolResult` - 工具执行结果
- `ToolRegistry` Protocol - 工具注册器接口
- `Agent` Protocol - Agent抽象接口（规划）

**测试验证**: ✅ 8/8 passed

### 2. **DeepSeek Harness (dsh) 深度调研**

完成了对 DeepSeek Harness 的全面调研，包含：

#### 关键发现

**dsh 概述**:
- 2026年8月13日开源，MIT许可证
- TypeScript 编写，基于 Cordis 插件系统
- "Everything is a Plugin" 架构
- 开发者预览版 (v0.1)

**技术栈**:
- 核心: TypeScript + Cordis 微内核
- Python 支持: 通过 JSON-RPC stdio 通信
- 运行时: Node.js ≥22.19

#### 集成可行性分析

完成了 4 种集成方案的详细评估：

| 方案 | 推荐度 | 风险 | 收益 | 投入 |
|------|--------|------|------|------|
| A. 完全替换 Agent-Harness | ❌ | 高 | 低 | 极高 |
| B. dsh 作为后端 | ⚠️ | 中高 | 中 | 高 |
| C. 借鉴设计，Python 实现 | ✅ | 低 | 高 | 中 |
| D. POC 概念验证 | ✅ | 无 | - | 低 |

#### 最终建议

**✅ 推荐路径**: 借鉴 dsh 的优秀设计，用 Python 实现我们的 Agent-Harness

**理由**:
1. 保持技术栈统一（Python）
2. 与现有模块无缝集成
3. 借鉴成熟框架经验
4. 避免过度复杂
5. 符合科研场景需求

**❌ 不推荐完全采用 dsh**:
1. 语言栈不匹配（TypeScript vs Python）
2. 过度设计（UI、沙箱对科研场景不必要）
3. 学习曲线陡峭（Cordis 插件系统）
4. 维护双栈复杂度高

### 3. **可借鉴的设计模式**

从 dsh 中提炼的关键设计：

#### 工具注册机制
```python
# 借鉴 dsh 的声明式注册
class ToolRegistry:
    def register(self, name, description, parameters, handler):
        # 类似 dsh 的 ctx.command()
        pass
```

#### Profile 系统
```python
# 配置组合与复用
RESEARCH_BASIC = Profile(
    name="research_basic",
    model_config={...},
    enabled_tools=[...],
    execution_policy={...},
)
```

#### 执行追踪
```python
# 记录、回放、分析
class ExecutionTracer:
    def record(self, tool_call, result, timing):
        # 类似 dsh-eval
        pass
```

### 4. **文档产出**

创建了完整的文档体系：

- **`Agent-Harness/docs/dsh-research-and-integration.md`** (829行)
  - dsh 架构分析
  - Python 集成方式
  - 4种集成方案详细对比
  - 可借鉴的设计模式
  - 行动计划与决策矩阵
  - 完整的参考资源

- **`docs/dsh-research-summary.md`** (104行)
  - 执行摘要
  - 核心发现
  - 行动计划
  - 快速参考

- **Agent-Harness 模块文档更新**
  - README.md 添加 dsh 参考
  - 设计文档链接

---

## 🎯 下一步行动

### 立即执行（本周）

1. **创建 POC 实验**
   ```bash
   mkdir -p experiments/dsh-evaluation
   mkdir -p experiments/deepseek-tool-calling
   ```

2. **dsh 实际测试**
   - 安装测试 dsh
   - 评估 Python SDK 体验
   - 记录集成复杂度

3. **DeepSeek API 测试**
   - 直接测试 DeepSeek API 工具调用（无需 dsh）
   - 评估 V3.2 vs R1-0528
   - 验证响应质量

### 核心模块稳定后

4. **借鉴实现**（Phase 2）
   - 实现 ToolRegistry（参考 dsh）
   - 实现 Profile 系统（参考 dsh）
   - 实现 ExecutionTracer（参考 dsh）

5. **集成 DeepSeek 模型**
   - 在 ModelGateway 添加 DeepSeekAdapter
   - 通过 API 直接调用（无需 dsh 框架）
   - 集成到 Agent 模块

---

## 📊 价值总结

### 1. **清晰的技术决策**

通过深度调研，明确了：
- ❌ 不采用 dsh 作为完整解决方案
- ✅ 借鉴 dsh 的设计模式
- ✅ 保持 Python 技术栈
- ✅ 直接使用 DeepSeek API

### 2. **完整的设计参考**

dsh 调研提供了成熟框架的设计经验：
- 工具注册机制
- Profile 配置系统
- 执行追踪与回放
- Agent 编排模式

### 3. **渐进式开发路径**

明确了分阶段实施策略：
```
Phase 1: 核心协议 ✅ 完成
Phase 2: Tool Calling 基础（核心稳定后）
Phase 3: Agent 抽象（按需）
Phase 4: 多 Agent 编排（未来）
```

### 4. **风险管理**

通过 POC 验证降低决策风险：
- 先实验，再决策
- 数据驱动，而非猜测
- 保持灵活调整空间

---

## 📚 关键文档

### 立即有用
- **`Agent-Harness/README.md`** - 模块入口
- **`docs/dsh-research-summary.md`** - 快速参考
- **`docs/module-division-and-design.md`** - 模块划分

### 深度参考
- **`Agent-Harness/docs/dsh-research-and-integration.md`** - 完整调研 (829行)
- **`Agent-Harness/docs/design-notes.md`** - 设计决策
- **`docs/multi-agent-and-tool-integration-plan.md`** - 集成策略

### 待创建（实验后）
- `experiments/dsh-evaluation/evaluation-report.md`
- `experiments/deepseek-tool-calling/api-test-results.md`
- `Agent-Harness/docs/tool-registry-design.md`
- `Agent/docs/deepseek-integration.md`

---

## 🔗 参考资源

### DeepSeek Harness
- [官方主页](https://deepseek.com/harness/en/)
- [GitHub 仓库](https://github.com/deepseek-ai/deepseek-harness)
- [文档站点](https://deepseek-harness.github.io/deepseek-harness/)

### DeepSeek API
- [工具调用文档](https://api-docs.deepseek.com/guides/tool_calls/)

### 社区资源
- [hello-dsh 教程](https://github.com/pingfanfan/hello-dsh) - 22个技能实例
- [dsh-crew](https://github.com/ZSeven-W/dsh-crew) - Agent 编排
- [dsh-eval](https://github.com/hccccc01333/dsh-eval) - 评估平台

### 对比分析
- [Agent Frameworks Comparison](https://www.langchain.com/blog/agent-frameworks-runtimes-and-harnesses-oh-my)
- [AI Agent Harness Comparison 2026](https://winder.ai/ai-agent-harness-comparison/)

---

## ✨ 核心成果

1. **Agent-Harness 模块基础** - 协议定义完成，测试通过
2. **技术决策明确** - 知道采用什么、不采用什么、为什么
3. **设计参考充足** - 829行深度调研报告
4. **行动路径清晰** - 分阶段实施计划
5. **风险可控** - POC 验证先行

**项目现在有了清晰的扩展路径，可以专注于核心模块开发！** 🎉

---

**任务状态**: ✅ 完成\
**创建时间**: 2026-09-15\
**文档总量**: 933行（dsh调研829行 + 总结104行）\
**测试通过**: 8/8\
**下一步**: 创建 experiments/ 进行 POC 验证
