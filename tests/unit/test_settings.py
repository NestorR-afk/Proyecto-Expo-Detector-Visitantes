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
        self.assertEqual(
            settings.database_path,
            PROJECT_ROOT / "data" / "session.sqlite3",
        )
        self.assertEqual(
            (
                settings.counting_line_start_x,
                settings.counting_line_start_y,
                settings.counting_line_end_x,
                settings.counting_line_end_y,
            ),
            (0.0, 300.0, 1280.0, 300.0),
        )


if __name__ == "__main__":
    unittest.main()
