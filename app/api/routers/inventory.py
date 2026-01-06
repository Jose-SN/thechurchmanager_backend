from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from app.api.controllers import InventoryController
from app.api.services import InventoryService
from app.api.dependencies import get_db

inventory_router = APIRouter(tags=["Inventory"])

def get_inventory_service(db=Depends(get_db)):
    return InventoryService(db)

def get_inventory_controller(inventory_service=Depends(get_inventory_service)):
    return InventoryController(inventory_service)

@inventory_router.get("/get")
async def get_inventories(
    inventory_controller: InventoryController = Depends(get_inventory_controller),
    organization_id: Optional[str] = Query(None, description="Organization ID (required)"),
    team_id: Optional[str] = Query(None, description="Team ID (optional)")
):
    """
    Get list of inventories filtered by organization_id and optionally by team_id.
    
    Query Parameters:
    - organization_id: UUID (required)
    - team_id: UUID (optional)
    """
    filters = {}
    if organization_id:
        filters["organization_id"] = organization_id
    if team_id:
        filters["team_id"] = team_id
    
    return await inventory_controller.fetch_inventory_controller(filters)

@inventory_router.get("/get/{inventory_id}")
async def get_inventory_by_id(
    inventory_id: str,
    inventory_controller: InventoryController = Depends(get_inventory_controller)
):
    """
    Get a single inventory item by ID.
    """
    return await inventory_controller.get_inventory_by_id_controller(inventory_id)

@inventory_router.post("/save")
async def save_inventory(
    request: Request,
    inventory_controller: InventoryController = Depends(get_inventory_controller)
):
    """
    Create a new inventory item.
    
    Request Body:
    {
        "itemName": "string (required, max 255 chars)",
        "price": "number (optional, min 0, 2 decimal places)",
        "stockLeft": "integer (required, min 0)",
        "purchaseDate": "date string ISO format (optional, YYYY-MM-DD)",
        "patchTestDate": "date string ISO format (optional, YYYY-MM-DD)",
        "warrantyDate": "date string ISO format (optional, YYYY-MM-DD)",
        "organization_id": "UUID string (required)",
        "team_id": "UUID string (required)"
    }
    """
    return await inventory_controller.save_inventory_controller(request)

@inventory_router.put("/update/{inventory_id}")
async def update_inventory(
    inventory_id: str,
    request: Request,
    inventory_controller: InventoryController = Depends(get_inventory_controller)
):
    """
    Update an existing inventory item.
    
    Request Body: (same as POST, all fields optional except id in URL)
    """
    return await inventory_controller.update_inventory_controller(inventory_id, request)

@inventory_router.delete("/delete/{inventory_id}")
async def delete_inventory(
    inventory_id: str,
    inventory_controller: InventoryController = Depends(get_inventory_controller)
):
    """
    Delete an inventory item.
    """
    return await inventory_controller.delete_inventory_controller(inventory_id)
