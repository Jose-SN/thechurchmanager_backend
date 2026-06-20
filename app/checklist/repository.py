from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.checklist.models import (
    ChecklistItem,
    ChecklistItemStatus,
    ChecklistRecord,
    ChecklistTemplate,
    Team,
)


class ChecklistRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_team(self, team_id: uuid.UUID) -> Team | None:
        return await self.session.get(Team, team_id)

    async def get_template(
        self, template_id: uuid.UUID, organization_id: uuid.UUID
    ) -> ChecklistTemplate | None:
        stmt = (
            select(ChecklistTemplate)
            .options(selectinload(ChecklistTemplate.items), selectinload(ChecklistTemplate.team))
            .where(
                ChecklistTemplate.id == template_id,
                ChecklistTemplate.organization_id == organization_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_templates(
        self, organization_id: uuid.UUID, team_id: uuid.UUID | None = None
    ) -> list[ChecklistTemplate]:
        stmt = (
            select(ChecklistTemplate)
            .options(selectinload(ChecklistTemplate.items), selectinload(ChecklistTemplate.team))
            .where(ChecklistTemplate.organization_id == organization_id)
            .order_by(ChecklistTemplate.created_at.desc())
        )
        if team_id:
            stmt = stmt.where(ChecklistTemplate.team_id == team_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def create_template(
        self,
        *,
        organization_id: uuid.UUID,
        team_id: uuid.UUID,
        name: str,
        description: str | None,
        is_active: bool,
        created_by: str,
        items: list[dict],
    ) -> ChecklistTemplate:
        template = ChecklistTemplate(
            organization_id=organization_id,
            team_id=team_id,
            name=name,
            description=description,
            is_active=is_active,
            created_by=created_by,
        )
        self.session.add(template)
        await self.session.flush()
        for item in items:
            self.session.add(
                ChecklistItem(
                    template_id=template.id,
                    title=item["title"],
                    description=item.get("description"),
                    order=item.get("order", 0),
                    is_required=item.get("is_required", False),
                )
            )
        await self.session.flush()
        await self.session.refresh(template, attribute_names=["items", "team"])
        return template

    async def replace_template_items(
        self, template: ChecklistTemplate, items: list[dict]
    ) -> ChecklistTemplate:
        existing_by_id = {item.id: item for item in template.items}
        incoming_ids = {item["id"] for item in items if item.get("id")}

        for existing in list(template.items):
            if existing.id not in incoming_ids:
                await self.session.delete(existing)

        for item_data in items:
            item_id = item_data.get("id")
            if item_id and item_id in existing_by_id:
                row = existing_by_id[item_id]
                row.title = item_data["title"]
                row.description = item_data.get("description")
                row.order = item_data.get("order", 0)
                row.is_required = item_data.get("is_required", False)
            else:
                self.session.add(
                    ChecklistItem(
                        template_id=template.id,
                        title=item_data["title"],
                        description=item_data.get("description"),
                        order=item_data.get("order", 0),
                        is_required=item_data.get("is_required", False),
                    )
                )

        await self.session.flush()
        await self.session.refresh(template, attribute_names=["items", "team"])
        return template

    async def delete_template(self, template: ChecklistTemplate) -> None:
        await self.session.delete(template)

    async def get_record(
        self, record_id: uuid.UUID, organization_id: uuid.UUID
    ) -> ChecklistRecord | None:
        stmt = (
            select(ChecklistRecord)
            .options(
                selectinload(ChecklistRecord.item_statuses),
                selectinload(ChecklistRecord.template),
                selectinload(ChecklistRecord.team),
            )
            .where(
                ChecklistRecord.id == record_id,
                ChecklistRecord.organization_id == organization_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_record_by_unique(
        self,
        organization_id: uuid.UUID,
        template_id: uuid.UUID,
        team_id: uuid.UUID,
        record_date: date,
    ) -> ChecklistRecord | None:
        stmt = select(ChecklistRecord).where(
            ChecklistRecord.organization_id == organization_id,
            ChecklistRecord.template_id == template_id,
            ChecklistRecord.team_id == team_id,
            ChecklistRecord.date == record_date,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_records(
        self,
        organization_id: uuid.UUID,
        *,
        record_date: date | None = None,
        team_id: uuid.UUID | None = None,
        template_id: uuid.UUID | None = None,
        completed_by: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[ChecklistRecord], int]:
        filters = [ChecklistRecord.organization_id == organization_id]
        if record_date:
            filters.append(ChecklistRecord.date == record_date)
        if team_id:
            filters.append(ChecklistRecord.team_id == team_id)
        if template_id:
            filters.append(ChecklistRecord.template_id == template_id)
        if completed_by:
            filters.append(ChecklistRecord.completed_by == completed_by)
        if start_date:
            filters.append(ChecklistRecord.date >= start_date)
        if end_date:
            filters.append(ChecklistRecord.date <= end_date)

        count_stmt = select(func.count()).select_from(ChecklistRecord).where(and_(*filters))
        total = (await self.session.execute(count_stmt)).scalar_one()

        offset = max(page - 1, 0) * limit
        stmt = (
            select(ChecklistRecord)
            .options(
                selectinload(ChecklistRecord.item_statuses),
                selectinload(ChecklistRecord.template),
                selectinload(ChecklistRecord.team),
            )
            .where(and_(*filters))
            .order_by(ChecklistRecord.date.desc(), ChecklistRecord.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all()), total

    async def create_record(
        self,
        *,
        organization_id: uuid.UUID,
        template_id: uuid.UUID,
        team_id: uuid.UUID,
        record_date: date,
        completed_by: str,
        notes: str | None,
        template_items: list[ChecklistItem],
        item_statuses: list[dict],
    ) -> ChecklistRecord:
        record = ChecklistRecord(
            organization_id=organization_id,
            template_id=template_id,
            team_id=team_id,
            date=record_date,
            completed_by=completed_by,
            notes=notes,
        )
        self.session.add(record)
        await self.session.flush()

        status_by_item = {s["checklist_item_id"]: s for s in item_statuses}
        for item in template_items:
            payload = status_by_item.get(item.id, {})
            self.session.add(
                ChecklistItemStatus(
                    checklist_record_id=record.id,
                    checklist_item_id=item.id,
                    is_checked=payload.get("is_checked", False),
                    issue_reported=payload.get("issue_reported"),
                )
            )

        await self.session.flush()
        await self.session.refresh(
            record,
            attribute_names=["item_statuses", "template", "team"],
        )
        return record

    async def upsert_item_statuses(
        self, record: ChecklistRecord, item_statuses: list[dict]
    ) -> ChecklistRecord:
        existing = {s.checklist_item_id: s for s in record.item_statuses}
        for payload in item_statuses:
            item_id = payload["checklist_item_id"]
            if item_id in existing:
                row = existing[item_id]
                row.is_checked = payload.get("is_checked", False)
                if "issue_reported" in payload:
                    row.issue_reported = payload.get("issue_reported")
            else:
                self.session.add(
                    ChecklistItemStatus(
                        checklist_record_id=record.id,
                        checklist_item_id=item_id,
                        is_checked=payload.get("is_checked", False),
                        issue_reported=payload.get("issue_reported"),
                    )
                )
        await self.session.flush()
        await self.session.refresh(record, attribute_names=["item_statuses", "template", "team"])
        return record

    async def delete_statuses_not_in(
        self, record_id: uuid.UUID, keep_item_ids: set[uuid.UUID]
    ) -> None:
        if not keep_item_ids:
            return
        stmt = delete(ChecklistItemStatus).where(
            ChecklistItemStatus.checklist_record_id == record_id,
            ChecklistItemStatus.checklist_item_id.not_in(keep_item_ids),
        )
        await self.session.execute(stmt)
