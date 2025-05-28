from beanie import Document
from pydantic import Field, HttpUrl
from typing import Optional
from datetime import datetime
from bson import ObjectId

class Meeting(Document):
    title: str
    date: str
    speechBy: Optional[str]
    location: str
    language: Optional[str]
    videoURL: HttpUrl
    submittedBy: Optional[ObjectId]

    creation_date: datetime = Field(default_factory=datetime.utcnow)
    modification_date: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "meeting"  # collection name in MongoDB

    class Config:
        schema_extra = {
            "example": {
                "title": "Annual Conference",
                "date": "2025-05-28",
                "speechBy": "Jane Doe",
                "location": "New York",
                "language": "English",
                "videoURL": "https://example.com/video.mp4",
                "submittedBy": "60d0fe4f5311236168a109ca"
            }
        }
