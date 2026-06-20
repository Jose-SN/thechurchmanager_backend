import ssl
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _build_database_url() -> str:
    user = settings.POSTGRESQL_DB_USER
    password = settings.POSTGRESQL_DB_PASSWORD
    host = settings.POSTGRESQL_DB_HOST
    port = settings.POSTGRESQL_DB_PORT
    name = settings.POSTGRESQL_DB_NAME
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"


def _build_connect_args() -> dict:
    if settings.POSTGRESQL_SSL_MODE in ("require", "prefer"):
        ctx = ssl.create_default_context()
        if not settings.POSTGRESQL_SSL_REJECT_UNAUTHORIZED:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        return {"ssl": ctx}
    return {}


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            _build_database_url(),
            connect_args=_build_connect_args(),
            pool_pre_ping=True,
            echo=False,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session


async def init_sqlalchemy() -> None:
    get_engine()


async def close_sqlalchemy() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
