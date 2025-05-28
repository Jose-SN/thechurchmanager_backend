from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class MailTemplate(Document):
    subject: str
    body: str
    submittedBy: str  # Reference to User document (ObjectId as string)
    creation_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    modification_date: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "mailtemplates"  # Collection name

    class Config:
        schema_extra = {
            "example": {
                "subject": "Welcome Email",
                "body": "Hello, welcome to our app!",
                "submittedBy": "60c5fcf6f9b5c2001c3b5a91"
            }
        }
