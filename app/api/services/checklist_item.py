from typing import List
from fastapi import HTTPException
import asyncpg
import logging
from app.api import dependencies
from app.queries.checklist_item import (
    GET_CHECKLIST_ITEMS_QUERY,
    GET_CHECKLIST_ITEM_BY_ID_QUERY,
    GET_CHECKLIST_ITEMS_BY_TEMPLATE_QUERY,
    INSERT_CHECKLIST_ITEM_QUERY,
    UPDATE_CHECKLIST_ITEM_QUERY,
    DELETE_CHECKLIST_ITEM_QUERY,
)


class ChecklistItemService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_data(self, filters: dict = None) -> List[dict]:
        filters = filters or {}
        try:
            async with self.db_pool.acquire() as conn:
                if "id" in filters:
                    row = await conn.fetchrow(GET_CHECKLIST_ITEM_BY_ID_QUERY, filters["id"])
                    return [dependencies.convert_db_types(dict(row))] if row else []
                elif "template_id" in filters:
                    rows = await conn.fetch(GET_CHECKLIST_ITEMS_BY_TEMPLATE_QUERY, filters["template_id"])
                    return [dependencies.convert_db_types(dict(r)) for r in rows]
                rows = await conn.fetch(GET_CHECKLIST_ITEMS_QUERY)
                return [dependencies.convert_db_types(dict(r)) for r in rows]
        except Exception as e:
            logging.error(f"❌ Error fetching checklist item: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def save_data(self, data: dict) -> dict:
        try:
            async with self.db_pool.acquire() as conn:
                template_id = data.get("template_id")
                title = (data.get("title") or "").strip()
                description = data.get("description")
                order_val = data.get("order", 0)
                is_required = data.get("is_required", False)
                if not template_id:
                    raise HTTPException(status_code=400, detail="template_id is required")
                if not title:
                    raise HTTPException(status_code=400, detail="title is required")
                row = await conn.fetchrow(
                    INSERT_CHECKLIST_ITEM_QUERY,
                    template_id, title, description, int(order_val) if order_val is not None else 0, is_required
                )
                return dependencies.convert_db_types(dict(row)) if row else {}
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error saving checklist item: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_data(self, id: str, data: dict) -> dict:
        try:
            async with self.db_pool.acquire() as conn:
                existing = await conn.fetchrow(GET_CHECKLIST_ITEM_BY_ID_QUERY, id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Checklist item not found")
                merged = dict(existing)
                merged.update(data)
                title = (merged.get("title") or "").strip()
                if not title:
                    raise HTTPException(status_code=400, detail="title is required")
                row = await conn.fetchrow(
                    UPDATE_CHECKLIST_ITEM_QUERY,
                    title,
                    merged.get("description"),
                    int(merged.get("order", 0)),
                    merged.get("is_required", False),
                    id
                )
                return dependencies.convert_db_types(dict(row)) if row else {}
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error updating checklist item: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_data(self, id: str) -> str:
        try:
            async with self.db_pool.acquire() as conn:
                existing = await conn.fetchrow(GET_CHECKLIST_ITEM_BY_ID_QUERY, id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Checklist item not found")
                result = await conn.execute(DELETE_CHECKLIST_ITEM_QUERY, id)
                return "" if result else "Delete failed"
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error deleting checklist item: {e}")
            raise HTTPException(status_code=500, detail=str(e))
