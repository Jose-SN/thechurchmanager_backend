"""Checklist domain models mapped to existing PostgreSQL tables."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)


class ChecklistTemplate(Base):
    __tablename__ = "checklist_templates"
    __table_args__ = (
        Index("idx_checklist_templates_team_id", "team_id"),
        Index("idx_checklist_templates_organization_id", "organization_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    created_by: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )

    team: Mapped[Team] = relationship("Team", lazy="joined")
    items: Mapped[list[ChecklistItem]] = relationship(
        "ChecklistItem",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="ChecklistItem.order",
    )


class ChecklistItem(Base):
    __tablename__ = "checklist_items"
    __table_args__ = (Index("idx_checklist_items_template_id", "template_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("checklist_templates.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    order: Mapped[int] = mapped_column("order", Integer, nullable=False, server_default=text("0"))
    is_required: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )

    template: Mapped[ChecklistTemplate] = relationship("ChecklistTemplate", back_populates="items")


class ChecklistRecord(Base):
    __tablename__ = "checklist_records"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "template_id",
            "team_id",
            "date",
            name="uq_checklist_records_org_template_team_date",
        ),
        Index("idx_checklist_records_date", "date"),
        Index("idx_checklist_records_team", "team_id"),
        Index("idx_checklist_records_template", "template_id"),
        Index("idx_checklist_records_completed_by", "completed_by"),
        Index("idx_checklist_records_organization_id", "organization_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("checklist_templates.id"), nullable=False
    )
    team_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    completed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )

    template: Mapped[ChecklistTemplate] = relationship("ChecklistTemplate", lazy="joined")
    team: Mapped[Team] = relationship(
        "Team",
        primaryjoin="foreign(ChecklistRecord.team_id) == Team.id",
        lazy="joined",
        viewonly=True,
    )
    item_statuses: Mapped[list[ChecklistItemStatus]] = relationship(
        "ChecklistItemStatus",
        back_populates="record",
        cascade="all, delete-orphan",
    )


class ChecklistItemStatus(Base):
    __tablename__ = "checklist_item_statuses"
    __table_args__ = (
        UniqueConstraint(
            "checklist_record_id",
            "checklist_item_id",
            name="checklist_item_statuses_checklist_record_id_checklist_item_id_key",
        ),
        Index("idx_checklist_item_statuses_record", "checklist_record_id"),
        Index("idx_checklist_item_statuses_item", "checklist_item_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    checklist_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("checklist_records.id", ondelete="CASCADE"),
        nullable=False,
    )
    checklist_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("checklist_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    is_checked: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    issue_reported: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("NOW()")
    )

    record: Mapped[ChecklistRecord] = relationship("ChecklistRecord", back_populates="item_statuses")
