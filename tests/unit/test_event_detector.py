import unittest

from src.domain.counting import (
    CrossingDirection,
    CrossingLine,
    TrajectoryEventDetector,
)
from src.domain.counting.models import VisitEvent
from src.domain.models import BoundingBox, Point, TrackedPerson, TrackingID


LINE = CrossingLine(Point(0, 100), Point(1000, 100))


def person(tracking_id: int, x: float, y: float) -> TrackedPerson:
    return TrackedPerson(
        tracking_id=TrackingID(tracking_id),
        bounding_box=BoundingBox(x, y, x, y),
        confidence=1.0,
    )


class TrajectoryEventDetectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.detector = TrajectoryEventDetector(
            crossing_line=LINE,
            track_timeout_seconds=5,
        )

    def test_first_frame_does_not_generate_an_event(self) -> None:
        events = self.detector.update([person(1, 500, 150)], now=0)

        self.assertEqual(events, ())

    def test_direct_a_to_b_generates_one_event(self) -> None:
        self.detector.update([person(1, 500, 150)], now=0)

        events = self.detector.update([person(1, 500, 50)], now=1)

        self.assertEqual(
            events,
            (VisitEvent(TrackingID(1), CrossingDirection.SIDE_A_TO_B),),
        )

    def test_direct_b_to_a_generates_opposite_direction(self) -> None:
        self.detector.update([person(1, 500, 50)], now=0)

        events = self.detector.update([person(1, 500, 150)], now=1)

        self.assertEqual(
            events,
            (VisitEvent(TrackingID(1), CrossingDirection.SIDE_B_TO_A),),
        )

    def test_a_on_line_b_generates_one_event(self) -> None:
        self.detector.update([person(1, 500, 150)], now=0)
        self.detector.update([person(1, 500, 100)], now=1)

        events = self.detector.update([person(1, 500, 50)], now=2)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].direction, CrossingDirection.SIDE_A_TO_B)

    def test_multiple_on_line_frames_generate_one_event(self) -> None:
        self.detector.update([person(1, 500, 150)], now=0)
        self.detector.update([person(1, 500, 100)], now=1)
        self.detector.update([person(1, 500, 100)], now=2)

        events = self.detector.update([person(1, 500, 50)], now=3)

        self.assertEqual(len(events), 1)

    def test_same_side_does_not_generate_an_event(self) -> None:
        self.detector.update([person(1, 500, 150)], now=0)

        events = self.detector.update([person(1, 700, 200)], now=1)

        self.assertEqual(events, ())

    def test_stopped_track_does_not_generate_an_event(self) -> None:
        self.detector.update([person(1, 500, 150)], now=0)

        events = self.detector.update([person(1, 500, 150)], now=1)

        self.assertEqual(events, ())

    def test_oscillation_after_crossing_does_not_duplicate(self) -> None:
        self.detector.update([person(1, 500, 150)], now=0)
        first_events = self.detector.update([person(1, 500, 50)], now=1)
        second_events = self.detector.update([person(1, 500, 150)], now=2)
        third_events = self.detector.update([person(1, 500, 50)], now=3)

        self.assertEqual(len(first_events), 1)
        self.assertEqual(second_events, ())
        self.assertEqual(third_events, ())

    def test_two_tracks_crossing_simultaneously_generate_two_events(self) -> None:
        self.detector.update(
            [person(1, 300, 150), person(2, 700, 150)],
            now=0,
        )

        events = self.detector.update(
            [person(1, 300, 50), person(2, 700, 50)],
            now=1,
        )

        self.assertEqual({event.tracking_id for event in events}, {1, 2})

    def test_missing_track_does_not_generate_an_event(self) -> None:
        self.detector.update([person(1, 500, 150)], now=0)

        events = self.detector.update([], now=1)

        self.assertEqual(events, ())
        self.assertEqual(self.detector.active_track_count, 1)

    def test_expired_track_is_removed(self) -> None:
        self.detector.update([person(1, 500, 150)], now=0)

        self.detector.update([], now=4)
        self.assertEqual(self.detector.active_track_count, 1)

        self.detector.update([], now=5)

        self.assertEqual(self.detector.active_track_count, 0)

    def test_same_id_can_start_new_cycle_after_expiration(self) -> None:
        self.detector.update([person(1, 500, 150)], now=0)
        self.detector.update([person(1, 500, 50)], now=1)
        self.detector.update([], now=6)

        self.detector.update([person(1, 500, 150)], now=7)
        events = self.detector.update([person(1, 500, 50)], now=8)

        self.assertEqual(len(events), 1)

    def test_zero_tracks_is_valid(self) -> None:
        self.assertEqual(self.detector.update([], now=0), ())
        self.assertEqual(self.detector.active_track_count, 0)

    def test_multiple_tracks_can_be_tracked_without_crossing(self) -> None:
        events = self.detector.update(
            [person(1, 300, 150), person(2, 700, 150)],
            now=0,
        )

        self.assertEqual(events, ())
        self.assertEqual(self.detector.active_track_count, 2)

    def test_track_timeout_must_be_positive(self) -> None:
        with self.assertRaises(ValueError):
            TrajectoryEventDetector(LINE, track_timeout_seconds=0)


if __name__ == "__main__":
    unittest.main()
