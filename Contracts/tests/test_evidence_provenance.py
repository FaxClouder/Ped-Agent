from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from ped_contracts import EvidenceItem, EvidenceLocator, EvidenceOrigin


def _item(**kwargs: object) -> EvidenceItem:
    return EvidenceItem(
        evidence_id="e1",
        origin=EvidenceOrigin.LOCAL_OFFICIAL,
        title="title",
        quote="quote",
        retrieved_at=datetime.now(UTC),
        content_hash="a" * 64,
        **kwargs,
    )


def test_structured_locator_round_trips_with_evidence_item() -> None:
    item = _item(structured_locator=EvidenceLocator(page=2, page_end=3, element_id="p-4"))
    assert item.structured_locator.page == 2
    assert item.structured_locator.page_end == 3


def test_structured_locator_rejects_invalid_page_range() -> None:
    with pytest.raises(ValidationError):
        EvidenceLocator(page=3, page_end=2)
