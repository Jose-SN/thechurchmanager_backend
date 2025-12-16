from typing import List
from fastapi import HTTPException
import asyncpg

from app.queries.inventory import (
    GET_INVENTORIES_QUERY,
    GET_INVENTORY_BY_ID_QUERY,
    INSERT_INVENTORY_QUERY,
    INSERT_BULK_INVENTORIES_QUERY,
    UPDATE_INVENTORY_QUERY,
    DELETE_INVENTORY_QUERY,
)

class InventoryService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def get_inventory_data(self, filters: dict = {}) -> List[dict]:
        async with self.db_pool.acquire() as conn:
            if "id" in filters:
                inventory_id = filters.get("id")
                inventory = await conn.fetchrow(GET_INVENTORY_BY_ID_QUERY, inventory_id)
                if inventory:
                    return [dict(inventory)]
                return []
            rows = await conn.fetch(GET_INVENTORIES_QUERY)
            return [dict(row) for row in rows]

    async def save_inventory_data(self, inventory_data: dict) -> dict:
        async with self.db_pool.acquire() as conn:
            # Extract values in the correct order for INSERT_INVENTORY_QUERY
            name = inventory_data.get("name", "")
            description = inventory_data.get("description", "")
            quantity = inventory_data.get("quantity", 0)
            row = await conn.fetchrow(INSERT_INVENTORY_QUERY, name, description, quantity)
            return dict(row) if row else {}

    async def save_bulk_inventory_data(self, inventorys_data: list[dict]) -> list[dict]:
        """
        Bulk insert inventories and return the inserted inventory documents.
        """
        rows = []
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                for inventory in inventorys_data:
                    name = inventory.get("name", "")
                    description = inventory.get("description", "")
                    quantity = inventory.get("quantity", 0)
                    row = await conn.fetchrow(INSERT_INVENTORY_QUERY, name, description, quantity)
                    if row:
                        rows.append(dict(row))
        return rows

    async def update_inventory_data(self, inventory_data: dict) -> dict:
        inventory_id = inventory_data.get("id")
        if not inventory_id:
            raise HTTPException(status_code=400, detail="Inventory ID is required")
        
        async with self.db_pool.acquire() as conn:
            update_data = {k: v for k, v in inventory_data.items() if k not in ("id")}
            name = update_data.get("name", "")
            description = update_data.get("description", "")
            quantity = update_data.get("quantity", 0)
            
            row = await conn.fetchrow(UPDATE_INVENTORY_QUERY, name, description, quantity, inventory_id)
            if not row:
                raise ValueError("Inventory not found")
            return dict(row)

    async def delete_inventory_data(self, inventory_id: str) -> str:
        async with self.db_pool.acquire() as conn:
            result = await conn.execute(DELETE_INVENTORY_QUERY, inventory_id)
            if result and result.startswith("DELETE"):
                return ""
            return "Inventory not found"
