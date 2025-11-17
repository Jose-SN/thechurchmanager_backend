from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from uvicorn import Config
from fastapi import HTTPException
from bson import ObjectId

from app.api import dependencies
from app.core.config import Settings

class PermissionService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.permissions = db["permissions"]

    async def get_permission_data(self, filters: dict = {}) -> List[dict]:
        query = {}
        if filters:
            query = filters.copy()
            if "_id" in query:
                try:
                    query["_id"] = ObjectId(query["_id"])
                except Exception:
                    # Invalid ObjectId, will return empty result
                    return []
        permissions = await self.permissions.find(query).to_list(length=None)
        for permission in permissions:
            if "_id" in permission:
                permission["_id"] = str(permission["_id"])
        return permissions

    async def save_permission_data(self, permission_data: dict) -> dict:
        # Hash password before save
        # if "password" in permission_data and permission_data["password"]:
        #     permission_data["password"] = pwd_context.hash(permission_data["password"])

        result = await self.permissions.insert_one(permission_data)
        permission = await self.permissions.find_one({"_id": result.inserted_id})
        return permission if permission is not None else {}
    
    
    async def save_bulk_permission_data(self, permissions_data: list[dict], organization_id: str) -> list[dict]:
        """
        Save or update multiple permissions.
        - Updates permissions that already have _id.
        - Creates new permissions that don't.
        Returns the full list of updated/created permission documents.
        """

        updated_permissions = []

        for permission in permissions_data:
            # ✅ If _id exists, try updating
            if permission.get("_id"):
                try:
                    permission_id = str(permission["_id"])
                    update_data = {k: v for k, v in permission.items() if k != "_id"}

                    updated_permission = await self.permissions.find_one_and_update(
                        {"_id": dependencies.try_objectid(permission_id)},
                        {"$set": update_data},
                        return_document=True
                    )

                    if updated_permission:
                        updated_permissions.append(dependencies.convert_objectid(updated_permission))
                    else:
                        # fallback: if not found, insert as new
                        permission["organization_id"] = organization_id
                        insert_result = await self.permissions.insert_one(permission)
                        new_permission = await self.permissions.find_one({"_id": insert_result.inserted_id})
                        
                        updated_permissions.append(dependencies.convert_objectid(new_permission))
                except Exception as e:
                    print(f"⚠️ Error updating permission {permission.get('_id')}: {e}")

            else:
                # ✅ No _id → new permission
                permission["organization_id"] = organization_id
                insert_result = await self.permissions.insert_one(permission)
                new_permission = await self.permissions.find_one({"_id": insert_result.inserted_id})
                updated_permissions.append(dependencies.convert_objectid(new_permission))

        return updated_permissions


    async def update_permission_data(self, permission_data: dict) -> dict:
        permission_id = permission_data.get("_id")
        # if not permission_id or not ObjectId.is_valid(permission_id):
        #     raise ValueError("Invalid permission ID")

        # if "password" in permission_data and permission_data["password"]:
        #     permission_data["password"] = pwd_context.hash(permission_data["password"])
        update_fields = permission_data.copy()
        update_fields.pop("_id", None)
        update_result = await self.permissions.find_one_and_update(
            {"_id": dependencies.try_objectid(permission_id)},
            {"$set": update_fields},
            return_document=True  # Returns updated document
        )

        if not update_result:
            raise ValueError("Permission not found")
        return update_result

    async def delete_permission_data(self, permission_id: str) -> str:
        if not ObjectId.is_valid(permission_id):
            raise HTTPException(status_code=400, detail="Invalid permission ID")
        result = await self.permissions.find_one_and_delete({"_id": str(permission_id)})
        return "" if result else "Permission not found"
