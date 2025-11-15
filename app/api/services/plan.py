from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from uvicorn import Config
from fastapi import HTTPException
from bson import ObjectId

from app.api import dependencies
from app.core.config import Settings

class PlanService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.plans = db["plans"]

    async def get_plan_data(self, filters: dict = {}) -> List[dict]:
        query = {}
        if filters:
            query = filters.copy()
            if "_id" in query:
                try:
                    query["_id"] = ObjectId(query["_id"])
                except Exception:
                    # Invalid ObjectId, will return empty result
                    return []
        plans = await self.plans.find(query).to_list(length=None)
        for plan in plans:
            if "_id" in plan:
                plan["_id"] = str(plan["_id"])
        return plans

    async def save_plan_data(self, plan_data: dict) -> dict:
        # Hash password before save
        # if "password" in plan_data and plan_data["password"]:
        #     plan_data["password"] = pwd_context.hash(plan_data["password"])

        result = await self.plans.insert_one(plan_data)
        plan = await self.plans.find_one({"_id": result.inserted_id})
        return plan if plan is not None else {}
    
    
    async def save_bulk_plan_data(self, plans_data: list[dict]) -> list[dict]:
        """
        Bulk insert plans and return the inserted plan documents.
        """
        result = await self.plans.insert_many(plans_data)
        inserted_ids = result.inserted_ids
        plans = await self.plans.find({"_id": {"$in": inserted_ids}}).to_list(length=len(inserted_ids))
        return plans


    async def update_plan_data(self, plan_data: dict) -> dict:
        plan_id = plan_data.get("_id")
        # if not plan_id or not ObjectId.is_valid(plan_id):
        #     raise ValueError("Invalid plan ID")

        # if "password" in plan_data and plan_data["password"]:
        #     plan_data["password"] = pwd_context.hash(plan_data["password"])
        update_fields = plan_data.copy()
        update_fields.pop("_id", None)
        update_result = await self.plans.find_one_and_update(
            {"_id": dependencies.try_objectid(plan_id)},
            {"$set": update_fields},
            return_document=True  # Returns updated document
        )

        if not update_result:
            raise ValueError("Plan not found")
        return update_result

    async def delete_plan_data(self, plan_id: str) -> str:
        if not ObjectId.is_valid(plan_id):
            raise HTTPException(status_code=400, detail="Invalid plan ID")
        result = await self.plans.find_one_and_delete({"_id": str(plan_id)})
        return "" if result else "Plan not found"
