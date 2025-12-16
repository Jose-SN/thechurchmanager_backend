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

class OrganizationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.organizations = db["organizations"]

    async def get_organization_data(self, filters: dict = {}) -> List[dict]:
        query = {}
        if filters:
            query = filters.copy()
            if "id" in query:
                try:
                    query["id"] = ObjectId(query["id"])
                except Exception:
                    # Invalid ObjectId, will return empty result
                    return []
        organizations = await self.organizations.find(query).to_list(length=None)
        for org in organizations:
            if "id" in org:
                org["id"] = str(org["id"])
        return organizations

    async def save_organization_data(self, organization_data: dict):
        # Hash password before save
        # if "password" in organization_data and organization_data["password"]:
        #     organization_data["password"] = pwd_context.hash(organization_data["password"])

            result = await self.organizations.insert_one(organization_data)
            organization = await self.organizations.find_one({"id": result.inserted_id})
            if organization:
                organization = dependencies.convert_objectid(organization)
            else:
                organization = {}
            return organization
    
    
    async def save_bulk_organization_data(self, organizations_data: list[dict]) -> list[dict]:
        """
        Bulk insert organizations and return the inserted organization documents.
        """
        result = await self.organizations.insert_many(organizations_data)
        inserted_ids = result.inserted_ids
        organizations = await self.organizations.find({"id": {"$in": inserted_ids}}).to_list(length=len(inserted_ids))
        return organizations


    async def login_organization_data(self, email: str, password: str):
        organization = await self.organizations.find_one({"contact.email": email})
        if not organization:
            raise ValueError("No matching records found")
        # hashed_password = organization.get("password")
        # if not hashed_password or not pwd_context.verify(password, hashed_password):
        #     raise ValueError("Invalid credentials")
        return await self.generate_authorized_organization(organization)

    async def generate_authorized_organization(self, login_organization: dict):
        payload = self.get_jwt_payload(login_organization)
        expiry_seconds = dependencies.parse_expiry_to_seconds(settings.JWT_EXPIRY)
        payload["exp"] = datetime.utcnow() + timedelta(seconds=expiry_seconds)
        token = 'thechurchmanager'  # jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
        payload["jwt"] = token
        return payload

    def get_jwt_payload(self, login_organization: dict) -> dict:
        # Compose nested social and contact objects
        social = {
            "facebook": login_organization.get("social", {}).get("facebook") or login_organization.get("facebook"),
            "instagram": login_organization.get("social", {}).get("instagram") or login_organization.get("instagram"),
            "youtube": login_organization.get("social", {}).get("youtube") or login_organization.get("youtube"),
            "twitter": login_organization.get("social", {}).get("twitter") or login_organization.get("twitter"),
        }
        contact = {
            "phone": login_organization.get("contact", {}).get("phone") or login_organization.get("phone_number") or login_organization.get("phone"),
            "email": login_organization.get("contact", {}).get("email") or login_organization.get("email"),
            "website": login_organization.get("contact", {}).get("website") or login_organization.get("website"),
            "address": login_organization.get("contact", {}).get("address") or login_organization.get("address"),
            "officeHours": login_organization.get("contact", {}).get("officeHours"),
        }
        return {
            "id": str(login_organization.get("id")),
            "name": login_organization.get("name"),
            "title": login_organization.get("title"),
            "members": login_organization.get("members"),
            "volunteers": login_organization.get("volunteers"),
            "about": login_organization.get("about", ""),
            "contact": contact,
            "leadership": login_organization.get("leadership", []),
            "social": social,
            "profile_image": login_organization.get("profile_image"),
            "password": login_organization.get("password"),
        }



    async def update_organization_data(self, organization_data: dict) -> dict:
        try:
            organization_id = organization_data.get("id")
            update_fields = organization_data.copy()
            update_fields.pop("id", None)
            update_result = await self.organizations.find_one_and_update(
                {"id": dependencies.try_objectid(organization_id)},
                {"$set": update_fields},
                return_document=ReturnDocument.AFTER
            )
            if not update_result:
                raise ValueError("Organization not found")
            return update_result
        except Exception as err:
            return {"success": False, "error": str(err)}

    async def delete_organization_data(self, organization_id: str) -> str:
        if not ObjectId.is_valid(organization_id):
            raise HTTPException(status_code=400, detail="Invalid organization ID")
        result = await self.organizations.find_one_and_delete({"id": str(organization_id)})
        return "" if result else "Organization not found"


# # services/organization_service.py
# from typing import Optional, List
# from models.organization import Organization
# from schemas.organization import OrganizationCreate, OrganizationUpdate
# from motor.motor_asyncio import AsyncIOMotorClient
# from bson import ObjectId
# from models.user import User  # Assuming you have User model

# class OrganizationService:
#     def __init__(self):
#         pass

#     async def get_organization_data(self, organization_id: Optional[str] = None) -> Optional[List[Organization]]:
#         if organization_id:
#             org = await Organization.get(ObjectId(organization_id))
#             return org
#         else:
#             orgs = await Organization.find_all().to_list()
#             return orgs

#     async def get_organization_users(self, organization_id: Optional[str] = None):
#         if organization_id:
#             users = await User.find_many(User.organization_id == ObjectId(organization_id)).to_list()
#             return users
#         else:
#             users = await User.find_all().to_list()
#             return users

#     async def save_organization_data(self, organization: OrganizationCreate) -> Organization:
#         new_org = Organization(**organization.dict())
#         await new_org.insert()
#         return new_org

#     async def update_organization_data(self, organization: OrganizationUpdate) -> Optional[Organization]:
#         if organization.id is None:
#             # Save as new if no id provided
#             new_org = Organization(**organization.dict(exclude={"id"}, exclude_none=True))
#             await new_org.insert()
#             return new_org
#         existing_org = await Organization.get(organization.id)
#         if existing_org is None:
#             return None
#         update_data = organization.dict(exclude_unset=True, exclude={"id"})
#         for key, value in update_data.items():
#             setattr(existing_org, key, value)
#         await existing_org.save()
#         return existing_org

#     async def delete_organization_data(self, organization_id: str) -> str:
#         org = await Organization.get(ObjectId(organization_id))
#         if org:
#             await org.delete()
#             return ""
#         return "Organization not found"
