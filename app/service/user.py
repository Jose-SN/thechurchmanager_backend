import jwt
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timedelta
from passlib.context import CryptContext
from models.user import UserModel  # Assuming UserModel is a Beanie document or similar ORM model
from pydantic import BaseModel, EmailStr
from core.config import JWT_SECRET

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_EXPIRY_SECONDS = 3600  # example: 1 hour

class IUser(BaseModel):
    id: Optional[str]
    email: EmailStr
    password: Optional[str]

class IValidatedUser(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: Optional[str]
    role: Optional[str]
    phone: Optional[str]
    primary_user: Optional[bool]
    associated_users: Optional[List[str]]
    profile_image: Optional[str]
    approved: Optional[bool]
    relationship: Optional[str]
    date_of_birth: Optional[datetime]
    organization_id: Optional[str]
    jwt: Optional[str] = None


class UserService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users = db["users"]
        self.checkouts = db["checkouts"]

    def get_jwt_payload(self, login_user: dict) -> dict:
        return {
            "id": str(login_user["_id"]),
            "email": login_user["email"],
            "first_name": login_user.get("first_name") or login_user.get("firstName"),
            "last_name": login_user.get("last_name") or login_user.get("lastName"),
            "role": login_user.get("role"),
            "phone": login_user.get("phone", ""),
            "primary_user": login_user.get("primary_user") or login_user.get("primaryUser"),
            "associated_users": [str(u) for u in login_user.get("associated_users", [])] if login_user.get("associated_users") else [],
            "profile_image": login_user.get("profile_image") or login_user.get("profileImage"),
            "approved": login_user.get("approved"),
            "relationship": login_user.get("relationship"),
            "date_of_birth": login_user.get("date_of_birth") or login_user.get("dateOfBirth"),
            "organization_id": str(login_user.get("organization_id") or login_user.get("organizationId")),
        }

    async def generate_authorized_user(self, login_user: dict) -> IValidatedUser:
        payload = self.get_jwt_payload(login_user)
        payload["exp"] = datetime.utcnow() + timedelta(seconds=JWT_EXPIRY_SECONDS)
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        payload["jwt"] = token
        return IValidatedUser(**payload)

    async def get_user_data(self) -> List[dict]:
        cursor = self.users.find({})
        return await cursor.to_list(length=None)

    async def get_not_attended_user_data(self, event_id: str) -> List[dict]:
        if not ObjectId.is_valid(event_id):
            raise ValueError("Invalid event ID")

        attendees = await self.checkouts.distinct("userId", {"eventId": ObjectId(event_id)})

        non_attendees_cursor = self.users.find({"_id": {"$nin": attendees}})
        return await non_attendees_cursor.to_list(length=None)

    async def save_user_data(self, user_data: dict) -> dict:
        # Hash password before save
        if "password" in user_data and user_data["password"]:
            user_data["password"] = pwd_context.hash(user_data["password"])

        result = await self.users.insert_one(user_data)
        user = await self.users.find_one({"_id": result.inserted_id})
        return user

    async def validate_user_data(self, email: str, password: str) -> IValidatedUser:
        user = await self.users.find_one({"email": email})
        if not user:
            raise ValueError("No matching records found")
        hashed_password = user.get("password")
        if not hashed_password or not pwd_context.verify(password, hashed_password):
            raise ValueError("Invalid credentials")
        return await self.generate_authorized_user(user)

    async def update_user_data(self, user_data: dict) -> dict:
        user_id = user_data.get("id")
        if not user_id or not ObjectId.is_valid(user_id):
            raise ValueError("Invalid user ID")

        if "password" in user_data and user_data["password"]:
            user_data["password"] = pwd_context.hash(user_data["password"])

        update_result = await self.users.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": user_data},
            return_document=True  # Returns updated document
        )

        if not update_result:
            raise ValueError("User not found")
        return update_result

    async def delete_user_data(self, user_id: str) -> str:
        if not ObjectId.is_valid(user_id):
            raise ValueError("Invalid user ID")
        result = await self.users.find_one_and_delete({"_id": ObjectId(user_id)})
        return "" if result else "User not found"

    async def fetch_user_from_email(self, email: str) -> Optional[dict]:
        user = await self.users.find_one({"email": email})
        return user
