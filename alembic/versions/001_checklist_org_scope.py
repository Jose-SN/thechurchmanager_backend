"""Add organization_id to checklist tables and update record uniqueness.

Revision ID: 001_checklist_org_scope
Revises:
Create Date: 2026-06-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_checklist_org_scope"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- checklist_templates.organization_id ---
    op.add_column(
        "checklist_templates",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.execute(
        """
        UPDATE checklist_templates ct
        SET organization_id = t.organization_id
        FROM teams t
        WHERE ct.team_id = t.id AND ct.organization_id IS NULL
        """
    )
    op.alter_column("checklist_templates", "organization_id", nullable=False)
    op.create_index(
        "idx_checklist_templates_organization_id",
        "checklist_templates",
        ["organization_id"],
    )

    # --- checklist_records.organization_id ---
    op.add_column(
        "checklist_records",
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.execute(
        """
        UPDATE checklist_records cr
        SET organization_id = ct.organization_id
        FROM checklist_templates ct
        WHERE cr.template_id = ct.id AND cr.organization_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE checklist_records cr
        SET organization_id = t.organization_id
        FROM teams t
        WHERE cr.team_id = t.id AND cr.organization_id IS NULL
        """
    )
    op.alter_column("checklist_records", "organization_id", nullable=False)
    op.create_index(
        "idx_checklist_records_organization_id",
        "checklist_records",
        ["organization_id"],
    )

    # Replace unique constraint on records
    op.execute(
        """
        DO $$
        DECLARE
            constraint_name text;
        BEGIN
            SELECT con.conname INTO constraint_name
            FROM pg_constraint con
            JOIN pg_class rel ON rel.oid = con.conrelid
            WHERE rel.relname = 'checklist_records'
              AND con.contype = 'u'
              AND pg_get_constraintdef(con.oid) LIKE '%template_id%'
              AND pg_get_constraintdef(con.oid) LIKE '%team_id%'
              AND pg_get_constraintdef(con.oid) LIKE '%date%'
              AND pg_get_constraintdef(con.oid) NOT LIKE '%organization_id%'
            LIMIT 1;
            IF constraint_name IS NOT NULL THEN
                EXECUTE format('ALTER TABLE checklist_records DROP CONSTRAINT %I', constraint_name);
            END IF;
        END $$;
        """
    )
    op.create_unique_constraint(
        "uq_checklist_records_org_template_team_date",
        "checklist_records",
        ["organization_id", "template_id", "team_id", "date"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_checklist_records_org_template_team_date",
        "checklist_records",
        type_="unique",
    )
    op.create_unique_constraint(
        "checklist_records_template_id_team_id_date_key",
        "checklist_records",
        ["template_id", "team_id", "date"],
    )
    op.drop_index("idx_checklist_records_organization_id", table_name="checklist_records")
    op.drop_column("checklist_records", "organization_id")
    op.drop_index("idx_checklist_templates_organization_id", table_name="checklist_templates")
    op.drop_column("checklist_templates", "organization_id")
