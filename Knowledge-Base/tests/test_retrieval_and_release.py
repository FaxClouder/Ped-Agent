from __future__ import annotations

from pathlib import Path

import pytest

from ped_knowledge.contracts import (
    IndexHit,
    IngestionManifest,
    KnowledgeChunk,
    RerankCandidate,
    RerankScore,
)
from ped_knowledge.evaluation import (
    EvaluationAcceptanceConfig,
    EvaluationReport,
    audit_evaluation,
    compare_with_baseline,
    publish_retrieval_config,
)
from ped_knowledge.reranking import CrossEncoderReranker
from ped_knowledge.retrieval import HybridRetriever
from ped_knowledge.storage import Catalog


class FakeFTS:
    def __init__(self, hits: list[IndexHit]) -> None:
        self.hits = hits

    def search(self, query: str, *, limit: int) -> list[IndexHit]:
        return self.hits[:limit]


class ReverseReranker:
    async def rerank(self, query: str, candidates):
        return [
            RerankScore(chunk_id=item.chunk_id, score=float(index))
            for index, item in enumerate(candidates, start=1)
        ]


class BrokenReranker:
    async def rerank(self, query: str, candidates):
        raise RuntimeError("model unavailable")


class FakeCrossEncoder:
    def __init__(self) -> None:
        self.calls = 0

    def compute_score(self, pairs):
        self.calls += 1
        return tuple(float(index) for index, _ in enumerate(pairs, start=1))


def _catalog_with_chunks(tmp_path: Path) -> tuple[Catalog, list[str]]:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    record = IngestionManifest(
        resource_id="paper-rerank",
        resource_type="literature",
        title="Rerank evidence",
        language="en",
        source_path=tmp_path / "paper.pdf",
        sha256="c" * 64,
    )
    chunks = [
        KnowledgeChunk(
            chunk_id=f"child-{index}",
            resource_id=record.resource_id,
            version_id=record.sha256,
            ordinal=index,
            text=f"Evidence candidate {index}",
            page_start=1,
            page_end=1,
            locator=f"p.1#{index}",
            parser_version="test",
        )
        for index in range(2)
    ]
    catalog.upsert_resource(record, version_id=record.sha256, vault_path="objects/paper.pdf")
    catalog.replace_chunks(record.sha256, chunks)
    return catalog, [item.chunk_id for item in chunks]


@pytest.mark.asyncio
async def test_reranker_changes_order_and_failure_falls_back_to_rrf(tmp_path: Path) -> None:
    catalog, chunk_ids = _catalog_with_chunks(tmp_path)
    fts = FakeFTS([IndexHit(item, 1.0) for item in chunk_ids])
    reranked = await HybridRetriever(
        catalog,
        fts,
        None,
        embedding_fingerprint="unused",
        reranker=ReverseReranker(),
    ).retrieve("evidence")
    fallback = await HybridRetriever(
        catalog,
        fts,
        None,
        embedding_fingerprint="unused",
        reranker=BrokenReranker(),
    ).retrieve("evidence")

    assert [item.chunk_id for item in reranked.items] == list(reversed(chunk_ids))
    assert [item.chunk_id for item in fallback.items] == chunk_ids
    assert "reranker_unavailable" in fallback.degradation_reason


@pytest.mark.asyncio
async def test_cross_encoder_adapter_caches_scores() -> None:
    model = FakeCrossEncoder()
    reranker = CrossEncoderReranker(
        "test-model",
        model_factory=lambda _name, _fp16: model,
    )
    candidates = [
        {
            "chunk_id": "a",
            "text": "first",
            "initial_score": 0.1,
        },
        {
            "chunk_id": "b",
            "text": "second",
            "initial_score": 0.2,
        },
    ]
    typed = [RerankCandidate.model_validate(item) for item in candidates]
    first = await reranker.rerank("query", typed)
    second = await reranker.rerank("query", typed)

    assert [item.score for item in first] == [1.0, 2.0]
    assert second == first
    assert model.calls == 1


def test_failed_candidate_config_does_not_replace_active_baseline(tmp_path: Path) -> None:
    catalog = Catalog(tmp_path / "catalog.sqlite3")
    catalog.initialize()
    config = EvaluationAcceptanceConfig(
        question_count=1,
        k=5,
        minimum_recall_at_k=0.8,
        minimum_mrr=0.7,
        minimum_locator_hit_rate=0.8,
        maximum_non_official_leakage=0.0,
    )
    baseline = EvaluationReport(
        question_count=1,
        k=5,
        recall_at_k=1.0,
        mrr=1.0,
        ndcg_at_k=1.0,
        locator_hit_rate=1.0,
    )
    accepted = audit_evaluation(baseline, config, non_official_leakage=0.0)
    assert publish_retrieval_config(
        catalog,
        config_id="baseline",
        payload={"rrf_k": 60},
        acceptance=accepted,
        comparison=compare_with_baseline(baseline, None, config),
    )

    candidate = baseline.model_copy(update={"recall_at_k": 0.5})
    rejected = audit_evaluation(candidate, config, non_official_leakage=0.0)
    assert not publish_retrieval_config(
        catalog,
        config_id="candidate",
        payload={"rrf_k": 20},
        acceptance=rejected,
        comparison=compare_with_baseline(candidate, baseline, config),
    )
    assert catalog.active_retrieval_config()["config_id"] == "baseline"
