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

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+|[\u3400-\u9fff]|[^\s]")
SKIPPED_TYPES = {ElementType.IMAGE}


@dataclass(frozen=True)
class _ElementGroup:
    elements: tuple[DocumentElement, ...]
    token_count: int


class HierarchicalChunker:
    def __init__(self, policy: ChunkingPolicy | None = None) -> None:
        self.policy = policy or ChunkingPolicy()

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
                    child_text,
                    parent_id=parent_id,
                )
                output.append(
                    KnowledgeChunk(
                        chunk_id=child_id,
                        resource_id=document.resource_id,
                        version_id=document.version_id,
                        ordinal=ordinal,
                        text=child_text,
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
            token_count = len(_tokens(element.text))
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

    def _child_texts(self, text: str) -> list[str]:
        matches = list(TOKEN_PATTERN.finditer(text))
        if not matches:
            return []
        window = min(self.policy.child_target_tokens, self.policy.child_max_tokens)
        overlap = min(self.policy.child_overlap_tokens, max(0, window - 1))
        results: list[str] = []
        start = 0
        while start < len(matches):
            end = min(len(matches), start + window)
            character_start = matches[start].start()
            character_end = matches[end - 1].end()
            child = text[character_start:character_end].strip()
            if child:
                results.append(child)
            if end == len(matches):
                break
            start = end - overlap
        return results


def _tokens(text: str) -> list[str]:
    return [match.group(0) for match in TOKEN_PATTERN.finditer(text)]


def _render_elements(elements: tuple[DocumentElement, ...]) -> str:
    heading = " > ".join(elements[0].heading_path)
    body = "\n\n".join(item.text.strip() for item in elements if item.text.strip())
    return f"{heading}\n\n{body}".strip() if heading else body


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
            lineage,
            hashlib.sha256(text.encode("utf-8")).hexdigest(),
        )
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
    return f"{document.resource_id}:{document.version_id[:12]}:{level.value}:{digest}"


__all__ = ["ChunkingPolicy", "HierarchicalChunker"]
