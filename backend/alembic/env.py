import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from alembic import context
from models import Base

load_dotenv()
config = context.config

env_url = os.getenv("DATABASE_URL")
if env_url:
    config.set_main_option("sqlalchemy.url", env_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        compare_type=True,
        # version_table_schema="tracking_service",
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable: AsyncEngine = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        pool_timeout=30,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(_run_sync_migrations)


def _run_sync_migrations(connection: AsyncEngine) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        compare_type=True,
        # version_table_schema="tracking_service",
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
