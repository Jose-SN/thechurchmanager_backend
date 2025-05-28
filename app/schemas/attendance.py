# schemas/attendance.py
from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from datetime import datetime

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

class AttendanceBase(BaseModel):
    parentId: PyObjectId = Field(...)
    parentType: str = Field(...)
    questionId: PyObjectId = Field(...)
    attendance: Optional[str] = None
    submittedBy: PyObjectId = Field(...)

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(AttendanceBase):
    id: PyObjectId

class AttendanceResponse(AttendanceBase):
    id: PyObjectId
    creation_date: Optional[datetime]
    modification_date: Optional[datetime]

    class Config:
        orm_mode = True
