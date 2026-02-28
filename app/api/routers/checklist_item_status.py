from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from app.api.controllers.checklist_item_status import ChecklistItemStatusController
from app.api.services.checklist_item_status import ChecklistItemStatusService
from app.api.dependencies import get_db

router = APIRouter(tags=["ChecklistItemStatus"])


def get_service(db=Depends(get_db)):
    return ChecklistItemStatusService(db)


def get_controller(service=Depends(get_service)):
    return ChecklistItemStatusController(service)


@router.get("/get")
async def get_statuses(
    controller: ChecklistItemStatusController = Depends(get_controller),
    id: Optional[str] = Query(None),
    checklist_record_id: Optional[str] = Query(None),
):
    filters = {}
    if id:
        filters["id"] = id
    if checklist_record_id:
        filters["checklist_record_id"] = checklist_record_id
    return await controller.fetch(filters)


@router.post("/save")
async def save_status(request: Request, controller: ChecklistItemStatusController = Depends(get_controller)):
    return await controller.save(request)


@router.put("/update/{id}")
async def update_status(id: str, request: Request, controller: ChecklistItemStatusController = Depends(get_controller)):
    return await controller.update(id, request)


@router.delete("/delete/{id}")
async def delete_status(id: str, controller: ChecklistItemStatusController = Depends(get_controller)):
    return await controller.delete(id)


@router.get("/{id}")
async def get_status_by_id(id: str, controller: ChecklistItemStatusController = Depends(get_controller)):
    return await controller.get_by_id(id)
