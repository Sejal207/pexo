from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.services.attendance_service import AttendanceService, _hours_between

_SCHEDULE_LINE = {
    "day": "MON",
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "break_minutes": 30,
}
_MONDAY = date(2026, 1, 5)


def _service_with_line(line):
    service = AttendanceService(db=AsyncMock())
    service._resolve_schedule_line = AsyncMock(return_value=line)
    return service


def test_hours_between_rounds_to_two_decimals():
    start = datetime(2026, 1, 5, 9, 0, tzinfo=timezone.utc)
    end = datetime(2026, 1, 5, 17, 30, tzinfo=timezone.utc)
    assert _hours_between(start, end) == Decimal("8.5")


def test_hours_between_never_negative():
    start = datetime(2026, 1, 5, 17, 0, tzinfo=timezone.utc)
    end = datetime(2026, 1, 5, 16, 0, tzinfo=timezone.utc)
    assert _hours_between(start, end) == Decimal("0")


@pytest.mark.asyncio
async def test_present_when_on_time_and_within_expected_hours():
    service = _service_with_line(_SCHEDULE_LINE)
    check_in = datetime(2026, 1, 5, 9, 2, tzinfo=timezone.utc)
    status, overtime = await service._derive_status(
        employee_id=None,
        work_date=_MONDAY,
        check_in=check_in,
        worked_hours=Decimal("7.5"),
        bearer_token="x",
    )
    assert status == "PRESENT"
    assert overtime == Decimal("0")


@pytest.mark.asyncio
async def test_late_when_check_in_past_grace_period():
    service = _service_with_line(_SCHEDULE_LINE)
    check_in = datetime(2026, 1, 5, 9, 25, tzinfo=timezone.utc)  # 25 min late; grace is 10 min
    status, _ = await service._derive_status(
        employee_id=None,
        work_date=_MONDAY,
        check_in=check_in,
        worked_hours=Decimal("7.0"),
        bearer_token="x",
    )
    assert status == "LATE"


@pytest.mark.asyncio
async def test_not_late_within_grace_period():
    service = _service_with_line(_SCHEDULE_LINE)
    check_in = datetime(2026, 1, 5, 9, 8, tzinfo=timezone.utc)  # 8 min late; within 10 min grace
    status, _ = await service._derive_status(
        employee_id=None,
        work_date=_MONDAY,
        check_in=check_in,
        worked_hours=Decimal("7.5"),
        bearer_token="x",
    )
    assert status == "PRESENT"


@pytest.mark.asyncio
async def test_half_day_when_worked_under_half_of_expected():
    service = _service_with_line(_SCHEDULE_LINE)
    check_in = datetime(2026, 1, 5, 9, 0, tzinfo=timezone.utc)
    status, _ = await service._derive_status(
        employee_id=None,
        work_date=_MONDAY,
        check_in=check_in,
        worked_hours=Decimal("3.0"),  # expected is 7.5h; half is 3.75h
        bearer_token="x",
    )
    assert status == "HALF_DAY"


@pytest.mark.asyncio
async def test_overtime_computed_when_worked_beyond_expected():
    service = _service_with_line(_SCHEDULE_LINE)
    check_in = datetime(2026, 1, 5, 9, 0, tzinfo=timezone.utc)
    status, overtime = await service._derive_status(
        employee_id=None,
        work_date=_MONDAY,
        check_in=check_in,
        worked_hours=Decimal("10.0"),
        bearer_token="x",
    )
    assert overtime == Decimal("2.5")  # expected 7.5h, worked 10h


@pytest.mark.asyncio
async def test_falls_back_to_present_or_absent_when_no_schedule_found():
    service = _service_with_line(None)
    check_in = datetime(2026, 1, 5, 9, 0, tzinfo=timezone.utc)

    status, overtime = await service._derive_status(
        employee_id=None, work_date=_MONDAY, check_in=check_in, worked_hours=Decimal("8.0"), bearer_token="x",
    )
    assert status == "PRESENT"
    assert overtime == Decimal("0")

    status_absent, _ = await service._derive_status(
        employee_id=None, work_date=_MONDAY, check_in=check_in, worked_hours=Decimal("0"), bearer_token="x",
    )
    assert status_absent == "ABSENT"
