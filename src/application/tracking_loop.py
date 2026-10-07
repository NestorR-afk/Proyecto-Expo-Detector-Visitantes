"""Application orchestration for tracking and visit-event generation."""

from collections.abc import Callable
import logging
from time import monotonic

from src.application.ports import (
    FramePresenter,
    FrameSource,
    PersonTracker,
    PresentationState,
    VisitEventRepository,
)
from src.domain.counting import CrossingLine, TrajectoryEventDetector


LOGGER = logging.getLogger(__name__)


class TrackingLoop:
    """Coordinate capture, tracking, event detection, and presentation."""

    def __init__(
        self,
        frame_source: FrameSource,
        tracker: PersonTracker,
        event_detector: TrajectoryEventDetector,
        crossing_line: CrossingLine,
        presenter: FramePresenter,
        event_repository: VisitEventRepository,
        initial_total: int,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self._frame_source = frame_source
        self._tracker = tracker
        self._event_detector = event_detector
        self._crossing_line = crossing_line
        self._presenter = presenter
        self._event_repository = event_repository
        self._clock = clock
        self._total_visits = initial_total

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

                if self._camera_was_reopened():
                    self._event_detector.reset()
                    self._tracker.reset()
                    LOGGER.info("Reset ephemeral tracking state after camera recovery")

                people = tuple(self._tracker.track(frame))
                events = self._event_detector.update(people, now=self._clock())
                if events:
                    self._event_repository.save_many(events)
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
            try:
                self._frame_source.release()
            finally:
                try:
                    self._presenter.close()
                finally:
                    self._event_repository.close()

    def _camera_was_reopened(self) -> bool:
        return self._frame_source.consume_recovery()
