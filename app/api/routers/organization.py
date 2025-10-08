from fastapi import APIRouter, Depends, Query, Path
from controllers import organization_controller
from schemas import OrganizationCreate, OrganizationUpdate
from utils import get_current_user

router = APIRouter()

@router.get("/get")
async def fetch_organization(id: str = Query(None), current_user=Depends(get_current_user)):
    return await organization_controller.fetch_organization_controller(id, current_user)

@router.get("/users")
async def fetch_organization_users(id: str = Query(None), current_user=Depends(get_current_user)):
    return await organization_controller.fetch_organization_users_controller(id, current_user)

@router.post("/save")
async def insert_organization(org: OrganizationCreate, current_user=Depends(get_current_user)):
    return await organization_controller.insert_organization_controller(org, current_user)

@router.put("/update")
async def update_organization(org: OrganizationUpdate, current_user=Depends(get_current_user)):
    return await organization_controller.update_organization_controller(org, current_user)

@router.delete("/delete/{organizationid}")
async def delete_organization(organizationid: str = Path(...), current_user=Depends(get_current_user)):
    return await organization_controller.remove_organization_controller(organizationid, current_user)
