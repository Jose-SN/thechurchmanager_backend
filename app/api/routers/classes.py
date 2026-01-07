from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from app.api.controllers import ClassController
from app.api.services import ClassService
from app.api.dependencies import get_db

class_router = APIRouter(tags=["Class"])

def get_class_service(db=Depends(get_db)):
    return ClassService(db)

def get_class_controller(class_service=Depends(get_class_service)):
    return ClassController(class_service)

@class_router.post("/save", status_code=201)
async def save_class(request: Request, class_controller: ClassController = Depends(get_class_controller)):
    """Create a new class."""
    return await class_controller.save_class_controller(request)

@class_router.get("/get")
async def get_classes(
    class_controller: ClassController = Depends(get_class_controller),
    id: Optional[str] = Query(None, description="Class ID"),
    organization_id: Optional[str] = Query(None, description="Organization ID")
):
    """Get list of classes filtered by organization_id."""
    filters = {}
    if id:
        filters["id"] = id
    if organization_id:
        filters["organization_id"] = organization_id
    return await class_controller.fetch_class_controller(filters)

@class_router.get("/get/{class_id}")
async def get_class_by_id(
    class_id: str,
    class_controller: ClassController = Depends(get_class_controller)
):
    """Get a single class by ID."""
    return await class_controller.get_class_by_id_controller(class_id)

@class_router.put("/update/{class_id}")
async def update_class(
    class_id: str,
    request: Request,
    class_controller: ClassController = Depends(get_class_controller)
):
    """Update an existing class."""
    return await class_controller.update_class_controller(class_id, request)

@class_router.delete("/delete/{class_id}")
async def delete_class(
    class_id: str,
    class_controller: ClassController = Depends(get_class_controller)
):
    """Delete a class."""
    return await class_controller.delete_class_controller(class_id)

