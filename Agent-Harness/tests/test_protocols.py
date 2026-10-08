"""Tests for core protocols.

These tests verify the protocol definitions and Pydantic models.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ped_agent_harness.protocols import Tool, ToolCall, ToolResult


class TestTool:
    """Tests for Tool model."""

    def test_valid_tool(self) -> None:
        """Tool with valid schema should be created."""
        tool = Tool(
            name="search",
            description="Search for information",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
            },
        )
        assert tool.name == "search"
        assert tool.description == "Search for information"
        assert tool.parameters["type"] == "object"

    def test_tool_without_parameters(self) -> None:
        """Tool without parameters should be valid."""
        tool = Tool(
            name="get_time",
            description="Get current time",
        )
        assert tool.parameters == {}

    def test_tool_invalid_parameters_type(self) -> None:
        """Tool with non-object parameters should fail."""
        with pytest.raises(ValidationError):
            Tool(
                name="bad_tool",
                description="Bad tool",
                parameters={"type": "string"},  # Should be object
            )


class TestToolCall:
    """Tests for ToolCall model."""

    def test_valid_tool_call(self) -> None:
        """ToolCall with valid arguments should be created."""
        call = ToolCall(
            tool_call_id="call_123",
            tool_name="search",
            arguments={"query": "test"},
        )
        assert call.tool_call_id == "call_123"
        assert call.tool_name == "search"
        assert call.arguments["query"] == "test"

    def test_tool_call_without_arguments(self) -> None:
        """ToolCall without arguments should be valid."""
        call = ToolCall(
            tool_call_id="call_456",
            tool_name="get_time",
        )
        assert call.arguments == {}


class TestToolResult:
    """Tests for ToolResult model."""

    def test_successful_result(self) -> None:
        """Successful tool result should have is_error=False."""
        result = ToolResult(
            tool_call_id="call_123",
            content="Search results here",
        )
        assert result.tool_call_id == "call_123"
        assert result.content == "Search results here"
        assert result.is_error is False
        assert result.metadata == {}

    def test_error_result(self) -> None:
        """Error result should have is_error=True."""
        result = ToolResult(
            tool_call_id="call_456",
            content="Tool not found",
            is_error=True,
        )
        assert result.is_error is True

    def test_result_with_metadata(self) -> None:
        """Result can include metadata."""
        result = ToolResult(
            tool_call_id="call_789",
            content="Result",
            metadata={"duration_ms": 123, "tokens": 50},
        )
        assert result.metadata["duration_ms"] == 123
        assert result.metadata["tokens"] == 50
