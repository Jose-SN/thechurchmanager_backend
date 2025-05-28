# services/organization_service.py
from typing import Optional, List
from models.organization import Organization
from schemas.organization import OrganizationCreate, OrganizationUpdate
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from models.user import User  # Assuming you have User model

class OrganizationService:
    def __init__(self):
        pass

    async def get_organization_data(self, organization_id: Optional[str] = None) -> Optional[List[Organization]]:
        if organization_id:
            org = await Organization.get(ObjectId(organization_id))
            return org
        else:
            orgs = await Organization.find_all().to_list()
            return orgs

    async def get_organization_users(self, organization_id: Optional[str] = None):
        if organization_id:
            users = await User.find_many(User.organization_id == ObjectId(organization_id)).to_list()
            return users
        else:
            users = await User.find_all().to_list()
            return users

    async def save_organization_data(self, organization: OrganizationCreate) -> Organization:
        new_org = Organization(**organization.dict())
        await new_org.insert()
        return new_org

    async def update_organization_data(self, organization: OrganizationUpdate) -> Optional[Organization]:
        if organization.id is None:
            # Save as new if no id provided
            new_org = Organization(**organization.dict(exclude={"id"}, exclude_none=True))
            await new_org.insert()
            return new_org
        existing_org = await Organization.get(organization.id)
        if existing_org is None:
            return None
        update_data = organization.dict(exclude_unset=True, exclude={"id"})
        for key, value in update_data.items():
            setattr(existing_org, key, value)
        await existing_org.save()
        return existing_org

    async def delete_organization_data(self, organization_id: str) -> str:
        org = await Organization.get(ObjectId(organization_id))
        if org:
            await org.delete()
            return ""
        return "Organization not found"
