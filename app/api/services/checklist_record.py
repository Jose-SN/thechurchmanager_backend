from typing import List
from fastapi import HTTPException
import asyncpg
import logging
from datetime import datetime, date
from app.api import dependencies
from app.queries.checklist_record import (
    GET_CHECKLIST_RECORDS_QUERY,
    GET_CHECKLIST_RECORD_BY_ID_QUERY,
    GET_CHECKLIST_RECORDS_BY_TEMPLATE_QUERY,
    GET_CHECKLIST_RECORDS_BY_TEAM_QUERY,
    INSERT_CHECKLIST_RECORD_QUERY,
    UPDATE_CHECKLIST_RECORD_QUERY,
    DELETE_CHECKLIST_RECORD_QUERY,
)


class ChecklistRecordService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    def _parse_date(self, value) -> date | None:
        if value is None:
            return None
        if isinstance(value, date):
            return value if not isinstance(value, datetime) else value.date()
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
            except ValueError:
                try:
                    return datetime.strptime(value, "%Y-%m-%d").date()
                except ValueError:
                    return None
        return None

    async def get_data(self, filters: dict = None) -> List[dict]:
        filters = filters or {}
        try:
            async with self.db_pool.acquire() as conn:
                if "id" in filters:
                    row = await conn.fetchrow(GET_CHECKLIST_RECORD_BY_ID_QUERY, filters["id"])
                    return [dependencies.convert_db_types(dict(row))] if row else []
                elif "template_id" in filters:
                    rows = await conn.fetch(GET_CHECKLIST_RECORDS_BY_TEMPLATE_QUERY, filters["template_id"])
                    return [dependencies.convert_db_types(dict(r)) for r in rows]
                elif "team_id" in filters:
                    rows = await conn.fetch(GET_CHECKLIST_RECORDS_BY_TEAM_QUERY, filters["team_id"])
                    return [dependencies.convert_db_types(dict(r)) for r in rows]
                rows = await conn.fetch(GET_CHECKLIST_RECORDS_QUERY)
                return [dependencies.convert_db_types(dict(r)) for r in rows]
        except Exception as e:
            logging.error(f"❌ Error fetching checklist record: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def save_data(self, data: dict) -> dict:
        try:
            async with self.db_pool.acquire() as conn:
                template_id = data.get("template_id")
                team_id = data.get("team_id")
                date_val = self._parse_date(data.get("date"))
                completed_by = (data.get("completed_by") or "").strip()
                notes = data.get("notes")
                if not template_id:
                    raise HTTPException(status_code=400, detail="template_id is required")
                if not team_id:
                    raise HTTPException(status_code=400, detail="team_id is required")
                if not date_val:
                    raise HTTPException(status_code=400, detail="date is required")
                if not completed_by:
                    raise HTTPException(status_code=400, detail="completed_by is required")
                row = await conn.fetchrow(
                    INSERT_CHECKLIST_RECORD_QUERY,
                    template_id, team_id, date_val, completed_by, notes
                )
                return dependencies.convert_db_types(dict(row)) if row else {}
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error saving checklist record: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_data(self, id: str, data: dict) -> dict:
        try:
            async with self.db_pool.acquire() as conn:
                existing = await conn.fetchrow(GET_CHECKLIST_RECORD_BY_ID_QUERY, id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Checklist record not found")
                merged = dict(existing)
                merged.update(data)
                completed_by = (merged.get("completed_by") or "").strip()
                if not completed_by:
                    raise HTTPException(status_code=400, detail="completed_by is required")
                row = await conn.fetchrow(
                    UPDATE_CHECKLIST_RECORD_QUERY,
                    completed_by,
                    merged.get("notes"),
                    id
                )
                return dependencies.convert_db_types(dict(row)) if row else {}
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error updating checklist record: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_data(self, id: str) -> str:
        try:
            async with self.db_pool.acquire() as conn:
                existing = await conn.fetchrow(GET_CHECKLIST_RECORD_BY_ID_QUERY, id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Checklist record not found")
                result = await conn.execute(DELETE_CHECKLIST_RECORD_QUERY, id)
                return "" if result else "Delete failed"
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error deleting checklist record: {e}")
            raise HTTPException(status_code=500, detail=str(e))
