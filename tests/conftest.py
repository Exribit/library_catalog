import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock

from src.library_catalog.main import app
from src.library_catalog.api.dependencies import get_book_service
from src.library_catalog.domain.services.book_service import BookService

@pytest.fixture
def mock_book_service() -> AsyncMock:
    """Мок для бизнес-логики, чтобы не дергать реальную БД в тестах API."""
    return AsyncMock(spec=BookService)

@pytest.fixture
def app_with_mocks(mock_book_service: AsyncMock):
    """Подменяем реальный сервис на мок через Dependency Overrides."""
    app.dependency_overrides[get_book_service] = lambda: mock_book_service
    yield app
    app.dependency_overrides.clear()

@pytest.fixture
async def async_client(app_with_mocks) -> AsyncGenerator[AsyncClient, None]:
    """Асинхронный клиент для эмуляции HTTP запросов."""
    transport = ASGITransport(app=app_with_mocks)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client