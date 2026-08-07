"""Cross-encoder reranking adapters with bounded in-process score caching."""

from __future__ import annotations

import asyncio
import hashlib
from collections import OrderedDict
from collections.abc import Callable
from typing import Any

from ped_knowledge.contracts import RerankCandidate, RerankScore


class CrossEncoderReranker:
    """Lazy FlagEmbedding Cross-Encoder adapter.

    Model loading is delayed until the first request so deployments that configure RRF-only
    retrieval do not pay the import or memory cost.
    """

    def __init__(
        self,
        model_name: str,
        *,
        use_fp16: bool = True,
        cache_size: int = 4096,
        model_factory: Callable[[str, bool], Any] | None = None,
    ) -> None:
        self.model_name = model_name
        self.use_fp16 = use_fp16
        self.cache_size = cache_size
        self._model_factory = model_factory or _default_model_factory
        self._model: Any | None = None
        self._cache: OrderedDict[str, float] = OrderedDict()

    async def rerank(
        self,
        query: str,
        candidates: list[RerankCandidate],
    ) -> list[RerankScore]:
        missing = [item for item in candidates if self._cache_key(query, item) not in self._cache]
        if missing:
            scores = await asyncio.to_thread(self._compute_scores, query, missing)
            for candidate, score in zip(missing, scores, strict=True):
                self._remember(self._cache_key(query, candidate), score)
        return [
            RerankScore(
                chunk_id=item.chunk_id,
                score=self._cache[self._cache_key(query, item)],
            )
            for item in candidates
        ]

    def _compute_scores(self, query: str, candidates: list[RerankCandidate]) -> list[float]:
        if self._model is None:
            self._model = self._model_factory(self.model_name, self.use_fp16)
        raw = self._model.compute_score([[query, item.text] for item in candidates])
        if hasattr(raw, "tolist"):
            raw = raw.tolist()
        values = raw if isinstance(raw, (list, tuple)) else [raw]
        return [float(value) for value in values]

    def _remember(self, key: str, score: float) -> None:
        self._cache[key] = score
        self._cache.move_to_end(key)
        while len(self._cache) > self.cache_size:
            self._cache.popitem(last=False)

    def _cache_key(self, query: str, candidate: RerankCandidate) -> str:
        payload = f"{self.model_name}|{query}|{candidate.chunk_id}|{candidate.text}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _default_model_factory(model_name: str, use_fp16: bool) -> Any:
    try:
        from FlagEmbedding import FlagReranker
    except ImportError as exc:
        raise RuntimeError(
            "FlagEmbedding is required when Cross-Encoder reranking is enabled"
        ) from exc
    return FlagReranker(model_name, use_fp16=use_fp16)


__all__ = ["CrossEncoderReranker"]
