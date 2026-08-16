import argparse
from pathlib import Path
from typing import Sequence

from src.services import NoteService, NoteValidationError
from src.storage import JsonNoteRepository, StorageError


DEFAULT_STORAGE_PATH = Path(__file__).resolve().parents[1] / "data" / "notes.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Tworzenie i przechowywanie notatek w lokalnym pliku JSON."
    )
    parser.add_argument(
        "--storage",
        type=Path,
        default=DEFAULT_STORAGE_PATH,
        help=f"ścieżka do pliku z notatkami (domyślnie: {DEFAULT_STORAGE_PATH})",
    )

    commands = parser.add_subparsers(dest="command")
    add_parser = commands.add_parser("add", help="utwórz i zapisz nową notatkę")
    add_parser.add_argument("--title", required=True, help="tytuł notatki")
    add_parser.add_argument("--content", required=True, help="treść notatki")
    add_parser.add_argument("--author", required=True, help="nazwa autora")

    commands.add_parser("list", help="wyświetl zapisane notatki")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)

    if arguments.command is None:
        parser.print_help()
        return 0

    service = NoteService(JsonNoteRepository(arguments.storage))

    try:
        if arguments.command == "add":
            note = service.create_note(
                title=arguments.title,
                content=arguments.content,
                author_username=arguments.author,
            )
            print(f"Zapisano notatkę #{note.id}: {note.title}")
            return 0

        notes = service.list_notes()
    except (NoteValidationError, StorageError) as error:
        parser.error(str(error))

    if not notes:
        print("Brak zapisanych notatek.")
        return 0

    for note in notes:
        print(f"#{note.id} | {note.title} | autor: {note.author.username}")
        print(note.content)
        print(f"Utworzono: {note.created_at.isoformat()}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
