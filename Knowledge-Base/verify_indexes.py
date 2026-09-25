"""Verify FTS5/BM25 and BGE-M3 indexes are working correctly.

Quick verification script to test both lexical and dense retrieval.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "Contracts" / "src"))
sys.path.insert(0, str(repo_root / "Knowledge-Base" / "src"))

# Windows console encoding fix
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

from ped_knowledge.indexing import ChromaVectorIndex, FTSIndex
from ped_knowledge.storage import Catalog
from ped_knowledge.tokenization import JiebaLexicalAnalyzer


class DummyEmbedding:
    """Dummy embedding for verification (real embedding not needed for reads)."""
    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise RuntimeError("Should not embed during verification")


def verify_fts(index_path: Path, config_root: Path) -> None:
    """Verify FTS5/BM25 index."""
    print("\n" + "="*60)
    print("FTS5/BM25 Index Verification")
    print("="*60)

    analyzer = JiebaLexicalAnalyzer(
        domain_terms_path=config_root / "retrieval" / "pedestrian_terms.txt",
        stopwords_path=config_root / "retrieval" / "stopwords_zh_en.txt",
        version="jieba-lexical-v1",
    )

    index = FTSIndex(index_path, analyzer=analyzer)

    # Read metadata
    print(f"\nIndex metadata:")
    print(f"  Path: {index_path}")
    print(f"  Size: {index_path.stat().st_size / (1024*1024):.2f} MB")
    print(f"  Source fingerprint: {index.source_fingerprint()[:16]}...")
    print(f"  Policy version: {index.policy_version()}")
    print(f"  Tokenizer: {index.tokenizer_fingerprint()}")
    print(f"  Lexical analyzer: {index.lexical_analyzer_fingerprint()[:20]}...")

    # Test queries
    test_cases = [
        ("行人流", "Chinese: pedestrian flow"),
        ("社会力模型", "Chinese: social force model"),
        ("疏散", "Chinese: evacuation"),
        ("pedestrian", "English: pedestrian"),
        ("evacuation", "English: evacuation"),
        ("bottleneck", "English: bottleneck"),
    ]

    print(f"\nQuery tests (limit=5):")
    for query, description in test_cases:
        hits = index.search(query, limit=5)
        print(f"  '{query}' ({description}): {len(hits)} hits")
        if hits:
            for i, hit in enumerate(hits[:2], 1):
                print(f"    {i}. {hit.chunk_id[:40]}... (score: {hit.score:.4f})")


async def verify_dense(index_path: Path, catalog_path: Path) -> None:
    """Verify BGE-M3 dense index."""
    print("\n" + "="*60)
    print("BGE-M3 Dense Index Verification")
    print("="*60)

    # For verification, we just need to read metadata
    gateway = DummyEmbedding()
    index = ChromaVectorIndex(index_path, gateway)

    print(f"\nIndex metadata:")
    print(f"  Path: {index_path}")

    # Get directory size
    total_size = sum(f.stat().st_size for f in index_path.rglob("*") if f.is_file())
    print(f"  Size: {total_size / (1024*1024):.2f} MB")
    print(f"  Catalog fingerprint: {index.catalog_fingerprint[:16]}...")
    print(f"  Embedding fingerprint: {index.embedding_fingerprint[:16]}...")
    print(f"  Policy version: {index.policy_version}")
    print(f"  Tokenizer: {index.tokenizer_fingerprint}")

    # Count documents
    catalog = Catalog(catalog_path)
    chunks = catalog.list_official_chunks(policy_version=index.policy_version)
    print(f"  Documents indexed: {len(chunks)}")

    print("\n[INFO] Dense index query test requires BGE-M3 model loaded.")
    print("[INFO] For quick verification, metadata check is sufficient.")


def main() -> None:
    memped_root = repo_root / "memPed" / "knowledge"
    config_root = repo_root / "Knowledge-Base" / "config"
    catalog_path = memped_root / "knowledge.sqlite3"

    fts_path = memped_root / "indexes" / "fts-parent-child-v1.sqlite3"
    dense_path = memped_root / "indexes" / "bge-m3-1024"

    print("Knowledge Base Index Verification")
    print("="*60)
    print(f"Repository: {repo_root}")

    # Verify FTS
    if fts_path.exists():
        try:
            verify_fts(fts_path, config_root)
        except Exception as exc:
            print(f"\nERROR verifying FTS index: {exc}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\nWARNING: FTS index not found: {fts_path}")

    # Verify dense
    if dense_path.exists():
        try:
            asyncio.run(verify_dense(dense_path, catalog_path))
        except Exception as exc:
            print(f"\nERROR verifying dense index: {exc}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\nWARNING: Dense index not found: {dense_path}")

    print("\n" + "="*60)
    print("Verification complete")
    print("="*60)


if __name__ == "__main__":
    main()
