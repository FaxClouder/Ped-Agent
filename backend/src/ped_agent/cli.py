from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Annotated

import typer
import uvicorn

from ped_agent.api import create_app
from ped_agent.catalog import Catalog
from ped_agent.evaluation import audit_catalog, evaluate_rankings, load_gold
from ped_agent.importer import ImportService
from ped_agent.index import FTSIndex
from ped_agent.paths import WorkspacePaths
from ped_agent.retrieval import RetrievalService

app = typer.Typer(no_args_is_help=True)
library = typer.Typer(no_args_is_help=True)
app.add_typer(library, name="library")


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
def evaluate(gold: Path, output: Path, k: int = 5) -> None:
    paths = repo_paths()
    service = RetrievalService(Catalog(paths.catalog_path), FTSIndex(paths.index_path))
    questions = load_gold(gold)
    rankings = {
        item.question_id: [
            (hit.resource_id, hit.locator) for hit in service.search(item.query, limit=k)
        ]
        for item in questions
    }
    report = evaluate_rankings(questions, rankings, k=k)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    typer.echo(report.model_dump_json())


@app.command("audit")
def audit(output: Path) -> None:
    report = audit_catalog(Catalog(repo_paths().catalog_path))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    typer.echo(report.model_dump_json())


@app.command("serve")
def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    paths = repo_paths()
    uvicorn.run(
        create_app(catalog_path=paths.catalog_path, index_path=paths.index_path),
        host=host,
        port=port,
    )
