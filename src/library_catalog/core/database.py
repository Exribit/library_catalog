from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .config import settings
from typing import AsyncGenerator

class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    settings.database_url_str, 
    pool_size=settings.database_pool_size, 
    echo=settings.debug,)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
        finally:
            await session.close()