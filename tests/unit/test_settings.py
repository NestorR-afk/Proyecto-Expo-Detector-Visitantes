import unittest

from src.config.settings import PROJECT_ROOT, Settings


class SettingsTests(unittest.TestCase):
    def test_defaults_point_to_the_repository_model(self) -> None:
        settings = Settings()

        self.assertEqual(settings.camera_index, 0)
        self.assertEqual(settings.model_path, PROJECT_ROOT / "models" / "yolo11n.pt")
        self.assertTrue(settings.model_path.is_file())
        self.assertEqual(settings.imgsz, 320)
        self.assertEqual(settings.confidence, 0.25)
        self.assertEqual(settings.iou, 0.7)
        self.assertEqual(settings.tracker, "bytetrack.yaml")
        self.assertTrue(settings.show_preview)


if __name__ == "__main__":
    unittest.main()
