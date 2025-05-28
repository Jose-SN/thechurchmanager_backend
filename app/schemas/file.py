from beanie import Document
from pydantic import BaseModel
from bson import ObjectId
from typing import Optional
from datetime import datetime

class File(Document):
    parentId: ObjectId
    parentType: str  # 'Course', 'Chapter', 'User'
    description: str
    fileURL: str
    createdBy: ObjectId
    creation_date: Optional[datetime]
    modification_date: Optional[datetime]

    class Settings:
        name = "files"
