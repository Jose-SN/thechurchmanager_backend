from typing import List
from fastapi import HTTPException
import asyncpg
import logging
from app.api import dependencies

from app.queries.teacher import (
    GET_TEACHERS_QUERY,
    GET_TEACHER_BY_ID_QUERY,
    GET_TEACHERS_BY_ORGANIZATION_QUERY,
    INSERT_TEACHER_QUERY,
    UPDATE_TEACHER_QUERY,
    DELETE_TEACHER_QUERY,
)

class TeacherService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_teacher_data(self, filters: dict = {}) -> List[dict]:
        """Get teacher data with filtering"""
        try:
            async with self.db_pool.acquire() as conn:
                if "id" in filters:
                    teacher = await conn.fetchrow(GET_TEACHER_BY_ID_QUERY, filters["id"])
                    if teacher:
                        return [dependencies.convert_db_types(dict(teacher))]
                    return []
                elif "organization_id" in filters:
                    rows = await conn.fetch(
                        GET_TEACHERS_BY_ORGANIZATION_QUERY,
                        filters["organization_id"]
                    )
                    return [dependencies.convert_db_types(dict(row)) for row in rows]
                rows = await conn.fetch(GET_TEACHERS_QUERY)
                return [dependencies.convert_db_types(dict(row)) for row in rows]
        except Exception as e:
            logging.error(f"❌ Error fetching teacher data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def save_teacher_data(self, teacher_data: dict) -> dict:
        """Save new teacher"""
        try:
            async with self.db_pool.acquire() as conn:
                name = teacher_data.get('name', '')
                email = teacher_data.get('email')
                phone = teacher_data.get('phone')
                organization_id = teacher_data.get('organization_id')
                
                row = await conn.fetchrow(
                    INSERT_TEACHER_QUERY,
                    name,
                    email,
                    phone,
                    organization_id
                )
                if row:
                    return dependencies.convert_db_types(dict(row))
                return {}
        except Exception as e:
            logging.error(f"❌ Error saving teacher data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def save_bulk_teacher_data(self, teachers_data: list[dict]) -> list[dict]:
        """Save multiple teachers"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = []
                for teacher in teachers_data:
                    name = teacher.get('name', '')
                    email = teacher.get('email')
                    phone = teacher.get('phone')
                    organization_id = teacher.get('organization_id')
                    
                    row = await conn.fetchrow(
                        INSERT_TEACHER_QUERY,
                        name,
                        email,
                        phone,
                        organization_id
                    )
                    if row:
                        rows.append(dependencies.convert_db_types(dict(row)))
                return rows
        except Exception as e:
            logging.error(f"❌ Error saving bulk teacher data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def update_teacher_data(self, teacher_id: str, teacher_data: dict) -> dict:
        """Update existing teacher"""
        if not teacher_id:
            raise HTTPException(status_code=400, detail="Teacher ID is required")
        
        try:
            async with self.db_pool.acquire() as conn:
                # Check if teacher exists
                existing = await conn.fetchrow(GET_TEACHER_BY_ID_QUERY, teacher_id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Teacher not found")
                
                # Merge existing data with update data
                merged_data = dict(existing)
                merged_data.update(teacher_data)
                
                name = merged_data.get('name', '')
                email = merged_data.get('email')
                phone = merged_data.get('phone')
                organization_id = merged_data.get('organization_id')
                
                row = await conn.fetchrow(
                    UPDATE_TEACHER_QUERY,
                    name,
                    email,
                    phone,
                    organization_id,
                    teacher_id
                )
                if row:
                    return dependencies.convert_db_types(dict(row))
                raise HTTPException(status_code=404, detail="Teacher not found")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error updating teacher data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def delete_teacher_data(self, teacher_id: str) -> str:
        """Delete teacher"""
        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.execute(DELETE_TEACHER_QUERY, teacher_id)
                if result and result.startswith("DELETE 1"):
                    return ""
                raise HTTPException(status_code=404, detail="Teacher not found")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error deleting teacher data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
