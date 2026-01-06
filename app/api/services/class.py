from typing import List
from fastapi import HTTPException
import asyncpg
import logging
from app.api import dependencies
from app.queries.class import (
    GET_CLASSES_QUERY,
    GET_CLASS_BY_ID_QUERY,
    GET_CLASSES_BY_ORGANIZATION_QUERY,
    GET_CLASSES_BY_TEACHER_QUERY,
    INSERT_CLASS_QUERY,
    UPDATE_CLASS_QUERY,
    DELETE_CLASS_QUERY,
)

class ClassService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_class_data(self, filters: dict = {}) -> List[dict]:
        """Get class data with filtering"""
        try:
            async with self.db_pool.acquire() as conn:
                if "id" in filters:
                    class_item = await conn.fetchrow(GET_CLASS_BY_ID_QUERY, filters["id"])
                    if class_item:
                        return [convert_db_types(dict(class_item))]
                    return []
                elif "organization_id" in filters:
                    rows = await conn.fetch(
                        GET_CLASSES_BY_ORGANIZATION_QUERY,
                        filters["organization_id"]
                    )
                    return [convert_db_types(dict(row)) for row in rows]
                elif "teacher_id" in filters:
                    rows = await conn.fetch(
                        GET_CLASSES_BY_TEACHER_QUERY,
                        filters["teacher_id"]
                    )
                    return [convert_db_types(dict(row)) for row in rows]
                rows = await conn.fetch(GET_CLASSES_QUERY)
                return [convert_db_types(dict(row)) for row in rows]
        except Exception as e:
            logging.error(f"❌ Error fetching class data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def save_class_data(self, class_data: dict) -> dict:
        """Save new class"""
        try:
            async with self.db_pool.acquire() as conn:
                name = class_data.get('name', '')
                description = class_data.get('description')
                organization_id = class_data.get('organization_id')
                teacher_id = class_data.get('teacher_id')
                
                row = await conn.fetchrow(
                    INSERT_CLASS_QUERY,
                    name,
                    description,
                    organization_id,
                    teacher_id
                )
                if row:
                    return convert_db_types(dict(row))
                return {}
        except Exception as e:
            logging.error(f"❌ Error saving class data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def update_class_data(self, class_id: str, class_data: dict) -> dict:
        """Update existing class"""
        if not class_id:
            raise HTTPException(status_code=400, detail="Class ID is required")
        
        try:
            async with self.db_pool.acquire() as conn:
                # Check if class exists
                existing = await conn.fetchrow(GET_CLASS_BY_ID_QUERY, class_id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Class not found")
                
                # Merge existing data with update data
                merged_data = dict(existing)
                merged_data.update(class_data)
                
                name = merged_data.get('name', '')
                description = merged_data.get('description')
                organization_id = merged_data.get('organization_id')
                teacher_id = merged_data.get('teacher_id')
                
                row = await conn.fetchrow(
                    UPDATE_CLASS_QUERY,
                    name,
                    description,
                    organization_id,
                    teacher_id,
                    class_id
                )
                if row:
                    return convert_db_types(dict(row))
                raise HTTPException(status_code=404, detail="Class not found")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error updating class data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def delete_class_data(self, class_id: str) -> str:
        """Delete class"""
        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.execute(DELETE_CLASS_QUERY, class_id)
                if result and result.startswith("DELETE 1"):
                    return ""
                raise HTTPException(status_code=404, detail="Class not found")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error deleting class data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

