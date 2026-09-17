"""Deterministic parent-child chunking over canonical document elements."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from ped_knowledge.contracts import (
    CanonicalDocument,
    ChunkingPolicy,
    ChunkLevel,
    DocumentElement,
    ElementType,
    KnowledgeChunk,
)
from ped_knowledge.tokenization import RegexTokenCounter, TOKEN_PATTERN, TokenCounter

SKIPPED_TYPES = {ElementType.IMAGE}


@dataclass(frozen=True)
class _ElementGroup:
    elements: tuple[DocumentElement, ...]
    token_count: int


@dataclass(frozen=True)
class _ChildText:
    text: str
    character_start: int
    character_end: int
    hard_split: bool = False


@dataclass(frozen=True)
class _BoundaryUnit:
    text: str
    character_start: int
    character_end: int
    token_count: int
    hard_split: bool = False


_ABBREVIATIONS = {
    "dr",
    "e.g",
    "et al",
    "fig",
    "i.e",
    "mr",
    "mrs",
    "ms",
    "prof",
    "ref",
    "sec",
    "vs",
}


class HierarchicalChunker:
    def __init__(
        self,
        policy: ChunkingPolicy | None = None,
        *,
        token_counter: TokenCounter | None = None,
    ) -> None:
        self.policy = policy or ChunkingPolicy()
        self.token_counter = token_counter or RegexTokenCounter()

    def chunk(self, document: CanonicalDocument) -> list[KnowledgeChunk]:
        groups = self._parent_groups(document)
        output: list[KnowledgeChunk] = []
        ordinal = 0
        for parent_index, group in enumerate(groups):
            parent_text = _render_elements(group.elements)
            heading_path = group.elements[0].heading_path
            parent_id = _chunk_id(
                document,
                self.policy.policy_version,
                ChunkLevel.PARENT,
                parent_index,
                group.elements,
                parent_text,
                tokenizer_fingerprint=self.token_counter.fingerprint,
            )
            parent = KnowledgeChunk(
                chunk_id=parent_id,
                resource_id=document.resource_id,
                version_id=document.version_id,
                ordinal=ordinal,
                text=parent_text,
                page_start=min(item.page_number for item in group.elements),
                page_end=max(item.page_number for item in group.elements),
                locator=_group_locator(group.elements),
                section=heading_path[-1] if heading_path else None,
                parser_version=document.parser_version,
                chunk_level=ChunkLevel.PARENT,
                heading_path=heading_path,
                policy_version=self.policy.policy_version,
                element_ids=tuple(item.element_id for item in group.elements),
                token_count=self.token_counter.count(parent_text),
                tokenizer_fingerprint=self.token_counter.fingerprint,
            )
            output.append(parent)
            ordinal += 1
            for child_index, child_text in enumerate(self._child_texts(parent_text)):
                child_id = _chunk_id(
                    document,
                    self.policy.policy_version,
                    ChunkLevel.CHILD,
                    child_index,
                    group.elements,
                    child_text.text,
                    parent_id=parent_id,
                    tokenizer_fingerprint=self.token_counter.fingerprint,
                )
                output.append(
                    KnowledgeChunk(
                        chunk_id=child_id,
                        resource_id=document.resource_id,
                        version_id=document.version_id,
                        ordinal=ordinal,
                        text=child_text.text,
                        page_start=parent.page_start,
                        page_end=parent.page_end,
                        locator=parent.locator,
                        section=parent.section,
                        parser_version=document.parser_version,
                        chunk_level=ChunkLevel.CHILD,
                        parent_chunk_id=parent_id,
                        heading_path=heading_path,
                        policy_version=self.policy.policy_version,
                        element_ids=parent.element_ids,
                        token_count=self.token_counter.count(child_text.text),
                        tokenizer_fingerprint=self.token_counter.fingerprint,
                        character_start=child_text.character_start,
                        character_end=child_text.character_end,
                        hard_split=child_text.hard_split,
                    )
                )
                ordinal += 1
        if not any(item.chunk_level is ChunkLevel.CHILD for item in output):
            raise ValueError("canonical document produced no child chunks")
        return output

    def _parent_groups(self, document: CanonicalDocument) -> list[_ElementGroup]:
        elements = [
            item
            for item in document.elements
            if item.element_type not in SKIPPED_TYPES and item.text.strip()
        ]
        groups: list[_ElementGroup] = []
        current: list[DocumentElement] = []
        current_tokens = 0
        current_heading: tuple[str, ...] | None = None
        for element in elements:
            token_count = self.token_counter.count(element.text)
            heading_changed = current and element.heading_path != current_heading
            would_overflow = (
                current and current_tokens + token_count > self.policy.parent_max_tokens
            )
            if heading_changed or would_overflow:
                groups.append(_ElementGroup(tuple(current), current_tokens))
                current = []
                current_tokens = 0
            current.append(element)
            current_tokens += token_count
            current_heading = element.heading_path
            if current_tokens >= self.policy.parent_target_tokens:
                groups.append(_ElementGroup(tuple(current), current_tokens))
                current = []
                current_tokens = 0
                current_heading = None
        if current:
            groups.append(_ElementGroup(tuple(current), current_tokens))
        return groups

    def _child_texts(self, text: str) -> list[_ChildText]:
        if self.policy.policy_version == "parent-child-v2":
            return self._boundary_child_texts(text)
        if isinstance(self.token_counter, RegexTokenCounter):
            return self._regex_child_texts(text)
        return self._token_child_texts(text)

    def _boundary_child_texts(self, text: str) -> list[_ChildText]:
        units: list[_BoundaryUnit] = []
        for character_start, character_end in _sentence_spans(text):
            unit_text = text[character_start:character_end]
            token_count = self.token_counter.count(unit_text)
            if token_count <= self.policy.child_max_tokens:
                units.append(
                    _BoundaryUnit(
                        text=unit_text,
                        character_start=character_start,
                        character_end=character_end,
                        token_count=token_count,
                    )
                )
            else:
                units.extend(
                    self._split_oversized_unit(
                        text,
                        character_start=character_start,
                        character_end=character_end,
                    )
                )
        return self._merge_boundary_units(text, units)

    def _split_oversized_unit(
        self,
        source_text: str,
        *,
        character_start: int,
        character_end: int,
    ) -> list[_BoundaryUnit]:
        unit_text = source_text[character_start:character_end]
        token_ids = self.token_counter.encode(unit_text)
        window = min(self.policy.child_target_tokens, self.policy.child_max_tokens)
        overlap = min(self.policy.child_overlap_tokens, max(0, window - 1))
        output: list[_BoundaryUnit] = []
        start = 0
        search_start = 0
        while start < len(token_ids):
            end = min(len(token_ids), start + window)
            decoded = self.token_counter.decode(token_ids[start:end]).strip()
            local_start = unit_text.find(decoded, search_start)
            if local_start < 0:
                local_start = unit_text.find(decoded)
            if local_start < 0:
                raise ValueError("decoded child text cannot be located in source text")
            local_end = local_start + len(decoded)
            output.append(
                _BoundaryUnit(
                    text=decoded,
                    character_start=character_start + local_start,
                    character_end=character_start + local_end,
                    token_count=self.token_counter.count(decoded),
                    hard_split=True,
                )
            )
            if end == len(token_ids):
                break
            search_start = local_start + 1
            start = end - overlap
        return output

    def _merge_boundary_units(
        self,
        source_text: str,
        units: list[_BoundaryUnit],
    ) -> list[_ChildText]:
        if not units:
            return []
        output: list[_ChildText] = []
        current: list[_BoundaryUnit] = []
        current_tokens = 0

        def emit() -> None:
            if not current:
                return
            start = current[0].character_start
            end = current[-1].character_end
            if output and (
                output[-1].character_start == start
                and output[-1].character_end == end
            ):
                return
            output.append(
                _ChildText(
                    text=source_text[start:end].strip(),
                    character_start=start,
                    character_end=end,
                    hard_split=any(unit.hard_split for unit in current),
                )
            )

        for index, unit in enumerate(units):
            if unit.hard_split:
                emit()
                current = []
                current_tokens = 0
                output.append(
                    _ChildText(
                        text=unit.text,
                        character_start=unit.character_start,
                        character_end=unit.character_end,
                        hard_split=True,
                    )
                )
                continue
            if current and current_tokens + unit.token_count > self.policy.child_max_tokens:
                emit()
                current = _overlap_units(current, self.policy.child_overlap_tokens)
                current_tokens = sum(item.token_count for item in current)
                while current and current_tokens + unit.token_count > self.policy.child_max_tokens:
                    current_tokens -= current.pop(0).token_count
            current.append(unit)
            current_tokens += unit.token_count
            if current_tokens >= self.policy.child_target_tokens:
                emit()
                if index == len(units) - 1:
                    current = []
                    current_tokens = 0
                else:
                    current = _overlap_units(current, self.policy.child_overlap_tokens)
                    current_tokens = sum(item.token_count for item in current)
        if current:
            candidate_start = current[0].character_start
            candidate_end = current[-1].character_end
            if not output or (
                output[-1].character_start != candidate_start
                or output[-1].character_end != candidate_end
            ):
                emit()
        return output

    def _regex_child_texts(self, text: str) -> list[_ChildText]:
        matches = list(TOKEN_PATTERN.finditer(text))
        if not matches:
            return []
        window = min(self.policy.child_target_tokens, self.policy.child_max_tokens)
        overlap = min(self.policy.child_overlap_tokens, max(0, window - 1))
        results: list[_ChildText] = []
        start = 0
        while start < len(matches):
            end = min(len(matches), start + window)
            character_start = matches[start].start()
            character_end = matches[end - 1].end()
            raw_child = text[character_start:character_end]
            child = raw_child.strip()
            if child:
                left_trim = len(raw_child) - len(raw_child.lstrip())
                right_trim = len(raw_child) - len(raw_child.rstrip())
                results.append(
                    _ChildText(
                        text=child,
                        character_start=character_start + left_trim,
                        character_end=character_end - right_trim,
                    )
                )
            if end == len(matches):
                break
            start = end - overlap
        return results

    def _token_child_texts(self, text: str) -> list[_ChildText]:
        token_ids = self.token_counter.encode(text)
        if not token_ids:
            return []
        window = min(self.policy.child_target_tokens, self.policy.child_max_tokens)
        overlap = min(self.policy.child_overlap_tokens, max(0, window - 1))
        results: list[_ChildText] = []
        start = 0
        search_start = 0
        while start < len(token_ids):
            end = min(len(token_ids), start + window)
            child = self.token_counter.decode(token_ids[start:end]).strip()
            if child:
                character_start = text.find(child, search_start)
                if character_start < 0:
                    character_start = text.find(child)
                if character_start < 0:
                    raise ValueError("decoded child text cannot be located in source text")
                character_end = character_start + len(child)
                results.append(
                    _ChildText(
                        text=child,
                        character_start=character_start,
                        character_end=character_end,
                        hard_split=len(token_ids) > self.policy.child_max_tokens,
                    )
                )
                search_start = character_start + 1
            if end == len(token_ids):
                break
            start = end - overlap
        return results


def _render_elements(elements: tuple[DocumentElement, ...]) -> str:
    heading = " > ".join(elements[0].heading_path)
    body = "\n\n".join(item.text.strip() for item in elements if item.text.strip())
    return f"{heading}\n\n{body}".strip() if heading else body


def _sentence_spans(text: str) -> list[tuple[int, int]]:
    """Return deterministic paragraph/sentence spans without external models."""
    spans: list[tuple[int, int]] = []
    start = 0
    for index, character in enumerate(text):
        boundary = character in "。！？!?"
        if character == ".":
            prefix = text[start:index].rstrip()
            word_match = re.search(r"([A-Za-z]+(?:\s+[A-Za-z]+)?)$", prefix)
            abbreviation = word_match.group(1).lower() if word_match else ""
            next_character = text[index + 1 : index + 2]
            boundary = abbreviation not in _ABBREVIATIONS and (
                not next_character or next_character.isspace()
            )
        paragraph_break = character == "\n" and text[index : index + 2] == "\n\n"
        if boundary or paragraph_break:
            end = index + 1 if boundary else index
            unit_start, unit_end = _trim_span(text, start, end)
            if unit_start < unit_end:
                spans.append((unit_start, unit_end))
            start = index + 1 if boundary else index + 2
    unit_start, unit_end = _trim_span(text, start, len(text))
    if unit_start < unit_end:
        spans.append((unit_start, unit_end))
    return spans


def _trim_span(text: str, start: int, end: int) -> tuple[int, int]:
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    return start, end


def _overlap_units(
    units: list[_BoundaryUnit],
    overlap_tokens: int,
) -> list[_BoundaryUnit]:
    if overlap_tokens <= 0:
        return []
    overlap: list[_BoundaryUnit] = []
    token_count = 0
    for unit in reversed(units):
        overlap.insert(0, unit)
        token_count += unit.token_count
        if token_count >= overlap_tokens:
            break
    return overlap


def _group_locator(elements: tuple[DocumentElement, ...]) -> str:
    first = elements[0]
    last = elements[-1]
    if first.page_number == last.page_number:
        return first.locator
    return f"p.{first.page_number}-{last.page_number}"


def _chunk_id(
    document: CanonicalDocument,
    policy_version: str,
    level: ChunkLevel,
    index: int,
    elements: tuple[DocumentElement, ...],
    text: str,
    *,
    parent_id: str = "",
    tokenizer_fingerprint: str,
) -> str:
    lineage = ",".join(item.element_id for item in elements)
    payload = "|".join(
        (
            document.resource_id,
            document.version_id,
            policy_version,
            level.value,
            str(index),
            parent_id,
            tokenizer_fingerprint,
            lineage,
            hashlib.sha256(text.encode("utf-8")).hexdigest(),
        )
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
    return f"{document.resource_id}:{document.version_id[:12]}:{level.value}:{digest}"


__all__ = ["ChunkingPolicy", "HierarchicalChunker"]
