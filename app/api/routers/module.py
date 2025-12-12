from fastapi import APIRouter, Depends, Query, Request
from app.api.controllers import UserController, ModuleController
from app.api.services import UserService, ModuleService
from app.api.dependencies import get_db

module_router = APIRouter(tags=["Module"])

def get_module_service(db=Depends(get_db)):
    return ModuleService(db)

def get_module_controller(module_service=Depends(get_module_service)):
    return ModuleController(module_service)

@module_router.get("/get")
async def get_all_modules(module_controller: ModuleController = Depends(get_module_controller),
    id: str = Query(None),
    organization_id: str = Query(None)):
    filters = {}
    if id:
        filters["id"] = id
    if organization_id:
        filters["organization_id"] = organization_id
    return await module_controller.fetch_module_controller(filters)

@module_router.post("/save")
async def save_module(request: Request, module_controller: ModuleController = Depends(get_module_controller)):
    return await module_controller.save_module_controller(request)

@module_router.post("/bulk-save")
async def save_bulk_module(request: Request, module_controller: ModuleController = Depends(get_module_controller)):
    return await module_controller.save_bulk_module_controller(request)

@module_router.put("/update")
async def update_module(request: Request, module_controller: ModuleController = Depends(get_module_controller)):
    return await module_controller.update_module_controller(request)

@module_router.delete("/delete/{module_id}")
async def delete_module(module_id: str, module_controller: ModuleController = Depends(get_module_controller)):
    return await module_controller.delete_module_controller(module_id)