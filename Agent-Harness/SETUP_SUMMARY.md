# Agent-Harness 模块创建总结

*历史设计快照 · status: historical · 2026-10-04 整理；不代表当前实现或当前上游版本*

本文件保留原始正文，当前替代入口：[2026-10-04 研究文档](docs/legacy-content-review.md)。旧测试、完成状态与环境结论只适用于原记录时点。


## ✅ 已完成

### 1. 模块结构
```
Agent-Harness/
├── src/ped_agent_harness/
│   ├── __init__.py              # 模块入口
│   ├── protocols.py             # 核心协议定义 (Tool, ToolCall, ToolResult, etc.)
│   ├── tools/
│   │   └── __init__.py          # 工具注册与执行 (待实现)
│   ├── agents/
│   │   └── __init__.py          # Agent抽象 (待实现)
│   ├── runtime/
│   │   └── __init__.py          # 运行时框架 (待实现)
│   ├── orchestration/
│   │   └── __init__.py          # 多Agent编排 (未来)
│   └── evaluation/
│       └── __init__.py          # 评测框架 (未来)
├── tests/
│   └── test_protocols.py        # 协议测试 (8 tests, 全部通过)
├── examples/
│   └── tool_calling_demo.py     # 示例代码 (占位符)
├── docs/
│   └── design-notes.md          # 设计文档
├── pyproject.toml               # 项目配置
├── README.md                    # 模块文档
└── .gitignore                   # Git忽略规则
```

### 2. 核心协议定义完成

**protocols.py** 定义了 Phase 1 所需的核心接口：

- ✅ `Tool`: 工具定义（name, description, parameters JSON Schema）
- ✅ `ToolCall`: 工具调用请求（tool_call_id, tool_name, arguments）
- ✅ `ToolResult`: 工具执行结果（content, is_error, metadata）
- ✅ `ToolRegistry` Protocol: 工具注册与执行接口
- ✅ `Agent` Protocol: Agent抽象接口（规划）
- ✅ `ExecutionContext`: 执行上下文（规划）

### 3. 测试验证

```bash
pytest tests/test_protocols.py -v
# 8 passed, 2 warnings in 1.74s
```

所有协议的Pydantic模型验证通过。

### 4. 文档更新

- ✅ `Agent-Harness/README.md`: 完整的模块说明文档
- ✅ `Agent-Harness/docs/design-notes.md`: 详细的设计决策文档
- ✅ `docs/README.md`: 添加Agent-Harness到导航
- ✅ `docs/project-architecture.md`: 更新架构图和模块表

---

## 🎯 设计原则

1. **渐进式**: 先Tool Calling，多Agent按需
2. **Protocol优先**: 接口与实现解耦
3. **与Agent模块协作**: Agent专注证据图，Harness提供通用能力
4. **可测试**: 每个组件独立可测
5. **可复现**: 保留执行日志

---

## 📋 开发阶段

### Phase 1: Tool Calling基础 (当前设计阶段)
- ✅ 模块结构创建
- ✅ 核心Protocol定义
- 🚧 ToolRegistry实现
- 🚧 ToolExecutor实现
- 🚧 参数验证

**时间线**: 与核心模块开发并行进行

### Phase 2: Agent抽象 (待设计)
- ⏸️ BaseAgent实现
- ⏸️ 生命周期管理
- ⏸️ 与Agent模块集成

**前置条件**: Agent模块基础功能稳定

### Phase 3: 运行时与追踪 (规划中)
- ⏸️ Session管理
- ⏸️ Execution tracing
- ⏸️ Metrics收集

### Phase 4: 多Agent编排 (未来)
- ⏸️ Coordinator
- ⏸️ Communication
- ⏸️ Strategies

**触发条件**: 仅在有明确需求时实现

---

## 🔗 与其他模块关系

### Agent模块
- **Agent职责**: 证据收集、问答生成、引用验证（领域逻辑）
- **Harness职责**: 工具调用、Agent运行时、编排框架（通用能力）
- **集成方式**: Agent使用Harness的ToolRegistry和执行能力

### Contracts模块
- Harness定义的Tool、ToolCall、ToolResult可能成为稳定契约
- 待接口稳定后下沉到Contracts

### Knowledge-Base & Video-Analysis
- 可以注册工具到Harness
- 通过工具接口被Agent调用，而不是直接耦合

---

## 🚀 下一步行动

### 立即（与核心模块并行）
1. 继续完善核心模块：
   - Knowledge-Base 文献检索流程
   - Video-Analysis 轨迹分析验证
   - Agent 证据图端到端测试

2. 在Agent-Harness中逐步设计：
   - ToolRegistry实现细节
   - ToolExecutor实现细节
   - 参数验证策略

### 核心模块稳定后
3. 实现Tool Calling基础设施
4. 在experiments/验证实际效果
5. 集成到Agent模块

### 按需扩展
6. Agent抽象（如有必要）
7. 运行时追踪（用于调试）
8. 多Agent编排（需求驱动）

---

## 📝 待决策问题

记录在 `Agent-Harness/docs/design-notes.md`:

1. **工具超时机制**: 默认超时？可配置？
2. **重试策略**: 是否支持工具执行重试？
3. **并发控制**: 多个工具调用如何管理并发？
4. **ToolRegistry单例**: 单例 vs 非单例？
5. **参数验证库**: JSON Schema + jsonschema vs Pydantic动态模型？
6. **工具执行隔离**: 需要沙箱吗？

---

## ✨ 关键设计亮点

### 1. Protocol优先
```python
@runtime_checkable
class ToolRegistry(Protocol):
    def register(...) -> None: ...
    async def execute(...) -> ToolResult: ...
```
- 接口与实现解耦
- 支持多种实现
- 便于测试

### 2. Pydantic验证
```python
class Tool(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any]
```
- 自动验证
- 序列化支持
- 类型安全

### 3. 异步优先
```python
async def execute(self, tool_call: ToolCall) -> ToolResult
```
- 支持I/O密集型工具
- 并发执行
- 与现有Agent模块一致

---

## 📚 参考资源

- [LangChain Tools](https://python.langchain.com/docs/modules/tools/)
- [Anthropic Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- 项目文档: `docs/multi-agent-and-tool-integration-plan.md`

---

**创建时间**: 2026-09-15  
**状态**: ✅ 模块结构就绪，核心协议定义完成，测试通过  
**下一步**: 与核心模块开发并行，逐步设计Tool Calling实现细节
