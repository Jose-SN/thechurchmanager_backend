from fastapi import APIRouter, Depends, Query, Request
from app.api.controllers import UserController, RoleController
from app.api.services import UserService, RoleService
from app.api.dependencies import get_db

role_router = APIRouter(tags=["Role"])

def get_role_service(db=Depends(get_db)):
    return RoleService(db)

def get_role_controller(role_service=Depends(get_role_service)):
    return RoleController(role_service)

@role_router.get("/get")
async def get_all_roles(role_controller: RoleController = Depends(get_role_controller),
    _id: str = Query(None),
    organization_id: str = Query(None)):
    filters = {}
    if _id:
        filters["_id"] = _id
    if organization_id:
        filters["organization_id"] = organization_id
    return await role_controller.fetch_role_controller(filters)

@role_router.post("/save")
async def save_role(request: Request, role_controller: RoleController = Depends(get_role_controller)):
    return await role_controller.save_role_controller(request)

@role_router.post("/bulk-save")
async def save_bulk_role(request: Request, role_controller: RoleController = Depends(get_role_controller)):
    return await role_controller.save_bulk_role_controller(request)

@role_router.put("/update")
async def update_role(request: Request, role_controller: RoleController = Depends(get_role_controller)):
    return await role_controller.update_role_controller(request)

@role_router.delete("/delete/{role_id}")
async def delete_role(role_id: str, role_controller: RoleController = Depends(get_role_controller)):
    return await role_controller.delete_role_controller(role_id)