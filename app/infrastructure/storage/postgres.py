import logging
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)

from core.config import get_settings, Settings

logger = logging.getLogger(__name__)


class Postgres:

    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session: Optional[async_sessionmaker] = None
        self._settings = get_settings()

    async def init(self) -> None:
        if self._engine is not None:
            logger.warning("Postgres already initialized")
            return
        try:
            logger.info("Creating Postgres engine")
            self._engine = create_async_engine(
                self._settings.sqlalchemy_database_uri,
                echo=True if self._settings.env == "development" else False,
            )
            self._session_factory = async_sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
            logger.info("Postgres engine created")
            async with self._engine.begin() as async_conn:
                await async_conn.execute(
                    text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; ')
                )
                logger.info("Postgres engine created and install uuid-ossp extension")
        except Exception as e:
            logger.error(f"Postgres initialization failed with {str(e)}")
            raise e

    async def shutdown(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Postgres engine shut down")
        get_postgres.cache_clear()

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            raise RuntimeError("Postgres not initialized")
        return self._session_factory


@lru_cache
def get_postgres() -> Postgres:
    return Postgres()


async def get_db_session() -> AsyncSession:
    db = get_postgres()
    session_factory = db.session_factory

    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
