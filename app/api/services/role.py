from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from uvicorn import Config
from fastapi import HTTPException
from bson import ObjectId

from app.api import dependencies
from app.core.config import Settings

class RoleService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.roles = db["roles"]

    async def get_role_data(self) -> List[dict]:
        roles = await self.roles.find({}).to_list(length=None)
        for role in roles:
            if "_id" in role:
                role["_id"] = str(role["_id"])
        return roles

    async def save_role_data(self, role_data: dict) -> dict:
        # Hash password before save
        # if "password" in role_data and role_data["password"]:
        #     role_data["password"] = pwd_context.hash(role_data["password"])

        result = await self.roles.insert_one(role_data)
        role = await self.roles.find_one({"_id": result.inserted_id})
        return role if role is not None else {}
    
    
    async def save_bulk_role_data(self, roles_data: list[dict]) -> list[dict]:
        """
        Bulk insert roles and return the inserted role documents.
        """
        result = await self.roles.insert_many(roles_data)
        inserted_ids = result.inserted_ids
        roles = await self.roles.find({"_id": {"$in": inserted_ids}}).to_list(length=len(inserted_ids))
        return roles


    async def update_role_data(self, role_data: dict) -> dict:
        role_id = role_data.get("id")
        # if not role_id or not ObjectId.is_valid(role_id):
        #     raise ValueError("Invalid role ID")

        # if "password" in role_data and role_data["password"]:
        #     role_data["password"] = pwd_context.hash(role_data["password"])

        update_result = await self.roles.find_one_and_update(
            {"_id": str(role_id)},
            {"$set": role_data},
            return_document=True  # Returns updated document
        )

        if not update_result:
            raise ValueError("Role not found")
        return update_result

    async def delete_role_data(self, role_id: str) -> str:
        if not ObjectId.is_valid(role_id):
            raise HTTPException(status_code=400, detail="Invalid role ID")
        result = await self.roles.find_one_and_delete({"_id": str(role_id)})
        return "" if result else "Role not found"
