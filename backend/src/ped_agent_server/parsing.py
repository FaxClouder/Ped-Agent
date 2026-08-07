"""Compatibility export for knowledge parsing."""

from ped_knowledge.parsing import (
    LEGACY_CHUNK_OVERLAP as CHUNK_OVERLAP,
)
from ped_knowledge.parsing import (
    LEGACY_CHUNK_SIZE as CHUNK_SIZE,
)
from ped_knowledge.parsing import (
    PARSER_VERSION,
    parse_document,
    parse_pdf,
    write_derived_assets,
)

__all__ = [
    "CHUNK_OVERLAP",
    "CHUNK_SIZE",
    "PARSER_VERSION",
    "parse_document",
    "parse_pdf",
    "write_derived_assets",
]
