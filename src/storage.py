import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.models import Note, User


class StorageError(RuntimeError):
    """Raised when notes cannot be read from or written to storage."""


class JsonNoteRepository:
    """Persist notes in a human-readable JSON file."""

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path

    def list_notes(self) -> list[Note]:
        if not self._file_path.exists():
            return []

        try:
            with self._file_path.open(encoding="utf-8") as file:
                payload = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            raise StorageError(
                f"Nie udało się odczytać notatek z {self._file_path}."
            ) from error

        if not isinstance(payload, dict) or not isinstance(payload.get("notes"), list):
            raise StorageError(f"Plik {self._file_path} ma nieprawidłowy format.")

        try:
            return [self._deserialize_note(item) for item in payload["notes"]]
        except (KeyError, TypeError, ValueError) as error:
            raise StorageError(
                f"Plik {self._file_path} zawiera nieprawidłową notatkę."
            ) from error

    def save_note(self, note: Note) -> None:
        notes = self.list_notes()
        if any(existing_note.id == note.id for existing_note in notes):
            raise StorageError(f"Notatka o identyfikatorze {note.id} już istnieje.")

        notes.append(note)
        self._write_notes(notes)

    def _write_notes(self, notes: list[Note]) -> None:
        temporary_path = self._file_path.with_name(f".{self._file_path.name}.tmp")
        payload = {"notes": [self._serialize_note(note) for note in notes]}

        try:
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            with temporary_path.open("w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)
                file.write("\n")
            temporary_path.replace(self._file_path)
        except OSError as error:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise StorageError(
                f"Nie udało się zapisać notatek w {self._file_path}."
            ) from error

    @staticmethod
    def _serialize_note(note: Note) -> dict[str, Any]:
        return {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "author": {
                "id": note.author.id,
                "username": note.author.username,
            },
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat(),
        }

    @staticmethod
    def _deserialize_note(data: Any) -> Note:
        if not isinstance(data, dict) or not isinstance(data.get("author"), dict):
            raise TypeError("Invalid note data")

        author_data = data["author"]
        note_id = data["id"]
        title = data["title"]
        content = data["content"]
        author_id = author_data["id"]
        username = author_data["username"]
        created_at = data["created_at"]
        updated_at = data["updated_at"]

        if (
            not isinstance(note_id, int)
            or isinstance(note_id, bool)
            or not isinstance(title, str)
            or not isinstance(content, str)
            or not isinstance(author_id, int)
            or isinstance(author_id, bool)
            or not isinstance(username, str)
            or not isinstance(created_at, str)
            or not isinstance(updated_at, str)
        ):
            raise TypeError("Invalid note field type")

        return Note(
            id=note_id,
            title=title,
            content=content,
            author=User(
                id=author_id,
                username=username,
            ),
            created_at=datetime.fromisoformat(created_at),
            updated_at=datetime.fromisoformat(updated_at),
        )
