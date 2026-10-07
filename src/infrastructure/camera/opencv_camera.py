"""OpenCV implementation of the frame source port."""

from typing import Any

import cv2


class OpenCVCamera:
    """Read frames from a local camera through OpenCV."""

    def __init__(
        self,
        camera_index: int,
        width: int | None = None,
        height: int | None = None,
    ) -> None:
        self._capture = cv2.VideoCapture(camera_index)
        if not self._capture.isOpened():
            self._capture.release()
            raise RuntimeError(f"Unable to open camera index {camera_index}")

        if width is not None:
            self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        if height is not None:
            self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def read(self) -> tuple[bool, Any]:
        return self._capture.read()

    def release(self) -> None:
        self._capture.release()
