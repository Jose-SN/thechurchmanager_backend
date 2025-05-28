from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

class EventSchema(BaseModel):
    id: Optional[str]
    title: str
    start: str
    end: str
    allDay: Optional[bool] = False
    description: Optional[str] = None
    venue: str
    ended: bool = False
    isOnline: bool = False
    link: str
    className: Optional[str] = None
    submittedBy: str  # ObjectId as str
    creation_date: Optional[str]
    modification_date: Optional[str]
