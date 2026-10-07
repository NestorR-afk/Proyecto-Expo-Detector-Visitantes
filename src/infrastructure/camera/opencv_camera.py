"""OpenCV implementation of the frame source port."""

from typing import Any

import cv2


class OpenCVCamera:
    """Read frames from a local camera through OpenCV."""

    def __init__(self, camera_index: int) -> None:
        self._capture = cv2.VideoCapture(camera_index)

    def read(self) -> tuple[bool, Any]:
        return self._capture.read()

    def release(self) -> None:
        self._capture.release()
