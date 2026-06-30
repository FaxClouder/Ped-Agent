from __future__ import annotations

import pytest
from pydantic import ValidationError

from ped_agent.models.trajectory import PedestrianTrack, Position


def test_pedestrian_track_rejects_mismatched_confidence_length():
    with pytest.raises(ValidationError, match="confidence length must match frames length"):
        PedestrianTrack(
            track_id=1,
            frames=[0, 1],
            positions=[Position(x=0, y=0), Position(x=1, y=0)],
            timestamps=[0.0, 1.0],
            confidence=[0.9],
        )
