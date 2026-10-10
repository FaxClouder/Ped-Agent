"""Core protocols for Agent-Harness.

This module defines the fundamental abstractions for tools, agents, and execution.
These protocols serve as contracts between components and will eventually stabilize
into the Contracts module.

Status (2026-10-07): superseded by ``ped_agent_harness.contracts`` and the executor modules;
kept only for compatibility with older references and scheduled for removal. New code must not
import from this module. See ``docs/contract-and-controller-design.md`` §1.6 for the mapping.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field


# ==============================================================================
# Tool Protocols
# ==============================================================================


class Tool(BaseModel):
    """Tool definition following OpenAI/Anthropic function calling schema.

    A tool represents a capability that an agent can invoke. The parameters field
    follows JSON Schema format to describe expected inputs.

    Examples:
        >>> tool = Tool(
        ...     name="search_knowledge",
        ...     description="Search the local knowledge base for relevant documents",
        ...     parameters={
        ...         "type": "object",
        ...         "properties": {
        ...             "query": {"type": "string", "description": "Search query"},
        ...             "top_k": {"type": "integer", "default": 5},
        ...         },
        ...         "required": ["query"],
        ...     },
        ... )
    """

    name: str = Field(..., description="Unique tool identifier")
    description: str = Field(..., description="Human-readable description for LLM")
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="JSON Schema describing tool parameters",
    )

    def model_post_init(self, __context: Any) -> None:
        """Validate that parameters is a valid JSON Schema object."""
        if self.parameters and self.parameters.get("type") != "object":
            msg = "Tool parameters must be a JSON Schema object type"
            raise ValueError(msg)


class ToolCall(BaseModel):
    """A request to invoke a tool with specific arguments.

    This is returned by the LLM when it decides to use a tool.
    """

    tool_call_id: str = Field(..., description="Unique ID for this invocation")
    tool_name: str = Field(..., description="Name of the tool to invoke")
    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments matching the tool's parameter schema",
    )


class ToolResult(BaseModel):
    """Result of executing a tool call.

    The content field contains the tool's output, which will be fed back to the LLM.
    """

    tool_call_id: str = Field(..., description="ID from the original ToolCall")
    content: str = Field(..., description="Tool execution result as string")
    is_error: bool = Field(default=False, description="Whether execution failed")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata (timing, cost, etc.)",
    )


# ==============================================================================
# Tool Registry Protocol
# ==============================================================================


@runtime_checkable
class ToolRegistry(Protocol):
    """Protocol for tool registration and discovery.

    Implementations manage a collection of tools and provide methods to:
    - Register new tools with their execution functions
    - Retrieve tool definitions for LLM consumption
    - Execute tool calls with argument validation
    """

    def register(
        self,
        name: str,
        func: Any,  # Callable[..., Any] or async callable
        description: str,
        parameters: dict[str, Any],
    ) -> None:
        """Register a tool with its execution function.

        Args:
            name: Unique tool identifier
            func: Callable (sync or async) to execute when tool is invoked
            description: Human-readable description for LLM
            parameters: JSON Schema describing function parameters
        """
        ...

    def get_tools(self) -> list[Tool]:
        """Retrieve all registered tool definitions.

        Returns:
            List of Tool objects suitable for LLM function calling
        """
        ...

    async def execute(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call with validation.

        Args:
            tool_call: The tool invocation request

        Returns:
            ToolResult with execution output or error
        """
        ...


# ==============================================================================
# Agent Protocols (Planned)
# ==============================================================================


class AgentInput(BaseModel):
    """Input to an agent execution (planned)."""

    query: str
    context: dict[str, Any] = Field(default_factory=dict)


class AgentOutput(BaseModel):
    """Output from an agent execution (planned)."""

    result: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


@runtime_checkable
class Agent(Protocol):
    """Protocol for agent implementations (planned).

    An agent is a stateless execution unit that:
    - Takes an input and context
    - May use tools to gather information
    - Produces an output
    """

    async def run(self, input: AgentInput) -> AgentOutput:
        """Execute the agent's logic.

        Args:
            input: The agent input with query and context

        Returns:
            AgentOutput with result and metadata
        """
        ...


# ==============================================================================
# Execution Context (Planned)
# ==============================================================================


class ExecutionContext(BaseModel):
    """Context for agent/tool execution (planned).

    Tracks session state, tool usage, and execution metadata.
    """

    session_id: str
    parent_call_id: str | None = None
    max_tool_calls: int = Field(default=10, description="Circuit breaker")
    tool_call_count: int = Field(default=0, description="Current tool usage")
    metadata: dict[str, Any] = Field(default_factory=dict)


# ==============================================================================
# Future: Multi-Agent Protocols
# ==============================================================================

# These will be defined when multi-agent orchestration is needed:
# - CoordinatorProtocol
# - AgentCommunicationProtocol
# - OrchestrationStrategy
