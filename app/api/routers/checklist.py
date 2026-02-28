from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from app.api.controllers.checklist_template import ChecklistTemplateController
from app.api.services.checklist_template import ChecklistTemplateService
from app.api.dependencies import get_db

router = APIRouter(prefix="/checklist", tags=["Checklist"])

templates_router = APIRouter(tags=["ChecklistTemplates"])


def get_service(db=Depends(get_db)):
    return ChecklistTemplateService(db)


def get_controller(service=Depends(get_service)):
    return ChecklistTemplateController(service)


# Route order matters: specific paths before path params
@templates_router.post("")
async def create_template(request: Request, controller: ChecklistTemplateController = Depends(get_controller)):
    """Create template, optionally with items. POST /checklist/templates"""
    return await controller.save(request)


@templates_router.get("")
async def get_templates(
    controller: ChecklistTemplateController = Depends(get_controller),
    id: Optional[str] = Query(None),
    team_id: Optional[str] = Query(None),
):
    filters = {}
    if id:
        filters["id"] = id
    if team_id:
        filters["team_id"] = team_id
    return await controller.fetch(filters)


@templates_router.put("/{id}")
async def update_template(id: str, request: Request, controller: ChecklistTemplateController = Depends(get_controller)):
    return await controller.update(id, request)


@templates_router.delete("/{id}")
async def delete_template(id: str, controller: ChecklistTemplateController = Depends(get_controller)):
    return await controller.delete(id)


@templates_router.get("/{id}")
async def get_template_by_id(id: str, controller: ChecklistTemplateController = Depends(get_controller)):
    return await controller.get_by_id(id)


router.include_router(templates_router, prefix="/templates")
