from __future__ import annotations

from collections.abc import AsyncIterator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.app_config import app_settings

engine: AsyncEngine = create_async_engine(
    app_settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=app_settings.DATABASE_POOL_SIZE,
    max_overflow=app_settings.DATABASE_MAX_OVERFLOW,
)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def get_database_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def check_database_connection() -> dict[str, str]:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    return {"status": "healthy"}


async def close_database() -> None:
    await engine.dispose()
