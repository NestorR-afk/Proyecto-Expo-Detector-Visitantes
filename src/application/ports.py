"""Ports used to keep the application loop independent from OpenCV."""

from dataclasses import dataclass
from collections.abc import Sequence
from typing import Any, Protocol

from src.domain.counting import CrossingLine, VisitEvent
from src.domain.models import TrackedPerson


@dataclass(frozen=True, slots=True)
class PresentationState:
    """Application data required to render one processed frame."""

    people: tuple[TrackedPerson, ...]
    events: tuple[VisitEvent, ...]
    total_visits: int
    crossing_line: CrossingLine


class FrameSource(Protocol):
    """Source of sequential image frames."""

    def read(self) -> tuple[bool, Any]:
        """Return whether a frame was read and the frame value."""

    def release(self) -> None:
        """Release the underlying capture resource."""


class PersonTracker(Protocol):
    """Produces temporary tracks from one frame."""

    def track(self, frame: Any) -> Sequence[TrackedPerson]:
        """Track people in the supplied frame."""


class FramePresenter(Protocol):
    """Renders a frame and reports whether the application should stop."""

    def show(self, frame: Any, state: PresentationState) -> bool:
        """Render one frame and return ``True`` when shutdown was requested."""

    def close(self) -> None:
        """Release presentation resources."""
