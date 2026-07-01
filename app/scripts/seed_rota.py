#!/usr/bin/env python3
"""Seed Service Rota demo data for an organization."""

from __future__ import annotations

import argparse
import asyncio
import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_session_factory, init_sqlalchemy
from app.service_rota.models import (
    RotaAssignment,
    RotaAvailability,
    RotaClockSession,
    RotaService,
)


async def seed(organization_id: uuid.UUID) -> None:
    await init_sqlalchemy()
    factory = get_session_factory()
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    async with factory() as session:
        for i in range(10):
            svc_date = week_start + timedelta(days=i % 7)
            name = f"Sunday Service {svc_date.isoformat()}"
            existing = (
                await session.execute(
                    select(RotaService).where(
                        RotaService.organization_id == organization_id,
                        RotaService.name == name,
                        RotaService.date == svc_date,
                    )
                )
            ).scalar_one_or_none()
            if existing:
                service = existing
            else:
                service = RotaService(
                    organization_id=organization_id,
                    name=name,
                    date=svc_date,
                    time="10:00",
                    location="Main Sanctuary",
                    description="Weekly worship service",
                    status="published" if i % 3 else "draft",
                    volunteer_count=0,
                )
                session.add(service)
                await session.flush()

            for v in range(3):
                user_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"volunteer-{v}-{organization_id}")
                avail = (
                    await session.execute(
                        select(RotaAvailability).where(
                            RotaAvailability.organization_id == organization_id,
                            RotaAvailability.service_id == service.id,
                            RotaAvailability.user_id == user_id,
                        )
                    )
                ).scalar_one_or_none()
                if not avail:
                    session.add(
                        RotaAvailability(
                            organization_id=organization_id,
                            service_id=service.id,
                            user_id=user_id,
                            user_name=f"Volunteer {v + 1}",
                            team_name="Worship Team",
                            role="Musician",
                            availability="available" if v % 2 == 0 else "not_sure",
                        )
                    )

                team_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"team-worship-{organization_id}")
                assignment = (
                    await session.execute(
                        select(RotaAssignment).where(
                            RotaAssignment.organization_id == organization_id,
                            RotaAssignment.service_id == service.id,
                            RotaAssignment.user_id == user_id,
                            RotaAssignment.team_id == team_id,
                        )
                    )
                ).scalar_one_or_none()
                if not assignment and v < 2:
                    session.add(
                        RotaAssignment(
                            organization_id=organization_id,
                            service_id=service.id,
                            user_id=user_id,
                            user_name=f"Volunteer {v + 1}",
                            team_id=team_id,
                            team_name="Worship Team",
                            role="Musician",
                            status="confirmed",
                        )
                    )

        await session.commit()

        # Sample clock sessions for first volunteer on today
        user_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"volunteer-0-{organization_id}")
        service = (
            await session.execute(
                select(RotaService).where(
                    RotaService.organization_id == organization_id,
                    RotaService.date == today,
                )
            )
        ).scalar_one_or_none()
        if service:
            existing_clock = (
                await session.execute(
                    select(RotaClockSession).where(
                        RotaClockSession.organization_id == organization_id,
                        RotaClockSession.user_id == user_id,
                        RotaClockSession.service_id == service.id,
                    )
                )
            ).scalar_one_or_none()
            if not existing_clock:
                now = datetime.now(timezone.utc)
                session.add(
                    RotaClockSession(
                        organization_id=organization_id,
                        user_id=user_id,
                        service_id=service.id,
                        shift_date=today,
                        service_name=service.name,
                        service_location=service.location,
                        role="Musician",
                        status="completed",
                        clock_in_time=now - timedelta(hours=2),
                        clock_out_time=now - timedelta(hours=1),
                    )
                )
                await session.commit()

    print(f"Seeded service rota data for organization {organization_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Service Rota demo data")
    parser.add_argument("--organization-id", required=True, help="Organization UUID")
    args = parser.parse_args()
    if not settings.is_postgresql_configured():
        raise SystemExit("DATABASE_URL is not configured")
    asyncio.run(seed(uuid.UUID(args.organization_id)))


if __name__ == "__main__":
    main()
