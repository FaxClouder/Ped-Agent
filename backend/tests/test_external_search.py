import httpx
import pytest
from langsmith.run_helpers import is_traceable_function, tracing_context
from ped_agent.agent.contracts import EvidenceOrigin

from ped_agent_server.evidence_executor import HybridLocalEvidenceRetriever
from ped_agent_server.external_search import ExternalSearchCoordinator, SearchCandidate
from ped_agent_server.hybrid_retrieval import HybridRetrievalResult


class FakeTraceClient:
    otel_exporter = None

    def __init__(self) -> None:
        self.created: list[dict[str, object]] = []
        self.updated: list[dict[str, object]] = []

    def create_run(self, **kwargs: object) -> None:
        self.created.append(kwargs)

    def update_run(self, **kwargs: object) -> None:
        self.updated.append(kwargs)


def mock_response(request: httpx.Request) -> httpx.Response:
    if request.url.host == "api.semanticscholar.org":
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "paperId": "s2-1",
                        "title": "Bottleneck study",
                        "abstract": "A verified academic abstract.",
                        "url": "https://example.org/paper",
                        "externalIds": {"DOI": "10.1000/paper"},
                    }
                ]
            },
        )
    if request.url.host == "api.openalex.org":
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "id": "https://openalex.org/W1",
                        "display_name": "OpenAlex study",
                        "doi": "https://doi.org/10.1000/openalex",
                        "abstract_inverted_index": {"Verified": [0], "abstract": [1]},
                        "primary_location": {"landing_page_url": "https://example.org/openalex"},
                    }
                ]
            },
        )
    if request.url.host == "api.parallel.ai":
        return httpx.Response(
            200,
            json={"results": [{"title": "Web result", "url": "https://site.test/page"}]},
        )
    if request.url.host == "site.test":
        return httpx.Response(
            200, text="<html><body><h1>Verified page</h1><p>Body text.</p></body></html>"
        )
    return httpx.Response(404)


def test_external_search_boundaries_are_traceable() -> None:
    assert is_traceable_function(HybridLocalEvidenceRetriever.retrieve)
    assert is_traceable_function(ExternalSearchCoordinator.search)
    assert is_traceable_function(ExternalSearchCoordinator._semantic_scholar)
    assert is_traceable_function(ExternalSearchCoordinator._openalex)
    assert is_traceable_function(ExternalSearchCoordinator._parallel)
    assert is_traceable_function(ExternalSearchCoordinator._fetch_web)


@pytest.mark.asyncio
async def test_enabled_trace_sanitizes_mapping_candidate_before_business_error() -> None:
    candidate = {
        "source": "parallel",
        "title": "Unsafe mapping",
        "url": "https://user:password@example.org/path?token=secret#fragment",
        "doi": None,
        "abstract": "private abstract",
    }
    trace_client = FakeTraceClient()
    async with httpx.AsyncClient(transport=httpx.MockTransport(mock_response)) as client:
        coordinator = ExternalSearchCoordinator(client)
        with tracing_context(enabled=True, client=trace_client), pytest.raises(AttributeError):
            await coordinator._fetch_web(candidate)  # type: ignore[arg-type]

    assert trace_client.created[0]["inputs"] == {
        "candidate": {
            "source": "parallel",
            "title": "Unsafe mapping",
            "url": "https://example.org/path",
            "doi": None,
        }
    }
    rendered = str(trace_client.created)
    for private_value in ("password", "token", "secret", "fragment", "private abstract"):
        assert private_value not in rendered


@pytest.mark.asyncio
async def test_enabled_trace_updates_failed_source_span_without_processor_error() -> None:
    def invalid_json_response(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not valid json")

    trace_client = FakeTraceClient()
    async with httpx.AsyncClient(transport=httpx.MockTransport(invalid_json_response)) as client:
        coordinator = ExternalSearchCoordinator(client)
        with tracing_context(enabled=True, client=trace_client), pytest.raises(ValueError):
            await coordinator._semantic_scholar("bottleneck")

    assert len(trace_client.created) == 1
    assert trace_client.created[0]["inputs"] == {"query": "bottleneck"}
    assert len(trace_client.updated) == 1
    assert trace_client.updated[0]["outputs"] == {"count": 0, "candidates": []}
    assert trace_client.updated[0]["error"] is not None
    assert trace_client.updated[0]["end_time"] is not None


@pytest.mark.asyncio
async def test_enabled_local_retrieval_trace_redacts_query_without_changing_business_input() -> (
    None
):
    class RecordingHybrid:
        def __init__(self) -> None:
            self.queries: list[str] = []

        async def retrieve(self, query: str) -> HybridRetrievalResult:
            self.queries.append(query)
            return HybridRetrievalResult(items=[])

    combined_query = "private history current question"
    hybrid = RecordingHybrid()
    trace_client = FakeTraceClient()

    with tracing_context(enabled=True, client=trace_client):  # type: ignore[arg-type]
        batch = await HybridLocalEvidenceRetriever(hybrid).retrieve(combined_query)  # type: ignore[arg-type]

    assert hybrid.queries == [combined_query]
    assert batch.items == []
    assert trace_client.created[0]["inputs"] == {"query": "[REDACTED]"}
    rendered = str(trace_client.created)
    assert "private history" not in rendered
    assert "current question" not in rendered


@pytest.mark.asyncio
async def test_enabled_external_search_trace_keeps_only_current_query() -> None:
    current_query = "current question"
    trace_client = FakeTraceClient()
    async with httpx.AsyncClient(transport=httpx.MockTransport(mock_response)) as client:
        coordinator = ExternalSearchCoordinator(client, academic_enabled=False)
        with tracing_context(enabled=True, client=trace_client):  # type: ignore[arg-type]
            result = await coordinator.search(current_query)

    assert result == []
    assert trace_client.created
    assert all(item["inputs"] == {"query": current_query} for item in trace_client.created)
    rendered = str(trace_client.created)
    assert "self" not in rendered
    assert "private history" not in rendered


@pytest.mark.asyncio
async def test_enabled_trace_omits_self_candidate_secrets_and_fetched_quote() -> None:
    def private_web_response(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html><body>PRIVATE_QUOTE</body></html>")

    candidate = SearchCandidate(
        source="parallel",
        title="Safe page",
        url="https://user:password@site.test/page?token=secret#fragment",
        abstract="PRIVATE_ABSTRACT",
    )
    trace_client = FakeTraceClient()
    async with httpx.AsyncClient(transport=httpx.MockTransport(private_web_response)) as client:
        coordinator = ExternalSearchCoordinator(
            client,
            parallel_api_key="PRIVATE_CLIENT_SECRET",
        )
        with tracing_context(enabled=True, client=trace_client):  # type: ignore[arg-type]
            result = await coordinator._fetch_web(candidate)

    assert result is not None
    assert trace_client.created[0]["inputs"] == {
        "candidate": {
            "source": "parallel",
            "title": "Safe page",
            "url": "https://site.test/page",
            "doi": None,
        }
    }
    assert trace_client.updated[0]["outputs"] == {
        "count": 1,
        "evidence": [
            {
                "evidence_id": result.evidence_id,
                "origin": "external_web",
                "title": "Safe page",
                "locator": None,
                "content_hash": result.content_hash,
            }
        ],
    }
    rendered = str([trace_client.created, trace_client.updated])
    for private_value in (
        "self",
        "password",
        "token",
        "secret",
        "fragment",
        "PRIVATE_ABSTRACT",
        "PRIVATE_CLIENT_SECRET",
        "PRIVATE_QUOTE",
    ):
        assert private_value not in rendered


@pytest.mark.asyncio
async def test_disabled_trace_does_not_call_client_or_change_business_result() -> None:
    def web_response(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html><body>Verified page</body></html>")

    trace_client = FakeTraceClient()
    async with httpx.AsyncClient(transport=httpx.MockTransport(web_response)) as client:
        coordinator = ExternalSearchCoordinator(client)
        candidate = SearchCandidate(
            source="parallel",
            title="Page",
            url="https://site.test/page",
        )
        with tracing_context(enabled=False, client=trace_client):  # type: ignore[arg-type]
            result = await coordinator._fetch_web(candidate)

    assert result is not None
    assert result.quote == "Verified page"
    assert trace_client.created == []
    assert trace_client.updated == []


@pytest.mark.asyncio
async def test_external_search_normalizes_academic_and_fetched_web_evidence() -> None:
    async with httpx.AsyncClient(transport=httpx.MockTransport(mock_response)) as client:
        result = await ExternalSearchCoordinator(
            client,
            parallel_api_key="parallel-key",
        ).search("bottleneck")

    assert {item.origin for item in result} == {
        EvidenceOrigin.EXTERNAL_ACADEMIC,
        EvidenceOrigin.EXTERNAL_WEB,
    }
    assert sum(item.origin is EvidenceOrigin.EXTERNAL_ACADEMIC for item in result) == 2
    assert next(
        item for item in result if item.origin is EvidenceOrigin.EXTERNAL_WEB
    ).quote.startswith("Verified page")


def failing_web_response(request: httpx.Request) -> httpx.Response:
    if request.url.host == "api.parallel.ai":
        return httpx.Response(
            200,
            json={"results": [{"title": "Unfetched", "url": "https://bad.test/page"}]},
        )
    if request.url.host in {"api.semanticscholar.org", "api.openalex.org"}:
        return httpx.Response(200, json={"data": [], "results": []})
    return httpx.Response(503)


@pytest.mark.asyncio
async def test_external_search_drops_web_results_when_page_fetch_fails() -> None:
    async with httpx.AsyncClient(transport=httpx.MockTransport(failing_web_response)) as client:
        result = await ExternalSearchCoordinator(
            client,
            parallel_api_key="parallel-key",
        ).search("bottleneck")

    assert result == []
