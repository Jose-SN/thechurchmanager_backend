from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from app.api.controllers.checklist_record import ChecklistRecordController
from app.api.services.checklist_record import ChecklistRecordService
from app.api.dependencies import get_db

router = APIRouter(tags=["ChecklistRecord"])


def get_service(db=Depends(get_db)):
    return ChecklistRecordService(db)


def get_controller(service=Depends(get_service)):
    return ChecklistRecordController(service)


@router.get("/get")
async def get_records(
    controller: ChecklistRecordController = Depends(get_controller),
    id: Optional[str] = Query(None),
    template_id: Optional[str] = Query(None),
    team_id: Optional[str] = Query(None),
):
    filters = {}
    if id:
        filters["id"] = id
    if template_id:
        filters["template_id"] = template_id
    if team_id:
        filters["team_id"] = team_id
    return await controller.fetch(filters)


@router.post("/save")
async def save_record(request: Request, controller: ChecklistRecordController = Depends(get_controller)):
    return await controller.save(request)


@router.put("/update/{id}")
async def update_record(id: str, request: Request, controller: ChecklistRecordController = Depends(get_controller)):
    return await controller.update(id, request)


@router.delete("/delete/{id}")
async def delete_record(id: str, controller: ChecklistRecordController = Depends(get_controller)):
    return await controller.delete(id)


@router.get("/{id}")
async def get_record_by_id(id: str, controller: ChecklistRecordController = Depends(get_controller)):
    return await controller.get_by_id(id)
