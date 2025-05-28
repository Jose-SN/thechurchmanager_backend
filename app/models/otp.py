from datetime import datetime, timedelta
from beanie import Document, Indexed
from bson import ObjectId
from pydantic import Field


class OTPModel(Document):
    user_id: ObjectId = Field(..., alias="userId")
    otp: int = Field(..., ge=10000, le=99999)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(minutes=10), alias="expiresAt")
    creation_date: datetime = Field(default_factory=datetime.utcnow)
    modification_date: datetime = Field(default_factory=datetime.utcnow)

    class Collection:
        name = "otp"
        indexes = [
            [("expires_at", 1)],  # TTL index will be created by you manually or by migration
        ]

    class Settings:
        use_state_management = True
        use_revision = True

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
