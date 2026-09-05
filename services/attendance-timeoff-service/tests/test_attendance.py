import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.models.attendance import Attendance


def _make_record(employee_id, **overrides) -> Attendance:
    defaults = dict(
        id=uuid.uuid4(),
        employee_id=employee_id,
        work_date=datetime.now(timezone.utc).date(),
        check_in=datetime.now(timezone.utc),
        check_out=None,
        worked_hours=None,
        overtime_hours=None,
        status="PRESENT",
        is_manual_correction=False,
        corrected_by_user_id=None,
        correction_reason=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return Attendance(**defaults)


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_unauthenticated_request_rejected(client):
    response = await client.post("/api/v1/attendance/check-in")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_check_in_requires_employee_link(client, hr_manager_headers):
    """An HR_MANAGER token with no employee_id claim cannot check in."""
    response = await client.post("/api/v1/attendance/check-in", headers=hr_manager_headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_check_in_success(client, employee_headers_factory):
    emp_id = uuid.uuid4()
    record = _make_record(emp_id)
    with patch(
        "app.services.attendance_service.AttendanceService.check_in", new_callable=AsyncMock
    ) as mock_check_in:
        mock_check_in.return_value = record
        response = await client.post(
            "/api/v1/attendance/check-in", headers=employee_headers_factory(str(emp_id))
        )
        assert response.status_code == 201
        assert response.json()["employee_id"] == str(emp_id)
        mock_check_in.assert_awaited_once_with(emp_id)


@pytest.mark.asyncio
async def test_check_in_conflict_when_already_open(client, employee_headers_factory):
    emp_id = uuid.uuid4()
    with patch(
        "app.services.attendance_service.AttendanceService.check_in", new_callable=AsyncMock
    ) as mock_check_in:
        mock_check_in.side_effect = HTTPException(status_code=409, detail="Already checked in for today.")
        response = await client.post(
            "/api/v1/attendance/check-in", headers=employee_headers_factory(str(emp_id))
        )
        assert response.status_code == 409


@pytest.mark.asyncio
async def test_widget_status_route_not_captured_by_id_route(client, employee_headers_factory):
    """/attendance/widget-status must resolve to the widget endpoint, not {attendance_id}."""
    emp_id = uuid.uuid4()
    with patch(
        "app.services.attendance_service.AttendanceService.get_widget_status", new_callable=AsyncMock
    ) as mock_status:
        mock_status.return_value = {"open": False, "since": None, "elapsed_seconds": None}
        response = await client.get(
            "/api/v1/attendance/widget-status", headers=employee_headers_factory(str(emp_id))
        )
        assert response.json() == {"open": False, "since": None, "elapsed_seconds": None, "attendance_id": None}
        mock_status.assert_awaited_once_with(emp_id)


@pytest.mark.asyncio
async def test_list_attendance_scopes_employee_to_self(client, employee_headers_factory):
    emp_id = uuid.uuid4()
    other_id = uuid.uuid4()
    with patch(
        "app.services.attendance_service.AttendanceService.list_all", new_callable=AsyncMock
    ) as mock_list:
        mock_list.return_value = []
        response = await client.get(
            f"/api/v1/attendance/?employee_id={other_id}",
            headers=employee_headers_factory(str(emp_id)),
        )
        assert response.status_code == 200
        _, kwargs = mock_list.call_args
        # Regardless of the employee_id query param requested, an EMPLOYEE token
        # must only ever be able to list their own records.
        assert kwargs["employee_id"] == emp_id


@pytest.mark.asyncio
async def test_list_attendance_hr_manager_can_filter_any_employee(client, hr_manager_headers):
    target_id = uuid.uuid4()
    with patch(
        "app.services.attendance_service.AttendanceService.list_all", new_callable=AsyncMock
    ) as mock_list:
        mock_list.return_value = []
        response = await client.get(
            f"/api/v1/attendance/?employee_id={target_id}", headers=hr_manager_headers
        )
        assert response.status_code == 200
        _, kwargs = mock_list.call_args
        assert kwargs["employee_id"] == target_id


@pytest.mark.asyncio
async def test_get_attendance_forbidden_for_other_employee(client, employee_headers_factory):
    owner_id = uuid.uuid4()
    requester_id = uuid.uuid4()
    record = _make_record(owner_id)
    with patch(
        "app.services.attendance_service.AttendanceService.get_by_id", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = record
        response = await client.get(
            f"/api/v1/attendance/{record.id}", headers=employee_headers_factory(str(requester_id))
        )
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_attendance_allowed_for_owner(client, employee_headers_factory):
    owner_id = uuid.uuid4()
    record = _make_record(owner_id)
    with patch(
        "app.services.attendance_service.AttendanceService.get_by_id", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = record
        response = await client.get(
            f"/api/v1/attendance/{record.id}", headers=employee_headers_factory(str(owner_id))
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_attendance_not_found(client, hr_manager_headers):
    with patch(
        "app.services.attendance_service.AttendanceService.get_by_id", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = None
        response = await client.get(f"/api/v1/attendance/{uuid.uuid4()}", headers=hr_manager_headers)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_check_out_rejects_non_owner_via_service(client, employee_headers_factory):
    emp_id = uuid.uuid4()
    with patch(
        "app.services.attendance_service.AttendanceService.check_out", new_callable=AsyncMock
    ) as mock_check_out:
        mock_check_out.side_effect = HTTPException(status_code=403, detail="You may only check yourself out")
        response = await client.post(
            f"/api/v1/attendance/{uuid.uuid4()}/check-out",
            headers=employee_headers_factory(str(emp_id)),
        )
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_check_out_success(client, employee_headers_factory):
    emp_id = uuid.uuid4()
    record = _make_record(
        emp_id,
        check_out=datetime.now(timezone.utc),
        worked_hours=Decimal("8.0"),
        overtime_hours=Decimal("0"),
    )
    with patch(
        "app.services.attendance_service.AttendanceService.check_out", new_callable=AsyncMock
    ) as mock_check_out:
        mock_check_out.return_value = record
        response = await client.post(
            f"/api/v1/attendance/{record.id}/check-out",
            headers=employee_headers_factory(str(emp_id)),
        )
        assert response.status_code == 200
        assert Decimal(response.json()["worked_hours"]) == Decimal("8.0")


@pytest.mark.asyncio
async def test_correct_attendance_forbidden_for_employee(client, employee_headers_factory):
    emp_id = uuid.uuid4()
    payload = {"reason": "forgot to check in"}
    response = await client.patch(
        f"/api/v1/attendance/{uuid.uuid4()}",
        json=payload,
        headers=employee_headers_factory(str(emp_id)),
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_correct_attendance_success_for_hr_manager(client, hr_manager_headers):
    owner_id = uuid.uuid4()
    corrected = _make_record(
        owner_id,
        is_manual_correction=True,
        correction_reason="forgot to check in",
        worked_hours=Decimal("8.0"),
    )
    with patch(
        "app.services.attendance_service.AttendanceService.correct", new_callable=AsyncMock
    ) as mock_correct:
        mock_correct.return_value = corrected
        response = await client.patch(
            f"/api/v1/attendance/{corrected.id}",
            json={"reason": "forgot to check in"},
            headers=hr_manager_headers,
        )
        assert response.status_code == 200
        assert response.json()["is_manual_correction"] is True
