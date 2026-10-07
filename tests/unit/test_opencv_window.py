import unittest
from unittest.mock import patch

import cv2

from src.application.ports import PresentationState
from src.domain.counting import CrossingLine
from src.domain.models import Point
from src.presentation.opencv.window import OpenCVWindow


class OpenCVWindowTests(unittest.TestCase):
    def test_closed_window_requests_shutdown(self) -> None:
        state = PresentationState(
            people=(),
            events=(),
            total_visits=0,
            crossing_line=CrossingLine(Point(0, 300), Point(640, 300)),
        )
        window = OpenCVWindow("test")

        with (
            patch.object(cv2, "line"),
            patch.object(cv2, "putText"),
            patch.object(cv2, "imshow"),
            patch.object(cv2, "waitKey", return_value=-1),
            patch.object(
                cv2,
                "getWindowProperty",
                side_effect=cv2.error("window closed"),
            ),
        ):
            self.assertTrue(window.show(object(), state))


if __name__ == "__main__":
    unittest.main()
