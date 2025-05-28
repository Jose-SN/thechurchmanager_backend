from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional
from datetime import datetime

class EventSchema(BaseModel):
    id: Optional[ObjectId] = Field(alias="_id")
    title: str
    start: str
    end: Optional[str] = None
    allDay: Optional[bool] = False
    description: Optional[str] = None
    venue: Optional[str] = None
    ended: bool = False
    isOnline: bool = False
    link: Optional[str] = None
    className: Optional[str] = None
    submittedBy: ObjectId
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
