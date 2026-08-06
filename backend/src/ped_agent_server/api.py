from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from ped_agent.vision.model_registry import ModelManifestRegistry
from pydantic import BaseModel, Field

from ped_agent_server.agent_repository import TERMINAL_STATUSES, ActiveRunError, AgentRepository
from ped_agent_server.catalog import Catalog
from ped_agent_server.index import FTSIndex
from ped_agent_server.models import EvidenceHit
from ped_agent_server.retrieval import IndexStaleError, RetrievalService
from ped_agent_server.run_service import RunService
from ped_agent_server.scene_registry import SceneProfileRegistry
from ped_agent_server.vision_api import build_vision_router
from ped_agent_server.vision_repository import VisionRepository
from ped_agent_server.vision_service import VisionTaskService
from ped_agent_server.vision_storage import VisionStorage


class ConversationCreate(BaseModel):
    title: str | None = None


class RunCreate(BaseModel):
    query: str = Field(min_length=1)


def create_app(
    *,
    catalog_path: Path,
    index_path: Path,
    agent_repository: AgentRepository | None = None,
    run_service: RunService | None = None,
    vision_repository: VisionRepository | None = None,
    vision_storage: VisionStorage | None = None,
    model_registry: ModelManifestRegistry | None = None,
    scene_registry: SceneProfileRegistry | None = None,
    vision_service: VisionTaskService | None = None,
    shutdown_callback: Callable[[], Awaitable[None]] | None = None,
) -> FastAPI:
    catalog = Catalog(catalog_path)
    retrieval = RetrievalService(catalog, FTSIndex(index_path))
    repository = agent_repository or AgentRepository(catalog_path.parent / "agent.sqlite3")
    repository.initialize()
    resolved_vision_storage = vision_storage or VisionStorage(catalog_path.parent / "vision")
    resolved_vision_storage.ensure_dirs()
    resolved_vision_repository = vision_repository or VisionRepository(
        catalog_path.parent / "vision.sqlite3"
    )
    resolved_vision_repository.initialize()
    resolved_model_registry = model_registry or ModelManifestRegistry(
        resolved_vision_storage.paths.model_manifests_dir
    )
    resolved_scene_registry = scene_registry or SceneProfileRegistry(
        resolved_vision_storage.paths.scenes_dir
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        repository.interrupt_active_runs()
        if vision_service is not None:
            await vision_service.start()
        yield
        if shutdown_callback is not None:
            await shutdown_callback()
        elif run_service is not None:
            await run_service.shutdown()
        if vision_service is not None:
            await vision_service.shutdown()

    app = FastAPI(title="Ped-Agent Knowledge API", version="0.1.0", lifespan=lifespan)
    app.state.agent_repository = repository
    app.state.vision_repository = resolved_vision_repository
    app.include_router(
        build_vision_router(
            repository=resolved_vision_repository,
            storage=resolved_vision_storage,
            model_registry=resolved_model_registry,
            scene_registry=resolved_scene_registry,
            service=vision_service,
        )
    )

    @app.post("/api/conversations", status_code=status.HTTP_201_CREATED)
    def create_conversation(payload: ConversationCreate) -> dict[str, object]:
        return repository.create_conversation(payload.title)

    @app.get("/api/conversations")
    def list_conversations() -> list[dict[str, object]]:
        return repository.list_conversations()

    @app.get("/api/conversations/{conversation_id}")
    def get_conversation(conversation_id: str) -> dict[str, object]:
        result = repository.get_conversation(conversation_id)
        if result is None:
            raise HTTPException(status_code=404, detail="conversation not found")
        return result

    @app.post(
        "/api/conversations/{conversation_id}/runs",
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def create_run(conversation_id: str, payload: RunCreate) -> dict[str, str]:
        try:
            if run_service is None:
                run = repository.create_run(conversation_id, query=payload.query)
                repository.add_message(conversation_id, role="user", content=payload.query)
            else:
                run = await run_service.submit(conversation_id, payload.query)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="conversation not found") from exc
        except ActiveRunError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {
            "run_id": str(run["id"]),
            "events_url": f"/api/runs/{run['id']}/events",
        }

    @app.get("/api/runs/{run_id}/events")
    def stream_run_events(
        run_id: str,
        last_event_id: Annotated[str | None, Header(alias="Last-Event-ID")] = None,
    ) -> StreamingResponse:
        if repository.get_run(run_id) is None:
            raise HTTPException(status_code=404, detail="run not found")
        try:
            cursor = max(0, int(last_event_id or 0))
        except ValueError:
            cursor = 0

        async def event_stream():
            nonlocal cursor
            heartbeat_ticks = 0
            while True:
                events = repository.list_events(run_id, after_id=cursor)
                for event in events:
                    cursor = int(event["id"])
                    yield _format_sse(event)
                run = repository.get_run(run_id)
                if run is None or (run["status"] in TERMINAL_STATUSES and not events):
                    break
                heartbeat_ticks += 1
                if heartbeat_ticks >= 60:
                    heartbeat_ticks = 0
                    yield "event: heartbeat\ndata: {}\n\n"
                await asyncio.sleep(0.25)

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @app.post("/api/runs/{run_id}/cancel", status_code=status.HTTP_202_ACCEPTED)
    def cancel_run(run_id: str) -> dict[str, str]:
        if repository.get_run(run_id) is None:
            raise HTTPException(status_code=404, detail="run not found")
        if not repository.request_cancel(run_id):
            raise HTTPException(status_code=409, detail="run is not active")
        return {"run_id": run_id, "status": "cancelled"}

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


def _format_sse(event: dict[str, object]) -> str:
    payload = json.dumps(event["payload"], ensure_ascii=False, separators=(",", ":"))
    return f"id: {event['id']}\nevent: {event['event']}\ndata: {payload}\n\n"
