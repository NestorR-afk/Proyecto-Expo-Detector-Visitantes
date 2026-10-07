"""Application loop for the current YOLO tracking prototype."""

from src.application.ports import FramePresenter, FrameSource, PersonTracker


class TrackingLoop:
    """Coordinate capture, tracking, and presentation without owning either."""

    def __init__(
        self,
        frame_source: FrameSource,
        tracker: PersonTracker,
        presenter: FramePresenter,
    ) -> None:
        self._frame_source = frame_source
        self._tracker = tracker
        self._presenter = presenter

    def run(self) -> None:
        """Process frames until capture ends or the presenter requests shutdown."""
        try:
            while True:
                frame_ok, frame = self._frame_source.read()
                if not frame_ok:
                    break

                people = self._tracker.track(frame)
                if self._presenter.show(frame, people):
                    break
        finally:
            self._frame_source.release()
            self._presenter.close()
