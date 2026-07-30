import httpx
import pytest
from ped_agent.agent.contracts import EvidenceOrigin

from ped_agent_server.external_search import ExternalSearchCoordinator


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
        return httpx.Response(200, text="<html><body><h1>Verified page</h1><p>Body text.</p></body></html>")
    return httpx.Response(404)


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
    assert next(item for item in result if item.origin is EvidenceOrigin.EXTERNAL_WEB).quote.startswith(
        "Verified page"
    )


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
