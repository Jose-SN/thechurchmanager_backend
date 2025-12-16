from datetime import datetime, timedelta
from warnings import filters
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from uvicorn import Config
from fastapi import HTTPException
from bson import ObjectId

from app.api import dependencies
from app.core.config import Settings

class FileService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.files = db["files"]

    async def get_file_data(self, filters: dict = {}) -> List[dict]:
        query = {}
        if filters:
            query = filters.copy()
            if "id" in query:
                try:
                    query["id"] = ObjectId(query["id"])
                except Exception:
                    # Invalid ObjectId, will return empty result
                    return []
        files = await self.files.find(query).to_list(length=None)
        for file in files:
            if "id" in file:
                file["id"] = str(file["id"])
        return files

    async def save_file_data(self, file_data: dict) -> dict:
        # Hash password before save
        # if "password" in file_data and file_data["password"]:
        #     file_data["password"] = pwd_context.hash(file_data["password"])

        result = await self.files.insert_one(file_data)
        file = await self.files.find_one({"id": result.inserted_id})
        return file if file is not None else {}
    
    
        
    async def save_bulk_file_data(self, files_data: list[dict], organization_id: str) -> list[dict]:
        """
        Save or update multiple files.
        - Updates files that already have id.
        - Creates new files that don't.
        Returns the full list of updated/created file documents.
        """

        updated_files = []

        for file in files_data:
            # ✅ If id exists, try updating
            if file.get("id"):
                try:
                    file_id = str(file["id"])
                    update_data = {k: v for k, v in file.items() if k != "id"}

                    updated_file = await self.files.find_one_and_update(
                        {"id": dependencies.try_objectid(file_id)},
                        {"$set": update_data},
                        return_document=True
                    )

                    if updated_file:
                        updated_files.append(dependencies.convert_objectid(updated_file))
                    else:
                        # fallback: if not found, insert as new
                        file["organization_id"] = organization_id
                        insert_result = await self.files.insert_one(file)
                        new_file = await self.files.find_one({"id": insert_result.inserted_id})
                        
                        updated_files.append(dependencies.convert_objectid(new_file))
                except Exception as e:
                    print(f"⚠️ Error updating file {file.get('id')}: {e}")

            else:
                # ✅ No id → new file
                file["organization_id"] = organization_id
                insert_result = await self.files.insert_one(file)
                new_file = await self.files.find_one({"id": insert_result.inserted_id})
                updated_files.append(dependencies.convert_objectid(new_file))

        return updated_files


    async def update_file_data(self, file_data: dict) -> dict:
        file_id = file_data.get("id")
        update_fields = file_data.copy()
        update_fields.pop("id", None)

        update_result = await self.files.find_one_and_update(
            {"id": dependencies.try_objectid(file_id)},
            {"$set": update_fields},
            return_document=True  # Returns updated document
        )

        if not update_result:
            raise ValueError("File not found")
        return update_result

    async def delete_file_data(self, file_id: str) -> str:
        if not ObjectId.is_valid(file_id):
            raise HTTPException(status_code=400, detail="Invalid file ID")
        result = await self.files.find_one_and_delete({"id": ObjectId(file_id)})
        return "" if result else "File not found"
