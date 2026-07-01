from __future__ import annotations

from datetime import date as DateType, datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RotaServiceCreate(BaseModel):
    organization_id: UUID
    name: str
    date: DateType
    time: str = "10:00"
    location: str = ""
    description: str = ""
    languages: list[str] = Field(default_factory=lambda: ["English"])
    availability_options: list[str] | None = None
    max_volunteers: int | None = None
    notes: str = ""
    status: str = "draft"
    team_id: UUID | None = None


class RotaServiceUpdate(BaseModel):
    name: Optional[str] = None
    date: Optional[DateType] = None
    time: str | None = None
    location: str | None = None
    description: str | None = None
    languages: list[str] | None = None
    availability_options: list[str] | None = None
    max_volunteers: int | None = None
    notes: str | None = None
    team_id: UUID | None = None


class AvailabilityCreate(BaseModel):
    organization_id: UUID
    service_id: UUID
    user_id: UUID
    user_name: str
    team_id: UUID | None = None
    team_name: str | None = None
    role: str | None = None
    availability: str = "not_sure"
    comment: str = ""
    comments: list[Any] = Field(default_factory=list)


class AvailabilityBulkCreate(BaseModel):
    organization_id: UUID
    service_id: UUID
    records: list[AvailabilityCreate]


class AssignmentCreate(BaseModel):
    organization_id: UUID
    service_id: UUID
    user_id: UUID
    user_name: str
    user_email: str | None = None
    user_phone: str | None = None
    team_id: UUID
    team_name: str
    role: str
    arrival_time: str | None = None
    notes: str = ""
    status: str = "assigned"
    sort_order: int = 0


class AssignmentUpdate(BaseModel):
    user_name: str | None = None
    user_email: str | None = None
    user_phone: str | None = None
    team_id: UUID | None = None
    team_name: str | None = None
    role: str | None = None
    arrival_time: str | None = None
    notes: str | None = None
    status: str | None = None
    sort_order: int | None = None


class AttendancePatch(BaseModel):
    status: str | None = None
    check_in_time: datetime | None = None
    check_out_time: datetime | None = None
    notes: str | None = None
    replacement_user_id: UUID | None = None
    replacement_user_name: str | None = None


class ClockInCreate(BaseModel):
    organization_id: UUID
    service_id: UUID
    user_id: UUID | None = None
    user_name: str | None = None
    clock_in_lat: float | None = None
    clock_in_lng: float | None = None
    clock_in_accuracy: float | None = None
    clock_in_label: str | None = None


class ClockOutCreate(BaseModel):
    organization_id: UUID
    session_id: UUID | None = None
    service_id: UUID | None = None
    user_id: UUID | None = None
    clock_out_lat: float | None = None
    clock_out_lng: float | None = None
    clock_out_accuracy: float | None = None
    clock_out_label: str | None = None


class RotaServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    name: str
    date: DateType
    time: str
    location: str
    description: str
    languages: list[Any]
    availability_options: list[Any]
    max_volunteers: int | None
    notes: str
    status: str
    team_id: str | None
    volunteer_count: int
    attendance_summary: dict | None
    created_at: datetime
    updated_at: datetime
