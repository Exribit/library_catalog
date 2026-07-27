from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class BookCreate(BaseModel):
    title: str
    author: str
    year: int
    genre: str
    pages: int
    isbn: str | None = None
    description: str | None = None

class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    year: int | None = None
    genre: str | None = None
    pages: int | None = None
    isbn: str | None = None
    description: str | None = None

class ShowBook(BaseModel):
    book_id: UUID
    title: str
    author: str
    year: int
    genre: str
    pages: int
    available: bool
    isbn: str | None
    description: str | None
    extra: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)