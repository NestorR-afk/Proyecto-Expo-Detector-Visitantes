"""Application orchestration for tracking and visit-event generation."""

from collections.abc import Callable
from time import monotonic

from src.application.ports import (
    FramePresenter,
    FrameSource,
    PersonTracker,
    PresentationState,
)
from src.domain.counting import CrossingLine, TrajectoryEventDetector


class TrackingLoop:
    """Coordinate capture, tracking, event detection, and presentation."""

    def __init__(
        self,
        frame_source: FrameSource,
        tracker: PersonTracker,
        event_detector: TrajectoryEventDetector,
        crossing_line: CrossingLine,
        presenter: FramePresenter,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self._frame_source = frame_source
        self._tracker = tracker
        self._event_detector = event_detector
        self._crossing_line = crossing_line
        self._presenter = presenter
        self._clock = clock
        self._total_visits = 0

    @property
    def total_visits(self) -> int:
        """Return the number of events produced during this process run."""
        return self._total_visits

    def run(self) -> None:
        """Process frames until capture ends or the presenter requests shutdown."""
        try:
            while True:
                frame_ok, frame = self._frame_source.read()
                if not frame_ok:
                    break

                people = tuple(self._tracker.track(frame))
                events = self._event_detector.update(people, now=self._clock())
                self._total_visits += len(events)
                state = PresentationState(
                    people=people,
                    events=events,
                    total_visits=self._total_visits,
                    crossing_line=self._crossing_line,
                )
                if self._presenter.show(frame, state):
                    break
        finally:
            self._frame_source.release()
            self._presenter.close()
