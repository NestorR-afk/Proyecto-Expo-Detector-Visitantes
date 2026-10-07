"""Domain models for trajectory-based visit events."""

from dataclasses import dataclass

from src.domain.counting.geometry import CrossingDirection
from src.domain.models import TrackingID


@dataclass(frozen=True, slots=True)
class VisitEvent:
    """A confirmed geometric crossing by one temporary tracking ID."""

    tracking_id: TrackingID
    direction: CrossingDirection
