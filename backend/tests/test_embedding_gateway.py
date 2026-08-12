from pathlib import Path
from types import SimpleNamespace

import pytest

from ped_agent_server.embedding_gateway import (
    LocalBGEM3EmbeddingGateway,
    configured_embedding_fingerprint,
    validate_embedding_environment,
)
from ped_agent_server.settings import EmbeddingSettings


class FakeVectors(list):
    def tolist(self):
        return list(self)


class FakeSentenceTransformer:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def encode(self, texts, **kwargs):
        self.calls.append({"texts": texts, **kwargs})
        return FakeVectors([[1.0, 0.0], [0.0, 1.0]])


@pytest.mark.asyncio
async def test_local_bge_gateway_runs_lazy_embedding_off_the_event_loop(
    tmp_path: Path,
) -> None:
    model = FakeSentenceTransformer()
    settings = EmbeddingSettings(
        model="BAAI/test-bge-m3",
        device="cuda",
        dimensions=2,
        batch_size=8,
    )
    gateway = LocalBGEM3EmbeddingGateway(
        settings,
        repo_root=tmp_path,
        model_loader=lambda: model,
    )

    vectors = await gateway.embed(["pedestrian flow", "crowd density"])

    assert vectors == [[1.0, 0.0], [0.0, 1.0]]
    assert model.calls == [
        {
            "texts": ["pedestrian flow", "crowd density"],
            "batch_size": 8,
            "normalize_embeddings": True,
            "convert_to_numpy": True,
            "show_progress_bar": False,
        }
    ]


@pytest.mark.asyncio
async def test_local_bge_gateway_rejects_unexpected_dimensions(tmp_path: Path) -> None:
    settings = EmbeddingSettings(dimensions=1024)
    gateway = LocalBGEM3EmbeddingGateway(
        settings,
        repo_root=tmp_path,
        model_loader=FakeSentenceTransformer,
    )

    with pytest.raises(RuntimeError, match="dimension mismatch"):
        await gateway.embed(["one", "two"])


def test_local_cuda_validation_fails_closed_without_gpu(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "ped_agent_server.embedding_gateway.importlib.util.find_spec",
        lambda name: object() if name == "sentence_transformers" else None,
    )
    monkeypatch.setitem(
        __import__("sys").modules,
        "torch",
        SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: False)),
    )

    with pytest.raises(RuntimeError, match="no CUDA GPU"):
        validate_embedding_environment(EmbeddingSettings())


def test_embedding_fingerprint_changes_with_precision_and_protocol() -> None:
    local = EmbeddingSettings()
    cpu = local.model_copy(update={"device": "cpu", "use_fp16": False})
    remote = local.model_copy(
        update={
            "protocol": "openai_compatible",
            "api_key": "secret",
            "base_url": "https://embedding.example/v1",
        }
    )

    assert configured_embedding_fingerprint(local) != configured_embedding_fingerprint(cpu)
    assert configured_embedding_fingerprint(local) != configured_embedding_fingerprint(remote)
