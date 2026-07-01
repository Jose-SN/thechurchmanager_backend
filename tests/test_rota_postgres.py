"""Service Rota PostgreSQL integration tests."""

from __future__ import annotations

import os
from datetime import date, timedelta
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt

from app.core.config import settings
from main import app

pytestmark = pytest.mark.asyncio

ORG_ID = uuid4()
USER_A = uuid4()
USER_B = uuid4()


def _headers(org_id: UUID | None = None, user_id: str | None = None):
    org_id = org_id or ORG_ID
    user_id = user_id or str(USER_A)
    token = jwt.encode(
        {
            "organization_id": str(org_id),
            "user_id": user_id,
            "sub": user_id,
        },
        settings.JWT_SECRET,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_rota_get_requires_organization_id(client):
    response = await client.get("/rota/get")
    if settings.IAM_AUTH_ENABLED:
        assert response.status_code == 401
    else:
        assert response.status_code == 400


@pytest.mark.integration
async def test_service_crud(client):
    if not os.getenv("RUN_ROTA_DB_TESTS"):
        pytest.skip("Set RUN_ROTA_DB_TESTS=1 to run database integration tests")

    headers = _headers()
    today = date.today()

    create = await client.post(
        "/rota/save",
        headers=headers,
        json={
            "organization_id": str(ORG_ID),
            "name": "Test Service",
            "date": today.isoformat(),
            "time": "09:30",
            "location": "Hall A",
            "status": "draft",
        },
    )
    assert create.status_code == 201
    body = create.json()
    assert body["success"] is True
    service_id = body["data"]["id"]

    listing = await client.get(
        "/rota/get",
        headers=headers,
        params={"organization_id": str(ORG_ID), "search": "Test"},
    )
    assert listing.status_code == 200
    assert listing.json()["success"] is True

    update = await client.put(
        f"/rota/update/{service_id}",
        headers=headers,
        json={"name": "Updated Service"},
    )
    assert update.status_code == 200
    assert update.json()["data"]["name"] == "Updated Service"

    publish = await client.post(
        f"/rota/published/{service_id}",
        headers=headers,
        params={"organization_id": str(ORG_ID)},
    )
    assert publish.status_code == 200
    assert publish.json()["data"]["status"] == "published"

    delete = await client.delete(
        f"/rota/delete/{service_id}",
        headers=headers,
        params={"organization_id": str(ORG_ID)},
    )
    assert delete.status_code == 200
    assert delete.json()["data"]["deleted"] is True


@pytest.mark.integration
async def test_availability_and_assignments(client):
    if not os.getenv("RUN_ROTA_DB_TESTS"):
        pytest.skip("Set RUN_ROTA_DB_TESTS=1 to run database integration tests")

    headers = _headers()
    today = date.today()
    team_id = uuid4()

    create = await client.post(
        "/rota/save",
        headers=headers,
        json={
            "organization_id": str(ORG_ID),
            "name": "Availability Service",
            "date": today.isoformat(),
            "status": "published",
        },
    )
    service_id = create.json()["data"]["id"]

    avail = await client.post(
        "/rota/availability",
        headers=headers,
        json={
            "organization_id": str(ORG_ID),
            "service_id": service_id,
            "user_id": str(USER_A),
            "user_name": "Alice",
            "availability": "available",
        },
    )
    assert avail.status_code == 201

    assignment = await client.post(
        "/rota/assignments",
        headers=headers,
        json={
            "organization_id": str(ORG_ID),
            "service_id": service_id,
            "user_id": str(USER_A),
            "user_name": "Alice",
            "team_id": str(team_id),
            "team_name": "Worship",
            "role": "Singer",
            "status": "confirmed",
        },
    )
    assert assignment.status_code == 201

    dashboard = await client.get(
        "/rota/dashboard",
        headers=headers,
        params={"organization_id": str(ORG_ID)},
    )
    assert dashboard.status_code == 200
    assert dashboard.json()["success"] is True


@pytest.mark.integration
async def test_my_schedule_scoped_to_user(client):
    if not os.getenv("RUN_ROTA_DB_TESTS"):
        pytest.skip("Set RUN_ROTA_DB_TESTS=1 to run database integration tests")

    headers_a = _headers(user_id=str(USER_A))
    headers_b = _headers(user_id=str(USER_B))
    today = date.today()
    team_id = uuid4()

    create = await client.post(
        "/rota/save",
        headers=headers_a,
        json={
            "organization_id": str(ORG_ID),
            "name": "My Schedule Service",
            "date": today.isoformat(),
            "status": "published",
        },
    )
    service_id = create.json()["data"]["id"]

    await client.post(
        "/rota/assignments",
        headers=headers_a,
        json={
            "organization_id": str(ORG_ID),
            "service_id": service_id,
            "user_id": str(USER_A),
            "user_name": "Alice",
            "team_id": str(team_id),
            "team_name": "Worship",
            "role": "Singer",
            "status": "confirmed",
        },
    )

    mine = await client.get(
        "/rota/my/schedule",
        headers=headers_a,
        params={
            "organization_id": str(ORG_ID),
            "start_date": today.isoformat(),
            "end_date": today.isoformat(),
        },
    )
    assert mine.status_code == 200
    assert len(mine.json()["data"]) >= 1

    other = await client.get(
        "/rota/my/schedule",
        headers=headers_b,
        params={
            "organization_id": str(ORG_ID),
            "start_date": today.isoformat(),
            "end_date": today.isoformat(),
        },
    )
    assert other.status_code == 200
    assert other.json()["data"] == []
