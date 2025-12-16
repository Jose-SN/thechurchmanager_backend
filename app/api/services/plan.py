from typing import List
from fastapi import HTTPException
import asyncpg

from app.queries.plan import (
    GET_PLANS_QUERY,
    GET_PLAN_BY_ID_QUERY,
    INSERT_PLAN_QUERY,
    INSERT_BULK_PLANS_QUERY,
    UPDATE_PLAN_QUERY,
    DELETE_PLAN_QUERY,
)

class PlanService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_plan_data(self, filters: dict = {}) -> List[dict]:
        async with self.db_pool.acquire() as conn:
            if "id" in filters:
                plan_id = filters.get("id")
                plan = await conn.fetchrow(GET_PLAN_BY_ID_QUERY, plan_id)
                if plan:
                    return [dict(plan)]
                return []
            rows = await conn.fetch(GET_PLANS_QUERY)
            return [dict(row) for row in rows]

    async def save_plan_data(self, plan_data: dict) -> dict:
        async with self.db_pool.acquire() as conn:
            # Extract values in the correct order for INSERT_PLAN_QUERY
            name = plan_data.get("name", "")
            description = plan_data.get("description", "")
            row = await conn.fetchrow(INSERT_PLAN_QUERY, name, description)
            return dict(row) if row else {}

    async def save_bulk_plan_data(self, plans_data: list[dict]) -> list[dict]:
        """
        Bulk insert plans and return the inserted plan documents.
        """
        rows = []
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                for plan in plans_data:
                    name = plan.get("name", "")
                    description = plan.get("description", "")
                    row = await conn.fetchrow(INSERT_PLAN_QUERY, name, description)
                    if row:
                        rows.append(dict(row))
        return rows

    async def update_plan_data(self, plan_data: dict) -> dict:
        plan_id = plan_data.get("id")
        if not plan_id:
            raise HTTPException(status_code=400, detail="Plan ID is required")
        
        async with self.db_pool.acquire() as conn:
            update_data = {k: v for k, v in plan_data.items() if k not in ("id")}
            name = update_data.get("name", "")
            description = update_data.get("description", "")
            
            row = await conn.fetchrow(UPDATE_PLAN_QUERY, name, description, plan_id)
            if not row:
                raise ValueError("Plan not found")
            return dict(row)

    async def delete_plan_data(self, plan_id: str) -> str:
        async with self.db_pool.acquire() as conn:
            result = await conn.execute(DELETE_PLAN_QUERY, plan_id)
            if result and result.startswith("DELETE"):
                return ""
            return "Plan not found"
