from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser

import httpx

from ped_contracts.evidence import EvidenceItem, EvidenceOrigin


@dataclass(frozen=True)
class SearchCandidate:
    source: str
    title: str
    url: str | None
    doi: str | None = None
    abstract: str | None = None


class ExternalSearchCoordinator:
    def __init__(
        self,
        client: httpx.AsyncClient,
        *,
        academic_enabled: bool = True,
        parallel_api_key: str | None = None,
        max_candidates_per_source: int = 5,
        max_pages: int = 3,
    ) -> None:
        self.client = client
        self.academic_enabled = academic_enabled
        self.parallel_api_key = parallel_api_key
        self.max_candidates_per_source = max_candidates_per_source
        self.max_pages = max_pages

    async def search(self, query: str) -> list[EvidenceItem]:
        semantic, openalex, web = await asyncio.gather(
            self._semantic_scholar(query) if self.academic_enabled else _empty_candidates(),
            self._openalex(query) if self.academic_enabled else _empty_candidates(),
            self._parallel(query),
        )
        academic = self._deduplicate([*semantic, *openalex])
        evidence = [self._academic_evidence(item) for item in academic if item.abstract]
        pages = await asyncio.gather(
            *(self._fetch_web(item) for item in web[: self.max_pages]),
        )
        evidence.extend(item for item in pages if item is not None)
        return evidence

    async def _semantic_scholar(self, query: str) -> list[SearchCandidate]:
        try:
            response = await self.client.get(
                "https://api.semanticscholar.org/graph/v1/paper/search",
                params={
                    "query": query,
                    "limit": self.max_candidates_per_source,
                    "fields": "title,abstract,url,externalIds",
                },
            )
            response.raise_for_status()
        except httpx.HTTPError:
            return []
        return [
            SearchCandidate(
                source="semantic_scholar",
                title=str(item.get("title") or "Untitled"),
                url=item.get("url"),
                doi=(item.get("externalIds") or {}).get("DOI"),
                abstract=item.get("abstract"),
            )
            for item in response.json().get("data", [])[: self.max_candidates_per_source]
        ]

    async def _openalex(self, query: str) -> list[SearchCandidate]:
        try:
            response = await self.client.get(
                "https://api.openalex.org/works",
                params={"search": query, "per-page": self.max_candidates_per_source},
            )
            response.raise_for_status()
        except httpx.HTTPError:
            return []
        return [
            SearchCandidate(
                source="openalex",
                title=str(item.get("display_name") or "Untitled"),
                url=(item.get("primary_location") or {}).get("landing_page_url"),
                doi=_normalize_doi(item.get("doi")),
                abstract=_restore_abstract(item.get("abstract_inverted_index")),
            )
            for item in response.json().get("results", [])[: self.max_candidates_per_source]
        ]

    async def _parallel(self, query: str) -> list[SearchCandidate]:
        if not self.parallel_api_key:
            return []
        try:
            response = await self.client.post(
                "https://api.parallel.ai/v1beta/search",
                headers={"Authorization": f"Bearer {self.parallel_api_key}"},
                json={"objective": query, "max_results": self.max_candidates_per_source},
            )
            response.raise_for_status()
        except httpx.HTTPError:
            return []
        return [
            SearchCandidate(
                source="parallel",
                title=str(item.get("title") or "Untitled"),
                url=item.get("url"),
            )
            for item in response.json().get("results", [])[: self.max_candidates_per_source]
            if item.get("url")
        ]

    async def _fetch_web(self, candidate: SearchCandidate) -> EvidenceItem | None:
        if candidate.url is None:
            return None
        try:
            response = await self.client.get(candidate.url, follow_redirects=True)
            response.raise_for_status()
        except httpx.HTTPError:
            return None
        parser = _VisibleTextParser()
        parser.feed(response.text)
        quote = parser.text()
        if not quote:
            return None
        return _evidence(candidate, quote, EvidenceOrigin.EXTERNAL_WEB)

    @staticmethod
    def _academic_evidence(candidate: SearchCandidate) -> EvidenceItem:
        return _evidence(candidate, candidate.abstract or "", EvidenceOrigin.EXTERNAL_ACADEMIC)

    @staticmethod
    def _deduplicate(candidates: list[SearchCandidate]) -> list[SearchCandidate]:
        result: list[SearchCandidate] = []
        seen: set[str] = set()
        for candidate in candidates:
            key = (candidate.doi or candidate.url or candidate.title).casefold()
            if key in seen:
                continue
            seen.add(key)
            result.append(candidate)
        return result


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth and data.strip():
            self._parts.append(data.strip())

    def text(self) -> str:
        return " ".join(self._parts)[:12000]


def _restore_abstract(index: dict[str, list[int]] | None) -> str | None:
    if not index:
        return None
    positioned = sorted(
        (position, word) for word, positions in index.items() for position in positions
    )
    return " ".join(word for _, word in positioned)


async def _empty_candidates() -> list[SearchCandidate]:
    return []


def _normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    return value.removeprefix("https://doi.org/").removeprefix("http://doi.org/")


def _evidence(
    candidate: SearchCandidate,
    quote: str,
    origin: EvidenceOrigin,
) -> EvidenceItem:
    content_hash = hashlib.sha256(quote.encode("utf-8")).hexdigest()
    identity = candidate.doi or candidate.url or f"{candidate.source}:{candidate.title}"
    evidence_id = f"external:{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:24]}"
    return EvidenceItem(
        evidence_id=evidence_id,
        origin=origin,
        title=candidate.title,
        quote=quote,
        url=candidate.url,
        doi=candidate.doi,
        publisher=candidate.source,
        authority="primary" if origin is EvidenceOrigin.EXTERNAL_ACADEMIC else "secondary",
        retrieved_at=datetime.now(UTC),
        content_hash=content_hash,
        score=0.0,
    )
