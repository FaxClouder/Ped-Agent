# Agent-Harness Design Notes

*历史设计快照 · status: historical · 2026-10-04 整理；不代表当前实现或当前上游版本*

本文件保留原始正文，当前替代入口：[2026-10-04 研究文档](configuration-design.md)。旧测试、完成状态与环境结论只适用于原记录时点。


_Design decisions and roadmap for Agent-Harness module · updated 2026-09-15_

---

## 设计阶段划分

### Phase 1: Tool Calling 基础设施 (当前)

**目标**: 建立工具调用的核心能力

**核心组件**:
- ✅ `protocols.py`: Tool、ToolCall、ToolResult 定义
- 🚧 `tools/registry.py`: 工具注册器实现
- 🚧 `tools/executor.py`: 工具执行器实现
- 🚧 `tools/schema.py`: 参数验证

**设计决策**:
1. **Protocol优先**: 先定义接口契约，再实现具体类
2. **JSON Schema验证**: 使用标准JSON Schema验证参数
3. **异步优先**: 所有工具执行都是async，同步函数自动包装
4. **错误隔离**: 工具执行失败不应导致Agent崩溃

**待决策问题**:
- [ ] 工具超时机制：默认超时时间？可配置？
- [ ] 重试策略：是否支持工具执行重试？
- [ ] 并发控制：多个工具调用如何管理并发？

### Phase 2: Agent 抽象 (设计中)

**目标**: 统一Agent接口，与现有Agent模块集成

**核心组件**:
- ⏸️ `agents/base.py`: BaseAgent抽象类
- ⏸️ `agents/lifecycle.py`: 生命周期钩子

**设计考虑**:
1. **与现有Agent模块关系**:
   - Agent模块: 领域逻辑（证据图、引用验证）
   - Harness: 通用能力（工具调用、追踪）
   - 集成方式: Agent模块使用Harness提供的ToolRegistry

2. **状态管理**:
   - Agent应该是无状态的吗？
   - 如何处理多轮对话的上下文？

3. **工具访问**:
   - Agent如何声明需要哪些工具？
   - 工具权限控制？

### Phase 3: 运行时与追踪 (规划中)

**目标**: 提供可观测性和调试能力

**核心组件**:
- ⏸️ `runtime/session.py`: 会话管理
- ⏸️ `runtime/tracing.py`: 执行追踪
- ⏸️ `runtime/metrics.py`: 指标收集

**设计考虑**:
1. **追踪粒度**: 追踪到什么级别？
   - 工具调用
   - LLM调用
   - Agent执行阶段

2. **持久化**: 追踪数据存储在哪里？
   - 内存（开发）
   - 文件（科研可复现）
   - 数据库（生产，如需要）

3. **性能影响**: 追踪开销可接受吗？

### Phase 4: 多Agent编排 (未来)

**触发条件**: 仅在有明确需求时实现

**核心组件**:
- ⏸️ `orchestration/coordinator.py`
- ⏸️ `orchestration/communication.py`
- ⏸️ `orchestration/strategies.py`

**设计考虑**:
- 什么场景需要多Agent？
- 如何保证可复现性？
- 调试复杂度是否可控？

---

## 接口设计原则

### 1. Protocol优先

所有核心抽象首先定义为Protocol：
```python
@runtime_checkable
class ToolRegistry(Protocol):
    def register(...) -> None: ...
    def get_tools(...) -> list[Tool]: ...
    async def execute(...) -> ToolResult: ...
```

**优点**:
- 接口与实现解耦
- 支持多种实现
- 便于测试（mock）

### 2. Pydantic验证

所有数据结构使用Pydantic：
```python
class Tool(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any]
```

**优点**:
- 自动验证
- 序列化支持
- 类型安全

### 3. 异步优先

所有执行接口都是async：
```python
async def execute(self, tool_call: ToolCall) -> ToolResult
```

**理由**:
- 工具可能涉及I/O（检索、API调用）
- 支持并发执行
- 与现有Agent模块一致

---

## 与现有模块的集成

### Agent 模块集成路径

```python
# 当前 Agent/src/ped_research_agent/evidence_graph.py
class EvidenceGraph:
    def __init__(
        self,
        model_gateway: ModelGateway,
        local_retriever: LocalEvidenceRetriever,
        external_searcher: ExternalEvidenceSearcher,
    ):
        ...

# 未来集成 Agent-Harness 后
class EvidenceGraph:
    def __init__(
        self,
        model_gateway: ModelGateway,
        tool_registry: ToolRegistry,  # 来自Harness
    ):
        # LocalEvidenceRetriever 注册为工具
        # ExternalEvidenceSearcher 注册为工具
        ...
```

### Contracts 模块下沉

当接口稳定后，这些定义可能下沉到Contracts：
- `Tool`
- `ToolCall`
- `ToolResult`

时机：Phase 1 完成，Agent模块集成验证后

---

## 实现优先级

### 立即实现（与核心模块并行）
1. ✅ 模块结构创建
2. ✅ `protocols.py` 核心接口定义
3. 🚧 `tools/registry.py` 基础实现
4. 🚧 `tools/executor.py` 基础实现
5. 🚧 单元测试

### 核心模块稳定后实现
6. ⏸️ 在experiments/验证实际效果
7. ⏸️ Agent模块集成
8. ⏸️ 工具参数验证增强
9. ⏸️ 错误处理完善

### 按需实现
10. ⏸️ Agent抽象（如有必要）
11. ⏸️ 运行时追踪（用于调试）
12. ⏸️ 多Agent编排（需求驱动）

---

## 开放问题

### 技术决策待定

1. **工具注册方式**:
   ```python
   # 方式1: 装饰器
   @registry.register(name="...", description="...", parameters={...})
   async def my_tool(arg1: str): ...
   
   # 方式2: 显式调用
   registry.register("my_tool", my_tool, description="...", parameters={...})
   ```
   → 倾向方式2，更显式

2. **参数验证库选择**:
   - JSON Schema + jsonschema库？
   - Pydantic动态模型？
   - 保持简单，先用dict验证？

3. **工具执行隔离**:
   - 需要沙箱吗？（科研环境可能不需要）
   - 超时控制？
   - 资源限制？

### 设计讨论点

1. **ToolRegistry是否应该单例**？
   - 单例：全局工具池，简单
   - 非单例：每个Agent独立工具集，灵活

2. **工具如何访问Agent状态**？
   - 通过context参数传递？
   - 工具应该无状态吗？

3. **错误处理策略**：
   - 工具失败后Agent如何继续？
   - 是否支持fallback工具？

---

## 参考实现

### LangChain工具系统
```python
from langchain.tools import BaseTool

class CustomTool(BaseTool):
    name = "search"
    description = "Search for information"
    
    def _run(self, query: str) -> str:
        return search(query)
```

**借鉴**:
- 工具定义结构
- 参数schema格式

**不采用**:
- 继承BaseTool（我们用Protocol）
- _run/_arun分离（我们只用async）

### Anthropic Tool Use
```json
{
  "name": "get_weather",
  "description": "Get weather data",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": {"type": "string"}
    },
    "required": ["location"]
  }
}
```

**借鉴**:
- JSON Schema参数定义
- Tool定义格式

---

## 测试策略

### 单元测试
- 每个组件独立测试
- Mock外部依赖
- 异步测试（pytest-asyncio）

### 集成测试
- ToolRegistry + ToolExecutor
- 实际工具执行
- 错误场景

### 端到端测试
- 在experiments/中验证
- 真实Agent场景
- 性能基准

---

## 文档计划

### 开发文档
- [ ] Tool开发指南
- [ ] 如何注册工具
- [ ] 参数schema编写规范

### API文档
- [ ] Protocol接口说明
- [ ] 使用示例
- [ ] 最佳实践

### 集成文档
- [ ] 与Agent模块集成
- [ ] 迁移指南

---

**维护者**: 项目团队  
**状态**: Living Document  
**更新频率**: 每次设计决策后
