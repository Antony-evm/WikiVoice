from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings
from app.logging_config import get_logger
from custom_exceptions import DatabaseConnectionError, DatabaseError, DomainError

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_engine(echo: bool = False) -> AsyncEngine:
    """Create a singleton async engine from settings."""
    return create_async_engine(
        get_settings().database_url,
        echo=echo,
        future=True,
        pool_pre_ping=True,
        pool_size=get_settings().database_pool_size,
        max_overflow=get_settings().database_max_overflow,
        pool_recycle=get_settings().database_pool_recycle,
        pool_timeout=get_settings().database_pool_timeout,
    )


@lru_cache(maxsize=1)
def get_session_factory(engine: AsyncEngine | None = None) -> async_sessionmaker[AsyncSession]:
    """Return a singleton session factory bound to the engine."""
    if engine is None:
        engine = get_engine()
    return async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency that yields a DB session with error handling."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            logger.info("[Database] Session started")
            yield session
            await session.commit()
            logger.info("[Database] Session committed successfully")
        except IntegrityError as e:
            await session.rollback()
            logger.exception("database_integrity_error", error_type=type(e).__name__)
            raise DatabaseError("Database integrity constraint violated", e) from e
        except OperationalError as e:
            await session.rollback()
            logger.exception("database_operational_error", error_type=type(e).__name__)
            raise DatabaseConnectionError("Unable to connect to the database") from e
        except DomainError:
            await session.rollback()
            logger.warning("[Database] Session rolled back due to DomainError")
            raise
        except Exception as e:
            await session.rollback()
            logger.exception(
                "unexpected_database_error",
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise DatabaseError("An unexpected database error occurred", e) from e
