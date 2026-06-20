from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChecklistItemInput(BaseModel):
    id: UUID | None = None
    title: str
    description: str | None = None
    order: int = 0
    is_required: bool = False


class ChecklistItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    template_id: UUID
    title: str
    description: str | None = None
    order: int
    is_required: bool


class ChecklistTemplateCreate(BaseModel):
    team_id: UUID
    name: str
    description: str | None = None
    is_active: bool = True
    items: list[ChecklistItemInput] = Field(default_factory=list)


class ChecklistTemplateUpdate(BaseModel):
    team_id: UUID | None = None
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None
    items: list[ChecklistItemInput] | None = None


class ChecklistTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    team_id: UUID
    team_name: str | None = None
    name: str
    description: str | None = None
    is_active: bool
    created_at: datetime
    created_by: str | None = None
    items: list[ChecklistItemOut] = Field(default_factory=list)


class ItemStatusInput(BaseModel):
    checklist_item_id: UUID
    is_checked: bool = False
    issue_reported: str | None = None


class ItemStatusOut(BaseModel):
    checklist_item_id: UUID
    is_checked: bool
    issue_reported: str | None = None


class ChecklistRecordCreate(BaseModel):
    template_id: UUID
    team_id: UUID
    date: date
    completed_by: str | None = None
    notes: str | None = None
    item_statuses: list[ItemStatusInput] = Field(default_factory=list)


class ChecklistRecordUpdate(BaseModel):
    completed_by: str | None = None
    notes: str | None = None
    item_statuses: list[ItemStatusInput] = Field(default_factory=list)


class ChecklistRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    template_id: UUID
    team_id: UUID
    date: date
    completed_by: str
    notes: str | None = None
    created_at: datetime
    template_name: str | None = None
    team_name: str | None = None
    item_statuses: list[ItemStatusOut] = Field(default_factory=list)


class DataResponse(BaseModel):
    data: Any
