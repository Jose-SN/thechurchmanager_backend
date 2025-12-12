from fastapi import APIRouter, Depends, Query, Request
from app.api.controllers import UserController, PermissionController
from app.api.services import UserService, PermissionService
from app.api.dependencies import get_db

permission_router = APIRouter(tags=["Permission"])

def get_permission_service(db=Depends(get_db)):
    return PermissionService(db)

def get_permission_controller(permission_service=Depends(get_permission_service)):
    return PermissionController(permission_service)

@permission_router.get("/get")
async def get_all_permissions(permission_controller: PermissionController = Depends(get_permission_controller),
    id: str = Query(None),
    organization_id: str = Query(None),
    role_id: str = Query(None),
    module_id: str = Query(None),
    team_id: str = Query(None)):
    filters = {}
    if id:
        filters["id"] = id
    if organization_id:
        filters["organization_id"] = organization_id
    if role_id:
        filters["role_id"] = role_id
    if module_id:
        filters["module_id"] = module_id
    if team_id:
        filters["team_id"] = team_id
    return await permission_controller.fetch_permission_controller(filters)

@permission_router.post("/save")
async def save_permission(request: Request, permission_controller: PermissionController = Depends(get_permission_controller)):
    return await permission_controller.save_permission_controller(request)

@permission_router.post("/bulk-save")
async def save_bulk_permission(request: Request, permission_controller: PermissionController = Depends(get_permission_controller)):
    return await permission_controller.save_bulk_permission_controller(request)

@permission_router.put("/update")
async def update_permission(request: Request, permission_controller: PermissionController = Depends(get_permission_controller)):
    return await permission_controller.update_permission_controller(request)

@permission_router.delete("/delete/{permission_id}")
async def delete_permission(permission_id: str, permission_controller: PermissionController = Depends(get_permission_controller)):
    return await permission_controller.delete_permission_controller(permission_id)