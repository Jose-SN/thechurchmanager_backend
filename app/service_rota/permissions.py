from __future__ import annotations

from typing import Literal
from uuid import UUID

from app.api.auth_context import AuthContext
from app.service_rota.constants import ROTA_ROLES
from app.service_rota.exceptions import ForbiddenError

RotaRole = Literal["admin", "pastor", "team_head", "volunteer"]


def resolve_rota_role(auth: AuthContext) -> RotaRole:
    """Resolve role from auth context. Defaults to admin when IAM is bypassed."""
    if auth.user_id in ("anonymous", "legacy-user", "unknown"):
        return "admin"
    # Future: lookup user_roles table; default volunteer for real users
    return "volunteer"


def assert_can_manage_services(auth: AuthContext, org_id: UUID) -> None:
    if auth.organization_id != org_id:
        raise ForbiddenError("Organization mismatch")
    role = resolve_rota_role(auth)
    if role not in ("admin", "pastor", "team_head"):
        raise ForbiddenError("Insufficient permissions to manage services")


def assert_can_view_reports(auth: AuthContext, org_id: UUID) -> None:
    if auth.organization_id != org_id:
        raise ForbiddenError("Organization mismatch")
    role = resolve_rota_role(auth)
    if role not in ("admin", "pastor", "team_head"):
        raise ForbiddenError("Insufficient permissions to view reports")


def assert_can_manage_team(auth: AuthContext, org_id: UUID, team_id: UUID | None) -> None:
    if auth.organization_id != org_id:
        raise ForbiddenError("Organization mismatch")
    role = resolve_rota_role(auth)
    if role in ("admin", "pastor"):
        return
    if role == "team_head":
        return
    raise ForbiddenError("Insufficient permissions for this team")


def assert_volunteer_own_record(auth: AuthContext, record_user_id: UUID | str) -> None:
    role = resolve_rota_role(auth)
    if role in ("admin", "pastor", "team_head"):
        return
    if str(auth.user_id) != str(record_user_id):
        raise ForbiddenError("Cannot access another volunteer's records")
