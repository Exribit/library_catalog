import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...core.database import Base


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)
class Book(Base):
    """
    SQLAlchemy-модель книги.

    Представляет запись о книге в таблице `books`.
    Содержит основную информацию о книге, включая название,
    автора, жанр, год издания, количество страниц, статус
    доступности, ISBN, описание, дополнительные данные и
    служебные временные метки создания и обновления записи.
    """

    
    __tablename__='books'

    book_id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    title:Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True
    )

    author: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True,
    )

    year: Mapped[int] = mapped_column(index=True)

    genre: Mapped[str] = mapped_column(
        String(100),
        index=True
    )

    pages: Mapped[int]

    available: Mapped[bool] = mapped_column(
        default=True,
        index=True)
    
    isbn: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
    )

    description: Mapped[str | None] = mapped_column(Text)

    extra: Mapped[dict | None] = mapped_column(JSON)

    #Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now
    )

    def __repr__(self) -> str:
        return f"<Book(id={self.book_id}, title='{self.title}')>"