"""
Run Service Rota SQL migration against PostgreSQL.

Usage:
    py -3 app/scripts/run_service_rota_migration.py

Requires DATABASE_URL or POSTGRESQL_DB_* in .env (same as the rest of the app).
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import asyncpg

from app.core.config import settings


async def run() -> None:
    if not settings.is_postgresql_configured():
        raise SystemExit("DATABASE_URL / POSTGRESQL_DB_* is not configured")

    sql_path = Path(__file__).parent / "create_service_rota_tables.sql"
    sql_content = sql_path.read_text(encoding="utf-8")

    kwargs = settings.get_asyncpg_connect_kwargs()
    if settings.POSTGRESQL_SSL_MODE and settings.POSTGRESQL_SSL_MODE != "disable":
        kwargs["ssl"] = settings.POSTGRESQL_SSL_MODE

    conn = await asyncpg.connect(**kwargs)
    try:
        print(f"Connected to {kwargs.get('database')} — running {sql_path.name}")
        await conn.execute(sql_content)
        print("Service Rota tables created successfully.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run())
