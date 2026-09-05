import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock
import pytest
from app.models.department import Department


@pytest.mark.asyncio
async def test_list_departments(client, hr_manager_headers, mock_db_session):
    mock_depts = [
        Department(
            id=uuid.uuid4(),
            name="Engineering",
            parent_department_id=None,
            manager_employee_id=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    ]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_depts
    mock_db_session.execute.return_value = mock_result

    response = await client.get("/api/v1/departments/", headers=hr_manager_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Engineering"


@pytest.mark.asyncio
async def test_create_department_as_employee_forbidden(client, employee_headers_factory):
    headers = employee_headers_factory(str(uuid.uuid4()))
    payload = {"name": "Finance"}
    response = await client.post("/api/v1/departments/", json=payload, headers=headers)
    assert response.status_code == 403
