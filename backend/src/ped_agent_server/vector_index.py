"""Compatibility export for dense knowledge indexing."""

from ped_knowledge.contracts import EmbeddingGateway
from ped_knowledge.indexing import ChromaVectorIndex, embedding_fingerprint

__all__ = ["ChromaVectorIndex", "EmbeddingGateway", "embedding_fingerprint"]
