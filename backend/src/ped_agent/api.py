from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query

from ped_agent.catalog import Catalog
from ped_agent.index import FTSIndex
from ped_agent.models import EvidenceHit
from ped_agent.retrieval import IndexStaleError, RetrievalService


def create_app(*, catalog_path: Path, index_path: Path) -> FastAPI:
    app = FastAPI(title="Ped-Agent Knowledge API", version="0.1.0")
    catalog = Catalog(catalog_path)
    retrieval = RetrievalService(catalog, FTSIndex(index_path))

    @app.get("/api/library/resources")
    def list_resources(
        resource_type: str | None = None,
        topic: str | None = None,
        year: str | None = None,
        effective_status: str | None = None,
    ) -> list[dict[str, object]]:
        return catalog.list_resources(
            resource_type,
            topic=topic,
            year=year,
            effective_status=effective_status,
        )

    @app.get("/api/library/resources/{resource_id}")
    def get_resource(resource_id: str) -> dict[str, object]:
        result = catalog.get_resource(resource_id)
        if result is None:
            raise HTTPException(status_code=404, detail="resource not found")
        return result

    @app.get("/api/library/search")
    def search(
        q: Annotated[str, Query(min_length=1)],
        limit: Annotated[int, Query(ge=1, le=50)] = 10,
    ) -> list[EvidenceHit]:
        try:
            return retrieval.search(q, limit=limit)
        except IndexStaleError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    return app
