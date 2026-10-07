import unittest

from src.domain.models import BoundingBox, Point, TrackedPerson, TrackingID


class BoundingBoxTests(unittest.TestCase):
    def test_center_is_calculated_from_box_coordinates(self) -> None:
        box = BoundingBox(10, 20, 30, 60)

        self.assertEqual(box.center, Point(20, 40))

    def test_rejects_reversed_coordinates(self) -> None:
        with self.assertRaises(ValueError):
            BoundingBox(30, 20, 10, 60)


class TrackedPersonTests(unittest.TestCase):
    def test_keeps_temporary_tracking_identity_and_detection_data(self) -> None:
        person = TrackedPerson(
            tracking_id=TrackingID(7),
            bounding_box=BoundingBox(0, 0, 20, 40),
            confidence=0.95,
        )

        self.assertEqual(person.tracking_id, 7)
        self.assertEqual(person.bounding_box.center, Point(10, 20))
        self.assertEqual(person.confidence, 0.95)


if __name__ == "__main__":
    unittest.main()
