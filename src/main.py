"""Command-line entrypoint for the current PC YOLO prototype."""

from src.application.tracking_loop import TrackingLoop
from src.config.settings import Settings
from src.infrastructure.camera.opencv_camera import OpenCVCamera
from src.infrastructure.tracking.ultralytics_tracker import UltralyticsTracker
from src.presentation.opencv.window import OpenCVWindow


def build_application(settings: Settings) -> TrackingLoop:
    """Build the concrete adapters used by the current prototype."""
    tracker = UltralyticsTracker(
        model_path=settings.model_path,
        image_size=settings.image_size,
        person_class_id=settings.person_class_id,
        tracker_config=settings.tracker_config,
    )
    camera = OpenCVCamera(settings.camera_index)
    window = OpenCVWindow(settings.window_title)
    return TrackingLoop(camera, tracker, window)


def main() -> None:
    """Run the current prototype until the camera ends or Q is pressed."""
    build_application(Settings()).run()


if __name__ == "__main__":
    main()
