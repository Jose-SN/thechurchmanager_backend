from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from uvicorn import Config
from fastapi import HTTPException
from bson import ObjectId

from app.api import dependencies
from app.core.config import Settings

class ModuleService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.modules = db["modules"]

    async def get_module_data(self) -> List[dict]:
        modules = await self.modules.find({}).to_list(length=None)
        for module in modules:
            if "_id" in module:
                module["_id"] = str(module["_id"])
        return modules

    async def save_module_data(self, module_data: dict) -> dict:
        # Hash password before save
        # if "password" in module_data and module_data["password"]:
        #     module_data["password"] = pwd_context.hash(module_data["password"])

        result = await self.modules.insert_one(module_data)
        module = await self.modules.find_one({"_id": result.inserted_id})
        return module if module is not None else {}
    
    
    async def save_bulk_module_data(self, modules_data: list[dict]) -> list[dict]:
        """
        Bulk insert modules and return the inserted module documents.
        """
        result = await self.modules.insert_many(modules_data)
        inserted_ids = result.inserted_ids
        modules = await self.modules.find({"_id": {"$in": inserted_ids}}).to_list(length=len(inserted_ids))
        return modules


    async def update_module_data(self, module_data: dict) -> dict:
        module_id = module_data.get("id")
        # if not module_id or not ObjectId.is_valid(module_id):
        #     raise ValueError("Invalid module ID")

        # if "password" in module_data and module_data["password"]:
        #     module_data["password"] = pwd_context.hash(module_data["password"])

        update_result = await self.modules.find_one_and_update(
            {"_id": str(module_id)},
            {"$set": module_data},
            return_document=True  # Returns updated document
        )

        if not update_result:
            raise ValueError("Module not found")
        return update_result

    async def delete_module_data(self, module_id: str) -> str:
        if not ObjectId.is_valid(module_id):
            raise HTTPException(status_code=400, detail="Invalid module ID")
        result = await self.modules.find_one_and_delete({"_id": str(module_id)})
        return "" if result else "Module not found"
