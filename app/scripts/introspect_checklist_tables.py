"""
Inspect checklist table schemas (columns, FKs, indexes) against the target contract.

Usage:
    py -3 -m app.scripts.introspect_checklist_tables
"""
import asyncio
import json

import asyncpg
import ssl

from app.core.config import settings

TABLES = [
    "checklist_templates",
    "checklist_items",
    "checklist_records",
    "checklist_item_statuses",
]

TARGET = {
    "checklist_templates": [
        "id",
        "organization_id",
        "team_id",
        "name",
        "description",
        "is_active",
        "created_by",
        "created_at",
        "updated_at",
    ],
    "checklist_items": [
        "id",
        "template_id",
        "title",
        "description",
        "order",
        "is_required",
        "created_at",
        "updated_at",
    ],
    "checklist_records": [
        "id",
        "organization_id",
        "template_id",
        "team_id",
        "date",
        "completed_by",
        "notes",
        "created_at",
        "updated_at",
    ],
    "checklist_item_statuses": [
        "id",
        "checklist_record_id",
        "checklist_item_id",
        "is_checked",
        "issue_reported",
        "updated_at",
    ],
}


async def main() -> None:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    conn = await asyncpg.connect(
        host=settings.POSTGRESQL_DB_HOST,
        port=settings.POSTGRESQL_DB_PORT,
        user=settings.POSTGRESQL_DB_USER,
        password=settings.POSTGRESQL_DB_PASSWORD,
        database=settings.POSTGRESQL_DB_NAME,
        ssl=ctx,
    )
    report: dict = {"tables": {}, "gaps": {}}
    for table in TABLES:
        cols = await conn.fetch(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = $1
            ORDER BY ordinal_position
            """,
            table,
        )
        fks = await conn.fetch(
            """
            SELECT tc.constraint_name, kcu.column_name, ccu.table_name AS foreign_table
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
              ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'public'
              AND tc.table_name = $1
            """,
            table,
        )
        idx = await conn.fetch(
            """
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = 'public' AND tablename = $1
            """,
            table,
        )
        existing_cols = [c["column_name"] for c in cols]
        missing = [c for c in TARGET[table] if c not in existing_cols]
        report["tables"][table] = {
            "columns": [dict(c) for c in cols],
            "foreign_keys": [dict(f) for f in fks],
            "indexes": [dict(i) for i in idx],
        }
        report["gaps"][table] = {"missing_columns": missing}

    await conn.close()
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
