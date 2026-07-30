from ..models.book import Book
from .base_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from collections.abc import Sequence



class BookRepository(BaseRepository[Book]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Book)

    async def find_by_filters(
            self,
            title: str | None = None,
            author: str | None = None,
            genre: str | None = None,
            year: int | None = None,
            available: bool | None = None,
            limit: int = 20,
            offset: int = 0,
    ) -> Sequence[Book]:
        '''Поиск книг с фильтрацией.'''
        
        query = select(Book)

        if title:
            query = query.where(Book.title.ilike(f'%{title}%'))
        
        if author:
            query = query.where(Book.author.ilike(f'%{author}%'))
        
        if genre:
            query = query.where(Book.genre.ilike(f'%{genre}%'))

        if year is not None:
            query = query.where(Book.year == year)

        if available is not None:
            query = query.where(Book.available == available)
        
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        
        return result.scalars().all()

    
    async def find_by_isbn(self, isbn: str) -> Book | None:
        '''Найти книгу по ISBN.'''
        query = select(Book).where(Book.isbn == isbn)

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def count_by_filters(
            self,
            title: str | None = None,
            author: str | None = None,
            genre: str | None = None,
            year: int | None = None,
            available: bool | None = None,
            limit: int = 20,
            offset: int = 0,
    ) -> int:
        '''Подсчитать количество книг по фильтрам.'''
        raise NotImplementedError