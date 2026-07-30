from typing import Generic, TypeVar, Type
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.book import Book

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]) -> None:
        self.session = session
        self.model = model

    async def create(self, **kwargs):
        '''Создать запись.'''
        obj = self.model(**kwargs)

        self.session.add(obj)

        await self.session.commit()
        await self.session.refresh(obj)

        return obj

    async def get_by_id(self, book_id: UUID) -> T | None:
        '''
        Получить по ID.
        
        Примечание: session.get() автоматически работает с primary key модели,
        независимо от его названия (id, book_id, user_id и т.д.)
        '''
        book = await self.session.get(self.model, book_id)
        return book

    async def update(self, id: UUID, **kwargs) -> T | None:
        '''Обновить запись.'''
        book = await self.session.get(self.model, id)

        if not book:
            return None

        for key, value in kwargs.items():
            setattr(book, key, value)

        await self.session.commit()
        await self.session.refresh(book)

        return book

    async def delete(self, id: UUID) -> bool:
        '''Удалить запись'''
        raise NotImplementedError

    async def get_all(self, 
                      limit: int = 100, 
                      offset: int = 0,
    ) -> list[T]:
        '''Получить все записи с пагинацией.'''
        raise NotImplementedError