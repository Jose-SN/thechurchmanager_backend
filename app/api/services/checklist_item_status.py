from typing import List
from fastapi import HTTPException
import asyncpg
import logging
from app.api import dependencies
from app.queries.checklist_item_status import (
    GET_CHECKLIST_ITEM_STATUSES_QUERY,
    GET_CHECKLIST_ITEM_STATUS_BY_ID_QUERY,
    GET_CHECKLIST_ITEM_STATUSES_BY_RECORD_QUERY,
    INSERT_CHECKLIST_ITEM_STATUS_QUERY,
    UPDATE_CHECKLIST_ITEM_STATUS_QUERY,
    DELETE_CHECKLIST_ITEM_STATUS_QUERY,
)


class ChecklistItemStatusService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_data(self, filters: dict = None) -> List[dict]:
        filters = filters or {}
        try:
            async with self.db_pool.acquire() as conn:
                if "id" in filters:
                    row = await conn.fetchrow(GET_CHECKLIST_ITEM_STATUS_BY_ID_QUERY, filters["id"])
                    return [dependencies.convert_db_types(dict(row))] if row else []
                elif "checklist_record_id" in filters:
                    rows = await conn.fetch(
                        GET_CHECKLIST_ITEM_STATUSES_BY_RECORD_QUERY,
                        filters["checklist_record_id"]
                    )
                    return [dependencies.convert_db_types(dict(r)) for r in rows]
                rows = await conn.fetch(GET_CHECKLIST_ITEM_STATUSES_QUERY)
                return [dependencies.convert_db_types(dict(r)) for r in rows]
        except Exception as e:
            logging.error(f"❌ Error fetching checklist item status: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def save_data(self, data: dict) -> dict:
        try:
            async with self.db_pool.acquire() as conn:
                record_id = data.get("checklist_record_id")
                item_id = data.get("checklist_item_id")
                is_checked = data.get("is_checked", False)
                issue_reported = data.get("issue_reported")
                if not record_id:
                    raise HTTPException(status_code=400, detail="checklist_record_id is required")
                if not item_id:
                    raise HTTPException(status_code=400, detail="checklist_item_id is required")
                row = await conn.fetchrow(
                    INSERT_CHECKLIST_ITEM_STATUS_QUERY,
                    record_id, item_id, is_checked, issue_reported
                )
                return dependencies.convert_db_types(dict(row)) if row else {}
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error saving checklist item status: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_data(self, id: str, data: dict) -> dict:
        try:
            async with self.db_pool.acquire() as conn:
                existing = await conn.fetchrow(GET_CHECKLIST_ITEM_STATUS_BY_ID_QUERY, id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Checklist item status not found")
                merged = dict(existing)
                merged.update(data)
                row = await conn.fetchrow(
                    UPDATE_CHECKLIST_ITEM_STATUS_QUERY,
                    merged.get("is_checked", False),
                    merged.get("issue_reported"),
                    id
                )
                return dependencies.convert_db_types(dict(row)) if row else {}
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error updating checklist item status: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_data(self, id: str) -> str:
        try:
            async with self.db_pool.acquire() as conn:
                existing = await conn.fetchrow(GET_CHECKLIST_ITEM_STATUS_BY_ID_QUERY, id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Checklist item status not found")
                result = await conn.execute(DELETE_CHECKLIST_ITEM_STATUS_QUERY, id)
                return "" if result else "Delete failed"
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error deleting checklist item status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
