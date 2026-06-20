import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from app.api.auth_context import AuthContext, decode_bearer_token, resolve_organization_id
from app.checklist.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.checklist.schemas import ChecklistRecordCreate, ChecklistTemplateCreate
from app.checklist.service import ChecklistService

ORG_ID = uuid4()
OTHER_ORG_ID = uuid4()
TEAM_ID = uuid4()
USER_ID = "test-user-1"


@pytest.fixture
def auth() -> AuthContext:
    return AuthContext(organization_id=ORG_ID, user_id=USER_ID, token="test-token")


@pytest.fixture
def service() -> ChecklistService:
    session = MagicMock()
    svc = ChecklistService(session)
    svc.repo = AsyncMock()
    return svc


def test_decode_legacy_token():
    payload = decode_bearer_token("thechurchmanager")
    assert payload is not None
    assert payload.get("sub") == "legacy-user"


def test_resolve_org_from_query():
    org_id = uuid4()
    payload = decode_bearer_token("thechurchmanager")
    resolved = resolve_organization_id(payload, query_organization_id=org_id)
    assert resolved == org_id


@pytest.mark.asyncio
async def test_create_template_rejects_foreign_team(service: ChecklistService, auth: AuthContext):
    service.repo.get_team.return_value = MagicMock(organization_id=OTHER_ORG_ID)
    payload = ChecklistTemplateCreate(
        team_id=TEAM_ID,
        name="Test Template",
        items=[],
    )
    with pytest.raises(ForbiddenError):
        await service.create_template(auth, payload)


@pytest.mark.asyncio
async def test_create_record_conflict(service: ChecklistService, auth: AuthContext):
    template = MagicMock()
    template.team_id = TEAM_ID
    template.items = []
    service.repo.get_template.return_value = template
    service.repo.get_team.return_value = MagicMock(organization_id=ORG_ID)
    service.repo.find_record_by_unique.return_value = MagicMock()
    payload = ChecklistRecordCreate(
        template_id=uuid4(),
        team_id=TEAM_ID,
        date=__import__("datetime").date(2026, 5, 23),
    )
    with pytest.raises(ConflictError):
        await service.create_record(auth, payload)


@pytest.mark.asyncio
async def test_get_record_not_found(service: ChecklistService, auth: AuthContext):
    service.repo.get_record.return_value = None
    with pytest.raises(NotFoundError):
        await service.get_record(auth, uuid4())


@pytest.mark.asyncio
async def test_delete_template_not_found(service: ChecklistService, auth: AuthContext):
    service.repo.get_template.return_value = None
    with pytest.raises(NotFoundError):
        await service.delete_template(auth, uuid4())


@pytest.mark.asyncio
async def test_org_isolation_list_templates(service: ChecklistService, auth: AuthContext):
    service.repo.list_templates.return_value = []
    await service.list_templates(auth, team_id=None)
    service.repo.list_templates.assert_awaited_once_with(ORG_ID, None)
