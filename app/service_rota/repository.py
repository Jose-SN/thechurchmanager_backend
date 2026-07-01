from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.service_rota.models import (
    RotaAssignment,
    RotaAttendance,
    RotaAuditLog,
    RotaAvailability,
    RotaClockSession,
    RotaService,
)


class RotaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_service(self, org_id: uuid.UUID, service_id: uuid.UUID) -> RotaService | None:
        stmt = select(RotaService).where(
            RotaService.id == service_id,
            RotaService.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_services(
        self,
        org_id: uuid.UUID,
        *,
        status: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        search: str | None = None,
        sort: str = "date",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[RotaService], int]:
        filters = [RotaService.organization_id == org_id]
        if status:
            filters.append(RotaService.status == status)
        if start_date:
            filters.append(RotaService.date >= start_date)
        if end_date:
            filters.append(RotaService.date <= end_date)
        if search:
            pattern = f"%{search}%"
            filters.append(or_(RotaService.name.ilike(pattern), RotaService.location.ilike(pattern)))

        count_stmt = select(func.count()).select_from(RotaService).where(*filters)
        total = (await self.session.execute(count_stmt)).scalar_one()

        sort_col = getattr(RotaService, sort, RotaService.date)
        order_clause = sort_col.asc() if order.lower() != "desc" else sort_col.desc()
        offset = max(page - 1, 0) * limit

        stmt = (
            select(RotaService)
            .where(*filters)
            .order_by(order_clause)
            .offset(offset)
            .limit(limit)
        )
        rows = (await self.session.execute(stmt)).scalars().all()
        return list(rows), total

    async def create_service(self, data: dict[str, Any]) -> RotaService:
        row = RotaService(**data)
        self.session.add(row)
        await self.session.flush()
        return row

    async def update_service(self, row: RotaService, data: dict[str, Any]) -> RotaService:
        for key, value in data.items():
            if value is not None and hasattr(row, key):
                setattr(row, key, value)
        await self.session.flush()
        return row

    async def delete_service(self, org_id: uuid.UUID, service_id: uuid.UUID) -> bool:
        stmt = delete(RotaService).where(
            RotaService.id == service_id,
            RotaService.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def set_service_status(
        self, org_id: uuid.UUID, service_id: uuid.UUID, status: str
    ) -> RotaService | None:
        row = await self.get_service(org_id, service_id)
        if not row:
            return None
        row.status = status
        await self.session.flush()
        return row

    async def recompute_volunteer_count(self, org_id: uuid.UUID, service_id: uuid.UUID) -> int:
        stmt = select(func.count()).select_from(RotaAvailability).where(
            RotaAvailability.organization_id == org_id,
            RotaAvailability.service_id == service_id,
            RotaAvailability.availability.in_(("available", "available_all_day")),
        )
        count = (await self.session.execute(stmt)).scalar_one()
        await self.session.execute(
            update(RotaService)
            .where(RotaService.id == service_id, RotaService.organization_id == org_id)
            .values(volunteer_count=count)
        )
        return count

    async def list_availability(
        self, org_id: uuid.UUID, service_id: uuid.UUID | None = None
    ) -> list[RotaAvailability]:
        filters = [RotaAvailability.organization_id == org_id]
        if service_id:
            filters.append(RotaAvailability.service_id == service_id)
        stmt = select(RotaAvailability).where(*filters).order_by(RotaAvailability.user_name)
        return list((await self.session.execute(stmt)).scalars().all())

    async def upsert_availability(self, data: dict[str, Any]) -> RotaAvailability:
        stmt = select(RotaAvailability).where(
            RotaAvailability.organization_id == data["organization_id"],
            RotaAvailability.service_id == data["service_id"],
            RotaAvailability.user_id == data["user_id"],
        )
        existing = (await self.session.execute(stmt)).scalar_one_or_none()
        if existing:
            for key, value in data.items():
                if key not in ("organization_id", "service_id", "user_id") and value is not None:
                    setattr(existing, key, value)
            await self.session.flush()
            return existing
        row = RotaAvailability(**data)
        self.session.add(row)
        await self.session.flush()
        return row

    async def list_assignments(
        self, org_id: uuid.UUID, service_id: uuid.UUID | None = None
    ) -> list[RotaAssignment]:
        filters = [RotaAssignment.organization_id == org_id]
        if service_id:
            filters.append(RotaAssignment.service_id == service_id)
        stmt = select(RotaAssignment).where(*filters).order_by(RotaAssignment.sort_order)
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_assignment(
        self, org_id: uuid.UUID, assignment_id: uuid.UUID
    ) -> RotaAssignment | None:
        stmt = select(RotaAssignment).where(
            RotaAssignment.id == assignment_id,
            RotaAssignment.organization_id == org_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def create_assignment(self, data: dict[str, Any]) -> RotaAssignment:
        row = RotaAssignment(**data)
        self.session.add(row)
        await self.session.flush()
        return row

    async def update_assignment(
        self, row: RotaAssignment, data: dict[str, Any]
    ) -> RotaAssignment:
        for key, value in data.items():
            if value is not None:
                setattr(row, key, value)
        await self.session.flush()
        return row

    async def list_attendance(
        self, org_id: uuid.UUID, service_id: uuid.UUID
    ) -> list[RotaAttendance]:
        stmt = select(RotaAttendance).where(
            RotaAttendance.organization_id == org_id,
            RotaAttendance.service_id == service_id,
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_attendance(
        self, org_id: uuid.UUID, record_id: uuid.UUID
    ) -> RotaAttendance | None:
        stmt = select(RotaAttendance).where(
            RotaAttendance.id == record_id,
            RotaAttendance.organization_id == org_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def upsert_attendance(self, data: dict[str, Any]) -> RotaAttendance:
        stmt = select(RotaAttendance).where(
            RotaAttendance.organization_id == data["organization_id"],
            RotaAttendance.service_id == data["service_id"],
            RotaAttendance.user_id == data["user_id"],
        )
        existing = (await self.session.execute(stmt)).scalar_one_or_none()
        if existing:
            for key, value in data.items():
                if key not in ("organization_id", "service_id", "user_id") and value is not None:
                    setattr(existing, key, value)
            await self.session.flush()
            return existing
        row = RotaAttendance(**data)
        self.session.add(row)
        await self.session.flush()
        return row

    async def list_clock_sessions(
        self,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        *,
        shift_date: date | None = None,
        status: str | None = None,
    ) -> list[RotaClockSession]:
        filters = [
            RotaClockSession.organization_id == org_id,
            RotaClockSession.user_id == user_id,
        ]
        if shift_date:
            filters.append(RotaClockSession.shift_date == shift_date)
        if status:
            filters.append(RotaClockSession.status == status)
        stmt = select(RotaClockSession).where(*filters).order_by(RotaClockSession.clock_in_time.desc())
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_active_clock_session(
        self, org_id: uuid.UUID, user_id: uuid.UUID
    ) -> RotaClockSession | None:
        stmt = select(RotaClockSession).where(
            RotaClockSession.organization_id == org_id,
            RotaClockSession.user_id == user_id,
            RotaClockSession.status == "clocked_in",
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_clock_session(
        self, org_id: uuid.UUID, session_id: uuid.UUID
    ) -> RotaClockSession | None:
        stmt = select(RotaClockSession).where(
            RotaClockSession.id == session_id,
            RotaClockSession.organization_id == org_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def create_clock_session(self, data: dict[str, Any]) -> RotaClockSession:
        row = RotaClockSession(**data)
        self.session.add(row)
        await self.session.flush()
        return row

    async def update_clock_session(
        self, row: RotaClockSession, data: dict[str, Any]
    ) -> RotaClockSession:
        for key, value in data.items():
            if value is not None:
                setattr(row, key, value)
        await self.session.flush()
        return row

    async def write_audit_log(self, data: dict[str, Any]) -> RotaAuditLog:
        row = RotaAuditLog(**data)
        self.session.add(row)
        await self.session.flush()
        return row

    async def list_audit_logs(
        self, org_id: uuid.UUID, *, limit: int = 100
    ) -> list[RotaAuditLog]:
        stmt = (
            select(RotaAuditLog)
            .where(RotaAuditLog.organization_id == org_id)
            .order_by(RotaAuditLog.created_at.desc())
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def my_schedule(
        self,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        stmt = (
            select(RotaAssignment, RotaService)
            .join(RotaService, RotaService.id == RotaAssignment.service_id)
            .where(
                RotaAssignment.organization_id == org_id,
                RotaAssignment.user_id == user_id,
                RotaAssignment.status.in_(("assigned", "confirmed")),
                RotaService.status == "published",
                RotaService.date >= start_date,
                RotaService.date <= end_date,
            )
            .order_by(RotaService.date, RotaAssignment.arrival_time)
        )
        rows = (await self.session.execute(stmt)).all()
        result = []
        for assignment, service in rows:
            result.append(
                {
                    "id": str(assignment.id),
                    "service_id": str(assignment.service_id),
                    "date": service.date.isoformat(),
                    "start_time": assignment.arrival_time or service.time,
                    "role": assignment.role,
                    "service_name": service.name,
                    "location": service.location,
                    "team_name": assignment.team_name,
                    "status": assignment.status,
                }
            )
        return result

    async def week_services(
        self, org_id: uuid.UUID, week_start: date, week_end: date
    ) -> list[RotaService]:
        stmt = select(RotaService).where(
            RotaService.organization_id == org_id,
            RotaService.status == "published",
            RotaService.date >= week_start,
            RotaService.date <= week_end,
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def week_assignments(
        self,
        org_id: uuid.UUID,
        week_start: date,
        week_end: date,
        team_id: uuid.UUID | None = None,
    ) -> list[tuple[RotaAssignment, RotaService]]:
        filters = [
            RotaAssignment.organization_id == org_id,
            RotaService.date >= week_start,
            RotaService.date <= week_end,
        ]
        if team_id:
            filters.append(RotaAssignment.team_id == team_id)
        stmt = (
            select(RotaAssignment, RotaService)
            .join(RotaService, RotaService.id == RotaAssignment.service_id)
            .where(*filters)
        )
        return list((await self.session.execute(stmt)).all())

    async def dashboard_stats(self, org_id: uuid.UUID) -> dict[str, Any]:
        svc_stmt = select(
            func.count().filter(
                and_(RotaService.date >= date.today(), RotaService.status.notin_(("cancelled", "completed")))
            ).label("upcoming_count"),
            func.count().filter(RotaService.date == date.today()).label("today_count"),
        ).where(RotaService.organization_id == org_id)
        svc_row = (await self.session.execute(svc_stmt)).one()

        av_stmt = select(
            func.count().filter(RotaAvailability.availability == "not_sure").label("waiting_availability"),
            func.count()
            .filter(RotaAvailability.availability.in_(("available", "available_all_day")))
            .label("confirmed_volunteers"),
            func.count().filter(RotaAvailability.availability == "unavailable").label("unavailable_volunteers"),
            func.count(func.distinct(RotaAvailability.user_id)).label("total_volunteers"),
        ).where(RotaAvailability.organization_id == org_id)
        av_row = (await self.session.execute(av_stmt)).one()

        return {
            "upcoming_count": svc_row.upcoming_count or 0,
            "today_count": svc_row.today_count or 0,
            "waiting_availability": av_row.waiting_availability or 0,
            "confirmed_volunteers": av_row.confirmed_volunteers or 0,
            "unavailable_volunteers": av_row.unavailable_volunteers or 0,
            "total_volunteers": av_row.total_volunteers or 0,
        }

    async def reports_by_team(self, org_id: uuid.UUID) -> list[dict[str, Any]]:
        stmt = (
            select(
                RotaAvailability.team_id,
                RotaAvailability.team_name,
                func.count().filter(
                    RotaAvailability.availability.in_(("available", "available_all_day"))
                ).label("available"),
                func.count().filter(RotaAvailability.availability == "unavailable").label("unavailable"),
                func.count().filter(RotaAvailability.availability == "not_sure").label("not_sure"),
                func.count().label("total"),
            )
            .where(RotaAvailability.organization_id == org_id)
            .group_by(RotaAvailability.team_id, RotaAvailability.team_name)
        )
        rows = (await self.session.execute(stmt)).all()
        return [
            {
                "team_id": str(r.team_id) if r.team_id else None,
                "team_name": r.team_name,
                "available": r.available,
                "unavailable": r.unavailable,
                "not_sure": r.not_sure,
                "total": r.total,
            }
            for r in rows
        ]

    async def find_assignment_for_clock(
        self, org_id: uuid.UUID, service_id: uuid.UUID, user_id: uuid.UUID
    ) -> RotaAssignment | None:
        stmt = select(RotaAssignment).where(
            RotaAssignment.organization_id == org_id,
            RotaAssignment.service_id == service_id,
            RotaAssignment.user_id == user_id,
            RotaAssignment.status.in_(("assigned", "confirmed")),
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()
