from typing import List
from fastapi import HTTPException
import asyncpg
import logging
from app.api import dependencies
from app.queries.checklist_template import (
    GET_CHECKLIST_TEMPLATES_QUERY,
    GET_CHECKLIST_TEMPLATE_BY_ID_QUERY,
    GET_CHECKLIST_TEMPLATES_BY_TEAM_QUERY,
    INSERT_CHECKLIST_TEMPLATE_QUERY,
    UPDATE_CHECKLIST_TEMPLATE_QUERY,
    DELETE_CHECKLIST_TEMPLATE_QUERY,
)
from app.queries.checklist_item import INSERT_CHECKLIST_ITEM_QUERY


class ChecklistTemplateService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_data(self, filters: dict = None) -> List[dict]:
        filters = filters or {}
        try:
            async with self.db_pool.acquire() as conn:
                if "id" in filters:
                    row = await conn.fetchrow(GET_CHECKLIST_TEMPLATE_BY_ID_QUERY, filters["id"])
                    return [dependencies.convert_db_types(dict(row))] if row else []
                elif "team_id" in filters:
                    rows = await conn.fetch(GET_CHECKLIST_TEMPLATES_BY_TEAM_QUERY, filters["team_id"])
                    return [dependencies.convert_db_types(dict(r)) for r in rows]
                rows = await conn.fetch(GET_CHECKLIST_TEMPLATES_QUERY)
                return [dependencies.convert_db_types(dict(r)) for r in rows]
        except Exception as e:
            logging.error(f"❌ Error fetching checklist template: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def save_data(self, data: dict) -> dict:
        try:
            async with self.db_pool.acquire() as conn:
                items = data.pop("items", [])  # Extract items before template insert
                team_id = data.get("team_id")
                name = (data.get("name") or "").strip()
                description = data.get("description")
                is_active = data.get("is_active", True)
                created_by = data.get("created_by")
                if not team_id:
                    raise HTTPException(status_code=400, detail="team_id is required")
                if not name:
                    raise HTTPException(status_code=400, detail="name is required")
                row = await conn.fetchrow(
                    INSERT_CHECKLIST_TEMPLATE_QUERY,
                    team_id, name, description, is_active, created_by
                )
                if not row:
                    return {}
                template_id = row["id"]
                # Create items if provided
                created_items = []
                if items and isinstance(items, list):
                    for i, item in enumerate(items):
                        title = (item.get("title") or "").strip()
                        desc = item.get("description")
                        order_val = item.get("order", i)
                        is_req = item.get("is_required", False)
                        if title:
                            item_row = await conn.fetchrow(
                                INSERT_CHECKLIST_ITEM_QUERY,
                                template_id, title, desc,
                                int(order_val) if order_val is not None else i,
                                is_req
                            )
                            if item_row:
                                created_items.append(dependencies.convert_db_types(dict(item_row)))
                result = dependencies.convert_db_types(dict(row))
                if created_items:
                    result["items"] = created_items
                return result
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error saving checklist template: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_data(self, id: str, data: dict) -> dict:
        try:
            async with self.db_pool.acquire() as conn:
                existing = await conn.fetchrow(GET_CHECKLIST_TEMPLATE_BY_ID_QUERY, id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Checklist template not found")
                merged = dict(existing)
                merged.update(data)
                name = (merged.get("name") or "").strip()
                if not name:
                    raise HTTPException(status_code=400, detail="name is required")
                row = await conn.fetchrow(
                    UPDATE_CHECKLIST_TEMPLATE_QUERY,
                    name,
                    merged.get("description"),
                    merged.get("is_active", True),
                    merged.get("created_by"),
                    id
                )
                return dependencies.convert_db_types(dict(row)) if row else {}
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error updating checklist template: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_data(self, id: str) -> str:
        try:
            async with self.db_pool.acquire() as conn:
                existing = await conn.fetchrow(GET_CHECKLIST_TEMPLATE_BY_ID_QUERY, id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Checklist template not found")
                result = await conn.execute(DELETE_CHECKLIST_TEMPLATE_QUERY, id)
                return "" if result else "Delete failed"
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error deleting checklist template: {e}")
            raise HTTPException(status_code=500, detail=str(e))
