from typing import List
from fastapi import HTTPException
import asyncpg

from app.queries.teacher import (
    GET_TEACHERS_QUERY,
    GET_TEACHER_BY_ID_QUERY,
    INSERT_TEACHER_QUERY,
    INSERT_BULK_TEACHERS_QUERY,
    UPDATE_TEACHER_QUERY,
    DELETE_TEACHER_QUERY,
)

class TeacherService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_teacher_data(self, filters: dict = {}) -> List[dict]:
        async with self.db_pool.acquire() as conn:
            if "_id" in filters:
                teacher = await conn.fetchrow(GET_TEACHER_BY_ID_QUERY, filters["_id"])
                if teacher:
                    return [dict(teacher)]
                return []
            rows = await conn.fetch(GET_TEACHERS_QUERY)
            return [dict(row) for row in rows]

    async def save_teacher_data(self, teacher_data: dict) -> dict:
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(INSERT_TEACHER_QUERY, *teacher_data.values())
            return dict(row) if row else {}

    async def save_bulk_teacher_data(self, teachers_data: list[dict]) -> list[dict]:
        async with self.db_pool.acquire() as conn:
            rows = []
            for teacher in teachers_data:
                row = await conn.fetchrow(INSERT_TEACHER_QUERY, *teacher.values())
                if row:
                    rows.append(dict(row))
            return rows

    async def update_teacher_data(self, teacher_data: dict) -> dict:
        teacher_id = teacher_data.get("id") or teacher_data.get("_id")
        if not teacher_id:
            raise HTTPException(status_code=400, detail="Teacher ID is required")
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(UPDATE_TEACHER_QUERY, *teacher_data.values(), teacher_id)
            if not row:
                raise ValueError("Teacher not found")
            return dict(row)

    async def delete_teacher_data(self, teacher_id: str) -> str:
        async with self.db_pool.acquire() as conn:
            result = await conn.execute(DELETE_TEACHER_QUERY, teacher_id)
            if result and result.startswith("DELETE"):
                return ""
            return "Teacher not found"
