import uuid
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.library_catalog.api.v1.schemas.book import BookCreate, BookUpdate
from src.library_catalog.data.models.book import Book
from src.library_catalog.data.repositories.book_repository import BookRepository
from src.library_catalog.domain.exceptions import (
    BookAlreadyExistsException,
    BookNotFoundException,
    InvalidPagesException,
    InvalidYearException,
    OpenLibraryTimeoutException,
)
from src.library_catalog.domain.services.book_service import BookService
from src.library_catalog.external.openlibrary.client import OpenLibraryClient


@pytest.fixture
def mock_book_repo() -> AsyncMock:
    return AsyncMock(spec=BookRepository)


@pytest.fixture
def mock_ol_client() -> AsyncMock:
    return AsyncMock(spec=OpenLibraryClient)


@pytest.fixture
def book_service(mock_book_repo: AsyncMock, mock_ol_client: AsyncMock) -> BookService:
    return BookService(
        book_repository=mock_book_repo,
        openlibrary_client=mock_ol_client,
    )


@pytest.fixture
def sample_book_entity() -> Book:
    now = datetime.now()
    return Book(
        book_id=uuid.uuid4(),
        title="Clean Architecture",
        author="Robert Martin",
        year=2017,
        genre="Software Engineering",
        pages=352,
        available=True,
        isbn="9780134494166",
        description="Software Structure and Design",
        extra={"cover_url": "https://covers.openlibrary.org/b/id/1-L.jpg"},
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_create_book_success(
    book_service: BookService,
    mock_book_repo: AsyncMock,
    mock_ol_client: AsyncMock,
    sample_book_entity: Book,
):
    # Arrange
    book_data = BookCreate(
        title="Clean Architecture",
        author="Robert Martin",
        year=2017,
        genre="Software Engineering",
        pages=352,
        isbn="9780134494166",
    )
    mock_book_repo.find_by_isbn.return_value = None
    mock_ol_client.enrich.return_value = {"cover_url": "https://covers.openlibrary.org/b/id/1-L.jpg"}
    mock_book_repo.create.return_value = sample_book_entity

    # Act
    result = await book_service.create_book(book_data)

    # Assert
    assert result.book_id == sample_book_entity.book_id
    assert result.title == book_data.title
    mock_book_repo.find_by_isbn.assert_awaited_once_with(book_data.isbn)
    mock_ol_client.enrich.assert_awaited_once_with(
        title=book_data.title,
        author=book_data.author,
        isbn=book_data.isbn,
    )
    mock_book_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_book_enrichment_fails_gracefully(
    book_service: BookService,
    mock_book_repo: AsyncMock,
    mock_ol_client: AsyncMock,
    sample_book_entity: Book,
):
    # Arrange: сервис OpenLibrary падает с таймаутом
    book_data = BookCreate(
        title="Clean Architecture",
        author="Robert Martin",
        year=2017,
        genre="Software Engineering",
        pages=352,
        isbn="9780134494166",
    )
    mock_book_repo.find_by_isbn.return_value = None
    mock_ol_client.enrich.side_effect = OpenLibraryTimeoutException(10.0)

    sample_book_entity.extra = None
    mock_book_repo.create.return_value = sample_book_entity

    # Act: книга всё равно должна успешно создаться
    result = await book_service.create_book(book_data)

    # Assert
    assert result.extra is None
    mock_book_repo.create.assert_awaited_once_with(
        title=book_data.title,
        author=book_data.author,
        year=book_data.year,
        genre=book_data.genre,
        pages=book_data.pages,
        isbn=book_data.isbn,
        description=book_data.description,
        extra=None,
    )


@pytest.mark.asyncio
async def test_create_book_invalid_year(book_service: BookService):
    future_year = datetime.now().year + 5
    book_data = BookCreate(
        title="Future Book",
        author="Author",
        year=future_year,
        genre="Sci-Fi",
        pages=100,
    )

    with pytest.raises(InvalidYearException):
        await book_service.create_book(book_data)


@pytest.mark.asyncio
async def test_create_book_duplicate_isbn(
    book_service: BookService,
    mock_book_repo: AsyncMock,
    sample_book_entity: Book,
):
    book_data = BookCreate(
        title="Duplicate",
        author="Author",
        year=2020,
        genre="IT",
        pages=200,
        isbn="9780134494166",
    )
    mock_book_repo.find_by_isbn.return_value = sample_book_entity

    with pytest.raises(BookAlreadyExistsException):
        await book_service.create_book(book_data)


@pytest.mark.asyncio
async def test_get_book_not_found(book_service: BookService, mock_book_repo: AsyncMock):
    random_id = uuid.uuid4()
    mock_book_repo.get_by_id.return_value = None

    with pytest.raises(BookNotFoundException):
        await book_service.get_book(random_id)


@pytest.mark.asyncio
async def test_update_book_invalid_pages(
    book_service: BookService,
    mock_book_repo: AsyncMock,
    sample_book_entity: Book,
):
    book_id = sample_book_entity.book_id
    mock_book_repo.get_by_id.return_value = sample_book_entity

    # Обновление с некорректными страницами (0 или отрицательное значение)
    # В обход Pydantic валидации схемы передаем напрямую невалидный DTO
    update_data = BookUpdate.model_construct(pages=0)

    with pytest.raises(InvalidPagesException):
        await book_service.update_book(book_id, update_data)


@pytest.mark.asyncio
async def test_delete_book_not_found(book_service: BookService, mock_book_repo: AsyncMock):
    random_id = uuid.uuid4()
    mock_book_repo.delete.return_value = False

    with pytest.raises(BookNotFoundException):
        await book_service.delete_book(random_id)