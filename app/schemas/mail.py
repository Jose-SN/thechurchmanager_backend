from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MailTemplateBase(BaseModel):
    subject: str
    body: str
    submittedBy: str  # store ObjectId as string

class MailTemplateInDB(MailTemplateBase):
    id: Optional[str] = Field(None, alias="_id")
    creation_date: Optional[datetime]
    modification_date: Optional[datetime]

    class Config:
        allow_population_by_field_name = True
