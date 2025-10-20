from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from uvicorn import Config
from fastapi import HTTPException
from bson import ObjectId

from app.api import dependencies
from app.core.config import Settings

class OrganizationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.organizations = db["organizations"]

    async def get_organization_data(self) -> List[dict]:
        organizations = await self.organizations.find({}).to_list(length=None)
        for organization in organizations:
            if "_id" in organization:
                organization["_id"] = str(organization["_id"])
        return organizations

    async def save_organization_data(self, organization_data: dict) -> dict:
        # Hash password before save
        # if "password" in organization_data and organization_data["password"]:
        #     organization_data["password"] = pwd_context.hash(organization_data["password"])

        result = await self.organizations.insert_one(organization_data)
        organization = await self.organizations.find_one({"_id": result.inserted_id})
        return organization if organization is not None else {}
    
    
    async def save_bulk_organization_data(self, organizations_data: list[dict]) -> list[dict]:
        """
        Bulk insert organizations and return the inserted organization documents.
        """
        result = await self.organizations.insert_many(organizations_data)
        inserted_ids = result.inserted_ids
        organizations = await self.organizations.find({"_id": {"$in": inserted_ids}}).to_list(length=len(inserted_ids))
        return organizations


    async def update_organization_data(self, organization_data: dict) -> dict:
        organization_id = organization_data.get("id")
        # if not organization_id or not ObjectId.is_valid(organization_id):
        #     raise ValueError("Invalid organization ID")

        # if "password" in organization_data and organization_data["password"]:
        #     organization_data["password"] = pwd_context.hash(organization_data["password"])

        update_result = await self.organizations.find_one_and_update(
            {"_id": str(organization_id)},
            {"$set": organization_data},
            return_document=True  # Returns updated document
        )

        if not update_result:
            raise ValueError("Organization not found")
        return update_result

    async def delete_organization_data(self, organization_id: str) -> str:
        if not ObjectId.is_valid(organization_id):
            raise HTTPException(status_code=400, detail="Invalid organization ID")
        result = await self.organizations.find_one_and_delete({"_id": str(organization_id)})
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
