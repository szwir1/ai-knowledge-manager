import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.services import NoteService, NoteValidationError
from src.storage import JsonNoteRepository, StorageError


class NoteServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.storage_path = Path(self.temporary_directory.name) / "notes.json"
        self.repository = JsonNoteRepository(self.storage_path)
        self.service = NoteService(self.repository)

    def test_create_note_persists_it_in_json(self) -> None:
        created_note = self.service.create_note(
            title="  Pierwsza notatka  ",
            content="  Ważna treść  ",
            author_username="  Jan  ",
        )

        stored_notes = JsonNoteRepository(self.storage_path).list_notes()

        self.assertEqual(created_note.id, 1)
        self.assertEqual(created_note.title, "Pierwsza notatka")
        self.assertEqual(created_note.content, "Ważna treść")
        self.assertEqual(created_note.author.username, "Jan")
        self.assertEqual(stored_notes, [created_note])

    def test_create_note_assigns_sequential_ids_and_reuses_author(self) -> None:
        first_note = self.service.create_note("Tytuł 1", "Treść 1", "Jan")
        second_note = self.service.create_note("Tytuł 2", "Treść 2", "jan")

        self.assertEqual(second_note.id, 2)
        self.assertEqual(second_note.author, first_note.author)

    def test_create_note_rejects_empty_fields(self) -> None:
        with self.assertRaisesRegex(NoteValidationError, "Tytuł"):
            self.service.create_note("  ", "Treść", "Jan")

        self.assertFalse(self.storage_path.exists())

    def test_repository_reports_invalid_json(self) -> None:
        self.storage_path.write_text("not-json", encoding="utf-8")

        with self.assertRaises(StorageError):
            self.repository.list_notes()

    def test_repository_rejects_invalid_note_schema(self) -> None:
        self.storage_path.write_text(
            json.dumps({"notes": [{"id": 1, "author": {}}]}),
            encoding="utf-8",
        )

        with self.assertRaises(StorageError):
            self.repository.list_notes()

    def test_json_uses_readable_unicode(self) -> None:
        self.service.create_note("Zażółć", "Gęślą jaźń", "Łukasz")

        payload = self.storage_path.read_text(encoding="utf-8")

        self.assertIn("Zażółć", payload)
        self.assertEqual(len(json.loads(payload)["notes"]), 1)


if __name__ == "__main__":
    unittest.main()
