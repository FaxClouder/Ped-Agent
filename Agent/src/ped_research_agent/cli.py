"""Small offline demo and archive replay. This command never configures a live model."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import tempfile
from pathlib import Path
from uuid import uuid4

from pydantic import JsonValue

from ped_agent_harness.model_contracts import (
    ModelCapabilities,
    ModelReply,
    ModelRequest,
    ModelUsage,
)
from ped_research_agent.agentic.config import HarnessPolicy, KnowledgeSnapshot, RunProfile
from ped_research_agent.integrations.knowledge import KnowledgeAdapter, SnapshotIdentity
from ped_research_agent.integrations.research_run import run_research
from ped_research_agent.integrations.run_records import ReplayError, replay_run


class OfflineModel:
    """Deterministic synthetic responses; no reasoning/model-quality claim."""

    def capabilities(self, role: str) -> ModelCapabilities:
        return ModelCapabilities(structured=True)

    async def invoke(self, request: ModelRequest) -> ModelReply:
        data: dict[str, JsonValue]
        if request.role == "planner":
            data = {
                "requirements": [
                    {
                        "id": "density",
                        "statement": "Synthetic density fact",
                        "queries": ["density bottleneck"],
                    }
                ]
            }
        elif request.role == "judge":
            state = json.loads(request.messages[-1].content)["state"]
            ids = list(state["evidence"])
            data = {
                "status": "satisfied" if ids else "unknown",
                "support_evidence_ids": ids,
                "rationale": "Scripted fixture declaration; not a real judgment",
            }
        elif request.role == "replan":
            data = {"rationale": "No scripted changes"}
        elif request.role == "verify":
            data = {"claims": [{"claim_id": "c1", "status": "supported"}]}
        else:
            # The shared prompt supplies the exact labeled canonical evidence.
            text = request.messages[-1].content
            pack = json.loads(text.split("<evidence>", 1)[1].split("</evidence>", 1)[0])
            first = pack[0]
            label = first["label"]
            data = {
                "answer_markdown": f"Synthetic density rises near the bottleneck [{label}]",
                "claims": [
                    {
                        "claim_id": "c1",
                        "text": "Synthetic density rises",
                        "citation_labels": [label],
                    }
                ],
                "citations": [
                    {"label": label, "evidence_id": first["evidence_id"], "claim_ids": ["c1"]}
                ],
                "limitations": ["Offline fixture; not a real model or research result"],
            }
        return ModelReply(
            content=json.dumps(data),
            structured=data,
            model="offline-script-v1",
            finish_reason="stop",
            usage=ModelUsage(input_tokens=10, output_tokens=5),
        )


def make_fixture(directory: Path) -> KnowledgeAdapter:
    """Tiny real SQLite/FTS corpus; no PDF, dense index or model dependency."""
    # Optional KB dependency is needed only by the demo, never by replay.
    from ped_knowledge.contracts import IngestionManifest, KnowledgeChunk, ResourceType
    from ped_knowledge.indexing import FTSIndex
    from ped_knowledge.retrieval import HybridRetriever
    from ped_knowledge.storage import Catalog

    catalog = Catalog(directory / "catalog.sqlite3")
    catalog.initialize()
    version = hashlib.sha256(b"agent-core-offline-fixture-v1").hexdigest()
    record = IngestionManifest(
        resource_id="offline-fixture-v1",
        resource_type=ResourceType.LITERATURE,
        title="Synthetic density",
        language="en",
        source_path=directory / "never-read.pdf",
        sha256=version,
    )
    catalog.upsert_resource(record, version_id=version, vault_path="unused")
    chunk = KnowledgeChunk(
        resource_id=record.resource_id,
        version_id=version,
        chunk_id="synthetic-child",
        ordinal=0,
        page_start=1,
        page_end=1,
        locator="fixture:p.1",
        parser_version="synthetic-v1",
        text="Synthetic density rises near the bottleneck.",
    )
    catalog.replace_chunks(version, [chunk], policy_version="parent-child-v1")
    fingerprint = catalog.official_fingerprint(policy_version="parent-child-v1")
    index = FTSIndex(directory / "fts.sqlite3")
    index.rebuild(
        catalog.list_official_chunks(policy_version="parent-child-v1"),
        source_fingerprint=fingerprint,
    )
    snapshot = SnapshotIdentity(
        policy_version="parent-child-v1",
        catalog_fingerprint=fingerprint,
        index_fingerprint=index.source_fingerprint(),
    )
    return KnowledgeAdapter(
        HybridRetriever(catalog, index, None, embedding_fingerprint="unused"),
        catalog,
        snapshot=snapshot,
        current_index_fingerprint=index.source_fingerprint,
        baseline_sufficiency=lambda query, items: bool(items),
    )


async def demo(output_root: Path, question: str) -> tuple[Path, str]:
    identity = str(uuid4())
    directory = output_root.resolve() / identity
    with tempfile.TemporaryDirectory(prefix="ped-agent-fixture-") as temporary:
        source = Path(temporary)
        knowledge = make_fixture(source)
        manifest = source / "snapshot.json"
        manifest.write_text(knowledge.snapshot.model_dump_json())
        profile = RunProfile(
            profile_id="offline-fixture-v1",
            knowledge=KnowledgeSnapshot(
                manifest=manifest, sha256=hashlib.sha256(manifest.read_bytes()).hexdigest()
            ),
            output_dir=directory,
            harness=HarnessPolicy(model_max_output_tokens=128),
        )
        result = await run_research(profile, knowledge, OfflineModel(), question, run_id=identity)
    rebuilt, _ = replay_run(directory)
    if rebuilt != result:
        raise ReplayError("invalid", "demo replay differs from execution")
    return directory, result.stop_reason.value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("demo", help="offline synthetic SQLite/FTS and scripted model")
    run.add_argument("--output-root", type=Path, default=Path("outputs/agent-core-offline"))
    run.add_argument("--question", default="What does the synthetic density fixture state?")
    replay = commands.add_parser(
        "replay", help="verify files and rebuild state without providers/tools"
    )
    replay.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "demo":
            directory, reason = asyncio.run(demo(args.output_root, args.question))
            print(
                json.dumps({"run_dir": str(directory), "stop_reason": reason, "replay": "verified"})
            )
        else:
            result, usage = replay_run(args.run_dir)
            print(
                json.dumps(
                    {
                        "stop_reason": result.stop_reason.value,
                        "outcome": result.outcome,
                        "requirements": len(result.state.requirements),
                        "evidence": len(result.state.evidence),
                        "usage": usage.model_dump(),
                    }
                )
            )
    except (ReplayError, ValueError, ImportError, OSError) as exc:
        print(json.dumps({"error": type(exc).__name__, "detail": str(exc)}))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
