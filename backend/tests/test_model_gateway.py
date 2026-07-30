from types import SimpleNamespace

import pytest

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

