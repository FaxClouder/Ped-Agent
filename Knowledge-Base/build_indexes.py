"""Build FTS5/BM25 and BGE-M3 indexes for the knowledge base.

Usage:
    python -m build_indexes [--policy-version parent-child-v1] [--skip-fts] [--skip-dense]

This script:
1. Reads active chunks from the catalog (official retrieval eligibility)
2. Builds FTS5/BM25 index with jieba lexical analyzer
3. Builds BGE-M3 dense vector index with Chroma
4. Records index fingerprints and metadata
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Windows consoles default to gbk, which cannot encode the bilingual probe queries.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

# Add src to path for imports
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "Contracts" / "src"))
sys.path.insert(0, str(repo_root / "Knowledge-Base" / "src"))

from ped_knowledge.indexing import ChromaVectorIndex, FTSIndex, embedding_fingerprint
from ped_knowledge.storage import Catalog
from ped_knowledge.tokenization import JiebaLexicalAnalyzer


class BGE_M3_Gateway:
    """Embedding gateway for BGE-M3 model."""

    def __init__(
        self,
        model_path: Path,
        *,
        device: str = "cuda",
        use_fp16: bool = True,
        max_length: int = 1024,
    ) -> None:
        try:
            from FlagEmbedding import BGEM3FlagModel
        except ImportError as exc:
            raise RuntimeError(
                "FlagEmbedding is required for BGE-M3. "
                "Install with: uv pip install FlagEmbedding==1.4.2"
            ) from exc

        print(f"Loading BGE-M3 from {model_path}...")
        self.model = BGEM3FlagModel(
            str(model_path),
            devices=device,
            use_fp16=use_fp16,
        )
        self.max_length = max_length
        print(f"BGE-M3 loaded on {device} (fp16={use_fp16})")

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed texts using BGE-M3 dense vectors."""
        if not texts:
            return []

        # BGE-M3 encode is synchronous, run in executor to avoid blocking
        result = self.model.encode(
            texts,
            batch_size=8,
            max_length=self.max_length,
            return_dense=True,
            return_sparse=False,
            return_colbert_vecs=False,
        )

        # Convert to list of lists
        import numpy as np
        dense_vecs = np.asarray(result["dense_vecs"])
        return dense_vecs.tolist()


def build_fts_index(
    catalog_path: Path,
    index_path: Path,
    lexical_config: dict[str, Path],
    *,
    policy_version: str,
) -> None:
    """Build FTS5/BM25 index with jieba lexical analyzer."""
    print(f"\n{'='*60}")
    print("Building FTS5/BM25 Index")
    print(f"{'='*60}")

    # Initialize lexical analyzer
    print(f"Initializing jieba analyzer...")
    print(f"  Domain terms: {lexical_config['domain_terms_path']}")
    print(f"  Stopwords: {lexical_config['stopwords_path']}")

    analyzer = JiebaLexicalAnalyzer(
        domain_terms_path=lexical_config["domain_terms_path"],
        stopwords_path=lexical_config["stopwords_path"],
        version="jieba-lexical-v1",
    )
    print(f"  Fingerprint: {analyzer.fingerprint}")

    # Load chunks from catalog
    print(f"\nLoading chunks from catalog...")
    print(f"  Catalog: {catalog_path}")
    print(f"  Policy: {policy_version}")

    catalog = Catalog(catalog_path)
    chunks = catalog.list_official_chunks(policy_version=policy_version)
    print(f"  Loaded {len(chunks)} official child chunks")

    if not chunks:
        print("  WARNING: No chunks found! Check catalog and policy version.")
        return

    # Compute source fingerprint
    source_fingerprint = catalog.official_fingerprint(policy_version=policy_version)
    print(f"  Source fingerprint: {source_fingerprint[:16]}...")

    # Build index
    print(f"\nBuilding FTS5 index...")
    print(f"  Output: {index_path}")

    fts_index = FTSIndex(index_path, analyzer=analyzer)

    # Get tokenizer fingerprint from first chunk
    tokenizer_fingerprint = chunks[0].get("tokenizer_fingerprint", "regex-token-v1")

    fts_index.rebuild(
        chunks,
        source_fingerprint=source_fingerprint,
        policy_version=policy_version,
        tokenizer_fingerprint=tokenizer_fingerprint,
    )

    print(f"  [OK] FTS5 index built successfully")
    print(f"  Size: {index_path.stat().st_size / (1024*1024):.2f} MB")

    # Verify index
    print(f"\nVerifying index...")
    test_queries = ["行人流", "社会力模型", "pedestrian", "evacuation"]
    for query in test_queries:
        hits = fts_index.search(query, limit=3)
        print(f"  Query '{query}': {len(hits)} hits")
        if hits:
            print(f"    Top hit: {hits[0].chunk_id} (score: {hits[0].score:.4f})")


async def build_dense_index(
    catalog_path: Path,
    index_path: Path,
    model_config: dict,
    lexical_config: dict[str, Path],
    *,
    policy_version: str,
) -> None:
    """Build BGE-M3 dense vector index with Chroma."""
    print(f"\n{'='*60}")
    print("Building BGE-M3 Dense Vector Index")
    print(f"{'='*60}")

    # Initialize embedding gateway
    print(f"Initializing BGE-M3 gateway...")
    print(f"  Model path: {model_config['model_path']}")
    print(f"  Device: {model_config['device']}")
    print(f"  Dimensions: {model_config['dimensions']}")

    gateway = BGE_M3_Gateway(
        model_path=model_config["model_path"],
        device=model_config["device"],
        use_fp16=model_config["use_fp16"],
        max_length=model_config["max_length"],
    )

    # Load chunks from catalog
    print(f"\nLoading chunks from catalog...")
    print(f"  Catalog: {catalog_path}")
    print(f"  Policy: {policy_version}")

    catalog = Catalog(catalog_path)
    chunks = catalog.list_official_chunks(policy_version=policy_version)
    print(f"  Loaded {len(chunks)} official child chunks")

    if not chunks:
        print("  WARNING: No chunks found! Check catalog and policy version.")
        return

    # Compute fingerprints
    catalog_fingerprint = catalog.official_fingerprint(policy_version=policy_version)
    print(f"  Catalog fingerprint: {catalog_fingerprint[:16]}...")

    embed_fingerprint = embedding_fingerprint(
        model=model_config["model_id"],
        base_url=None,
        dimensions=model_config["dimensions"],
    )
    print(f"  Embedding fingerprint: {embed_fingerprint[:16]}...")

    # Initialize lexical analyzer for fingerprint
    analyzer = JiebaLexicalAnalyzer(
        domain_terms_path=lexical_config["domain_terms_path"],
        stopwords_path=lexical_config["stopwords_path"],
        version="jieba-lexical-v1",
    )
    lexical_fingerprint = analyzer.fingerprint
    print(f"  Lexical fingerprint: {lexical_fingerprint[:16]}...")

    # Build index
    print(f"\nBuilding Chroma index...")
    print(f"  Output: {index_path}")
    print(f"  Batch size: {model_config['batch_size']}")

    chroma_index = ChromaVectorIndex(
        index_path,
        embedding_gateway=gateway,
        batch_size=model_config["batch_size"],
    )

    tokenizer_fingerprint = chunks[0].get("tokenizer_fingerprint", "regex-token-v1")

    await chroma_index.rebuild(
        chunks,
        catalog_fingerprint=catalog_fingerprint,
        embedding_fingerprint=embed_fingerprint,
        policy_version=policy_version,
        tokenizer_fingerprint=tokenizer_fingerprint,
        embedding_max_length=model_config["max_length"],
        normalize_embeddings=model_config["normalize_embeddings"],
        lexical_analyzer_fingerprint=lexical_fingerprint,
    )

    print(f"  [OK] Chroma index built successfully")

    # Verify index
    print(f"\nVerifying index...")
    test_queries = ["行人流基本图", "社会力模型", "pedestrian dynamics", "crowd evacuation"]
    for query in test_queries:
        hits = await chroma_index.search(query, limit=3)
        print(f"  Query '{query}': {len(hits)} hits")
        if hits:
            print(f"    Top hit: {hits[0].chunk_id} (score: {hits[0].score:.4f})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build FTS5/BM25 and BGE-M3 indexes for knowledge base"
    )
    parser.add_argument(
        "--policy-version",
        default="parent-child-v1",
        help="Chunking policy version (default: parent-child-v1)",
    )
    parser.add_argument(
        "--skip-fts",
        action="store_true",
        help="Skip FTS5/BM25 index building",
    )
    parser.add_argument(
        "--skip-dense",
        action="store_true",
        help="Skip BGE-M3 dense index building",
    )
    args = parser.parse_args()

    # Paths
    memped_root = repo_root / "memPed" / "knowledge"
    catalog_path = memped_root / "knowledge.sqlite3"
    config_root = repo_root / "Knowledge-Base" / "config"

    # Check catalog exists
    if not catalog_path.exists():
        print(f"ERROR: Catalog not found: {catalog_path}")
        print("Run ingestion first to populate the catalog.")
        sys.exit(1)

    # Lexical config
    lexical_config = {
        "domain_terms_path": config_root / "retrieval" / "pedestrian_terms.txt",
        "stopwords_path": config_root / "retrieval" / "stopwords_zh_en.txt",
    }

    # Verify lexical files exist
    for key, path in lexical_config.items():
        if not path.exists():
            print(f"ERROR: Lexical file not found: {path}")
            sys.exit(1)

    print(f"Knowledge Base Index Builder")
    print(f"{'='*60}")
    print(f"Repository root: {repo_root}")
    print(f"Catalog: {catalog_path}")
    print(f"Policy version: {args.policy_version}")
    print(f"{'='*60}")

    # Build FTS5/BM25 index
    if not args.skip_fts:
        fts_index_path = memped_root / "indexes" / f"fts-{args.policy_version}.sqlite3"
        fts_index_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            build_fts_index(
                catalog_path,
                fts_index_path,
                lexical_config,
                policy_version=args.policy_version,
            )
        except Exception as exc:
            print(f"\nERROR building FTS index: {exc}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("\nSkipping FTS5/BM25 index (--skip-fts)")

    # Build BGE-M3 dense index
    if not args.skip_dense:
        model_path = memped_root / "models" / "bge-m3"
        if not model_path.exists():
            print(f"\nERROR: BGE-M3 model not found: {model_path}")
            print("Download model first. See Knowledge-Base/config/embeddings/bge-m3/README.md")
            sys.exit(1)

        model_config = {
            "model_id": "BAAI/bge-m3",
            "model_path": model_path,
            "device": "cuda",
            "use_fp16": True,
            "dimensions": 1024,
            "batch_size": 8,
            "max_length": 1024,
            "normalize_embeddings": True,
        }

        dense_index_path = memped_root / "indexes" / "bge-m3-1024"
        dense_index_path.mkdir(parents=True, exist_ok=True)

        try:
            asyncio.run(
                build_dense_index(
                    catalog_path,
                    dense_index_path,
                    model_config,
                    lexical_config,
                    policy_version=args.policy_version,
                )
            )
        except Exception as exc:
            print(f"\nERROR building dense index: {exc}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("\nSkipping BGE-M3 dense index (--skip-dense)")

    print(f"\n{'='*60}")
    print("[OK] Index building complete!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
