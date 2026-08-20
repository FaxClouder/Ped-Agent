import httpx
import pytest

from ped_contracts.evidence import EvidenceOrigin
from ped_research_agent.external_search import ExternalSearchCoordinator, SearchCandidate


def mock_response(request: httpx.Request) -> httpx.Response:
    if request.url.host == "api.semanticscholar.org":
        return httpx.Response(
            200,
            json={
                "data": [
                    {
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
                        "display_name": "OpenAlex study",
                        "doi": "https://doi.org/10.1000/openalex",
                        "abstract_inverted_index": {"Verified": [0], "abstract": [1]},
                        "primary_location": {
                            "landing_page_url": "https://example.org/openalex"
                        },
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
        return httpx.Response(200, text="<html><body>Verified page</body></html>")
    return httpx.Response(404)


@pytest.mark.asyncio
async def test_external_search_normalizes_academic_and_web_evidence() -> None:
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


def test_external_search_deduplicates_candidates_by_doi() -> None:
    candidates = [
        SearchCandidate("semantic_scholar", "First", None, doi="10.1000/shared"),
        SearchCandidate("openalex", "Second", None, doi="10.1000/shared"),
    ]

    assert ExternalSearchCoordinator._deduplicate(candidates) == [candidates[0]]
