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
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# Base user schema with MongoDB _id
class IUserSchema(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    first_name: str
    last_name: Optional[str]
    profile_image: Optional[str]
    primary_user: Optional[bool]
    associated_users: Optional[List[PyObjectId]]
    email: EmailStr
    password: Optional[str]
    phone: Optional[str]
    role: Optional[str]
    approved: Optional[str]
    relationship: Optional[str]
    date_of_birth: Optional[date]
    organization_id: Optional[str]
    creation_date: datetime
    modification_date: datetime

    class Config:
        allow_population_by_field_name = True
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
    phone: Optional[str]
    role: Optional[str]
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
class IValidatedUser(BaseModel):
    id: PyObjectId
    first_name: str
    last_name: Optional[str]
    profile_image: Optional[str]
    primary_user: Optional[bool]
    associated_users: Optional[List[PyObjectId]]
    email: EmailStr
    phone: str
    role: Optional[str]
    approved: Optional[str]
    relationship: Optional[str]
    date_of_birth: Optional[date]
    organization_id: Optional[str]
    jwt: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Forgot password request schema
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    password: str
