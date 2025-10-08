from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from bson import ObjectId

# Helper for ObjectId validation
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class GuestBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    details: str
    phone_number: str
    referrer: Optional[str] = None
    referralSource: Optional[str] = None
    prayerRequests: Optional[str] = None

class GuestCreate(GuestBase):
    pass

class GuestUpdate(GuestBase):
    id: PyObjectId = Field(..., alias="_id")

class GuestDB(GuestBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    creation_date: Optional[datetime]
    modification_date: Optional[datetime]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
