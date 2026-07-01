from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from app.service_rota.models import (
    RotaAssignment,
    RotaAttendance,
    RotaAvailability,
    RotaAuditLog,
    RotaClockSession,
    RotaService,
)


def _uuid(value: UUID | None) -> str | None:
    return str(value) if value is not None else None


def _dt(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _date(value: date | None) -> str | None:
    return value.isoformat() if value is not None else None


def service_to_dict(row: RotaService) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "organization_id": str(row.organization_id),
        "name": row.name,
        "date": _date(row.date),
        "time": row.time,
        "location": row.location,
        "description": row.description or "",
        "languages": row.languages or ["English"],
        "availability_options": row.availability_options or [],
        "max_volunteers": row.max_volunteers,
        "notes": row.notes or "",
        "status": row.status,
        "team_id": _uuid(row.team_id),
        "volunteer_count": row.volunteer_count,
        "attendance_summary": row.attendance_summary,
        "created_at": _dt(row.created_at),
        "updated_at": _dt(row.updated_at),
    }


def availability_to_dict(row: RotaAvailability) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "organization_id": str(row.organization_id),
        "service_id": str(row.service_id),
        "user_id": str(row.user_id),
        "user_name": row.user_name,
        "team_id": _uuid(row.team_id),
        "team_name": row.team_name,
        "role": row.role,
        "availability": row.availability,
        "comment": row.comment or "",
        "comments": row.comments or [],
        "updated_by_id": _uuid(row.updated_by_id),
        "updated_by_name": row.updated_by_name,
        "updated_at": _dt(row.updated_at),
        "created_at": _dt(row.created_at),
    }


def assignment_to_dict(row: RotaAssignment, *, service_date: date | None = None, service_time: str | None = None, service_name: str | None = None) -> dict[str, Any]:
    data = {
        "id": str(row.id),
        "organization_id": str(row.organization_id),
        "service_id": str(row.service_id),
        "user_id": str(row.user_id),
        "user_name": row.user_name,
        "user_email": row.user_email,
        "user_phone": row.user_phone,
        "team_id": str(row.team_id),
        "team_name": row.team_name,
        "role": row.role,
        "arrival_time": row.arrival_time,
        "notes": row.notes or "",
        "status": row.status,
        "sort_order": row.sort_order,
        "created_at": _dt(row.created_at),
        "updated_at": _dt(row.updated_at),
    }
    if service_date is not None:
        data["date"] = _date(service_date)
    if service_time is not None:
        data["time"] = service_time
    if service_name is not None:
        data["service_name"] = service_name
    return data


def attendance_to_dict(row: RotaAttendance) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "organization_id": str(row.organization_id),
        "service_id": str(row.service_id),
        "assignment_id": _uuid(row.assignment_id),
        "user_id": str(row.user_id),
        "user_name": row.user_name,
        "team_id": str(row.team_id),
        "team_name": row.team_name,
        "role": row.role,
        "status": row.status,
        "check_in_time": _dt(row.check_in_time),
        "check_out_time": _dt(row.check_out_time),
        "notes": row.notes or "",
        "replacement_user_id": _uuid(row.replacement_user_id),
        "replacement_user_name": row.replacement_user_name,
        "created_at": _dt(row.created_at),
        "updated_at": _dt(row.updated_at),
    }


def clock_session_to_dict(row: RotaClockSession) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "organization_id": str(row.organization_id),
        "user_id": str(row.user_id),
        "service_id": str(row.service_id),
        "assignment_id": _uuid(row.assignment_id),
        "shift_date": _date(row.shift_date),
        "service_name": row.service_name,
        "service_location": row.service_location or "",
        "role": row.role,
        "status": row.status,
        "clock_in_time": _dt(row.clock_in_time),
        "clock_in_lat": row.clock_in_lat,
        "clock_in_lng": row.clock_in_lng,
        "clock_in_accuracy": row.clock_in_accuracy,
        "clock_in_label": row.clock_in_label,
        "clock_out_time": _dt(row.clock_out_time),
        "clock_out_lat": row.clock_out_lat,
        "clock_out_lng": row.clock_out_lng,
        "clock_out_accuracy": row.clock_out_accuracy,
        "clock_out_label": row.clock_out_label,
        "created_at": _dt(row.created_at),
        "updated_at": _dt(row.updated_at),
    }


def audit_log_to_dict(row: RotaAuditLog) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "organization_id": str(row.organization_id),
        "service_id": _uuid(row.service_id),
        "user_id": _uuid(row.user_id),
        "user_name": row.user_name,
        "action": row.action,
        "field_name": row.field_name,
        "old_value": row.old_value,
        "new_value": row.new_value,
        "created_at": _dt(row.created_at),
    }
