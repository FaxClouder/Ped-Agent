"""Compatibility export for the knowledge Catalog.

Active runtime code imports :mod:`ped_knowledge.storage` directly.
"""

from ped_knowledge.storage import SCHEMA, Catalog

__all__ = ["SCHEMA", "Catalog"]
