from app.api.auth_context import AuthContext, get_auth_context, get_checklist_context
from app.core.config import settings
from fastapi import Header, Query, Request
from uuid import UUID


async def get_service_rota_context(
    request: Request,
    authorization: str | None = Header(None, alias="Authorization"),
    organization_id: UUID | None = Query(None),
    x_organization_id: UUID | None = Header(None, alias="X-Organization-Id"),
) -> AuthContext:
    """Service Rota auth — same IAM bypass pattern as checklist when disabled."""
    if not settings.IAM_AUTH_ENABLED:
        return await get_checklist_context(
            request=request,
            authorization=authorization,
            organization_id=organization_id,
            x_organization_id=x_organization_id,
        )
    return await get_auth_context(
        request=request,
        authorization=authorization,
        organization_id=organization_id,
        x_organization_id=x_organization_id,
    )
