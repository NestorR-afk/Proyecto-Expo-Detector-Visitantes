"""Command-line entrypoint for the current PC YOLO prototype."""

from src.application.tracking_loop import TrackingLoop
from src.config.settings import Settings
from src.infrastructure.camera.opencv_camera import OpenCVCamera
from src.infrastructure.tracking.ultralytics_tracker import UltralyticsTracker
from src.presentation.noop import NoOpPresenter
from src.presentation.opencv.window import OpenCVWindow


def build_application(settings: Settings) -> TrackingLoop:
    """Build the concrete adapters used by the current prototype."""
    tracker = UltralyticsTracker(
        model_path=settings.model_path,
        imgsz=settings.imgsz,
        confidence=settings.confidence,
        iou=settings.iou,
        person_class_id=settings.person_class_id,
        tracker=settings.tracker,
    )
    camera = OpenCVCamera(
        camera_index=settings.camera_index,
        width=settings.camera_width,
        height=settings.camera_height,
    )
    presenter = (
        OpenCVWindow(settings.window_title)
        if settings.show_preview
        else NoOpPresenter()
    )
    return TrackingLoop(camera, tracker, presenter)


def main() -> None:
    """Run the current prototype until the camera ends or Q is pressed."""
    build_application(Settings()).run()


if __name__ == "__main__":
    main()
