from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from ped_agent_server.model_gateway import DirectModelGateway


class FakeChatClient:
    def __init__(self, content: str) -> None:
        self.content = content
        self.prompts: list[str] = []

    async def ainvoke(self, prompt: str) -> SimpleNamespace:
        self.prompts.append(prompt)
        return SimpleNamespace(content=self.content, response_metadata={"model_name": "fake-chat"})


class FakeEmbeddingClient:
    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(text))] for text in texts]


class StructuredPayload(BaseModel):
    value: str


class FakeStructuredRunnable:
    def __init__(self, result):
        self.result = result

    async def ainvoke(self, prompt: str):
        return self.result


class FakeStructuredClient(FakeChatClient):
    def __init__(self, result) -> None:
        super().__init__("unused")
        self.result = result
        self.structured_kwargs: dict[str, object] = {}

    def with_structured_output(self, schema, **kwargs):
        self.schema = schema
        self.structured_kwargs = kwargs
        return FakeStructuredRunnable(self.result)


@pytest.mark.asyncio
async def test_direct_gateway_uses_fixed_answer_verify_and_embedding_roles() -> None:
    answer = FakeChatClient("answer")
    verifier = FakeChatClient("verified")
    gateway = DirectModelGateway(
        answer_client=answer,
        verify_client=verifier,
        embedding_client=FakeEmbeddingClient(),
    )

    generated = await gateway.generate("question")
    checked = await gateway.verify("draft")
    vectors = await gateway.embed(["one", "three"])

    assert generated.content == "answer"
    assert generated.model == "fake-chat"
    assert checked.content == "verified"
    assert vectors == [[3.0], [5.0]]
    assert gateway.verification_enabled is True


@pytest.mark.asyncio
async def test_direct_gateway_reports_disabled_verification() -> None:
    gateway = DirectModelGateway(
        answer_client=FakeChatClient("answer"),
        verify_client=None,
        embedding_client=FakeEmbeddingClient(),
    )

    assert gateway.verification_enabled is False
    with pytest.raises(RuntimeError, match="verification is disabled"):
        await gateway.verify("draft")


@pytest.mark.asyncio
async def test_direct_gateway_uses_configured_json_mode_for_both_roles() -> None:
    answer_raw = SimpleNamespace(
        content='{"value":"answer"}',
        response_metadata={"model_name": "deepseek-v4-flash"},
    )
    verify_raw = SimpleNamespace(
        content='{"value":"verified"}',
        response_metadata={"model_name": "deepseek-v4-pro"},
    )
    answer = FakeStructuredClient(
        {"raw": answer_raw, "parsed": {"value": "answer"}, "parsing_error": None}
    )
    verifier = FakeStructuredClient(
        {"raw": verify_raw, "parsed": {"value": "verified"}, "parsing_error": None}
    )
    gateway = DirectModelGateway(
        answer_client=answer,
        verify_client=verifier,
        embedding_client=FakeEmbeddingClient(),
        answer_structured_method="json_mode",
        verify_structured_method="json_mode",
    )

    generated, answer_output = await gateway.generate_structured(
        "Return answer JSON",
        StructuredPayload,
    )
    checked, verify_output = await gateway.verify_structured(
        "Return verification JSON",
        StructuredPayload,
    )

    assert generated == StructuredPayload(value="answer")
    assert checked == StructuredPayload(value="verified")
    assert answer_output.model == "deepseek-v4-flash"
    assert verify_output.model == "deepseek-v4-pro"
    assert answer.structured_kwargs == {"method": "json_mode", "include_raw": True}
    assert verifier.structured_kwargs == {"method": "json_mode", "include_raw": True}


@pytest.mark.asyncio
async def test_direct_gateway_omits_method_for_provider_native_default() -> None:
    raw = SimpleNamespace(
        content='{"value":"native"}',
        response_metadata={"model_name": "claude-test"},
    )
    answer = FakeStructuredClient(
        {"raw": raw, "parsed": {"value": "native"}, "parsing_error": None}
    )
    gateway = DirectModelGateway(
        answer_client=answer,
        verify_client=None,
        embedding_client=FakeEmbeddingClient(),
        answer_structured_method=None,
    )

    parsed, _ = await gateway.generate_structured("Return JSON", StructuredPayload)

    assert parsed == StructuredPayload(value="native")
    assert answer.structured_kwargs == {"include_raw": True}


@pytest.mark.asyncio
async def test_direct_gateway_returns_raw_output_when_native_parsing_fails() -> None:
    raw = SimpleNamespace(content="", response_metadata={"model_name": "deepseek-v4-flash"})
    answer = FakeStructuredClient({"raw": raw, "parsed": None, "parsing_error": ValueError("empty")})
    gateway = DirectModelGateway(
        answer_client=answer,
        verify_client=None,
        embedding_client=FakeEmbeddingClient(),
        answer_structured_method="json_mode",
    )

    parsed, model_output = await gateway.generate_structured("Return JSON", StructuredPayload)

    assert parsed is None
    assert model_output.content == ""
