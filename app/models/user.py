from typing import List, Optional
from datetime import datetime, date
from beanie import Document, Indexed, before_event, Insert
from pydantic import Field, EmailStr
from bson import ObjectId
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserModel(Document):
    first_name: str = Field(..., alias="first_name")
    last_name: Optional[str] = Field(None, alias="last_name")
    profile_image: Optional[str] = Field(None, alias="profile_image")
    email: Optional[EmailStr]
    password: Optional[str]
    phone_number: str
    # primary_user: Optional[bool] = Field(None, alias="primaryUser")
    # associated_users: Optional[List[ObjectId]] = Field(default_factory=list, alias="associatedUsers")
    roles: List[str] = Field(default_factory=list)
    # approved: Optional[bool] = False
    # relationship: Optional[str]
    date_of_birth: Optional[date] = Field(None, alias="dateOfBirth")
    organization_id: ObjectId = Field(..., alias="organizationId")
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None

    # class Settings:
    #     name = "users"  # MongoDB collection name

    # class Config:
    #     allow_population_by_field_name = True
    #     json_encoders = {ObjectId: str}

    @before_event(Insert)
    async def hash_password(self):
        if self.password:
            self.password = pwd_context.hash(self.password)

