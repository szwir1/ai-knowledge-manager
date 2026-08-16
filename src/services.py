from datetime import datetime, timezone
from typing import Protocol

from src.models import Note, User


class NoteRepository(Protocol):
    """Storage operations required by the note service."""

    def list_notes(self) -> list[Note]: ...

    def save_note(self, note: Note) -> None: ...


class NoteValidationError(ValueError):
    """Raised when note input is incomplete or invalid."""


class NoteService:
    """Create notes and coordinate their persistence."""

    def __init__(self, repository: NoteRepository) -> None:
        self._repository = repository

    def create_note(self, title: str, content: str, author_username: str) -> Note:
        normalized_title = self._require_text(title, "Tytuł")
        normalized_content = self._require_text(content, "Treść")
        normalized_username = self._require_text(author_username, "Autor")

        notes = self._repository.list_notes()
        author = self._find_or_create_author(notes, normalized_username)
        now = datetime.now(timezone.utc)
        note = Note(
            id=self._next_note_id(notes),
            title=normalized_title,
            content=normalized_content,
            author=author,
            created_at=now,
            updated_at=now,
        )

        self._repository.save_note(note)
        return note

    def list_notes(self) -> list[Note]:
        return sorted(self._repository.list_notes(), key=lambda note: note.id)

    @staticmethod
    def _require_text(value: str, field_name: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise NoteValidationError(f"{field_name} nie może być pusty.")
        return normalized_value

    @staticmethod
    def _next_note_id(notes: list[Note]) -> int:
        return max((note.id for note in notes), default=0) + 1

    @staticmethod
    def _find_or_create_author(notes: list[Note], username: str) -> User:
        for note in notes:
            if note.author.username.casefold() == username.casefold():
                return note.author

        next_author_id = max((note.author.id for note in notes), default=0) + 1
        return User(id=next_author_id, username=username)
