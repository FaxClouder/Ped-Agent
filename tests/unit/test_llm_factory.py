from __future__ import annotations

import sys
import types

from ped_agent.llm.factory import build_chat_model


class FakeChatAnthropic:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class FakeChatOpenAI:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def test_builds_claude_provider(monkeypatch):
    module = types.ModuleType("langchain_anthropic")
    module.ChatAnthropic = FakeChatAnthropic
    monkeypatch.setitem(sys.modules, "langchain_anthropic", module)

    model = build_chat_model(
        {
            "llm": {
                "default_provider": "claude",
                "providers": {
                    "claude": {
                        "model": "claude-sonnet-4-20250514",
                        "api_key": "test-key",
                        "max_tokens": 1024,
                    }
                },
            }
        }
    )

    assert isinstance(model, FakeChatAnthropic)
    assert model.kwargs["model"] == "claude-sonnet-4-20250514"
    assert model.kwargs["api_key"] == "test-key"


def test_builds_local_openai_compatible_provider(monkeypatch):
    module = types.ModuleType("langchain_openai")
    module.ChatOpenAI = FakeChatOpenAI
    monkeypatch.setitem(sys.modules, "langchain_openai", module)

    model = build_chat_model(
        {
            "llm": {
                "default_provider": "local",
                "providers": {
                    "local": {
                        "model": "qwen2.5:72b",
                        "base_url": "http://localhost:11434",
                    }
                },
            }
        }
    )

    assert isinstance(model, FakeChatOpenAI)
    assert model.kwargs["api_key"] == "local"
    assert model.kwargs["base_url"] == "http://localhost:11434"
