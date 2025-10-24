from fastapi import APIRouter, Depends, Query, Request
from app.api.controllers import UserController, InventoryController
from app.api.services import UserService, InventoryService
from app.api.dependencies import get_db

inventory_router = APIRouter(tags=["Inventory"])

def get_inventory_service(db=Depends(get_db)):
    return InventoryService(db)

def get_inventory_controller(inventory_service=Depends(get_inventory_service)):
    return InventoryController(inventory_service)

@inventory_router.get("/get")
async def get_all_inventorys(inventory_controller: InventoryController = Depends(get_inventory_controller),
    _id: str = Query(None),
    organization_id: str = Query(None)):
    filters = {}
    if _id:
        filters["_id"] = _id
    if organization_id:
        filters["organization_id"] = organization_id
    return await inventory_controller.fetch_inventory_controller(filters)

@inventory_router.post("/save")
async def save_inventory(request: Request, inventory_controller: InventoryController = Depends(get_inventory_controller)):
    return await inventory_controller.save_inventory_controller(request)

@inventory_router.post("/bulk-save")
async def save_bulk_inventory(request: Request, inventory_controller: InventoryController = Depends(get_inventory_controller)):
    return await inventory_controller.save_bulk_inventory_controller(request)

@inventory_router.put("/update")
async def update_inventory(request: Request, inventory_controller: InventoryController = Depends(get_inventory_controller)):
    return await inventory_controller.update_inventory_controller(request)

@inventory_router.post("/delete/{inventory_id}")
async def delete_inventory(inventory_id: str, inventory_controller: InventoryController = Depends(get_inventory_controller)):
    return await inventory_controller.delete_inventory_controller(inventory_id)