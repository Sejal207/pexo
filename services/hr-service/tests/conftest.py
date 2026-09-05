import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from jose import jwt

from app.main import app
from app.core.config import settings
from app.core.database import get_db


def create_test_token(user_id: str, roles: list[str], employee_id: str = None) -> str:
    payload = {
        "sub": user_id,
        "user_id": user_id,
        "roles": roles,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    if employee_id:
        payload["employee_id"] = employee_id
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@pytest_asyncio.fixture
async def mock_db_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()
    session.execute = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest_asyncio.fixture
async def client(mock_db_session):
    async def override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def hr_manager_headers():
    token = create_test_token(
        user_id=str(uuid.uuid4()),
        roles=["HR_MANAGER"],
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def payroll_user_headers():
    token = create_test_token(
        user_id=str(uuid.uuid4()),
        roles=["HR_PAYROLL_USER"],
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def employee_headers_factory():
    def _make(employee_id: str):
        token = create_test_token(
            user_id=str(uuid.uuid4()),
            roles=["EMPLOYEE"],
            employee_id=employee_id,
        )
        return {"Authorization": f"Bearer {token}"}
    return _make
