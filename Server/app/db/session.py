from collections.abc import AsyncIterator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine

    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.db_echo,
            pool_pre_ping=True,
            pool_recycle=settings.db_pool_recycle,
        )

    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory

    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            autoflush=False,
            expire_on_commit=False,
        )

    return _session_factory


async def get_db_session() -> AsyncIterator[AsyncSession]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session


async def check_database_connection(session: AsyncSession | None = None) -> bool:
    if session is not None:
        try:
            await session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    session_factory = get_session_factory()
    async with session_factory() as owned_session:
        try:
            await owned_session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
