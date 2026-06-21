import asyncio
import asyncpg
import logging
import ssl

from app.core.config import settings

pool = None

POSTGRESQL_CONFIG_HELP = (
    "Configure PostgreSQL via DATABASE_URL "
    "(recommended for Supabase) or POSTGRESQL_DB_* variables."
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
    connect_kwargs = settings.get_asyncpg_connect_kwargs()
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            pool = await asyncpg.create_pool(
                **connect_kwargs,
                ssl=ssl_config,
                min_size=1,
                max_size=10,
            )
            logging.info(
                "PostgreSQL connected to %s:%s/%s",
                connect_kwargs["host"],
                connect_kwargs["port"],
                connect_kwargs["database"],
            )
            print(
                f"PostgreSQL connected to {connect_kwargs['host']}:"
                f"{connect_kwargs['port']}/{connect_kwargs['database']}"
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
        f"{connect_kwargs['host']}:{connect_kwargs['port']}/"
        f"{connect_kwargs['database']}: {last_error}. {POSTGRESQL_CONFIG_HELP}"
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
