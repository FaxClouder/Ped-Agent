"""Ped-Agent governed knowledge processing package."""

from ped_knowledge.chunking import HierarchicalChunker
from ped_knowledge.contracts import (
    CanonicalDocument,
    ChunkingPolicy,
    DocumentElement,
    EvidenceHit,
    IngestionManifest,
    KnowledgeChunk,
    ParseReport,
    ResourceType,
)
from ped_knowledge.evaluation import evaluate_rankings, load_gold
from ped_knowledge.indexing import ChromaVectorIndex, FTSIndex
from ped_knowledge.ingestion import ImportService, preflight_manifest
from ped_knowledge.retrieval import HybridRetriever, RetrievalService
from ped_knowledge.storage import Catalog, ContentVault

__all__ = [
    "CanonicalDocument",
    "Catalog",
    "ChromaVectorIndex",
    "ChunkingPolicy",
    "ContentVault",
    "DocumentElement",
    "EvidenceHit",
    "FTSIndex",
    "HierarchicalChunker",
    "HybridRetriever",
    "ImportService",
    "IngestionManifest",
    "KnowledgeChunk",
    "ParseReport",
    "ResourceType",
    "RetrievalService",
    "evaluate_rankings",
    "load_gold",
    "preflight_manifest",
]
