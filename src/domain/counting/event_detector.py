"""Stateful trajectory processing that emits at most one event per active ID."""

from dataclasses import dataclass
from collections.abc import Sequence

from src.domain.counting.crossing import detect_crossing
from src.domain.counting.geometry import (
    CrossingDirection,
    CrossingLine,
    PointSide,
    segments_intersect,
)
from src.domain.counting.models import VisitEvent
from src.domain.models import Point, TrackedPerson, TrackingID


@dataclass(slots=True)
class _TrajectoryState:
    last_centroid: Point
    last_non_neutral_side: PointSide | None
    counted: bool
    last_seen_at: float


class TrajectoryEventDetector:
    """Convert active tracked trajectories into one-shot visit events.

    A tracking ID is only a temporary key for this state. Once its state
    expires, a later track using the same numeric ID starts a new cycle.
    """

    def __init__(
        self,
        crossing_line: CrossingLine,
        track_timeout_seconds: float = 5.0,
    ) -> None:
        if track_timeout_seconds <= 0:
            raise ValueError("track_timeout_seconds must be positive")

        self._crossing_line = crossing_line
        self._track_timeout_seconds = track_timeout_seconds
        self._states: dict[TrackingID, _TrajectoryState] = {}

    @property
    def active_track_count(self) -> int:
        """Return the number of non-expired trajectory states."""
        return len(self._states)

    def update(
        self,
        tracked_people: Sequence[TrackedPerson],
        now: float,
    ) -> tuple[VisitEvent, ...]:
        """Process one frame worth of tracks and return new events only."""
        self._expire(now)
        events: list[VisitEvent] = []

        for person in tracked_people:
            state = self._states.get(person.tracking_id)
            if state is None:
                self._states[person.tracking_id] = self._new_state(person, now)
                continue

            event = self._process_existing_state(state, person, now)
            if event is not None:
                events.append(event)

        return tuple(events)

    def reset(self) -> None:
        """Discard active trajectory state after a camera/tracker reset."""
        self._states.clear()

    def _new_state(
        self,
        person: TrackedPerson,
        now: float,
    ) -> _TrajectoryState:
        side = self._crossing_line.side(person.centroid)
        return _TrajectoryState(
            last_centroid=person.centroid,
            last_non_neutral_side=None if side is PointSide.ON_LINE else side,
            counted=False,
            last_seen_at=now,
        )

    def _process_existing_state(
        self,
        state: _TrajectoryState,
        person: TrackedPerson,
        now: float,
    ) -> VisitEvent | None:
        current_side = self._crossing_line.side(person.centroid)
        event = None

        if not state.counted:
            result = detect_crossing(
                state.last_centroid,
                person.centroid,
                self._crossing_line,
            )
            if result.crossed and result.direction is not None:
                event = VisitEvent(person.tracking_id, result.direction)
            elif (
                current_side is not PointSide.ON_LINE
                and state.last_non_neutral_side is not None
                and current_side is not state.last_non_neutral_side
                and segments_intersect(
                    state.last_centroid,
                    person.centroid,
                    self._crossing_line.start,
                    self._crossing_line.end,
                )
            ):
                event = VisitEvent(
                    person.tracking_id,
                    _direction(state.last_non_neutral_side, current_side),
                )

        state.last_centroid = person.centroid
        state.last_seen_at = now
        if current_side is not PointSide.ON_LINE:
            state.last_non_neutral_side = current_side
        if event is not None:
            state.counted = True

        return event

    def _expire(self, now: float) -> None:
        expired_ids = [
            tracking_id
            for tracking_id, state in self._states.items()
            if now - state.last_seen_at >= self._track_timeout_seconds
        ]
        for tracking_id in expired_ids:
            del self._states[tracking_id]


def _direction(
    previous_side: PointSide,
    current_side: PointSide,
) -> CrossingDirection:
    if previous_side is PointSide.SIDE_A and current_side is PointSide.SIDE_B:
        return CrossingDirection.SIDE_A_TO_B
    return CrossingDirection.SIDE_B_TO_A
