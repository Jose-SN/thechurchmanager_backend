# schemas/status.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

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

class StatusBase(BaseModel):
    parentId: PyObjectId = Field(...)
    parentType: str = Field(..., regex="^(Course|Chapter|File)$")  # restrict to allowed values
    percentage: Optional[str] = None
    comment: Optional[str] = None
    rating: Optional[int] = None
    reward: Optional[int] = None
    createdBy: PyObjectId = Field(...)

class StatusCreate(StatusBase):
    pass

class StatusUpdate(StatusBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

class StatusInDB(StatusBase):
    id: PyObjectId = Field(alias="_id")
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
