import unittest

from src.domain.counting import (
    CrossingDirection,
    CrossingLine,
    PointSide,
    detect_crossing,
)
from src.domain.models import Point


class CrossingGeometryTests(unittest.TestCase):
    def test_horizontal_line_crosses_from_side_a_to_side_b(self) -> None:
        line = CrossingLine(Point(0, 300), Point(1000, 300))

        result = detect_crossing(Point(500, 250), Point(500, 350), line)

        self.assertTrue(result.crossed)
        self.assertEqual(result.direction, CrossingDirection.SIDE_B_TO_A)

    def test_horizontal_line_crosses_from_side_b_to_side_a(self) -> None:
        line = CrossingLine(Point(0, 300), Point(1000, 300))

        result = detect_crossing(Point(500, 350), Point(500, 250), line)

        self.assertTrue(result.crossed)
        self.assertEqual(result.direction, CrossingDirection.SIDE_A_TO_B)

    def test_same_side_does_not_cross(self) -> None:
        line = CrossingLine(Point(0, 300), Point(1000, 300))

        result = detect_crossing(Point(200, 200), Point(800, 250), line)

        self.assertFalse(result.crossed)
        self.assertIsNone(result.direction)

    def test_vertical_line_crosses_left_to_right(self) -> None:
        line = CrossingLine(Point(500, 0), Point(500, 1000))

        result = detect_crossing(Point(400, 500), Point(600, 500), line)

        self.assertTrue(result.crossed)
        self.assertEqual(result.direction, CrossingDirection.SIDE_A_TO_B)

    def test_vertical_line_crosses_right_to_left(self) -> None:
        line = CrossingLine(Point(500, 0), Point(500, 1000))

        result = detect_crossing(Point(600, 500), Point(400, 500), line)

        self.assertTrue(result.crossed)
        self.assertEqual(result.direction, CrossingDirection.SIDE_B_TO_A)

    def test_diagonal_line_crosses(self) -> None:
        line = CrossingLine(Point(0, 0), Point(1000, 1000))

        result = detect_crossing(Point(200, 100), Point(100, 200), line)

        self.assertTrue(result.crossed)

    def test_point_on_line_is_neutral(self) -> None:
        line = CrossingLine(Point(0, 300), Point(1000, 300))

        self.assertEqual(line.side(Point(500, 300)), PointSide.ON_LINE)

    def test_transition_to_line_does_not_infer_crossing(self) -> None:
        line = CrossingLine(Point(0, 300), Point(1000, 300))

        result = detect_crossing(Point(500, 250), Point(500, 300), line)

        self.assertFalse(result.crossed)
        self.assertEqual(result.current_side, PointSide.ON_LINE)

    def test_transition_from_line_does_not_infer_crossing(self) -> None:
        line = CrossingLine(Point(0, 300), Point(1000, 300))

        result = detect_crossing(Point(500, 300), Point(500, 350), line)

        self.assertFalse(result.crossed)
        self.assertEqual(result.previous_side, PointSide.ON_LINE)

    def test_parallel_movement_does_not_cross(self) -> None:
        line = CrossingLine(Point(0, 300), Point(1000, 300))

        result = detect_crossing(Point(100, 200), Point(900, 200), line)

        self.assertFalse(result.crossed)

    def test_no_movement_does_not_cross(self) -> None:
        line = CrossingLine(Point(0, 300), Point(1000, 300))
        point = Point(500, 200)

        result = detect_crossing(point, point, line)

        self.assertFalse(result.crossed)

    def test_crossing_extension_outside_finite_segment_does_not_count(self) -> None:
        line = CrossingLine(Point(0, 300), Point(1000, 300))

        result = detect_crossing(Point(1500, 250), Point(1500, 350), line)

        self.assertFalse(result.crossed)

    def test_crossing_at_segment_endpoint_counts(self) -> None:
        line = CrossingLine(Point(0, 300), Point(1000, 300))

        result = detect_crossing(Point(-100, 200), Point(100, 400), line)

        self.assertTrue(result.crossed)

    def test_degenerate_line_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CrossingLine(Point(10, 10), Point(10, 10))


if __name__ == "__main__":
    unittest.main()
