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


class FakeStructuredClient(FakeChatClient):
    def with_structured_output(self, schema):
        self.schema = schema
        return self

    async def ainvoke(self, prompt: str):
        self.prompts.append(prompt)
        return {"value": "native"}


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
async def test_direct_gateway_uses_provider_native_structured_output() -> None:
    answer = FakeStructuredClient("unused")
    verifier = FakeStructuredClient("unused")
    gateway = DirectModelGateway(
        answer_client=answer,
        verify_client=verifier,
        embedding_client=FakeEmbeddingClient(),
    )

    generated, answer_model = await gateway.generate_structured("prompt", StructuredPayload)
    checked, verify_model = await gateway.verify_structured("prompt", StructuredPayload)

    assert generated == StructuredPayload(value="native")
    assert checked == StructuredPayload(value="native")
    assert answer_model == "unknown"
    assert verify_model == "unknown"
