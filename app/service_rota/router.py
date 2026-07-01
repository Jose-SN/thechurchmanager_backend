from __future__ import annotations

import logging
from datetime import date
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth_context import AuthContext
from app.db.session import get_db_session
from app.service_rota.auth import get_service_rota_context
from app.service_rota.exceptions import RotaError
from app.service_rota.schemas import (
    AssignmentCreate,
    AssignmentUpdate,
    AttendancePatch,
    AvailabilityBulkCreate,
    AvailabilityCreate,
    ClockInCreate,
    ClockOutCreate,
    RotaServiceCreate,
    RotaServiceUpdate,
)
from app.service_rota.service import ServiceRotaService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rota", tags=["Service Rota"])


def get_service(session: AsyncSession = Depends(get_db_session)) -> ServiceRotaService:
    return ServiceRotaService(session)


def _ok(data: Any, status_code: int = status.HTTP_200_OK) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"success": True, "data": data})


def _err(exc: Exception) -> JSONResponse:
    if isinstance(exc, HTTPException):
        raise exc
    if isinstance(exc, RotaError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": {"message": exc.message}},
        )
    logger.exception("Unhandled service rota error")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": {"message": str(exc)}},
    )


def _require_org(auth: AuthContext, organization_id: UUID | None) -> UUID:
    org_id = organization_id or auth.organization_id
    if org_id != auth.organization_id:
        raise HTTPException(status_code=403, detail={"error": "Organization mismatch"})
    return org_id


# --- A. Services ---


@router.get("/get")
async def get_services(
    organization_id: UUID = Query(...),
    status: str | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    search: str | None = Query(None),
    sort: str = Query("date"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, organization_id)
        data = await service.list_services(
            auth,
            status=status,
            start_date=start_date,
            end_date=end_date,
            search=search,
            sort=sort,
            order=order,
            page=page,
            limit=limit,
        )
        return _ok(data)
    except Exception as exc:
        return _err(exc)


@router.post("/save", status_code=status.HTTP_201_CREATED)
async def save_service(
    payload: RotaServiceCreate,
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        data = await service.save_service(auth, payload)
        return _ok(data, status.HTTP_201_CREATED)
    except Exception as exc:
        return _err(exc)


@router.put("/update/{service_id}")
async def update_service(
    service_id: UUID,
    payload: RotaServiceUpdate,
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        data = await service.update_service(auth, service_id, payload)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


@router.delete("/delete/{service_id}")
async def delete_service(
    service_id: UUID,
    organization_id: UUID = Query(...),
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, organization_id)
        data = await service.delete_service(auth, service_id)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


@router.post("/{status_value}/{service_id}")
async def set_service_status(
    status_value: str,
    service_id: UUID,
    organization_id: UUID = Query(...),
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, organization_id)
        data = await service.set_service_status(auth, service_id, status_value)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


# --- B. Availability ---


@router.get("/availability")
async def get_availability(
    organization_id: UUID = Query(...),
    service_id: UUID | None = Query(None),
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, organization_id)
        data = await service.get_availability(auth, service_id)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


@router.post("/availability", status_code=status.HTTP_201_CREATED)
async def save_availability(
    payload: AvailabilityCreate,
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        data = await service.save_availability(auth, payload)
        return _ok(data, status.HTTP_201_CREATED)
    except Exception as exc:
        return _err(exc)


@router.post("/availability/bulk")
async def bulk_save_availability(
    payload: AvailabilityBulkCreate,
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, payload.organization_id)
        data = await service.bulk_save_availability(auth, payload.service_id, payload.records)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


# --- C. Assignments ---


@router.get("/assignments")
async def get_assignments(
    organization_id: UUID = Query(...),
    service_id: UUID = Query(...),
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, organization_id)
        data = await service.get_assignments(auth, service_id)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


@router.post("/assignments", status_code=status.HTTP_201_CREATED)
async def save_assignment(
    payload: AssignmentCreate,
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        data = await service.save_assignment(auth, payload)
        return _ok(data, status.HTTP_201_CREATED)
    except Exception as exc:
        return _err(exc)


@router.put("/assignments/{assignment_id}")
async def update_assignment(
    assignment_id: UUID,
    payload: AssignmentUpdate,
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        data = await service.update_assignment(auth, assignment_id, payload)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


# --- D. Attendance ---


@router.get("/attendance")
async def get_attendance(
    organization_id: UUID = Query(...),
    service_id: UUID = Query(...),
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, organization_id)
        data = await service.get_attendance(auth, service_id)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


@router.patch("/attendance/{record_id}")
async def patch_attendance(
    record_id: UUID,
    payload: AttendancePatch,
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        data = await service.patch_attendance(auth, record_id, payload)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


@router.post("/attendance/sync/{service_id}")
async def sync_attendance(
    service_id: UUID,
    organization_id: UUID = Query(...),
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, organization_id)
        data = await service.sync_attendance(auth, service_id)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


# --- E. Dashboard & Reports ---


@router.get("/dashboard")
async def dashboard(
    organization_id: UUID = Query(...),
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, organization_id)
        data = await service.dashboard(auth)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


@router.get("/reports")
async def reports(
    organization_id: UUID = Query(...),
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, organization_id)
        data = await service.reports(auth)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


@router.get("/history")
async def history(
    organization_id: UUID = Query(...),
    limit: int = Query(100, ge=1, le=500),
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, organization_id)
        data = await service.history(auth, limit=limit)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


# --- F. Grid ---


@router.get("/grid")
async def rota_grid(
    organization_id: UUID = Query(...),
    week_start: date = Query(...),
    team_ids: list[UUID] | None = Query(None),
    user_ids: list[UUID] | None = Query(None),
    group_by: str = Query("team"),
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, organization_id)
        data = await service.grid(auth, week_start, team_ids, user_ids, group_by)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


# --- G. Timesheets ---


@router.get("/timesheets")
async def timesheets(
    organization_id: UUID = Query(...),
    week_start: date = Query(...),
    team_id: UUID | None = Query(None),
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, organization_id)
        data = await service.timesheets(auth, week_start, team_id)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


# --- H. Volunteer portal ---


@router.get("/my/schedule")
async def my_schedule(
    organization_id: UUID = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, organization_id)
        data = await service.my_schedule(auth, start_date, end_date)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


@router.get("/my/rota")
async def my_rota(
    organization_id: UUID = Query(...),
    target_date: date = Query(..., alias="date"),
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, organization_id)
        data = await service.my_rota(auth, target_date)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


@router.get("/my/shifts/{shift_date}")
async def my_shifts(
    shift_date: date,
    organization_id: UUID = Query(...),
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, organization_id)
        data = await service.my_shifts(auth, shift_date)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


# --- I. Clock in/out ---


@router.get("/clock/sessions")
async def clock_sessions(
    organization_id: UUID = Query(...),
    shift_date: date | None = Query(None, alias="date"),
    status: str | None = Query(None),
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, organization_id)
        data = await service.clock_sessions(auth, shift_date=shift_date, status=status)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


@router.get("/clock/active")
async def clock_active(
    organization_id: UUID = Query(...),
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        _require_org(auth, organization_id)
        data = await service.clock_active(auth)
        return _ok(data)
    except Exception as exc:
        return _err(exc)


@router.post("/clock/in", status_code=status.HTTP_201_CREATED)
async def clock_in(
    payload: ClockInCreate,
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        data = await service.clock_in(auth, payload)
        return _ok(data, status.HTTP_201_CREATED)
    except Exception as exc:
        return _err(exc)


@router.post("/clock/out")
async def clock_out(
    payload: ClockOutCreate,
    auth: AuthContext = Depends(get_service_rota_context),
    service: ServiceRotaService = Depends(get_service),
):
    try:
        data = await service.clock_out(auth, payload)
        return _ok(data)
    except Exception as exc:
        return _err(exc)
