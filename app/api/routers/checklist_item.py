from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from app.api.controllers.checklist_item import ChecklistItemController
from app.api.services.checklist_item import ChecklistItemService
from app.api.dependencies import get_db

router = APIRouter(tags=["ChecklistItem"])


def get_service(db=Depends(get_db)):
    return ChecklistItemService(db)


def get_controller(service=Depends(get_service)):
    return ChecklistItemController(service)


@router.get("/get")
async def get_items(
    controller: ChecklistItemController = Depends(get_controller),
    id: Optional[str] = Query(None),
    template_id: Optional[str] = Query(None),
):
    filters = {}
    if id:
        filters["id"] = id
    if template_id:
        filters["template_id"] = template_id
    return await controller.fetch(filters)


@router.post("/save")
async def save_item(request: Request, controller: ChecklistItemController = Depends(get_controller)):
    return await controller.save(request)


@router.put("/update/{id}")
async def update_item(id: str, request: Request, controller: ChecklistItemController = Depends(get_controller)):
    return await controller.update(id, request)


@router.delete("/delete/{id}")
async def delete_item(id: str, controller: ChecklistItemController = Depends(get_controller)):
    return await controller.delete(id)


@router.get("/{id}")
async def get_item_by_id(id: str, controller: ChecklistItemController = Depends(get_controller)):
    return await controller.get_by_id(id)
