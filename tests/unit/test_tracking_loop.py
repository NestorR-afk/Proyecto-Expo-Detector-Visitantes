import unittest

from src.application.ports import PresentationState
from src.application.tracking_loop import TrackingLoop
from src.domain.counting import CrossingLine, TrajectoryEventDetector
from src.domain.models import BoundingBox, Point, TrackedPerson, TrackingID
from src.presentation.noop import NoOpPresenter


LINE = CrossingLine(Point(0, 300), Point(1280, 300))


def person(tracking_id: int, y: float) -> TrackedPerson:
    return TrackedPerson(
        tracking_id=TrackingID(tracking_id),
        bounding_box=BoundingBox(100, y - 10, 140, y + 10),
        confidence=0.9,
    )


class FakeFrameSource:
    def __init__(self, count: int) -> None:
        self.frames = [(True, f"frame-{index}") for index in range(count)]
        self.frames.append((False, None))
        self.released = False

    def read(self) -> tuple[bool, object]:
        return self.frames.pop(0)

    def release(self) -> None:
        self.released = True


class FakeTracker:
    def __init__(self, tracks_by_frame: list[list[TrackedPerson]]) -> None:
        self._tracks_by_frame = tracks_by_frame
        self.received: list[object] = []

    def track(self, frame: object) -> list[TrackedPerson]:
        self.received.append(frame)
        return self._tracks_by_frame[len(self.received) - 1]


class RecordingPresenter:
    def __init__(self) -> None:
        self.states: list[PresentationState] = []
        self.closed = False

    def show(self, frame: object, state: PresentationState) -> bool:
        self.states.append(state)
        return False

    def close(self) -> None:
        self.closed = True


def run_loop(
    tracks_by_frame: list[list[TrackedPerson]],
    clock_values: list[float] | None = None,
) -> tuple[TrackingLoop, RecordingPresenter, FakeFrameSource]:
    source = FakeFrameSource(len(tracks_by_frame))
    tracker = FakeTracker(tracks_by_frame)
    presenter = RecordingPresenter()
    detector = TrajectoryEventDetector(LINE)
    values = iter(clock_values or range(len(tracks_by_frame)))
    loop = TrackingLoop(
        source,
        tracker,
        detector,
        LINE,
        presenter,
        clock=lambda: next(values),
    )
    loop.run()
    return loop, presenter, source


class TrackingLoopTests(unittest.TestCase):
    def test_empty_frame_keeps_total_at_zero(self) -> None:
        loop, presenter, _ = run_loop([[]])

        self.assertEqual(loop.total_visits, 0)
        self.assertEqual(presenter.states[0].events, ())

    def test_first_frame_does_not_generate_a_visit(self) -> None:
        loop, presenter, _ = run_loop([[person(1, 250)]])

        self.assertEqual(loop.total_visits, 0)
        self.assertEqual(presenter.states[0].total_visits, 0)

    def test_crossing_increments_total(self) -> None:
        loop, presenter, _ = run_loop([[person(1, 250)], [person(1, 350)]])

        self.assertEqual(loop.total_visits, 1)
        self.assertEqual(len(presenter.states[1].events), 1)
        self.assertEqual(presenter.states[1].total_visits, 1)

    def test_same_track_oscillation_is_counted_once(self) -> None:
        loop, presenter, _ = run_loop(
            [[person(1, 250)], [person(1, 350)], [person(1, 250)], [person(1, 350)]]
        )

        self.assertEqual(loop.total_visits, 1)
        self.assertEqual(sum(len(state.events) for state in presenter.states), 1)

    def test_two_tracks_crossing_in_same_frame_produce_two_events(self) -> None:
        loop, presenter, _ = run_loop(
            [
                [person(1, 250), person(2, 240)],
                [person(1, 350), person(2, 340)],
            ]
        )

        self.assertEqual(loop.total_visits, 2)
        self.assertEqual(len(presenter.states[1].events), 2)

    def test_clock_is_called_without_sleeping(self) -> None:
        loop, _, _ = run_loop([[person(1, 250)], [person(1, 350)]], [10.0, 11.0])

        self.assertEqual(loop.total_visits, 1)

    def test_presenter_and_source_are_closed(self) -> None:
        loop, presenter, source = run_loop([[]])

        self.assertEqual(loop.total_visits, 0)
        self.assertTrue(source.released)
        self.assertTrue(presenter.closed)

    def test_noop_presenter_keeps_preview_disabled_path_working(self) -> None:
        state = PresentationState((), (), 0, LINE)
        presenter = NoOpPresenter()

        self.assertFalse(presenter.show(object(), state))
        presenter.close()


if __name__ == "__main__":
    unittest.main()
