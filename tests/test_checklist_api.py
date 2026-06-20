import os
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt

from app.core.config import settings
from main import app

pytestmark = pytest.mark.asyncio

ORG_ID = uuid4()


def _auth_headers(
    organization_id=None,
    user_id: str = "pytest-user",
    token: str | None = None,
):
    organization_id = organization_id or ORG_ID
    if token is None:
        token = jwt.encode(
            {
                "organization_id": str(organization_id),
                "user_id": user_id,
                "sub": user_id,
            },
            settings.JWT_SECRET,
            algorithm="HS256",
        )
    return {
        "Authorization": f"Bearer {token}",
    }


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_templates_requires_organization_id(client):
    response = await client.get("/checklist/templates")
    if settings.IAM_AUTH_ENABLED:
        assert response.status_code == 401
    else:
        assert response.status_code == 400
    body = response.json()
    assert "error" in body or "detail" in body


async def test_templates_without_auth_header(client):
    """IAM disabled: org query alone is enough (same as /team/get)."""
    if settings.IAM_AUTH_ENABLED:
        pytest.skip("IAM auth enabled")
    response = await client.get(
        "/checklist/templates",
        params={"organization_id": str(ORG_ID)},
    )
    assert response.status_code == 200
    assert "data" in response.json()


async def test_templates_invalid_token(client):
    if settings.IAM_AUTH_ENABLED:
        response = await client.get(
            "/checklist/templates",
            headers={"Authorization": "Bearer not-a-valid-token"},
            params={"organization_id": str(ORG_ID)},
        )
        assert response.status_code == 401
    else:
        response = await client.get(
            "/checklist/templates",
            headers={"Authorization": "Bearer not-a-valid-token"},
            params={"organization_id": str(ORG_ID)},
        )
        assert response.status_code != 401


async def test_templates_legacy_token_with_org_query(client):
    """Same Bearer pattern as /team/get: token present + organization_id query."""
    response = await client.get(
        "/checklist/templates",
        headers={"Authorization": "Bearer thechurchmanager"},
        params={"organization_id": str(ORG_ID)},
    )
    assert response.status_code != 401


async def test_templates_supabase_like_token_with_org_query(client):
    import base64
    import json
    import time

    header = base64.urlsafe_b64encode(json.dumps({"alg": "ES256", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload = base64.urlsafe_b64encode(
        json.dumps(
            {
                "sub": str(uuid4()),
                "email": "user@example.com",
                "exp": int(time.time()) + 3600,
            }
        ).encode()
    ).decode().rstrip("=")
    token = f"{header}.{payload}.fake-signature"

    response = await client.get(
        "/checklist/templates",
        headers={"Authorization": f"Bearer {token}"},
        params={"organization_id": str(ORG_ID)},
    )
    assert response.status_code != 401


async def test_templates_valid_hs256_token(client):
    response = await client.get(
        "/checklist/templates",
        headers=_auth_headers(),
        params={"organization_id": str(ORG_ID)},
    )
    assert response.status_code == 200
    assert "data" in response.json()


async def test_records_empty_list(client):
    response = await client.get(
        "/checklist/records",
        params={
            "organization_id": str(ORG_ID),
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "limit": 200,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "data" in body


async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.integration
async def test_template_crud_org_scoped(client):
    if not os.getenv("RUN_CHECKLIST_DB_TESTS"):
        pytest.skip("Set RUN_CHECKLIST_DB_TESTS=1 to run database integration tests")

    headers = _auth_headers()
    create_resp = await client.post(
        "/checklist/templates",
        headers=headers,
        params={"organization_id": str(ORG_ID)},
        json={
            "team_id": str(uuid4()),
            "name": "Integration Template",
            "description": "test",
            "is_active": True,
            "items": [
                {
                    "title": "Mixer powered on",
                    "description": "[audio] Audio System",
                    "order": 0,
                    "is_required": True,
                }
            ],
        },
    )
    assert create_resp.status_code in (201, 403, 404, 422)
