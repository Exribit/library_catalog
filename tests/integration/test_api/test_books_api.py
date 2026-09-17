import uuid
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from src.library_catalog.api.v1.schemas.book import ShowBook

@pytest.fixture
def sample_show_book() -> dict:
    return {
        "book_id": str(uuid.uuid4()),
        "title": "FastAPI Testing",
        "author": "Test Author",
        "year": 2024,
        "genre": "Testing",
        "pages": 150,
        "available": True,
        "isbn": None,
        "description": None,
        "extra": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

@pytest.mark.asyncio
async def test_create_book_endpoint(
    async_client: AsyncClient, 
    mock_book_service: AsyncMock, 
    sample_show_book: dict
):
    # Указываем моку, что он должен вернуть DTO ShowBook
    mock_book_service.create_book.return_value = ShowBook(**sample_show_book)

    # Отправляем реальный HTTP POST запрос
    payload = {
        "title": "FastAPI Testing",
        "author": "Test Author",
        "year": 2024,
        "genre": "Testing",
        "pages": 150
    }
    response = await async_client.post("/api/v1/books/", json=payload)

    # Проверяем ответ API
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert "book_id" in data
    
    # Убеждаемся, что роутер реально вызвал наш сервис
    mock_book_service.create_book.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_book_validation_error(
    async_client: AsyncClient, 
    mock_book_service: AsyncMock
):
    # Пытаемся создать книгу без обязательного поля "title"
    payload = {
        "author": "Test Author",
        "year": 2024,
        "genre": "Testing",
        "pages": 150
    }
    response = await async_client.post("/api/v1/books/", json=payload)

    # Должна отработать валидация Pydantic (422 Unprocessable Entity)
    assert response.status_code == 422
    # Сервис при этом не должен быть вызван
    mock_book_service.create_book.assert_not_awaited()

@pytest.mark.asyncio
async def test_get_book_endpoint(
    async_client: AsyncClient, 
    mock_book_service: AsyncMock, 
    sample_show_book: dict
):
    book_id = sample_show_book["book_id"]
    mock_book_service.get_book.return_value = ShowBook(**sample_show_book)

    response = await async_client.get(f"/api/v1/books/{book_id}")

    assert response.status_code == 200
    assert response.json()["book_id"] == book_id
    mock_book_service.get_book.assert_awaited_once()