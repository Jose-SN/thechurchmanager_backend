from fastapi import APIRouter, Depends, Request
from app.api.controllers import UserController, OrganizationController
from app.api.services import UserService, OrganizationService
from app.api.dependencies import get_db

organization_router = APIRouter(tags=["Organization"])

def get_organization_service(db=Depends(get_db)):
    return OrganizationService(db)

def get_organization_controller(organization_service=Depends(get_organization_service)):
    return OrganizationController(organization_service)

@organization_router.get("/get")
async def get_all_organizations(organization_controller: OrganizationController = Depends(get_organization_controller)):
    return await organization_controller.fetch_organization_controller()

@organization_router.post("/save")
async def save_organization(request: Request, organization_controller: OrganizationController = Depends(get_organization_controller)):
    return await organization_controller.save_organization_controller(request)

@organization_router.post("/bulk-save")
async def save_bulk_organization(request: Request, organization_controller: OrganizationController = Depends(get_organization_controller)):
    return await organization_controller.save_bulk_organization_controller(request)

@organization_router.put("/update")
async def update_organization(request: Request, organization_controller: OrganizationController = Depends(get_organization_controller)):
    return await organization_controller.update_organization_controller(request)

@organization_router.post("/delete/{organization_id}")
async def delete_organization(organization_id: str, organization_controller: OrganizationController = Depends(get_organization_controller)):
    return await organization_controller.delete_organization_controller(organization_id)




# from fastapi import APIRouter, Depends, Query, Path
# from controllers import organization_controller
# from schemas import OrganizationCreate, OrganizationUpdate
# from utils import get_current_user

# router = APIRouter()

# @router.get("/get")
# async def fetch_organization(id: str = Query(None), current_user=Depends(get_current_user)):
#     return await organization_controller.fetch_organization_controller(id, current_user)

# @router.get("/users")
# async def fetch_organization_users(id: str = Query(None), current_user=Depends(get_current_user)):
#     return await organization_controller.fetch_organization_users_controller(id, current_user)

# @router.post("/save")
# async def insert_organization(org: OrganizationCreate, current_user=Depends(get_current_user)):
#     return await organization_controller.insert_organization_controller(org, current_user)

# @router.put("/update")
# async def update_organization(org: OrganizationUpdate, current_user=Depends(get_current_user)):
#     return await organization_controller.update_organization_controller(org, current_user)

# @router.delete("/delete/{organizationid}")
# async def delete_organization(organizationid: str = Path(...), current_user=Depends(get_current_user)):
#     return await organization_controller.remove_organization_controller(organizationid, current_user)
