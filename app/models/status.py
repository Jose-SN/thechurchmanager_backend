# models/status.py
from beanie import Document
from typing import Optional
from datetime import datetime

class Status(Document):
    parentId: str  # Stored as string ObjectId, but could use PyObjectId
    parentType: str  # "Course", "Chapter", or "File"
    percentage: Optional[str]
    comment: Optional[str]
    rating: Optional[int]
    reward: Optional[int]
    createdBy: str  # User ObjectId as string
    creation_date: Optional[datetime]
    modification_date: Optional[datetime]

    class Settings:
        name = "statuses"

    class Config:
        schema_extra = {
            "example": {
                "parentId": "60d5ec49f1d9d6c3f8a3b2e1",
                "parentType": "Course",
                "percentage": "75%",
                "comment": "Great progress",
                "rating": 4,
                "reward": 10,
                "createdBy": "60d5ec49f1d9d6c3f8a3b2e2"
            }
        }
