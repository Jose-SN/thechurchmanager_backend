from datetime import datetime, timedelta
from unittest import result
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from uvicorn import Config
from fastapi import HTTPException
from bson import ObjectId
from pymongo import ReturnDocument

from app.api import dependencies
from app.core.config import settings

class UserService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users = db["users"]

    async def get_user_data(self, filters: dict = {}) -> List[dict]:
        query = {}
        if filters:
            query = filters.copy()
            if "id" in query:
                try:
                    query["id"] = ObjectId(query["id"])
                except Exception:
                    # Invalid ObjectId, will return empty result
                    return []
        users = await self.users.find(query).to_list(length=None)
        for org in users:
            if "id" in org:
                org["id"] = str(org["id"])
        return users

    async def save_user_data(self, user_data: dict):
        # Hash password before save
        # if "password" in user_data and user_data["password"]:
        #     user_data["password"] = pwd_context.hash(user_data["password"])

            result = await self.users.insert_one(user_data)
            user = await self.users.find_one({"id": result.inserted_id})
            if user:
                user = dependencies.convert_objectid(user)
            else:
                user = {}
            return user
    
    
    async def save_bulk_user_data(self, users_data: list[dict]) -> list[dict]:
        """
        Bulk insert users and return the inserted user documents.
        """
        result = await self.users.insert_many(users_data)
        inserted_ids = result.inserted_ids
        users = await self.users.find({"id": {"$in": inserted_ids}}).to_list(length=len(inserted_ids))
        return users


    async def login_user_data(self, email: str, password: str):
        user = await self.users.find_one({"contact.email": email})
        if not user:
            raise ValueError("No matching records found")
        # hashed_password = user.get("password")
        # if not hashed_password or not pwd_context.verify(password, hashed_password):
        #     raise ValueError("Invalid credentials")
        return await self.generate_authorized_user(user)

    async def generate_authorized_user(self, login_user: dict):
        payload = self.get_jwt_payload(login_user)
        expiry_seconds = dependencies.parse_expiry_to_seconds(settings.JWT_EXPIRY)
        payload["exp"] = datetime.utcnow() + timedelta(seconds=expiry_seconds)
        token = 'thechurchmanager'  # jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
        payload["jwt"] = token
        return payload

    def get_jwt_payload(self, login_user: dict) -> dict:
        # Compose nested social and contact objects
        social = login_user.get("social", {
            "facebook": login_user.get("facebook"),
            "instagram": login_user.get("instagram"),
            "youtube": login_user.get("youtube"),
        })
        contact = login_user.get("contact", {
            "email": login_user.get("email"),
            "phone": login_user.get("phone_number") or login_user.get("phone"),
            "website": login_user.get("website"),
            "address": login_user.get("address"),
        })
        return {
            "id": str(login_user.get("id")),
            "first_name": login_user.get("first_name"),
            "last_name": login_user.get("last_name"),
            "organization_id": str(login_user.get("organization_id")),
            "is_imported": login_user.get("is_imported", False),
            "is_password_hashed": login_user.get("is_password_hashed", False),
            "roles": login_user.get("roles", []),
            "profile_image": login_user.get("profile_image", ""),
            "creation_date": login_user.get("creation_date"),
            "modification_date": login_user.get("modification_date"),
            "password": login_user.get("password"),
            "date_of_birth": login_user.get("date_of_birth"),
            "about": login_user.get("about", ""),
            "teams": login_user.get("teams", []),
            "social": social,
            "contact": contact,
            "status": login_user.get("date_of_birth"),
        }

    async def update_user_data(self, user_data: dict) -> dict:
        try:
            user_id = user_data.get("id")
            update_fields = user_data.copy()
            update_fields.pop("id", None)
            update_result = await self.users.find_one_and_update(
                {"id": dependencies.try_objectid(user_id)},
                {"$set": update_fields},
                return_document=ReturnDocument.AFTER
            )
            if not update_result:
                raise ValueError("User not found")
            return update_result
        except Exception as err:
            return {"success": False, "error": str(err)}

    async def delete_user_data(self, user_id: str) -> str:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        result = await self.users.find_one_and_delete({"id": str(user_id)})
        return "" if result else "User not found"




# from fastapi import Request
# import jwt
# from typing import List, Optional
# from motor.motor_asyncio import AsyncIOMotorDatabase
# from bson import ObjectId
# from datetime import datetime, timedelta
# from passlib.context import CryptContext
# # from models.user import UserModel  # Assuming UserModel is a Beanie document or similar ORM model
# from pydantic import BaseModel, EmailStr
# # from core.config import JWT_SECRET

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT_EXPIRY_SECONDS = 3600  # example: 1 hour

# class IUser(BaseModel):
#     id: Optional[str]
#     email: EmailStr
#     password: Optional[str]

# class IValidatedUser(BaseModel):
#     id: str
#     email: EmailStr
#     first_name: str
#     last_name: Optional[str]
#     roles: Optional[str]
#     phone_number: Optional[str]
#     primary_user: Optional[bool]
#     associated_users: Optional[List[str]]
#     profile_image: Optional[str]
#     approved: Optional[bool]
#     relationship: Optional[str]
#     date_of_birth: Optional[datetime]
#     user_id: Optional[str]
#     jwt: Optional[str] = None


# class UserService:
#     def __init__(self, db: AsyncIOMotorDatabase):
#         self.db = db
#         self.users = db["users"]
#         self.checkouts = db["checkouts"]

    # def get_jwt_payload(self, login_user: dict) -> dict:
    #     return {
    #         "id": str(login_user["_id"]),
    #         "email": login_user["email"],
    #         "first_name": login_user.get("first_name") or login_user.get("first_name"),
    #         "last_name": login_user.get("last_name") or login_user.get("last_name"),
    #         "roles": login_user.get("roles"),
    #         "phone_number": login_user.get("phone_number", ""),
    #         "primary_user": login_user.get("primary_user") or login_user.get("primaryUser"),
    #         "associated_users": [str(u) for u in login_user.get("associated_users", [])] if login_user.get("associated_users") else [],
    #         "profile_image": login_user.get("profile_image") or login_user.get("profileImage"),
    #         "approved": login_user.get("approved"),
    #         "relationship": login_user.get("relationship"),
    #         "date_of_birth": login_user.get("date_of_birth") or login_user.get("dateOfBirth"),
    #         "user_id": str(login_user.get("user_id") or login_user.get("userId")),
    #     }

    # async def generate_authorized_user(self, login_user: dict) -> IValidatedUser:
    #     payload = self.get_jwt_payload(login_user)
    #     payload["exp"] = datetime.utcnow() + timedelta(seconds=JWT_EXPIRY_SECONDS)
    #     token = 'thechurchmanager'  # jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    #     payload["jwt"] = token
    #     return IValidatedUser(**payload)

    # async def get_user_data(self) -> List[dict]:
    #     users = await self.users.find({}).to_list(length=None)
    #     # Optionally, convert ObjectId to str for each user
    #     for user in users:
    #         if "_id" in user:
    #             user["_id"] = str(user["_id"])
    #     return users

    # async def get_not_attended_user_data(self, event_id: str) -> List[dict]:
    #     if not ObjectId.is_valid(event_id):
    #         raise ValueError("Invalid event ID")

    #     attendees = await self.checkouts.distinct("userId", {"eventId": ObjectId(event_id)})

    #     non_attendees_cursor = self.users.find({"_id": {"$nin": attendees}})
    #     return await non_attendees_cursor.to_list(length=None)

    # async def save_user_data(self, user_data: dict) -> dict:
    #     # Hash password before save
    #     if "password" in user_data and user_data["password"]:
    #         user_data["password"] = pwd_context.hash(user_data["password"])

    #     result = await self.users.insert_one(user_data)
    #     user = await self.users.find_one({"_id": result.inserted_id})
    #     return user_data

    # async def validate_user_data(self, email: str, password: str) -> IValidatedUser:
    #     user = await self.users.find_one({"email": email})
    #     if not user:
    #         raise ValueError("No matching records found")
    #     hashed_password = user.get("password")
    #     if not hashed_password or not pwd_context.verify(password, hashed_password):
    #         raise ValueError("Invalid credentials")
    #     return await self.generate_authorized_user(user)

    # async def update_user_data(self, user_data: dict) -> dict:
    #     user_id = user_data.get("id")
    #     if not user_id or not ObjectId.is_valid(user_id):
    #         raise ValueError("Invalid user ID")

    #     if "password" in user_data and user_data["password"]:
    #         user_data["password"] = pwd_context.hash(user_data["password"])

    #     update_result = await self.users.find_one_and_update(
    #         {"_id": ObjectId(user_id)},
    #         {"$set": user_data},
    #         return_document=True  # Returns updated document
    #     )

    #     if not update_result:
    #         raise ValueError("User not found")
    #     return update_result

    # async def delete_user_data(self, user_id: str) -> str:
    #     if not ObjectId.is_valid(user_id):
    #         raise ValueError("Invalid user ID")
    #     result = await self.users.find_one_and_delete({"_id": ObjectId(user_id)})
    #     return "" if result else "User not found"

    # async def fetch_user_from_email(self, email: str) -> Optional[dict]:
    #     user = await self.users.find_one({"email": email})
    #     return user
