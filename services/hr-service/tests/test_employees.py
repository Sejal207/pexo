import uuid
from unittest.mock import AsyncMock, patch
from datetime import date, datetime, timezone
import pytest
from app.models.employee import Employee


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

    response_v1 = await client.get("/api/v1/health")
    assert response_v1.status_code == 200
    assert response_v1.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_unauthenticated_request_rejected(client):
    response = await client.get("/api/v1/employees/")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_employee_as_employee_role_forbidden(client, employee_headers_factory):
    emp_id = str(uuid.uuid4())
    headers = employee_headers_factory(emp_id)
    payload = {
        "employee_code": "EMP001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "date_joined": "2026-01-01",
    }
    response = await client.post("/api/v1/employees/", json=payload, headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_employee_cannot_access_other_record(client, employee_headers_factory):
    my_emp_id = str(uuid.uuid4())
    other_emp_id = str(uuid.uuid4())
    headers = employee_headers_factory(my_emp_id)

    response = await client.get(f"/api/v1/employees/{other_emp_id}", headers=headers)
    assert response.status_code == 403
    assert "not allowed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_employee_detail_with_smart_counts(client, hr_manager_headers):
    emp_id = uuid.uuid4()
    mock_employee = Employee(
        id=emp_id,
        employee_code="EMP002",
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        phone="1234567890",
        date_joined=date(2026, 1, 1),
        employment_status="ACTIVE",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    with patch("app.services.employee_service.EmployeeService.get_by_id", new_callable=AsyncMock) as mock_get:
        with patch("app.services.employee_service.EmployeeService.get_contracts_count", new_callable=AsyncMock) as mock_count:
            mock_get.return_value = mock_employee
            mock_count.return_value = 2

            response = await client.get(f"/api/v1/employees/{emp_id}", headers=hr_manager_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == str(emp_id)
            assert data["contracts_count"] == 2
            assert data["attendance_count"] == 0
            assert data["time_off_count"] == 0


@pytest.mark.asyncio
async def test_list_employees_with_filters(client, hr_manager_headers):
    mock_employees = [
        Employee(
            id=uuid.uuid4(),
            employee_code="EMP003",
            first_name="Bob",
            last_name="Jones",
            email="bob@example.com",
            date_joined=date(2026, 1, 1),
            employment_status="ACTIVE",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    ]
    with patch("app.services.employee_service.EmployeeService.get_all", new_callable=AsyncMock) as mock_get_all:
        mock_get_all.return_value = mock_employees
        response = await client.get("/api/v1/employees/?employment_status=ACTIVE", headers=hr_manager_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["employee_code"] == "EMP003"
