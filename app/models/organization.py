# models/organization.py
from beanie import Document
from datetime import datetime
from typing import Optional

class Organization(Document):
    name: str
    logo: str
    creation_date: Optional[datetime]
    modification_date: Optional[datetime]

    class Settings:
        name = "organizations"  # MongoDB collection name

    class Config:
        schema_extra = {
            "example": {
                "name": "Example Organization",
                "logo": "https://example.com/logo.png"
            }
        }
