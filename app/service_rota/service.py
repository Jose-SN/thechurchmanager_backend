from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth_context import AuthContext
from app.service_rota.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.service_rota.permissions import (
    assert_can_manage_services,
    assert_can_view_reports,
    assert_volunteer_own_record,
    resolve_rota_role,
)
from app.service_rota.repository import RotaRepository
from app.service_rota.schemas import (
    AssignmentCreate,
    AssignmentUpdate,
    AttendancePatch,
    AvailabilityCreate,
    ClockInCreate,
    ClockOutCreate,
    RotaServiceCreate,
    RotaServiceUpdate,
)
from app.service_rota.serializers import (
    assignment_to_dict,
    attendance_to_dict,
    audit_log_to_dict,
    availability_to_dict,
    clock_session_to_dict,
    service_to_dict,
)


def _parse_uuid(value: str | uuid.UUID | None, field: str = "id") -> uuid.UUID:
    if value is None:
        raise ValidationError(f"{field} is required")
    try:
        return uuid.UUID(str(value))
    except ValueError as exc:
        raise ValidationError(f"Invalid {field}") from exc


def _user_uuid(auth: AuthContext) -> uuid.UUID:
    try:
        return uuid.UUID(str(auth.user_id))
    except ValueError:
        return uuid.uuid5(uuid.NAMESPACE_DNS, auth.user_id)


class ServiceRotaService:
    def __init__(self, session: AsyncSession):
        self.repo = RotaRepository(session)
        self.session = session

    async def _audit(
        self,
        auth: AuthContext,
        *,
        action: str,
        service_id: uuid.UUID | None = None,
        field_name: str | None = None,
        old_value: str | None = None,
        new_value: str | None = None,
    ) -> None:
        await self.repo.write_audit_log(
            {
                "organization_id": auth.organization_id,
                "service_id": service_id,
                "user_id": _user_uuid(auth),
                "user_name": auth.user_id,
                "action": action,
                "field_name": field_name,
                "old_value": old_value,
                "new_value": new_value,
            }
        )

    async def list_services(
        self,
        auth: AuthContext,
        *,
        status: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        search: str | None = None,
        sort: str = "date",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> dict[str, Any]:
        assert_can_manage_services(auth, auth.organization_id)
        rows, total = await self.repo.list_services(
            auth.organization_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            search=search,
            sort=sort,
            order=order,
            page=page,
            limit=limit,
        )
        return {
            "items": [service_to_dict(r) for r in rows],
            "total": total,
            "page": page,
            "limit": limit,
        }

    async def save_service(self, auth: AuthContext, payload: RotaServiceCreate) -> dict[str, Any]:
        assert_can_manage_services(auth, payload.organization_id)
        if payload.organization_id != auth.organization_id:
            raise ForbiddenError("Organization mismatch")
        data = payload.model_dump(exclude_none=True)
        if data.get("availability_options") is None:
            data["availability_options"] = [
                "available",
                "available_all_day",
                "unavailable",
                "not_sure",
            ]
        row = await self.repo.create_service(data)
        await self._audit(auth, action="create_service", service_id=row.id)
        await self.session.commit()
        return service_to_dict(row)

    async def update_service(
        self, auth: AuthContext, service_id: uuid.UUID, payload: RotaServiceUpdate
    ) -> dict[str, Any]:
        assert_can_manage_services(auth, auth.organization_id)
        row = await self.repo.get_service(auth.organization_id, service_id)
        if not row:
            raise NotFoundError("Service not found")
        data = payload.model_dump(exclude_none=True)
        row = await self.repo.update_service(row, data)
        await self._audit(auth, action="update_service", service_id=row.id)
        await self.session.commit()
        return service_to_dict(row)

    async def delete_service(self, auth: AuthContext, service_id: uuid.UUID) -> dict[str, Any]:
        assert_can_manage_services(auth, auth.organization_id)
        deleted = await self.repo.delete_service(auth.organization_id, service_id)
        if not deleted:
            raise NotFoundError("Service not found")
        await self._audit(auth, action="delete_service", service_id=service_id)
        await self.session.commit()
        return {"deleted": True, "service_id": str(service_id)}

    async def set_service_status(
        self, auth: AuthContext, service_id: uuid.UUID, status: str
    ) -> dict[str, Any]:
        assert_can_manage_services(auth, auth.organization_id)
        row = await self.repo.set_service_status(auth.organization_id, service_id, status)
        if not row:
            raise NotFoundError("Service not found")
        await self._audit(
            auth,
            action="set_status",
            service_id=row.id,
            field_name="status",
            new_value=status,
        )
        await self.session.commit()
        return service_to_dict(row)

    async def get_availability(
        self, auth: AuthContext, service_id: uuid.UUID | None = None
    ) -> list[dict[str, Any]]:
        rows = await self.repo.list_availability(auth.organization_id, service_id)
        return [availability_to_dict(r) for r in rows]

    async def save_availability(
        self, auth: AuthContext, payload: AvailabilityCreate
    ) -> dict[str, Any]:
        if payload.organization_id != auth.organization_id:
            raise ForbiddenError("Organization mismatch")
        data = payload.model_dump()
        data["updated_by_id"] = _user_uuid(auth)
        data["updated_by_name"] = auth.user_id
        row = await self.repo.upsert_availability(data)
        await self.repo.recompute_volunteer_count(auth.organization_id, payload.service_id)
        await self._audit(auth, action="save_availability", service_id=payload.service_id)
        await self.session.commit()
        return availability_to_dict(row)

    async def bulk_save_availability(
        self, auth: AuthContext, service_id: uuid.UUID, records: list[AvailabilityCreate]
    ) -> list[dict[str, Any]]:
        results = []
        for record in records:
            if record.organization_id != auth.organization_id:
                raise ForbiddenError("Organization mismatch")
            data = record.model_dump()
            data["service_id"] = service_id
            data["organization_id"] = auth.organization_id
            data["updated_by_id"] = _user_uuid(auth)
            data["updated_by_name"] = auth.user_id
            row = await self.repo.upsert_availability(data)
            results.append(availability_to_dict(row))
        await self.repo.recompute_volunteer_count(auth.organization_id, service_id)
        await self._audit(auth, action="bulk_save_availability", service_id=service_id)
        await self.session.commit()
        return results

    async def get_assignments(
        self, auth: AuthContext, service_id: uuid.UUID
    ) -> list[dict[str, Any]]:
        rows = await self.repo.list_assignments(auth.organization_id, service_id)
        return [assignment_to_dict(r) for r in rows]

    async def save_assignment(
        self, auth: AuthContext, payload: AssignmentCreate
    ) -> dict[str, Any]:
        assert_can_manage_services(auth, payload.organization_id)
        data = payload.model_dump()
        row = await self.repo.create_assignment(data)
        await self._audit(auth, action="create_assignment", service_id=payload.service_id)
        await self.session.commit()
        return assignment_to_dict(row)

    async def update_assignment(
        self, auth: AuthContext, assignment_id: uuid.UUID, payload: AssignmentUpdate
    ) -> dict[str, Any]:
        row = await self.repo.get_assignment(auth.organization_id, assignment_id)
        if not row:
            raise NotFoundError("Assignment not found")
        assert_can_manage_services(auth, auth.organization_id)
        row = await self.repo.update_assignment(row, payload.model_dump(exclude_none=True))
        await self._audit(auth, action="update_assignment", service_id=row.service_id)
        await self.session.commit()
        return assignment_to_dict(row)

    async def get_attendance(
        self, auth: AuthContext, service_id: uuid.UUID
    ) -> list[dict[str, Any]]:
        rows = await self.repo.list_attendance(auth.organization_id, service_id)
        return [attendance_to_dict(r) for r in rows]

    async def patch_attendance(
        self, auth: AuthContext, record_id: uuid.UUID, payload: AttendancePatch
    ) -> dict[str, Any]:
        row = await self.repo.get_attendance(auth.organization_id, record_id)
        if not row:
            raise NotFoundError("Attendance record not found")
        assert_can_manage_services(auth, auth.organization_id)
        row = await self.repo.upsert_attendance(
            {**payload.model_dump(exclude_none=True), **{
                "organization_id": auth.organization_id,
                "service_id": row.service_id,
                "user_id": row.user_id,
                "user_name": row.user_name,
                "team_id": row.team_id,
                "team_name": row.team_name,
                "role": row.role,
            }}
        )
        await self._audit(auth, action="patch_attendance", service_id=row.service_id)
        await self.session.commit()
        return attendance_to_dict(row)

    async def sync_attendance(
        self, auth: AuthContext, service_id: uuid.UUID
    ) -> list[dict[str, Any]]:
        assert_can_manage_services(auth, auth.organization_id)
        assignments = await self.repo.list_assignments(auth.organization_id, service_id)
        results = []
        for assignment in assignments:
            row = await self.repo.upsert_attendance(
                {
                    "organization_id": auth.organization_id,
                    "service_id": service_id,
                    "assignment_id": assignment.id,
                    "user_id": assignment.user_id,
                    "user_name": assignment.user_name,
                    "team_id": assignment.team_id,
                    "team_name": assignment.team_name,
                    "role": assignment.role,
                    "status": "pending",
                }
            )
            results.append(attendance_to_dict(row))
        await self._audit(auth, action="sync_attendance", service_id=service_id)
        await self.session.commit()
        return results

    async def dashboard(self, auth: AuthContext) -> dict[str, Any]:
        assert_can_manage_services(auth, auth.organization_id)
        return await self.repo.dashboard_stats(auth.organization_id)

    async def reports(self, auth: AuthContext) -> list[dict[str, Any]]:
        assert_can_view_reports(auth, auth.organization_id)
        return await self.repo.reports_by_team(auth.organization_id)

    async def history(self, auth: AuthContext, limit: int = 100) -> list[dict[str, Any]]:
        rows = await self.repo.list_audit_logs(auth.organization_id, limit=limit)
        return [audit_log_to_dict(r) for r in rows]

    async def grid(
        self,
        auth: AuthContext,
        week_start: date,
        team_ids: list[uuid.UUID] | None = None,
        user_ids: list[uuid.UUID] | None = None,
        group_by: str = "team",
    ) -> dict[str, Any]:
        week_end = week_start + timedelta(days=6)
        services = await self.repo.week_services(auth.organization_id, week_start, week_end)
        assignments = []
        for team_id in team_ids or [None]:
            rows = await self.repo.week_assignments(
                auth.organization_id, week_start, week_end, team_id=team_id
            )
            assignments.extend(rows)
        if user_ids:
            user_set = {str(u) for u in user_ids}
            assignments = [
                (a, s) for a, s in assignments if str(a.user_id) in user_set
            ]
        return {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "group_by": group_by,
            "services": [service_to_dict(s) for s in services],
            "assignments": [
                assignment_to_dict(a, service_date=s.date, service_time=s.time, service_name=s.name)
                for a, s in assignments
            ],
        }

    async def timesheets(
        self, auth: AuthContext, week_start: date, team_id: uuid.UUID | None = None
    ) -> dict[str, Any]:
        week_end = week_start + timedelta(days=6)
        rows = await self.repo.week_assignments(
            auth.organization_id, week_start, week_end, team_id=team_id
        )
        return {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "team_id": str(team_id) if team_id else None,
            "assignments": [
                assignment_to_dict(a, service_date=s.date, service_time=s.time, service_name=s.name)
                for a, s in rows
            ],
        }

    async def my_schedule(
        self, auth: AuthContext, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        user_id = _user_uuid(auth)
        assert_volunteer_own_record(auth, user_id)
        return await self.repo.my_schedule(auth.organization_id, user_id, start_date, end_date)

    async def my_rota(self, auth: AuthContext, target_date: date) -> dict[str, Any]:
        items = await self.my_schedule(auth, target_date, target_date)
        return {"date": target_date.isoformat(), "shifts": items}

    async def my_shifts(self, auth: AuthContext, target_date: date) -> list[dict[str, Any]]:
        return await self.my_schedule(auth, target_date, target_date)

    async def clock_sessions(
        self,
        auth: AuthContext,
        shift_date: date | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        user_id = _user_uuid(auth)
        rows = await self.repo.list_clock_sessions(
            auth.organization_id, user_id, shift_date=shift_date, status=status
        )
        return [clock_session_to_dict(r) for r in rows]

    async def clock_active(self, auth: AuthContext) -> dict[str, Any] | None:
        user_id = _user_uuid(auth)
        row = await self.repo.get_active_clock_session(auth.organization_id, user_id)
        return clock_session_to_dict(row) if row else None

    async def clock_in(self, auth: AuthContext, payload: ClockInCreate) -> dict[str, Any]:
        user_id = payload.user_id or _user_uuid(auth)
        assert_volunteer_own_record(auth, user_id)
        service = await self.repo.get_service(auth.organization_id, payload.service_id)
        if not service:
            raise NotFoundError("Service not found")
        assignment = await self.repo.find_assignment_for_clock(
            auth.organization_id, payload.service_id, user_id
        )
        if not assignment:
            raise ForbiddenError("No assignment found for this service")
        active = await self.repo.get_active_clock_session(auth.organization_id, user_id)
        if active:
            raise ConflictError("Already clocked in")

        now = datetime.now(timezone.utc)
        session = await self.repo.create_clock_session(
            {
                "organization_id": auth.organization_id,
                "user_id": user_id,
                "service_id": payload.service_id,
                "assignment_id": assignment.id,
                "shift_date": service.date,
                "service_name": service.name,
                "service_location": service.location,
                "role": assignment.role,
                "status": "clocked_in",
                "clock_in_time": now,
                "clock_in_lat": payload.clock_in_lat,
                "clock_in_lng": payload.clock_in_lng,
                "clock_in_accuracy": payload.clock_in_accuracy,
                "clock_in_label": payload.clock_in_label,
            }
        )
        attendance_status = self._attendance_status_for_clock_in(service, assignment, now)
        await self.repo.upsert_attendance(
            {
                "organization_id": auth.organization_id,
                "service_id": payload.service_id,
                "assignment_id": assignment.id,
                "user_id": user_id,
                "user_name": assignment.user_name,
                "team_id": assignment.team_id,
                "team_name": assignment.team_name,
                "role": assignment.role,
                "status": attendance_status,
                "check_in_time": now,
            }
        )
        await self._audit(auth, action="clock_in", service_id=payload.service_id)
        await self.session.commit()
        return clock_session_to_dict(session)

    async def clock_out(self, auth: AuthContext, payload: ClockOutCreate) -> dict[str, Any]:
        user_id = payload.user_id or _user_uuid(auth)
        assert_volunteer_own_record(auth, user_id)
        session = None
        if payload.session_id:
            session = await self.repo.get_clock_session(auth.organization_id, payload.session_id)
        if session is None:
            session = await self.repo.get_active_clock_session(auth.organization_id, user_id)
        if not session:
            raise NotFoundError("No active clock session")
        now = datetime.now(timezone.utc)
        session = await self.repo.update_clock_session(
            session,
            {
                "status": "completed",
                "clock_out_time": now,
                "clock_out_lat": payload.clock_out_lat,
                "clock_out_lng": payload.clock_out_lng,
                "clock_out_accuracy": payload.clock_out_accuracy,
                "clock_out_label": payload.clock_out_label,
            },
        )
        assignment = None
        if session.assignment_id:
            assignment = await self.repo.get_assignment(auth.organization_id, session.assignment_id)
        await self.repo.upsert_attendance(
            {
                "organization_id": auth.organization_id,
                "service_id": session.service_id,
                "assignment_id": session.assignment_id,
                "user_id": user_id,
                "user_name": assignment.user_name if assignment else auth.user_id,
                "team_id": assignment.team_id if assignment else user_id,
                "team_name": assignment.team_name if assignment else "",
                "role": session.role,
                "status": "present",
                "check_out_time": now,
            }
        )
        await self._audit(auth, action="clock_out", service_id=session.service_id)
        await self.session.commit()
        return clock_session_to_dict(session)

    def _attendance_status_for_clock_in(self, service, assignment, clock_in_time: datetime) -> str:
        arrival = assignment.arrival_time or service.time
        try:
            hour, minute = map(int, arrival.split(":"))
            scheduled = datetime.combine(service.date, datetime.min.time()).replace(
                hour=hour, minute=minute, tzinfo=timezone.utc
            )
            if clock_in_time > scheduled + timedelta(minutes=5):
                return "late"
        except (ValueError, AttributeError):
            pass
        return "present"
