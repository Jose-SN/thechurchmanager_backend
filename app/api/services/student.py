from typing import List
from fastapi import HTTPException
import asyncpg
import logging
from app.api import dependencies
from app.queries.student import (
    GET_STUDENTS_QUERY,
    GET_STUDENT_BY_ID_QUERY,
    GET_STUDENTS_BY_ORGANIZATION_QUERY,
    GET_STUDENTS_BY_CLASS_QUERY,
    INSERT_STUDENT_QUERY,
    UPDATE_STUDENT_QUERY,
    DELETE_STUDENT_QUERY,
)

class StudentService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool


    async def get_student_data(self, filters: dict = {}) -> List[dict]:
        """Get student data with filtering"""
        try:
            async with self.db_pool.acquire() as conn:
                if "id" in filters:
                    student = await conn.fetchrow(GET_STUDENT_BY_ID_QUERY, filters["id"])
                    if student:
                        return [dependencies.convert_db_types(dict(student))]
                    return []
                elif "organization_id" in filters:
                    rows = await conn.fetch(
                        GET_STUDENTS_BY_ORGANIZATION_QUERY,
                        filters["organization_id"]
                    )
                    return [dependencies.convert_db_types(dict(row)) for row in rows]
                elif "class_id" in filters:
                    rows = await conn.fetch(
                        GET_STUDENTS_BY_CLASS_QUERY,
                        filters["class_id"]
                    )
                    return [dependencies.convert_db_types(dict(row)) for row in rows]
                rows = await conn.fetch(GET_STUDENTS_QUERY)
                return [dependencies.convert_db_types(dict(row)) for row in rows]
        except Exception as e:
            logging.error(f"❌ Error fetching student data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def save_student_data(self, student_data: dict) -> dict:
        """Save new student"""
        try:
            async with self.db_pool.acquire() as conn:
                first_name = student_data.get('first_name', '')
                last_name = student_data.get('last_name', '')
                email = student_data.get('email')
                phone = student_data.get('phone')
                organization_id = dependencies.convert_objectid(student_data.get('organization_id'))
                class_id = dependencies.convert_objectid(student_data.get('class_id'))
                
                row = await conn.fetchrow(
                    INSERT_STUDENT_QUERY,
                    first_name,
                    last_name,
                    email,
                    phone,
                    organization_id,
                    class_id
                )
                if row:
                    return dependencies.convert_db_types(dict(row))
                return {}
        except Exception as e:
            logging.error(f"❌ Error saving student data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def update_student_data(self, student_id: str, student_data: dict) -> dict:
        """Update existing student"""
        if not student_id:
            raise HTTPException(status_code=400, detail="Student ID is required")
        
        try:
            async with self.db_pool.acquire() as conn:
                # Check if student exists
                existing = await conn.fetchrow(GET_STUDENT_BY_ID_QUERY, student_id)
                if not existing:
                    raise HTTPException(status_code=404, detail="Student not found")
                
                # Merge existing data with update data
                merged_data = dict(existing)
                merged_data.update(student_data)
                
                first_name = merged_data.get('first_name', '')
                last_name = merged_data.get('last_name', '')
                email = merged_data.get('email')
                phone = merged_data.get('phone')
                organization_id = dependencies.convert_objectid(merged_data.get('organization_id'))
                class_id = dependencies.convert_objectid(merged_data.get('class_id'))
                
                row = await conn.fetchrow(
                    UPDATE_STUDENT_QUERY,
                    first_name,
                    last_name,
                    email,
                    phone,
                    organization_id,
                    class_id,
                    student_id
                )
                if row:
                    return dependencies.convert_db_types(dict(row))
                raise HTTPException(status_code=404, detail="Student not found")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error updating student data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

    async def delete_student_data(self, student_id: str) -> str:
        """Delete student"""
        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.execute(DELETE_STUDENT_QUERY, student_id)
                if result and result.startswith("DELETE 1"):
                    return ""
                raise HTTPException(status_code=404, detail="Student not found")
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"❌ Error deleting student data: {e}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

