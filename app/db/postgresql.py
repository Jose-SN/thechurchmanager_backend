import asyncio
import asyncpg
import logging
import ssl

from app.core.config import settings

pool = None

POSTGRESQL_CONFIG_HELP = (
    "Configure PostgreSQL via environment variables: "
    "POSTGRESQL_DB_HOST, POSTGRESQL_DB_PORT, POSTGRESQL_DB_NAME, "
    "POSTGRESQL_DB_USER, POSTGRESQL_DB_PASSWORD, POSTGRESQL_SSL_MODE=require "
    "(or set DATABASE_URL)."
)


def _build_ssl_config():
    ssl_mode = settings.POSTGRESQL_SSL_MODE
    if ssl_mode in ("require", "prefer"):
        ssl_config = ssl.create_default_context()
        if not settings.POSTGRESQL_SSL_REJECT_UNAUTHORIZED:
            ssl_config.check_hostname = False
            ssl_config.verify_mode = ssl.CERT_NONE
        return ssl_config
    return None


async def connect_postgresql(*, retries: int = 5, delay_seconds: float = 2.0):
    """Create and return an asyncpg connection pool with startup retries."""
    global pool

    if pool is not None:
        return pool

    if not settings.is_postgresql_configured():
        message = f"PostgreSQL is not configured. {POSTGRESQL_CONFIG_HELP}"
        logging.error(message)
        raise RuntimeError(message)

    ssl_config = _build_ssl_config()
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            pool = await asyncpg.create_pool(
                host=settings.POSTGRESQL_DB_HOST,
                port=settings.POSTGRESQL_DB_PORT,
                user=settings.POSTGRESQL_DB_USER,
                password=settings.POSTGRESQL_DB_PASSWORD,
                database=settings.POSTGRESQL_DB_NAME,
                ssl=ssl_config,
                min_size=1,
                max_size=10,
            )
            logging.info(
                "PostgreSQL connected to %s:%s/%s",
                settings.POSTGRESQL_DB_HOST,
                settings.POSTGRESQL_DB_PORT,
                settings.POSTGRESQL_DB_NAME,
            )
            print(
                f"PostgreSQL connected to {settings.POSTGRESQL_DB_HOST}:"
                f"{settings.POSTGRESQL_DB_PORT}/{settings.POSTGRESQL_DB_NAME}"
            )
            return pool
        except Exception as exc:
            last_error = exc
            logging.warning(
                "PostgreSQL connection attempt %s/%s failed: %s",
                attempt,
                retries,
                exc,
            )
            if attempt < retries:
                await asyncio.sleep(delay_seconds)

    message = (
        f"PostgreSQL connection failed after {retries} attempts to "
        f"{settings.POSTGRESQL_DB_HOST}:{settings.POSTGRESQL_DB_PORT}/"
        f"{settings.POSTGRESQL_DB_NAME}: {last_error}. {POSTGRESQL_CONFIG_HELP}"
    )
    logging.error(message)
    raise RuntimeError(message) from last_error


async def close_postgresql():
    """Close the PostgreSQL connection pool."""
    global pool
    if pool is not None:
        await pool.close()
        pool = None
        logging.info("PostgreSQL connection pool closed")


def get_pool():
    """Get the current PostgreSQL connection pool."""
    return pool


async def get_connection(*, retries: int = 5, delay_seconds: float = 2.0):
    """Return the PostgreSQL connection pool."""
    return await connect_postgresql(retries=retries, delay_seconds=delay_seconds)
