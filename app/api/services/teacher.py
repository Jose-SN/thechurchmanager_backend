from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from uvicorn import Config
from fastapi import HTTPException
from bson import ObjectId

from app.api import dependencies
from app.core.config import Settings

class TeacherService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.teachers = db["teachers"]

    async def get_teacher_data(self, filters: dict = {}) -> List[dict]:
        query = {}
        if filters:
            query = filters.copy()
            if "_id" in query:
                try:
                    query["_id"] = ObjectId(query["_id"])
                except Exception:
                    # Invalid ObjectId, will return empty result
                    return []
        teachers = await self.teachers.find(query).to_list(length=None)
        for teacher in teachers:
            if "_id" in teacher:
                teacher["_id"] = str(teacher["_id"])
        return teachers

    async def save_teacher_data(self, teacher_data: dict) -> dict:
        # Hash password before save
        # if "password" in teacher_data and teacher_data["password"]:
        #     teacher_data["password"] = pwd_context.hash(teacher_data["password"])

        result = await self.teachers.insert_one(teacher_data)
        teacher = await self.teachers.find_one({"_id": result.inserted_id})
        return teacher if teacher is not None else {}
    
    
    async def save_bulk_teacher_data(self, teachers_data: list[dict]) -> list[dict]:
        """
        Bulk insert teachers and return the inserted teacher documents.
        """
        result = await self.teachers.insert_many(teachers_data)
        inserted_ids = result.inserted_ids
        teachers = await self.teachers.find({"_id": {"$in": inserted_ids}}).to_list(length=len(inserted_ids))
        return teachers


    async def update_teacher_data(self, teacher_data: dict) -> dict:
        teacher_id = teacher_data.get("id")
        # if not teacher_id or not ObjectId.is_valid(teacher_id):
        #     raise ValueError("Invalid teacher ID")

        # if "password" in teacher_data and teacher_data["password"]:
        #     teacher_data["password"] = pwd_context.hash(teacher_data["password"])

        update_result = await self.teachers.find_one_and_update(
            {"_id": str(teacher_id)},
            {"$set": teacher_data},
            return_document=True  # Returns updated document
        )

        if not update_result:
            raise ValueError("Teacher not found")
        return update_result

    async def delete_teacher_data(self, teacher_id: str) -> str:
        if not ObjectId.is_valid(teacher_id):
            raise HTTPException(status_code=400, detail="Invalid teacher ID")
        result = await self.teachers.find_one_and_delete({"_id": str(teacher_id)})
        return "" if result else "Teacher not found"
