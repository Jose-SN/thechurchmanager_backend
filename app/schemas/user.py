from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId

# Helper to support MongoDB ObjectId in Pydantic
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        schema = handler(core_schema)
        schema.update(type="string")
        return schema

# Base user schema with MongoDB id
class IUserSchema(BaseModel):
    id: PyObjectId = Field(..., alias="id")
    first_name: str
    last_name: Optional[str]
    profile_image: Optional[str]
    primary_user: Optional[bool]
    associated_users: Optional[List[PyObjectId]]
    email: EmailStr
    password: Optional[str]
    phone_number: Optional[str]
    roles: Optional[str]
    approved: Optional[str]
    relationship: Optional[str]
    date_of_birth: Optional[date]
    organization_id: Optional[str]
    creation_date: datetime
    modification_date: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Equivalent to IUser interface, note some fields renamed to snake_case for Python style
class IUser(BaseModel):
    id: PyObjectId
    first_name: str
    last_name: Optional[str]
    profile_image: Optional[str]
    primary_user: Optional[bool]
    associated_users: Optional[List[PyObjectId]]
    email: EmailStr
    password: Optional[str]
    phone_number: Optional[str]
    roles: Optional[str]
    approved: Optional[str]
    relationship: Optional[str]
    date_of_birth: Optional[date]
    organization_id: Optional[str]
    creation_date: datetime
    modification_date: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Equivalent to IValidatedUser (excludes password, includes jwt token)

class SocialLinks(BaseModel):
    facebook: Optional[str]
    instagram: Optional[str]
    youtube: Optional[str]

class ContactInfo(BaseModel):
    email: Optional[EmailStr]
    phone: Optional[str]
    website: Optional[str]
    address: Optional[str]

class IValidatedUser(BaseModel):
    first_name: str
    last_name: Optional[str]
    organization_id: Optional[str]
    roles: Optional[List[str]]
    profile_image: Optional[str]
    creation_date: Optional[datetime]
    modification_date: Optional[datetime]
    password: Optional[str]
    date_of_birth: Optional[date]
    about: Optional[str]
    is_imported: Optional[bool]
    is_password_hashed: Optional[bool]
    teams: Optional[List[str]]
    social: Optional[SocialLinks]
    contact: Optional[ContactInfo]
    jwt: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Forgot password request schema
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    password: str
    password: str
