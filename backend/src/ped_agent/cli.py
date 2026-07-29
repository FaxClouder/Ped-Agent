from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Annotated

import typer

from ped_agent.importer import ImportService
from ped_agent.paths import WorkspacePaths

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
