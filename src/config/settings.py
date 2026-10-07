"""Minimal configuration for the current prototype."""

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class Settings:
    """Values needed to run the current camera and YOLO prototype."""

    camera_index: int = 0
    model_path: Path = PROJECT_ROOT / "models" / "yolo11n.pt"
    image_size: int = 320
    person_class_id: int = 0
    tracker_config: str = "bytetrack.yaml"
    window_title: str = "Expo Visitor Counter - YOLO Prototype"
