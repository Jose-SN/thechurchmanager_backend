"""Service Rota SQLAlchemy models."""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    Date,
    DateTime,
    Double,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ServiceStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    completed = "completed"
    cancelled = "cancelled"


class AvailabilityStatus(str, enum.Enum):
    available = "available"
    available_all_day = "available_all_day"
    unavailable = "unavailable"
    not_sure = "not_sure"


class AssignmentStatus(str, enum.Enum):
    assigned = "assigned"
    confirmed = "confirmed"
    declined = "declined"


class AttendanceStatus(str, enum.Enum):
    present = "present"
    absent = "absent"
    late = "late"
    replacement = "replacement"
    pending = "pending"


class ClockSessionStatus(str, enum.Enum):
    clocked_in = "clocked_in"
    completed = "completed"


class RotaService(Base):
    __tablename__ = "rota_services"
    __table_args__ = (
        Index("idx_rota_services_org_date", "organization_id", "date"),
        Index("idx_rota_services_org_status", "organization_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    time: Mapped[str] = mapped_column(String(10), nullable=False, server_default=text("'10:00'"))
    location: Mapped[str] = mapped_column(String(255), nullable=False, server_default=text("''"))
    description: Mapped[str] = mapped_column(Text, server_default=text("''"))
    languages: Mapped[list[Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[\"English\"]'::jsonb")
    )
    availability_options: Mapped[list[Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text(
            "'[\"available\",\"available_all_day\",\"unavailable\",\"not_sure\"]'::jsonb"
        ),
    )
    max_volunteers: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str] = mapped_column(Text, server_default=text("''"))
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'draft'")
    )
    team_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    volunteer_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    attendance_summary: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )

    availability: Mapped[list[RotaAvailability]] = relationship(
        "RotaAvailability", back_populates="service", cascade="all, delete-orphan"
    )
    assignments: Mapped[list[RotaAssignment]] = relationship(
        "RotaAssignment", back_populates="service", cascade="all, delete-orphan"
    )


class RotaAvailability(Base):
    __tablename__ = "rota_availability"
    __table_args__ = (
        UniqueConstraint("organization_id", "service_id", "user_id"),
        Index("idx_rota_availability_org_service", "organization_id", "service_id"),
        Index("idx_rota_availability_user", "organization_id", "user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rota_services.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    team_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    team_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str | None] = mapped_column(String(255))
    availability: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default=text("'not_sure'")
    )
    comment: Mapped[str] = mapped_column(Text, server_default=text("''"))
    comments: Mapped[list[Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    updated_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    updated_by_name: Mapped[str | None] = mapped_column(String(255))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )

    service: Mapped[RotaService] = relationship("RotaService", back_populates="availability")


class RotaAssignment(Base):
    __tablename__ = "rota_assignments"
    __table_args__ = (
        UniqueConstraint("organization_id", "service_id", "user_id", "team_id"),
        Index("idx_rota_assignments_service", "organization_id", "service_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rota_services.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_email: Mapped[str | None] = mapped_column(String(255))
    user_phone: Mapped[str | None] = mapped_column(String(50))
    team_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    team_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    arrival_time: Mapped[str | None] = mapped_column(String(10))
    notes: Mapped[str] = mapped_column(Text, server_default=text("''"))
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'assigned'")
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )

    service: Mapped[RotaService] = relationship("RotaService", back_populates="assignments")


class RotaAttendance(Base):
    __tablename__ = "rota_attendance"
    __table_args__ = (
        UniqueConstraint("organization_id", "service_id", "user_id"),
        Index("idx_rota_attendance_service", "organization_id", "service_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rota_services.id", ondelete="CASCADE"), nullable=False
    )
    assignment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rota_assignments.id", ondelete="SET NULL")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    team_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    team_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'pending'")
    )
    check_in_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    check_out_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str] = mapped_column(Text, server_default=text("''"))
    replacement_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    replacement_user_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )


class RotaClockSession(Base):
    __tablename__ = "rota_clock_sessions"
    __table_args__ = (
        Index("idx_rota_clock_user_date", "organization_id", "user_id", "shift_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rota_services.id", ondelete="CASCADE"), nullable=False
    )
    assignment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rota_assignments.id", ondelete="SET NULL")
    )
    shift_date: Mapped[date] = mapped_column(Date, nullable=False)
    service_name: Mapped[str] = mapped_column(String(255), nullable=False)
    service_location: Mapped[str] = mapped_column(String(255), server_default=text("''"))
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'clocked_in'")
    )
    clock_in_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    clock_in_lat: Mapped[float | None] = mapped_column(Double)
    clock_in_lng: Mapped[float | None] = mapped_column(Double)
    clock_in_accuracy: Mapped[float | None] = mapped_column(Double)
    clock_in_label: Mapped[str | None] = mapped_column(Text)
    clock_out_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    clock_out_lat: Mapped[float | None] = mapped_column(Double)
    clock_out_lng: Mapped[float | None] = mapped_column(Double)
    clock_out_accuracy: Mapped[float | None] = mapped_column(Double)
    clock_out_label: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )


class RotaAuditLog(Base):
    __tablename__ = "rota_audit_logs"
    __table_args__ = (
        Index("idx_rota_audit_org_created", "organization_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    service_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rota_services.id", ondelete="SET NULL")
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    field_name: Mapped[str | None] = mapped_column(String(255))
    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )
