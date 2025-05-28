from beanie import Document, Indexed
from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import Field

class Guest(Document):
    firstName: str
    lastName: str
    email: Optional[str]
    details: str
    phone: str
    referrer: Optional[str]
    referralSource: Optional[str]
    prayerRequests: Optional[str]
    creation_date: datetime = Field(default_factory=datetime.utcnow)
    modification_date: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "guests"
