from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from uvicorn import Config
from fastapi import HTTPException
from bson import ObjectId

from app.api import dependencies
from app.core.config import Settings

class InventoryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.inventorys = db["inventorys"]

    async def get_inventory_data(self, filters: dict = {}) -> List[dict]:
        query = {}
        if filters:
            query = filters.copy()
            if "_id" in query:
                try:
                    query["_id"] = ObjectId(query["_id"])
                except Exception:
                    # Invalid ObjectId, will return empty result
                    return []
        inventorys = await self.inventorys.find(query).to_list(length=None)
        for inventory in inventorys:
            if "_id" in inventory:
                inventory["_id"] = str(inventory["_id"])
        return inventorys

    async def save_inventory_data(self, inventory_data: dict) -> dict:
        # Hash password before save
        # if "password" in inventory_data and inventory_data["password"]:
        #     inventory_data["password"] = pwd_context.hash(inventory_data["password"])

        result = await self.inventorys.insert_one(inventory_data)
        inventory = await self.inventorys.find_one({"_id": result.inserted_id})
        return inventory if inventory is not None else {}
    
    
    async def save_bulk_inventory_data(self, inventorys_data: list[dict]) -> list[dict]:
        """
        Bulk insert inventorys and return the inserted inventory documents.
        """
        result = await self.inventorys.insert_many(inventorys_data)
        inserted_ids = result.inserted_ids
        inventorys = await self.inventorys.find({"_id": {"$in": inserted_ids}}).to_list(length=len(inserted_ids))
        return inventorys


    async def update_inventory_data(self, inventory_data: dict) -> dict:
        inventory_id = inventory_data.get("_id")
        # if not inventory_id or not ObjectId.is_valid(inventory_id):
        #     raise ValueError("Invalid inventory ID")

        # if "password" in inventory_data and inventory_data["password"]:
        #     inventory_data["password"] = pwd_context.hash(inventory_data["password"])

        update_fields = inventory_data.copy()
        update_fields.pop("_id", None)
        update_result = await self.inventorys.find_one_and_update(
            {"_id": dependencies.try_objectid(inventory_id)},
            {"$set": update_fields},
            return_document=True  # Returns updated document
        )

        if not update_result:
            raise ValueError("Inventory not found")
        return update_result

    async def delete_inventory_data(self, inventory_id: str) -> str:
        if not ObjectId.is_valid(inventory_id):
            raise HTTPException(status_code=400, detail="Invalid inventory ID")
        result = await self.inventorys.find_one_and_delete({"_id": str(inventory_id)})
        return "" if result else "Inventory not found"
