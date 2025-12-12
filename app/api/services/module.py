from typing import List
from fastapi import HTTPException
import asyncpg

from app.queries.module import (
    GET_MODULES_QUERY,
    GET_MODULE_BY_ID_QUERY,
    GET_MODULES_BY_ORGANIZATION_QUERY,
    INSERT_MODULE_QUERY,
    INSERT_BULK_MODULES_QUERY,
    UPDATE_MODULE_QUERY,
    DELETE_MODULE_QUERY,
)

class ModuleService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_module_data(self, filters: dict = {}) -> List[dict]:
        async with self.db_pool.acquire() as conn:
            if "id" in filters or "_id" in filters:
                module_id = filters.get("id") or filters.get("_id")
                module = await conn.fetchrow(GET_MODULE_BY_ID_QUERY, module_id)
                if module:
                    return [dict(module)]
                return []
            elif "organization_id" in filters:
                rows = await conn.fetch(GET_MODULES_BY_ORGANIZATION_QUERY, filters["organization_id"])
                return [dict(row) for row in rows]
            rows = await conn.fetch(GET_MODULES_QUERY)
            return [dict(row) for row in rows]

    async def save_module_data(self, module_data: dict) -> dict:
        async with self.db_pool.acquire() as conn:
            # Extract values in the correct order for INSERT_MODULE_QUERY
            name = module_data.get("name", "")
            description = module_data.get("description", "")
            organization_id = module_data.get("organization_id")
            
            row = await conn.fetchrow(INSERT_MODULE_QUERY, name, description, organization_id)
            return dict(row) if row else {}

    async def save_bulk_module_data(self, modules_data: list[dict]) -> list[dict]:
        """
        Bulk insert modules and return the inserted module documents.
        """
        rows = []
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                for module in modules_data:
                    name = module.get("name", "")
                    description = module.get("description", "")
                    organization_id = module.get("organization_id")
                    
                    row = await conn.fetchrow(INSERT_MODULE_QUERY, name, description, organization_id)
                    if row:
                        rows.append(dict(row))
        return rows

    async def update_module_data(self, module_data: dict) -> dict:
        module_id = module_data.get("id") or module_data.get("_id")
        if not module_id:
            raise HTTPException(status_code=400, detail="Module ID is required")
        
        async with self.db_pool.acquire() as conn:
            update_data = {k: v for k, v in module_data.items() if k not in ("_id", "id")}
            name = update_data.get("name", "")
            description = update_data.get("description", "")
            organization_id = update_data.get("organization_id", "")
            
            row = await conn.fetchrow(UPDATE_MODULE_QUERY, name, description, organization_id, module_id)
            if not row:
                raise ValueError("Module not found")
            return dict(row)

    async def delete_module_data(self, module_id: str) -> str:
        async with self.db_pool.acquire() as conn:
            result = await conn.execute(DELETE_MODULE_QUERY, module_id)
            if result and result.startswith("DELETE"):
                return ""
            return "Module not found"
