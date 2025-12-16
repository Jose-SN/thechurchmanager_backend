from fastapi import APIRouter, Depends, Query, Request
from app.api.controllers import UserController, OrganizationController
from app.api.services import UserService, OrganizationService
from app.api.dependencies import get_db

organization_router = APIRouter(tags=["Organization"])

def get_organization_service(db=Depends(get_db)):
    return OrganizationService(db)

def get_organization_controller(organization_service=Depends(get_organization_service)):
    return OrganizationController(organization_service)

@organization_router.get("/get")
async def get_all_organizations(
    organization_controller: OrganizationController = Depends(get_organization_controller),
    id: str = Query(None),
    organization_id: str = Query(None)):
    filters = {}
    if id:
        filters["id"] = id
    if organization_id:
        filters["organization_id"] = organization_id
    return await organization_controller.fetch_organization_controller(filters)

@organization_router.post("/save")
async def save_organization(request: Request, organization_controller: OrganizationController = Depends(get_organization_controller)):
    return await organization_controller.save_organization_controller(request)

@organization_router.post("/login")
async def login_organization(request: Request, organization_controller: OrganizationController = Depends(get_organization_controller)):
    return await organization_controller.login_organization_controller(request)

@organization_router.post("/bulk-save")
async def save_bulk_organization(request: Request, organization_controller: OrganizationController = Depends(get_organization_controller)):
    return await organization_controller.save_bulk_organization_controller(request)

@organization_router.put("/update")
async def update_organization(request: Request, organization_controller: OrganizationController = Depends(get_organization_controller)):
    return await organization_controller.update_organization_controller(request)

@organization_router.delete("/delete/{organization_id}")
async def delete_organization(organization_id: str, organization_controller: OrganizationController = Depends(get_organization_controller)):
    return await organization_controller.delete_organization_controller(organization_id)
