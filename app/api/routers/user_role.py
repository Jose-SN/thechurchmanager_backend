from fastapi import APIRouter, Depends, Query, Request
from app.api.controllers import UserRoleController
from app.api.services import UserRoleService
from app.api.dependencies import get_db

user_role_router = APIRouter(tags=["UserRole"])

def get_user_role_service(db=Depends(get_db)):
    return UserRoleService(db)

def get_user_role_controller(user_role_service=Depends(get_user_role_service)):
    return UserRoleController(user_role_service)

@user_role_router.get("/get")
async def get_all_user_roles(user_role_controller: UserRoleController = Depends(get_user_role_controller),
    id: str = Query(None),
    _id: str = Query(None),
    organization_id: str = Query(None),
    user_id: str = Query(None),
    role_id: str = Query(None),
    team_id: str = Query(None)):
    filters = {}
    if id or _id:
        filters["id"] = id or _id
    if organization_id:
        filters["organization_id"] = organization_id
    if user_id:
        filters["user_id"] = user_id
    if role_id:
        filters["role_id"] = role_id
    if team_id:
        filters["team_id"] = team_id
    return await user_role_controller.fetch_user_role_controller(filters)

@user_role_router.post("/save")
async def save_user_role(request: Request, user_role_controller: UserRoleController = Depends(get_user_role_controller)):
    return await user_role_controller.save_user_role_controller(request)

@user_role_router.post("/bulk-save")
async def save_bulk_user_role(request: Request, user_role_controller: UserRoleController = Depends(get_user_role_controller)):
    return await user_role_controller.save_bulk_user_role_controller(request)

@user_role_router.put("/update")
async def update_user_role(request: Request, user_role_controller: UserRoleController = Depends(get_user_role_controller)):
    return await user_role_controller.update_user_role_controller(request)

@user_role_router.delete("/delete/{user_role_id}")
async def delete_user_role(user_role_id: str, user_role_controller: UserRoleController = Depends(get_user_role_controller)):
    return await user_role_controller.delete_user_role_controller(user_role_id)

@user_role_router.post("/update-roles")
async def update_roles(request: Request, user_role_controller: UserRoleController = Depends(get_user_role_controller)):
    return await user_role_controller.update_roles_controller(request)

