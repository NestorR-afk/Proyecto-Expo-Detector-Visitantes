import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.domain.counting import CrossingDirection, VisitEvent
from src.domain.models import TrackingID
from src.infrastructure.persistence.sqlite_visit_event_repository import (
    SQLiteVisitEventRepository,
)


def event(tracking_id: int, direction: CrossingDirection) -> VisitEvent:
    return VisitEvent(TrackingID(tracking_id), direction)


class SQLiteVisitEventRepositoryTests(unittest.TestCase):
    def test_new_database_creates_schema_and_starts_empty(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = SQLiteVisitEventRepository(Path(directory) / "session.sqlite3")

            self.assertEqual(repository.count(), 0)
            repository.close()

    def test_save_one_event_and_count_it(self) -> None:
        repository = SQLiteVisitEventRepository(":memory:")

        repository.save_many((event(1, CrossingDirection.SIDE_A_TO_B),))

        self.assertEqual(repository.count(), 1)
        repository.close()

    def test_save_many_events_in_one_batch(self) -> None:
        repository = SQLiteVisitEventRepository(":memory:")

        repository.save_many(
            (
                event(1, CrossingDirection.SIDE_A_TO_B),
                event(2, CrossingDirection.SIDE_B_TO_A),
            )
        )

        self.assertEqual(repository.count(), 2)
        repository.close()

    def test_reopen_preserves_count_and_allows_repeated_tracking_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "session.sqlite3"
            first = SQLiteVisitEventRepository(database_path)
            first.save_many(
                (
                    event(7, CrossingDirection.SIDE_A_TO_B),
                    event(7, CrossingDirection.SIDE_B_TO_A),
                )
            )
            first.close()

            reopened = SQLiteVisitEventRepository(database_path)
            self.assertEqual(reopened.count(), 2)
            reopened.close()

            with sqlite3.connect(database_path) as connection:
                directions = connection.execute(
                    "SELECT direction FROM visit_events ORDER BY id"
                ).fetchall()
            self.assertEqual(
                directions,
                [
                    (CrossingDirection.SIDE_A_TO_B.value,),
                    (CrossingDirection.SIDE_B_TO_A.value,),
                ],
            )

    def test_empty_batch_does_not_change_count(self) -> None:
        repository = SQLiteVisitEventRepository(":memory:")

        repository.save_many(())

        self.assertEqual(repository.count(), 0)
        repository.close()


if __name__ == "__main__":
    unittest.main()
