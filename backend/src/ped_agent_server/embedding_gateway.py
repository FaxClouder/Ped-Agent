from __future__ import annotations

import asyncio
import importlib.util
from collections.abc import Callable
from pathlib import Path
from typing import Any

from langchain_openai import OpenAIEmbeddings
from ped_knowledge.indexing import embedding_fingerprint

from ped_agent_server.settings import EmbeddingSettings


class LocalBGEM3EmbeddingGateway:
    """Lazy local dense embedding adapter backed by Sentence Transformers."""

    def __init__(
        self,
        settings: EmbeddingSettings,
        *,
        repo_root: Path,
        model_loader: Callable[[], Any] | None = None,
    ) -> None:
        self.settings = settings
        self.cache_dir = _resolve_path(repo_root, settings.cache_dir)
        self._model_loader = model_loader or self._load_model
        self._model: Any | None = None
        self._lock = asyncio.Lock()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        async with self._lock:
            return await asyncio.to_thread(self._embed_sync, texts)

    def _embed_sync(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(
            texts,
            batch_size=self.settings.batch_size,
            normalize_embeddings=self.settings.normalize_embeddings,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        payload = vectors.tolist() if hasattr(vectors, "tolist") else vectors
        normalized = [[float(value) for value in vector] for vector in payload]
        _validate_dimensions(normalized, self.settings.dimensions)
        return normalized

    @property
    def model(self) -> Any:
        if self._model is None:
            self._model = self._model_loader()
        return self._model

    def _load_model(self) -> Any:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is required for local BGE-M3 embeddings"
            ) from exc

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        model = SentenceTransformer(
            self.settings.model,
            device=self.settings.device,
            cache_folder=str(self.cache_dir),
            revision=self.settings.revision,
        )
        if self.settings.use_fp16:
            model.half()
        return model


class OpenAIEmbeddingGateway:
    def __init__(self, settings: EmbeddingSettings) -> None:
        kwargs: dict[str, Any] = {
            "model": settings.model,
            "api_key": settings.api_key.get_secret_value() if settings.api_key else None,
            "request_timeout": settings.timeout_seconds,
            "max_retries": settings.max_retries,
        }
        if settings.base_url:
            kwargs["base_url"] = settings.base_url
        if settings.dimensions:
            kwargs["dimensions"] = settings.dimensions
        self.client = OpenAIEmbeddings(**kwargs)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return await self.client.aembed_documents(texts)


def build_embedding_gateway(
    settings: EmbeddingSettings,
    *,
    repo_root: Path,
) -> LocalBGEM3EmbeddingGateway | OpenAIEmbeddingGateway:
    validate_embedding_environment(settings)
    if settings.protocol == "local_bge_m3":
        return LocalBGEM3EmbeddingGateway(settings, repo_root=repo_root)
    return OpenAIEmbeddingGateway(settings)


def validate_embedding_environment(settings: EmbeddingSettings) -> None:
    if settings.protocol != "local_bge_m3":
        return
    if importlib.util.find_spec("sentence_transformers") is None:
        raise RuntimeError(
            "sentence-transformers is required; synchronize the backend environment"
        )
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError("PyTorch is required for local BGE-M3 embeddings") from exc

    if settings.device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA is the configured embedding device but no CUDA GPU is available; "
            "set PED_AGENT_EMBEDDING__DEVICE=cpu and "
            "PED_AGENT_EMBEDDING__USE_FP16=false for an explicit CPU fallback"
        )
    if settings.use_fp16 and not settings.device.startswith("cuda"):
        raise RuntimeError("FP16 local embeddings require a CUDA device")


def configured_embedding_fingerprint(settings: EmbeddingSettings) -> str:
    is_local = settings.protocol == "local_bge_m3"
    return embedding_fingerprint(
        protocol=settings.protocol,
        model=settings.model,
        revision=settings.revision if is_local else None,
        base_url=settings.base_url,
        dimensions=settings.dimensions,
        normalize_embeddings=settings.normalize_embeddings if is_local else None,
        use_fp16=settings.use_fp16 if is_local else None,
    )


def _validate_dimensions(vectors: list[list[float]], expected: int | None) -> None:
    if expected is None:
        return
    mismatched = [len(vector) for vector in vectors if len(vector) != expected]
    if mismatched:
        raise RuntimeError(
            f"embedding dimension mismatch: expected {expected}, got {mismatched[0]}"
        )


def _resolve_path(repo_root: Path, configured: Path) -> Path:
    return configured if configured.is_absolute() else repo_root / configured


__all__ = [
    "LocalBGEM3EmbeddingGateway",
    "OpenAIEmbeddingGateway",
    "build_embedding_gateway",
    "configured_embedding_fingerprint",
    "validate_embedding_environment",
]
