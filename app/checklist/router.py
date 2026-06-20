from __future__ import annotations

import logging
from datetime import date
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.checklist.auth import AuthContext, get_checklist_context
from app.checklist.exceptions import ChecklistError
from app.checklist.schemas import (
    ChecklistRecordCreate,
    ChecklistRecordUpdate,
    ChecklistTemplateCreate,
    ChecklistTemplateUpdate,
)
from app.checklist.service import ChecklistService
from app.db.session import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/checklist",
    tags=["Checklist"],
)


def get_service(session: AsyncSession = Depends(get_db_session)) -> ChecklistService:
    return ChecklistService(session)


def _wrap(data: Any, status_code: int = status.HTTP_200_OK) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"data": data})


def _handle_error(exc: Exception) -> JSONResponse:
    if isinstance(exc, HTTPException):
        raise exc
    if isinstance(exc, ChecklistError):
        return JSONResponse(status_code=exc.status_code, content={"error": exc.message})
    logger.exception("Unhandled checklist error")
    return JSONResponse(status_code=500, content={"error": str(exc)})


@router.get("/templates")
async def list_templates(
    team_id: UUID | None = Query(None),
    auth: AuthContext = Depends(get_checklist_context),
    service: ChecklistService = Depends(get_service),
):
    try:
        data = await service.list_templates(auth, team_id)
        return _wrap([item.model_dump(mode="json") for item in data])
    except Exception as exc:
        return _handle_error(exc)


@router.post("/templates", status_code=status.HTTP_201_CREATED)
async def create_template(
    payload: ChecklistTemplateCreate,
    auth: AuthContext = Depends(get_checklist_context),
    service: ChecklistService = Depends(get_service),
):
    try:
        data = await service.create_template(auth, payload)
        return _wrap(data.model_dump(mode="json"), status.HTTP_201_CREATED)
    except Exception as exc:
        return _handle_error(exc)


@router.put("/templates/{template_id}")
async def update_template(
    template_id: UUID,
    payload: ChecklistTemplateUpdate,
    auth: AuthContext = Depends(get_checklist_context),
    service: ChecklistService = Depends(get_service),
):
    try:
        data = await service.update_template(auth, template_id, payload)
        return _wrap(data.model_dump(mode="json"))
    except Exception as exc:
        return _handle_error(exc)


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: UUID,
    auth: AuthContext = Depends(get_checklist_context),
    service: ChecklistService = Depends(get_service),
):
    try:
        await service.delete_template(auth, template_id)
        return _wrap({"deleted": True, "id": str(template_id)})
    except Exception as exc:
        return _handle_error(exc)


@router.get("/records")
async def list_records(
    auth: AuthContext = Depends(get_checklist_context),
    service: ChecklistService = Depends(get_service),
    date: date | None = Query(None, alias="date"),
    team_id: UUID | None = Query(None),
    template_id: UUID | None = Query(None),
    completed_by: str | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    try:
        result = await service.list_records(
            auth,
            record_date=date,
            team_id=team_id,
            template_id=template_id,
            completed_by=completed_by,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit,
        )
        result["data"] = [item.model_dump(mode="json") for item in result["data"]]
        return JSONResponse(content=result)
    except Exception as exc:
        return _handle_error(exc)


@router.get("/records/{record_id}")
async def get_record(
    record_id: UUID,
    auth: AuthContext = Depends(get_checklist_context),
    service: ChecklistService = Depends(get_service),
):
    try:
        data = await service.get_record(auth, record_id)
        return _wrap(data.model_dump(mode="json"))
    except Exception as exc:
        return _handle_error(exc)


@router.post("/records", status_code=status.HTTP_201_CREATED)
async def create_record(
    payload: ChecklistRecordCreate,
    auth: AuthContext = Depends(get_checklist_context),
    service: ChecklistService = Depends(get_service),
):
    try:
        data = await service.create_record(auth, payload)
        return _wrap(data.model_dump(mode="json"), status.HTTP_201_CREATED)
    except Exception as exc:
        return _handle_error(exc)


@router.put("/records/{record_id}")
async def update_record(
    record_id: UUID,
    payload: ChecklistRecordUpdate,
    auth: AuthContext = Depends(get_checklist_context),
    service: ChecklistService = Depends(get_service),
):
    try:
        data = await service.update_record(auth, record_id, payload)
        return _wrap(data.model_dump(mode="json"))
    except Exception as exc:
        return _handle_error(exc)
