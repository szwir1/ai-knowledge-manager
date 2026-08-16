from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class User:
    """Author of a note."""

    id: int
    username: str


@dataclass(frozen=True, slots=True)
class Note:
    """A single note stored by the application."""

    id: int
    title: str
    content: str
    author: User
    created_at: datetime
    updated_at: datetime
