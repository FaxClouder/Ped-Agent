# 多Agent编排与Tool Calling集成方案

*历史设计快照 · status: historical · 2026-10-04 整理；不代表当前实现或当前上游版本*

本文件保留原始正文，当前替代入口：[2026-10-04 研究文档](../Agent-Harness/docs/agentic-research-plan.md)。旧测试、完成状态与环境结论只适用于原记录时点。


_Multi-agent orchestration and tool calling integration strategy · 2026-09-15_

---

## 当前能力盘点

### ✅ 已有实现

#### 1. 单Agent编排 - LangGraph StateGraph
**位置**: `Agent/src/ped_research_agent/evidence_graph.py`

当前Agent模块使用LangGraph的`StateGraph`构建了单Agent的证据收集工作流：

```python
# 当前架构
StateGraph(EvidenceState)
  → load_conversation
  → preflight_local_retrieval
  → assess_evidence
  → external_search (条件)
  → normalize_evidence
  → generate_draft
  → validate_rules
  → semantic_verify
  → revise_once (循环)
  → final_persist
```

**特点**:
- ✅ 状态机编排
- ✅ 条件分支
- ✅ 多轮修订循环
- ❌ 不支持多Agent协作
- ❌ 没有Tool Calling能力

#### 2. 模型抽象 - ModelGateway Protocol
**位置**: `Agent/src/ped_research_agent/ports.py`, `model_gateway.py`

```python
class ModelGateway(Protocol):
    async def generate(self, prompt: str) -> ModelOutput
    async def verify(self, prompt: str) -> ModelOutput
    async def generate_structured(self, prompt: str, schema: type[BaseModel]) -> ...
```

**特点**:
- ✅ 统一模型接口
- ✅ Structured Output支持
- ✅ Anthropic/OpenAI适配
- ❌ 没有Tool Calling接口
- ❌ 没有Function Calling支持

#### 3. 端口抽象
- `LocalEvidenceRetriever`: 本地证据检索
- `ExternalEvidenceSearcher`: 外部搜索

这些实际上是"工具"的雏形，但不是标准的LLM Tool Calling。

---

## 能力缺口分析

### ❌ 缺失能力

| 能力类别 | 当前状态 | 研究需求 |
|---------|---------|---------|
| **多Agent协作** | 无 | 中 - 可用于复杂分析任务分解 |
| **LLM Tool Calling** | 无 | 高 - 增强Agent工具使用能力 |
| **Agent Harness** | 无 | 中 - 统一Agent运行、监控、评测 |
| **Agent间通信** | 无 | 低 - 当前单Agent足够 |
| **工具注册机制** | 无 | 高 - 动态扩展工具能力 |
| **工具执行沙箱** | 无 | 低 - 科研环境可控 |

---

## 集成策略建议

### 方案对比

| 维度 | 新建独立模块 | 扩展Agent模块 | 实验目录探索 |
|-----|------------|--------------|-------------|
| **适用场景** | 通用Agent框架 | Agent内部能力增强 | 探索性多Agent研究 |
| **架构影响** | 新增一级模块 | 模块内扩展 | 零架构变更 |
| **复用性** | 高 - 可被其他项目用 | 中 - 仅本项目Agent | 低 - 实验性质 |
| **维护成本** | 高 - 独立维护 | 中 - 随Agent演进 | 低 - 可丢弃 |
| **成熟度要求** | 高 - 需稳定API | 中 - 随迭代稳定 | 低 - 快速验证 |

### 推荐策略：**渐进式集成**

```text
Phase 1: 实验验证 (experiments/)
  └─ 验证多Agent协作模式
  └─ 测试Tool Calling效果
  └─ 评估性能与可复现性

Phase 2: Agent模块扩展 (Agent/)
  └─ 扩展ModelGateway增加Tool Calling
  └─ 引入LangGraph的multi-agent支持
  └─ 增强ports.py的工具抽象

Phase 3: 独立模块提取 (可选)
  └─ 如需跨项目复用，提取为独立harness模块
  └─ 否则保持在Agent模块内
```

---

## 具体实施方案

### 🎯 方案A：扩展Agent模块（推荐用于工具能力）

**适用于**: Tool Calling、工具注册、单Agent增强

#### A1. 扩展ModelGateway支持Tool Calling

```python
# Agent/src/ped_research_agent/ports.py

class Tool(BaseModel):
    """工具定义"""
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema
    
class ToolCall(BaseModel):
    """工具调用"""
    tool_name: str
    arguments: dict[str, Any]
    
class ToolResult(BaseModel):
    """工具执行结果"""
    tool_call_id: str
    content: str
    is_error: bool = False

class ModelGateway(Protocol):
    # 现有方法...
    
    async def generate_with_tools(
        self,
        prompt: str,
        tools: list[Tool],
        tool_choice: Literal["auto", "required", "none"] = "auto",
    ) -> tuple[str | None, list[ToolCall], ModelOutput]:
        """支持工具调用的生成"""
        ...
```

#### A2. 工具注册器

```python
# Agent/src/ped_research_agent/tools.py

class ToolRegistry:
    """工具注册与执行"""
    
    def __init__(self):
        self._tools: dict[str, Callable] = {}
        self._schemas: dict[str, Tool] = {}
    
    def register(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: dict[str, Any],
    ):
        """注册工具"""
        self._tools[name] = func
        self._schemas[name] = Tool(
            name=name,
            description=description,
            parameters=parameters,
        )
    
    async def execute(
        self,
        tool_call: ToolCall,
    ) -> ToolResult:
        """执行工具调用"""
        func = self._tools.get(tool_call.tool_name)
        if not func:
            return ToolResult(
                tool_call_id=tool_call.tool_call_id,
                content=f"Unknown tool: {tool_call.tool_name}",
                is_error=True,
            )
        try:
            result = await func(**tool_call.arguments)
            return ToolResult(
                tool_call_id=tool_call.tool_call_id,
                content=str(result),
            )
        except Exception as e:
            return ToolResult(
                tool_call_id=tool_call.tool_call_id,
                content=str(e),
                is_error=True,
            )
    
    def get_tools(self) -> list[Tool]:
        """获取所有工具定义"""
        return list(self._schemas.values())
```

#### A3. 内置工具定义

```python
# Agent/src/ped_research_agent/builtin_tools.py

def register_builtin_tools(registry: ToolRegistry):
    """注册内置工具"""
    
    # 本地证据检索工具
    @registry.register(
        name="retrieve_local_evidence",
        description="从本地知识库检索相关证据",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "检索查询"},
                "top_k": {"type": "integer", "description": "返回结果数量", "default": 5},
            },
            "required": ["query"],
        },
    )
    async def retrieve_local_evidence(query: str, top_k: int = 5):
        # 调用LocalEvidenceRetriever
        ...
    
    # 外部学术搜索工具
    @registry.register(
        name="search_academic",
        description="搜索学术文献数据库",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "default": 3},
            },
            "required": ["query"],
        },
    )
    async def search_academic(query: str, max_results: int = 3):
        # 调用ExternalEvidenceSearcher
        ...
    
    # 计算工具
    @registry.register(
        name="calculate",
        description="执行数学计算",
        parameters={
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "数学表达式"},
            },
            "required": ["expression"],
        },
    )
    async def calculate(expression: str):
        # 安全计算逻辑
        ...
```

**优点**:
- ✅ 最小架构变更
- ✅ 与现有Agent工作流自然集成
- ✅ 保持模块边界清晰

**缺点**:
- ⚠️ 仅限Agent模块使用
- ⚠️ 不适合通用Agent框架

---

### 🎯 方案B：新建Agent-Harness模块（推荐用于通用框架）

**适用于**: 多Agent编排、通用Agent运行时、跨项目复用

#### 目录结构

```text
Agent-Harness/
├── src/ped_agent_harness/
│   ├── agents/
│   │   ├── base.py           # BaseAgent抽象
│   │   ├── registry.py       # Agent注册
│   │   └── research_agent.py # 科研Agent实现
│   ├── orchestration/
│   │   ├── coordinator.py    # 多Agent协调器
│   │   ├── communication.py  # Agent间通信
│   │   └── strategies.py     # 编排策略
│   ├── tools/
│   │   ├── registry.py       # 工具注册
│   │   ├── executor.py       # 工具执行器
│   │   └── sandbox.py        # 执行沙箱
│   ├── runtime/
│   │   ├── session.py        # 运行会话
│   │   ├── monitor.py        # 监控指标
│   │   └── tracing.py        # 执行追踪
│   └── evaluation/
│       ├── metrics.py        # 评测指标
│       └── benchmark.py      # 基准测试
├── examples/
│   ├── single_agent.py
│   └── multi_agent_research.py
└── tests/
```

#### 核心抽象

```python
# Agent-Harness/src/ped_agent_harness/agents/base.py

class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(
        self,
        name: str,
        model_gateway: ModelGateway,
        tool_registry: ToolRegistry,
    ):
        self.name = name
        self.model_gateway = model_gateway
        self.tool_registry = tool_registry
    
    @abstractmethod
    async def run(
        self,
        input: AgentInput,
        context: AgentContext,
    ) -> AgentOutput:
        """执行Agent任务"""
        ...
    
    async def use_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """使用工具"""
        return await self.tool_registry.execute(
            ToolCall(tool_name=tool_name, arguments=arguments)
        )

# Agent-Harness/src/ped_agent_harness/orchestration/coordinator.py

class MultiAgentCoordinator:
    """多Agent协调器"""
    
    def __init__(self, strategy: OrchestrationStrategy):
        self.strategy = strategy
        self.agents: dict[str, BaseAgent] = {}
    
    def register_agent(self, agent: BaseAgent):
        """注册Agent"""
        self.agents[agent.name] = agent
    
    async def coordinate(
        self,
        task: Task,
        session: Session,
    ) -> CoordinationResult:
        """协调多个Agent完成任务"""
        return await self.strategy.execute(
            task=task,
            agents=self.agents,
            session=session,
        )

# 编排策略示例
class SequentialStrategy(OrchestrationStrategy):
    """顺序执行策略"""
    async def execute(self, task, agents, session):
        results = []
        for agent_name in task.agent_sequence:
            agent = agents[agent_name]
            result = await agent.run(task.input, session.context)
            results.append(result)
        return CoordinationResult(results=results)

class ParallelStrategy(OrchestrationStrategy):
    """并行执行策略"""
    async def execute(self, task, agents, session):
        tasks = [
            agents[name].run(task.input, session.context)
            for name in task.agent_names
        ]
        results = await asyncio.gather(*tasks)
        return CoordinationResult(results=results)
```

**优点**:
- ✅ 通用性强，可跨项目复用
- ✅ 支持复杂多Agent编排
- ✅ 完整的监控和评测能力

**缺点**:
- ⚠️ 架构变更较大
- ⚠️ 维护成本高
- ⚠️ 当前项目可能用不到这么重

---

### 🎯 方案C：实验目录探索（推荐用于前期验证）

**适用于**: 快速验证、探索性研究、不确定性高的能力

#### 目录结构

```text
experiments/
├── multi-agent-research/
│   ├── README.md
│   ├── coordinator.py        # 简单协调逻辑
│   ├── research_agents.py    # 多个专门Agent
│   ├── tool_calling_demo.py  # Tool Calling示例
│   └── results/
│       ├── run_2026_09_15.jsonl
│       └── metrics.csv
└── tool-enhanced-qa/
    ├── README.md
    ├── qa_with_tools.py
    └── results/
```

#### 示例：多Agent文献分析实验

```python
# experiments/multi-agent-research/research_agents.py

class LiteratureReviewerAgent:
    """文献审查Agent"""
    async def review(self, paper_ids: list[str]) -> ReviewReport:
        # 调用Knowledge-Base检索
        # 调用LLM分析
        ...

class MethodExtractorAgent:
    """方法提取Agent"""
    async def extract_methods(self, paper_content: str) -> list[Method]:
        # 使用structured output提取方法
        ...

class EvidenceSynthesizerAgent:
    """证据综合Agent"""
    async def synthesize(
        self,
        reviews: list[ReviewReport],
        methods: list[Method],
    ) -> SynthesisReport:
        # 综合多个Agent的结果
        ...

# experiments/multi-agent-research/coordinator.py

async def multi_agent_research_pipeline(query: str):
    """多Agent研究流水线"""
    
    # Step 1: 文献审查（多个并行）
    reviewer1 = LiteratureReviewerAgent(focus="empirical")
    reviewer2 = LiteratureReviewerAgent(focus="theoretical")
    
    reviews = await asyncio.gather(
        reviewer1.review(query),
        reviewer2.review(query),
    )
    
    # Step 2: 方法提取
    extractor = MethodExtractorAgent()
    methods = []
    for review in reviews:
        paper_methods = await extractor.extract_methods(review.content)
        methods.extend(paper_methods)
    
    # Step 3: 证据综合
    synthesizer = EvidenceSynthesizerAgent()
    final_report = await synthesizer.synthesize(reviews, methods)
    
    return final_report
```

**优点**:
- ✅ 零架构变更
- ✅ 快速验证想法
- ✅ 灵活度最高
- ✅ 失败成本低

**缺点**:
- ⚠️ 不可复用
- ⚠️ 缺乏系统性
- ⚠️ 需要后续重构

---

## 推荐实施路线

### 阶段1：实验验证（1-2周）

**目标**: 验证多Agent和Tool Calling对研究工作的价值

**位置**: `experiments/agent-capabilities-exploration/`

**内容**:
1. 实现简单的Tool Calling Demo
2. 尝试2-3个Agent协作完成文献分析任务
3. 评估性能提升和复杂度增加

**产物**:
- 实验报告
- 性能对比数据
- 决策依据：是否值得集成

### 阶段2：能力扩展（2-3周）

**如果验证有价值，选择方案A或B**:

#### 路径A：轻量集成（推荐）
- 扩展`Agent/src/ped_research_agent/`
- 增加`tools.py`, `builtin_tools.py`
- 扩展`model_gateway.py`支持Tool Calling
- 在`evidence_graph.py`中集成工具使用

#### 路径B：独立模块（如需跨项目复用）
- 创建`Agent-Harness/`模块
- 实现BaseAgent、ToolRegistry、MultiAgentCoordinator
- `Agent/`模块依赖`Agent-Harness/`
- 更新`pyproject.toml` workspace配置

### 阶段3：文档与测试（1周）

**文档**:
- 更新`module-division-and-design.md`
- 编写工具开发指南
- 记录多Agent编排模式

**测试**:
- 工具注册与执行测试
- Tool Calling集成测试
- 多Agent协作测试（如适用）

---

## 架构决策记录

### ADR-001: Tool Calling集成方式

**决策**: 采用方案A（扩展Agent模块）

**理由**:
1. 当前项目是科研工程，不追求通用性
2. 工具能力主要服务于证据收集Agent
3. 避免过度工程化
4. 保持模块边界清晰

**后果**:
- 工具能力与Agent模块绑定
- 如需跨项目复用，需要后续重构
- 维护成本可控

### ADR-002: 多Agent编排时机

**决策**: 暂不引入，先在experiments验证

**理由**:
1. 当前单Agent工作流已经足够
2. 多Agent增加系统复杂度
3. 可复现性要求高，多Agent调试困难
4. 性能收益不明确

**后果**:
- 保持当前架构稳定
- 探索性研究在experiments进行
- 未来如需要，再基于实验结果决策

---

## 相关资源

### LangGraph多Agent支持
- [LangGraph Multi-Agent](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)
- [Agent Supervisor Pattern](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/)

### Tool Calling实现
- [Anthropic Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

### Agent Frameworks参考
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [AutoGen](https://microsoft.github.io/autogen/)
- [CrewAI](https://docs.crewai.com/)

---

## 后续行动

### 立即行动
1. ✅ 在`experiments/`创建tool-calling验证实验
2. ⏸️  评估Tool Calling对证据收集的价值
3. ⏸️  决定是否采用方案A扩展Agent模块

### 待观察
- LangGraph新版本的多Agent能力演进
- 社区最佳实践
- 项目实际需求变化
