from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime

class MeetingBase(BaseModel):
    title: str
    date: str
    speechBy: Optional[str] = None
    location: str
    language: Optional[str] = None
    videoURL: HttpUrl
    submittedBy: Optional[str] = None  # This will usually be a user ID (str)

class MeetingCreate(MeetingBase):
    pass  # same fields as base

class MeetingUpdate(MeetingBase):
    id: Optional[str] = None  # or _id, depending on MongoDB usage

class MeetingInDB(MeetingBase):
    id: str = Field(..., alias="_id")
    creation_date: datetime
    modification_date: datetime

    class Config:
        orm_mode = True
