import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.models.time_off_allocation import TimeOffAllocation
from app.models.time_off_request import TimeOffRequest
from app.models.time_off_type import TimeOffType


def _make_type(**overrides) -> TimeOffType:
    defaults = dict(
        id=uuid.uuid4(),
        name="Paid Time Off",
        unit="DAYS",
        requires_allocation=True,
        requires_approval=True,
        affects_payroll=True,
        color="#00ff00",
        payroll_work_entry_code="LEAVE_PAID",
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return TimeOffType(**defaults)


def _make_allocation(employee_id, **overrides) -> TimeOffAllocation:
    defaults = dict(
        id=uuid.uuid4(),
        employee_id=employee_id,
        time_off_type_id=uuid.uuid4(),
        allocated_amount=Decimal("10.00"),
        taken_amount=Decimal("0.00"),
        remaining_amount=Decimal("10.00"),
        valid_from=date(2026, 1, 1),
        valid_to=date(2026, 12, 31),
        approval_status="APPROVED",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return TimeOffAllocation(**defaults)


def _make_request(employee_id, **overrides) -> TimeOffRequest:
    defaults = dict(
        id=uuid.uuid4(),
        employee_id=employee_id,
        time_off_type_id=uuid.uuid4(),
        allocation_id=None,
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 2),
        duration=Decimal("2.00"),
        status="SUBMITTED",
        approved_by_user_id=None,
        approved_at=None,
        reason=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return TimeOffRequest(**defaults)


# ---------------------------------------------------------------------- #
# Types
# ---------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_create_time_off_type_forbidden_for_employee(client, employee_headers_factory):
    payload = {"name": "Sick Leave"}
    response = await client.post(
        "/api/v1/time-off/types", json=payload, headers=employee_headers_factory(str(uuid.uuid4()))
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_time_off_types_open_to_authenticated(client, employee_headers_factory, mock_db_session):
    from unittest.mock import MagicMock

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [_make_type()]
    mock_db_session.execute.return_value = mock_result

    response = await client.get(
        "/api/v1/time-off/types", headers=employee_headers_factory(str(uuid.uuid4()))
    )
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Paid Time Off"


# ---------------------------------------------------------------------- #
# Allocations
# ---------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_create_allocation_forbidden_for_employee(client, employee_headers_factory):
    payload = {
        "employee_id": str(uuid.uuid4()),
        "time_off_type_id": str(uuid.uuid4()),
        "allocated_amount": "10.00",
        "valid_from": "2026-01-01",
        "valid_to": "2026-12-31",
    }
    response = await client.post(
        "/api/v1/time-off/allocations", json=payload, headers=employee_headers_factory(str(uuid.uuid4()))
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_allocations_scopes_employee_to_self(client, employee_headers_factory):
    emp_id = uuid.uuid4()
    other_id = uuid.uuid4()
    with patch(
        "app.services.time_off_service.AllocationService.list_all", new_callable=AsyncMock
    ) as mock_list:
        mock_list.return_value = []
        response = await client.get(
            f"/api/v1/time-off/allocations?employee_id={other_id}",
            headers=employee_headers_factory(str(emp_id)),
        )
        assert response.status_code == 200
        _, kwargs = mock_list.call_args
        assert kwargs["employee_id"] == emp_id


@pytest.mark.asyncio
async def test_approve_allocation_conflict_when_not_pending(client, hr_manager_headers):
    with patch(
        "app.services.time_off_service.AllocationService.approve", new_callable=AsyncMock
    ) as mock_approve:
        mock_approve.side_effect = HTTPException(status_code=409, detail="Allocation is already APPROVED, not PENDING")
        response = await client.post(
            f"/api/v1/time-off/allocations/{uuid.uuid4()}/approve", headers=hr_manager_headers
        )
        assert response.status_code == 409


# ---------------------------------------------------------------------- #
# Requests
# ---------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_create_request_requires_employee_link(client, hr_manager_headers):
    payload = {
        "time_off_type_id": str(uuid.uuid4()),
        "start_date": "2026-03-01",
        "end_date": "2026-03-02",
        "duration": "2.00",
    }
    response = await client.post("/api/v1/time-off/requests", json=payload, headers=hr_manager_headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_request_uses_token_employee_id(client, employee_headers_factory):
    emp_id = uuid.uuid4()
    record = _make_request(emp_id)
    with patch(
        "app.services.time_off_service.TimeOffRequestService.create", new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = record
        payload = {
            "time_off_type_id": str(record.time_off_type_id),
            "start_date": "2026-03-01",
            "end_date": "2026-03-02",
            "duration": "2.00",
        }
        response = await client.post(
            "/api/v1/time-off/requests", json=payload, headers=employee_headers_factory(str(emp_id))
        )
        assert response.status_code == 201
        args, _ = mock_create.call_args
        assert args[0] == emp_id


@pytest.mark.asyncio
async def test_create_request_over_balance_rejected(client, employee_headers_factory):
    emp_id = uuid.uuid4()
    with patch(
        "app.services.time_off_service.TimeOffRequestService.create", new_callable=AsyncMock
    ) as mock_create:
        mock_create.side_effect = HTTPException(
            status_code=422, detail="Requested duration 5.00 exceeds remaining balance 2.00"
        )
        payload = {
            "time_off_type_id": str(uuid.uuid4()),
            "allocation_id": str(uuid.uuid4()),
            "start_date": "2026-03-01",
            "end_date": "2026-03-05",
            "duration": "5.00",
        }
        response = await client.post(
            "/api/v1/time-off/requests", json=payload, headers=employee_headers_factory(str(emp_id))
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_approve_request_forbidden_for_employee(client, employee_headers_factory):
    response = await client.post(
        f"/api/v1/time-off/requests/{uuid.uuid4()}/approve",
        headers=employee_headers_factory(str(uuid.uuid4())),
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_approve_request_success(client, hr_manager_headers):
    emp_id = uuid.uuid4()
    approved = _make_request(emp_id, status="APPROVED", approved_at=datetime.now(timezone.utc))
    with patch(
        "app.services.time_off_service.TimeOffRequestService.approve", new_callable=AsyncMock
    ) as mock_approve:
        mock_approve.return_value = approved
        response = await client.post(
            f"/api/v1/time-off/requests/{approved.id}/approve", headers=hr_manager_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "APPROVED"


@pytest.mark.asyncio
async def test_refuse_request_requires_reason(client, hr_manager_headers):
    response = await client.post(
        f"/api/v1/time-off/requests/{uuid.uuid4()}/refuse", json={}, headers=hr_manager_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_refuse_request_success(client, hr_manager_headers):
    emp_id = uuid.uuid4()
    refused = _make_request(emp_id, status="REFUSED", reason="not enough coverage")
    with patch(
        "app.services.time_off_service.TimeOffRequestService.refuse", new_callable=AsyncMock
    ) as mock_refuse:
        mock_refuse.return_value = refused
        response = await client.post(
            f"/api/v1/time-off/requests/{refused.id}/refuse",
            json={"reason": "not enough coverage"},
            headers=hr_manager_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "REFUSED"


# ---------------------------------------------------------------------- #
# Work entries (internal, consumed by payroll-service)
# ---------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_work_entries_forbidden_for_plain_employee(client, employee_headers_factory):
    emp_id = uuid.uuid4()
    response = await client.get(
        f"/api/v1/time-off/work-entries?employee_id={emp_id}&period_start=2026-01-01&period_end=2026-01-31",
        headers=employee_headers_factory(str(emp_id)),
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_work_entries_allowed_for_payroll_user(client):
    from tests.conftest import create_test_token
    from app.core.config import settings

    token = create_test_token(user_id=str(uuid.uuid4()), roles=["HR_PAYROLL_USER"])
    with patch(
        "app.services.time_off_service.TimeOffRequestService.get_work_entries", new_callable=AsyncMock
    ) as mock_entries:
        mock_entries.return_value = [{"payroll_work_entry_code": "LEAVE_PAID", "total_duration": "2.00"}]
        emp_id = uuid.uuid4()
        response = await client.get(
            f"/api/v1/time-off/work-entries?employee_id={emp_id}&period_start=2026-01-01&period_end=2026-01-31",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()[0]["payroll_work_entry_code"] == "LEAVE_PAID"
