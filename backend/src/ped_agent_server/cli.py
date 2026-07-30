from __future__ import annotations

import asyncio
import json
from dataclasses import asdict
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Annotated

import typer
import uvicorn

from ped_agent_server.agent_runtime import build_agent_runtime
from ped_agent_server.api import create_app
from ped_agent_server.catalog import Catalog
from ped_agent_server.evaluation import (
    EvaluationAcceptanceConfig,
    audit_catalog,
    audit_evaluation,
    evaluate_rankings,
    load_gold,
)
from ped_agent_server.governance import audit_literature_corpus, audit_regulation_corpus
from ped_agent_server.importer import ImportService
from ped_agent_server.index import FTSIndex
from ped_agent_server.manifest import load_and_preflight
from ped_agent_server.model_gateway import DirectModelGateway
from ped_agent_server.models import ResourceType
from ped_agent_server.paths import WorkspacePaths
from ped_agent_server.retrieval import RetrievalService
from ped_agent_server.settings import load_settings
from ped_agent_server.vector_index import embedding_fingerprint

app = typer.Typer(no_args_is_help=True)
library = typer.Typer(no_args_is_help=True)
agent = typer.Typer(no_args_is_help=True)
app.add_typer(library, name="library")
app.add_typer(agent, name="agent")


def repo_paths() -> WorkspacePaths:
    return WorkspacePaths.from_repo_root(Path(__file__).resolve().parents[3])


@library.command("import-manifest")
def import_manifest(
    path: Path,
    report_output: Annotated[Path | None, typer.Option("--report")] = None,
) -> None:
    paths = repo_paths()
    report = ImportService(paths).import_manifest(path)
    payload = json.dumps(asdict(report), ensure_ascii=False, indent=2)
    output = report_output or paths.reports_dir / f"{path.stem}-import.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload, encoding="utf-8")
    typer.echo(payload)


@library.command("validate-manifest")
def validate_manifest(
    path: Path,
    phase: Annotated[str, typer.Option("--phase")] = "pilot",
    as_of: Annotated[str | None, typer.Option("--as-of")] = None,
) -> None:
    try:
        reference_date = (
            date.fromisoformat(as_of) if as_of else datetime.now(UTC).date()
        )
    except ValueError as exc:
        raise typer.BadParameter("--as-of must use YYYY-MM-DD") from exc
    records = load_and_preflight(path, as_of=reference_date)
    resource_types = {record.resource_type for record in records}
    if resource_types == {ResourceType.LITERATURE}:
        report = audit_literature_corpus(
            [record for record in records if record.include],
            phase=phase,
            as_of=reference_date,
        )
    elif resource_types and resource_types.issubset(
        {ResourceType.REGULATION, ResourceType.STANDARD}
    ):
        report = audit_regulation_corpus(
            [record for record in records if record.include],
            phase=phase,
        )
    else:
        raise typer.BadParameter(
            "manifest must contain either literature or regulation/standard records"
        )
    typer.echo(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    if not report.is_compliant:
        raise typer.Exit(code=1)


@library.command("build-index")
def build_index() -> None:
    paths = repo_paths()
    catalog = Catalog(paths.catalog_path)
    FTSIndex(paths.index_path).rebuild(
        catalog.list_official_chunks(),
        source_fingerprint=catalog.official_fingerprint(),
    )
    typer.echo("index rebuilt")


@library.command("search")
def search(query: str, limit: int = 5) -> None:
    paths = repo_paths()
    hits = RetrievalService(Catalog(paths.catalog_path), FTSIndex(paths.index_path)).search(
        query, limit=limit
    )
    typer.echo(json.dumps([hit.model_dump(mode="json") for hit in hits], ensure_ascii=False))


@app.command("evaluate")
def evaluate(
    gold: Path,
    output: Path,
    k: int = 5,
    config: Annotated[Path | None, typer.Option("--config")] = None,
) -> None:
    paths = repo_paths()
    service = RetrievalService(Catalog(paths.catalog_path), FTSIndex(paths.index_path))
    questions = load_gold(gold)
    acceptance_config = (
        EvaluationAcceptanceConfig.model_validate_json(config.read_text(encoding="utf-8"))
        if config is not None
        else None
    )
    effective_k = acceptance_config.k if acceptance_config is not None else k
    rankings = {
        item.question_id: [
            (hit.resource_id, hit.locator)
            for hit in service.search(item.query, limit=effective_k)
        ]
        for item in questions
    }
    report = evaluate_rankings(questions, rankings, k=effective_k)
    acceptance = (
        audit_evaluation(report, acceptance_config, non_official_leakage=0.0)
        if acceptance_config is not None
        else None
    )
    payload = acceptance or report
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload.model_dump_json(indent=2), encoding="utf-8")
    typer.echo(payload.model_dump_json())
    if acceptance is not None and not acceptance.is_compliant:
        raise typer.Exit(code=1)


@app.command("audit")
def audit(output: Path) -> None:
    report = audit_catalog(Catalog(repo_paths().catalog_path))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    typer.echo(report.model_dump_json())


@agent.command("doctor")
def agent_doctor() -> None:
    try:
        settings = load_settings()
        DirectModelGateway.from_settings(settings)
        paths = repo_paths()
        report = {
            "configuration": "ok",
            "answer": {
                "protocol": settings.answer.protocol,
                "model": settings.answer.model,
            },
            "verify": {
                "enabled": settings.verify.enabled,
                "protocol": settings.resolved_verify.protocol
                if settings.verify.enabled
                else "disabled",
                "model": settings.resolved_verify.model if settings.verify.enabled else None,
            },
            "embedding": {
                "model": settings.embedding.model,
                "fingerprint": embedding_fingerprint(
                    model=settings.embedding.model,
                    base_url=settings.embedding.base_url,
                    dimensions=settings.embedding.dimensions,
                ),
            },
            "storage": {
                "catalog_exists": paths.catalog_path.exists(),
                "fts_exists": paths.index_path.exists(),
                "agent_db": str(settings.runtime.agent_db_path),
                "chroma": str(settings.runtime.chroma_path),
            },
        }
        typer.echo(json.dumps(report, ensure_ascii=False, indent=2))
    except Exception as exc:  # noqa: BLE001 - doctor must redact all configuration failures.
        typer.echo(
            json.dumps(
                {"configuration": "invalid", "error": type(exc).__name__},
                ensure_ascii=False,
            ),
            err=True,
        )
        raise typer.Exit(code=1) from None


@agent.command("rebuild-vector-index")
def rebuild_vector_index() -> None:
    settings = load_settings()
    paths = repo_paths()
    runtime = build_agent_runtime(settings, paths)

    async def rebuild() -> None:
        try:
            catalog = Catalog(paths.catalog_path)
            chunks = catalog.list_official_chunks()
            await runtime.vector_index.rebuild(
                chunks,
                catalog_fingerprint=catalog.official_fingerprint(),
                embedding_fingerprint=embedding_fingerprint(
                    model=settings.embedding.model,
                    base_url=settings.embedding.base_url,
                    dimensions=settings.embedding.dimensions,
                ),
            )
            typer.echo(json.dumps({"indexed_chunks": len(chunks)}, ensure_ascii=False))
        finally:
            await runtime.close()

    asyncio.run(rebuild())


@app.command("serve")
def serve(
    host: Annotated[str | None, typer.Option()] = None,
    port: Annotated[int | None, typer.Option()] = None,
) -> None:
    paths = repo_paths()
    settings = load_settings()
    runtime = build_agent_runtime(settings, paths)
    uvicorn.run(
        create_app(
            catalog_path=paths.catalog_path,
            index_path=paths.index_path,
            agent_repository=runtime.repository,
            run_service=runtime.run_service,
            shutdown_callback=runtime.close,
        ),
        host=host or settings.runtime.host,
        port=port or settings.runtime.port,
    )
