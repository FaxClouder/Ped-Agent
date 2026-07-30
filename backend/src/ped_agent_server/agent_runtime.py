from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import httpx
from ped_agent.agent.evidence_graph import EvidenceGraph

from ped_agent_server.agent_repository import AgentRepository
from ped_agent_server.catalog import Catalog
from ped_agent_server.evidence_executor import HybridLocalEvidenceRetriever, LangGraphRunExecutor
from ped_agent_server.external_search import ExternalSearchCoordinator
from ped_agent_server.hybrid_retrieval import HybridRetriever
from ped_agent_server.index import FTSIndex
from ped_agent_server.model_gateway import DirectModelGateway
from ped_agent_server.paths import WorkspacePaths
from ped_agent_server.run_service import RunService
from ped_agent_server.settings import AgentSettings
from ped_agent_server.vector_index import ChromaVectorIndex, embedding_fingerprint


@dataclass
class AgentRuntime:
    repository: AgentRepository
    run_service: RunService
    vector_index: ChromaVectorIndex
    http_client: httpx.AsyncClient

    async def close(self) -> None:
        await self.run_service.shutdown()
        await self.http_client.aclose()


def build_agent_runtime(settings: AgentSettings, paths: WorkspacePaths) -> AgentRuntime:
    _configure_langsmith(settings)
    repository = AgentRepository(_resolve_path(paths.repo_root, settings.runtime.agent_db_path))
    repository.initialize()
    gateway = DirectModelGateway.from_settings(settings)
    embedding_id = embedding_fingerprint(
        model=settings.embedding.model,
        base_url=settings.embedding.base_url,
        dimensions=settings.embedding.dimensions,
    )
    vector_index = ChromaVectorIndex(
        _resolve_path(paths.repo_root, settings.runtime.chroma_path),
        gateway,
    )
    hybrid = HybridRetriever(
        Catalog(paths.catalog_path),
        FTSIndex(paths.index_path),
        vector_index,
        embedding_fingerprint=embedding_id,
    )
    http_client = httpx.AsyncClient(timeout=settings.search.timeout_seconds)
    parallel_key = (
        settings.search.parallel_api_key.get_secret_value()
        if settings.search.parallel_enabled and settings.search.parallel_api_key
        else None
    )
    searcher = ExternalSearchCoordinator(
        http_client,
        academic_enabled=settings.search.academic_enabled,
        parallel_api_key=parallel_key,
        max_candidates_per_source=settings.search.max_candidates_per_source,
        max_pages=settings.search.max_pages,
    )
    graph = EvidenceGraph(
        gateway,
        HybridLocalEvidenceRetriever(hybrid),
        searcher,
        allow_rules_only=not settings.verify.enabled,
    )
    service = RunService(
        repository,
        LangGraphRunExecutor(graph),
        max_concurrent_runs=settings.runtime.max_concurrent_runs,
        recent_message_limit=settings.runtime.recent_message_limit,
    )
    return AgentRuntime(repository, service, vector_index, http_client)


def _resolve_path(repo_root: Path, configured: Path) -> Path:
    return configured if configured.is_absolute() else repo_root / configured


def _configure_langsmith(settings: AgentSettings) -> None:
    os.environ["LANGSMITH_TRACING"] = "true" if settings.langsmith.enabled else "false"
    if not settings.langsmith.enabled:
        return
    if settings.langsmith.api_key:
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith.api_key.get_secret_value()
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith.project
    if settings.langsmith.endpoint:
        os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith.endpoint
