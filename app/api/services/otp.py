from datetime import datetime, timedelta
from bson import ObjectId
from typing import Optional, Union

from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field


class OTPModel(BaseModel):
    id: Optional[ObjectId] = Field(alias="id")
    user_id: ObjectId
    otp: int
    expires_at: Optional[datetime] = None


class OtpService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["otp"]

    async def save_otp(self, user_id: ObjectId, otp: int) -> OTPModel:
        otp_data = {
            "user_id": user_id,
            "otp": otp,
            "expires_at": datetime.utcnow() + timedelta(minutes=10),
        }
        result = await self.collection.insert_one(otp_data)
        otp_data["id"] = result.inserted_id
        return OTPModel(**otp_data)

    async def get_otp(self, user_id: ObjectId, otp: Optional[int] = None) -> Optional[OTPModel]:
        query = {"user_id": user_id}
        if otp is not None:
            query["otp"] = otp
        doc = await self.collection.find_one(query)
        if doc:
            return OTPModel(**doc)
        return None

    async def update_otp(self, user_id: ObjectId, otp: int) -> bool:
        update_result = await self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"otp": otp, "expires_at": datetime.utcnow() + timedelta(minutes=10)}}
        )
        return update_result.modified_count == 1

    async def delete_otp(self, otp_id: ObjectId) -> str:
        delete_result = await self.collection.find_one_and_delete({"id": otp_id})
        return "" if delete_result else "OTP not found"
