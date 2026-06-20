from __future__ import annotations

import logging
from datetime import date
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth_context import AuthContext
from app.checklist.constants import DEFAULT_SVC_META
from app.checklist.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from app.checklist.models import ChecklistRecord, ChecklistTemplate
from app.checklist.repository import ChecklistRepository
from app.checklist.schemas import (
    ChecklistItemOut,
    ChecklistRecordCreate,
    ChecklistRecordOut,
    ChecklistRecordUpdate,
    ChecklistTemplateCreate,
    ChecklistTemplateOut,
    ChecklistTemplateUpdate,
    ItemStatusOut,
)

logger = logging.getLogger(__name__)


class ChecklistService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ChecklistRepository(session)

    async def _commit(self) -> None:
        await self.session.commit()

    async def _assert_team_in_org(self, team_id: UUID, organization_id: UUID) -> None:
        team = await self.repo.get_team(team_id)
        if team is None:
            raise NotFoundError("Team not found")
        if team.organization_id != organization_id:
            raise ForbiddenError("Team does not belong to your organization")

    def _template_to_out(self, template: ChecklistTemplate) -> ChecklistTemplateOut:
        items = sorted(template.items, key=lambda i: i.order)
        return ChecklistTemplateOut(
            id=template.id,
            team_id=template.team_id,
            team_name=template.team.name if template.team else None,
            name=template.name,
            description=template.description,
            is_active=template.is_active,
            created_at=template.created_at,
            created_by=template.created_by,
            items=[
                ChecklistItemOut(
                    id=item.id,
                    template_id=item.template_id,
                    title=item.title,
                    description=item.description,
                    order=item.order,
                    is_required=item.is_required,
                )
                for item in items
            ],
        )

    def _record_to_out(self, record: ChecklistRecord) -> ChecklistRecordOut:
        return ChecklistRecordOut(
            id=record.id,
            template_id=record.template_id,
            team_id=record.team_id,
            date=record.date,
            completed_by=record.completed_by,
            notes=record.notes,
            created_at=record.created_at,
            template_name=record.template.name if record.template else None,
            team_name=record.team.name if record.team else None,
            item_statuses=[
                ItemStatusOut(
                    checklist_item_id=status.checklist_item_id,
                    is_checked=status.is_checked,
                    issue_reported=status.issue_reported,
                )
                for status in record.item_statuses
            ],
        )

    async def list_templates(
        self, auth: AuthContext, team_id: UUID | None = None
    ) -> list[ChecklistTemplateOut]:
        if team_id:
            await self._assert_team_in_org(team_id, auth.organization_id)
        templates = await self.repo.list_templates(auth.organization_id, team_id)
        return [self._template_to_out(t) for t in templates]

    async def create_template(
        self, auth: AuthContext, payload: ChecklistTemplateCreate
    ) -> ChecklistTemplateOut:
        await self._assert_team_in_org(payload.team_id, auth.organization_id)
        if not payload.name.strip():
            raise ValidationError("name is required")

        items = [
            {
                "title": item.title.strip(),
                "description": item.description,
                "order": item.order,
                "is_required": item.is_required,
            }
            for item in payload.items
            if item.title.strip()
        ]

        template = await self.repo.create_template(
            organization_id=auth.organization_id,
            team_id=payload.team_id,
            name=payload.name.strip(),
            description=payload.description,
            is_active=payload.is_active,
            created_by=auth.user_id,
            items=items,
        )
        logger.info(
            "Created checklist template %s for org %s",
            template.id,
            auth.organization_id,
        )
        await self._commit()
        return self._template_to_out(template)

    async def update_template(
        self, auth: AuthContext, template_id: UUID, payload: ChecklistTemplateUpdate
    ) -> ChecklistTemplateOut:
        template = await self.repo.get_template(template_id, auth.organization_id)
        if template is None:
            raise NotFoundError("Checklist template not found")

        if payload.team_id:
            await self._assert_team_in_org(payload.team_id, auth.organization_id)
            template.team_id = payload.team_id
        if payload.name is not None:
            if not payload.name.strip():
                raise ValidationError("name is required")
            template.name = payload.name.strip()
        if payload.description is not None:
            template.description = payload.description
        if payload.is_active is not None:
            template.is_active = payload.is_active

        if payload.items is not None:
            items = [
                {
                    "id": item.id,
                    "title": item.title.strip(),
                    "description": item.description,
                    "order": item.order,
                    "is_required": item.is_required,
                }
                for item in payload.items
                if item.title.strip()
            ]
            template = await self.repo.replace_template_items(template, items)

        logger.info("Updated checklist template %s", template_id)
        await self._commit()
        return self._template_to_out(template)

    async def delete_template(self, auth: AuthContext, template_id: UUID) -> None:
        template = await self.repo.get_template(template_id, auth.organization_id)
        if template is None:
            raise NotFoundError("Checklist template not found")
        await self.repo.delete_template(template)
        await self._commit()
        logger.info("Deleted checklist template %s", template_id)

    async def list_records(
        self,
        auth: AuthContext,
        *,
        record_date: date | None = None,
        team_id: UUID | None = None,
        template_id: UUID | None = None,
        completed_by: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> dict:
        if team_id:
            await self._assert_team_in_org(team_id, auth.organization_id)
        if template_id:
            template = await self.repo.get_template(template_id, auth.organization_id)
            if template is None:
                raise NotFoundError("Checklist template not found")

        records, total = await self.repo.list_records(
            auth.organization_id,
            record_date=record_date,
            team_id=team_id,
            template_id=template_id,
            completed_by=completed_by,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit,
        )
        return {
            "data": [self._record_to_out(r) for r in records],
            "total": total,
            "page": page,
            "limit": limit,
        }

    async def get_record(self, auth: AuthContext, record_id: UUID) -> ChecklistRecordOut:
        record = await self.repo.get_record(record_id, auth.organization_id)
        if record is None:
            raise NotFoundError("Checklist record not found")
        return self._record_to_out(record)

    async def create_record(
        self, auth: AuthContext, payload: ChecklistRecordCreate
    ) -> ChecklistRecordOut:
        template = await self.repo.get_template(payload.template_id, auth.organization_id)
        if template is None:
            raise NotFoundError("Checklist template not found")
        await self._assert_team_in_org(payload.team_id, auth.organization_id)
        if template.team_id != payload.team_id:
            raise ValidationError("team_id does not match template team")

        existing = await self.repo.find_record_by_unique(
            auth.organization_id,
            payload.template_id,
            payload.team_id,
            payload.date,
        )
        if existing:
            raise ConflictError(
                "A checklist record already exists for this organization, template, team, and date"
            )

        notes = payload.notes if payload.notes is not None else DEFAULT_SVC_META
        completed_by = payload.completed_by or auth.user_id

        item_statuses = [
            {
                "checklist_item_id": s.checklist_item_id,
                "is_checked": s.is_checked,
                "issue_reported": s.issue_reported,
            }
            for s in payload.item_statuses
        ]

        try:
            record = await self.repo.create_record(
                organization_id=auth.organization_id,
                template_id=payload.template_id,
                team_id=payload.team_id,
                record_date=payload.date,
                completed_by=completed_by,
                notes=notes,
                template_items=template.items,
                item_statuses=item_statuses,
            )
        except IntegrityError as exc:
            logger.warning("Duplicate checklist record: %s", exc)
            raise ConflictError(
                "A checklist record already exists for this organization, template, team, and date"
            ) from exc

        logger.info("Created checklist record %s", record.id)
        await self._commit()
        return self._record_to_out(record)

    async def update_record(
        self, auth: AuthContext, record_id: UUID, payload: ChecklistRecordUpdate
    ) -> ChecklistRecordOut:
        record = await self.repo.get_record(record_id, auth.organization_id)
        if record is None:
            raise NotFoundError("Checklist record not found")

        if payload.completed_by is not None:
            record.completed_by = payload.completed_by
        if payload.notes is not None:
            record.notes = payload.notes

        if payload.item_statuses:
            statuses = [
                {
                    "checklist_item_id": s.checklist_item_id,
                    "is_checked": s.is_checked,
                    "issue_reported": s.issue_reported,
                }
                for s in payload.item_statuses
            ]
            record = await self.repo.upsert_item_statuses(record, statuses)

        logger.info("Updated checklist record %s", record_id)
        await self._commit()
        return self._record_to_out(record)
