"""
Shared request auth for multi-tenant API routes.

Matches the pattern used by /team/get: frontend sends Authorization Bearer token
(Supabase session, app JWT, or legacy token) plus organization_id via query/header.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import Header, HTTPException, Query, Request, status
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)

LEGACY_APP_TOKEN = "thechurchmanager"
ORG_CLAIM_KEYS = ("organization_id", "organizationId", "org_id", "orgId")
USER_CLAIM_KEYS = ("user_id", "sub", "id", "userId", "email")
METADATA_KEYS = ("user_metadata", "app_metadata", "metadata")


class AuthContext(BaseModel):
    organization_id: UUID
    user_id: str
    token: str


def _parse_uuid(value) -> UUID | None:
    if value is None:
        return None
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return None


def _find_org_in_mapping(data: dict) -> UUID | None:
    if not isinstance(data, dict):
        return None
    for key in ORG_CLAIM_KEYS:
        org_id = _parse_uuid(data.get(key))
        if org_id:
            return org_id
    for meta_key in METADATA_KEYS:
        org_id = _find_org_in_mapping(data.get(meta_key))
        if org_id:
            return org_id
    return None


def _extract_user_id(payload: dict) -> str | None:
    for key in USER_CLAIM_KEYS:
        value = payload.get(key)
        if value:
            return str(value)
    for meta_key in METADATA_KEYS:
        meta = payload.get(meta_key)
        if isinstance(meta, dict):
            for key in USER_CLAIM_KEYS:
                value = meta.get(key)
                if value:
                    return str(value)
    return None


def _token_expired(payload: dict) -> bool:
    exp = payload.get("exp")
    if exp is None:
        return False
    try:
        return datetime.now(timezone.utc).timestamp() > float(exp)
    except (TypeError, ValueError):
        return False


def decode_bearer_token(token: str) -> dict | None:
    """Decode Bearer token using the same strategies as the rest of the app."""
    if not token:
        return None

    if token == LEGACY_APP_TOKEN:
        return {"sub": "legacy-user", "token_type": "legacy"}

    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except JWTError:
        pass

    try:
        claims = jwt.get_unverified_claims(token)
        if _token_expired(claims):
            logger.warning("Auth failed: bearer token expired")
            return None
        return claims
    except JWTError as exc:
        logger.warning("Auth failed: could not parse bearer token: %s", exc)
        return None


def resolve_organization_id(
    payload: dict,
    *,
    query_organization_id: UUID | None = None,
    header_organization_id: UUID | None = None,
) -> UUID | None:
    if query_organization_id:
        return query_organization_id
    if header_organization_id:
        return header_organization_id
    return _find_org_in_mapping(payload)


async def lookup_organization_id_for_user(request: Request, user_key: str) -> UUID | None:
    """Resolve organization from DB when JWT/query do not include org (team/get parity)."""
    pool = getattr(request.app.state, "db", None)
    if pool is None or not user_key:
        return None
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id FROM organizations
                WHERE additional_information->>'supabase_user_id' = $1
                LIMIT 1
                """,
                user_key,
            )
            if row:
                return _parse_uuid(row["id"])

            row = await conn.fetchrow(
                """
                SELECT organization_id FROM user_roles
                WHERE user_id::text = $1 OR user_id::text = $2
                LIMIT 1
                """,
                user_key,
                user_key,
            )
            if row:
                return _parse_uuid(row["organization_id"])
    except Exception as exc:
        logger.warning("Organization lookup failed for user %s: %s", user_key, exc)
    return None


async def get_auth_context(
    request: Request,
    authorization: str | None = Header(None, alias="Authorization"),
    organization_id: UUID | None = Query(None, description="Organization scope (same as /team/get)"),
    x_organization_id: UUID | None = Header(None, alias="X-Organization-Id"),
) -> AuthContext:
    if not authorization:
        logger.warning("Auth failed: missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Missing Authorization header"},
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        logger.warning("Auth failed: invalid Authorization header format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Missing or invalid Authorization header"},
        )

    token = token.strip()
    payload = decode_bearer_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid or expired token"},
        )

    org_id = resolve_organization_id(
        payload,
        query_organization_id=organization_id,
        header_organization_id=x_organization_id,
    )
    if org_id is None:
        user_key = payload.get("sub") or _extract_user_id(payload)
        if user_key:
            org_id = await lookup_organization_id_for_user(request, str(user_key))
    if org_id is None:
        logger.warning(
            "Auth failed: no organization context (query=%s header=%s)",
            organization_id,
            x_organization_id,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Token missing organization context"},
        )

    user_id = _extract_user_id(payload) or "unknown"
    logger.info("Auth OK user_id=%s organization_id=%s", user_id, org_id)
    return AuthContext(organization_id=org_id, user_id=user_id, token=token)


async def get_checklist_context(
    request: Request,
    authorization: str | None = Header(None, alias="Authorization"),
    organization_id: UUID | None = Query(None, description="Organization scope (same as /team/get)"),
    x_organization_id: UUID | None = Header(None, alias="X-Organization-Id"),
) -> AuthContext:
    """
    Checklist auth entry point. When IAM_AUTH_ENABLED=false (default), skips JWT
    validation and scopes by organization_id query/header only — same as /team/get.
    """
    if not settings.IAM_AUTH_ENABLED:
        org_id = organization_id or x_organization_id
        if org_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "organization_id is required"},
            )
        logger.info(
            "Checklist auth bypass (IAM disabled) organization_id=%s",
            org_id,
        )
        return AuthContext(organization_id=org_id, user_id="anonymous", token="")

    return await get_auth_context(
        request=request,
        authorization=authorization,
        organization_id=organization_id,
        x_organization_id=x_organization_id,
    )
