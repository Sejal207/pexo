import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.time_off_allocation import TimeOffAllocation
from app.models.time_off_request import TimeOffRequest
from app.models.time_off_type import TimeOffType
from app.schemas.time_off import TimeOffRequestCreate
from app.services.time_off_service import AllocationService, TimeOffRequestService


def _scalar_result(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


class FakeSession:
    """Minimal AsyncSession stand-in: execute() replays canned results in order."""

    def __init__(self, execute_results):
        self._results = list(execute_results)
        self.add = MagicMock()
        self.flush = AsyncMock()
        self.commit = AsyncMock()
        self.refresh = AsyncMock()
        self.rollback = AsyncMock()

    async def execute(self, *args, **kwargs):
        return self._results.pop(0)


def _make_type(**overrides) -> TimeOffType:
    defaults = dict(
        id=uuid.uuid4(),
        name="Paid Time Off",
        unit="DAYS",
        requires_allocation=True,
        requires_approval=True,
        affects_payroll=True,
        color=None,
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
        valid_from=date(2026, 1, 1),
        valid_to=date(2026, 12, 31),
        approval_status="APPROVED",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return TimeOffAllocation(**defaults)


@pytest.mark.asyncio
async def test_request_create_rejects_over_balance():
    emp_id = uuid.uuid4()
    time_off_type = _make_type()
    allocation = _make_allocation(emp_id, allocated_amount=Decimal("2.00"), taken_amount=Decimal("0.00"))

    session = FakeSession([_scalar_result(time_off_type), _scalar_result(allocation)])
    service = TimeOffRequestService(session)

    data = TimeOffRequestCreate(
        time_off_type_id=time_off_type.id,
        allocation_id=allocation.id,
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 5),
        duration=Decimal("5.00"),
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create(emp_id, data)
    assert exc_info.value.status_code == 422
    assert "exceeds remaining balance" in exc_info.value.detail


@pytest.mark.asyncio
async def test_request_create_rejects_unapproved_allocation():
    emp_id = uuid.uuid4()
    time_off_type = _make_type()
    allocation = _make_allocation(emp_id, approval_status="PENDING")

    session = FakeSession([_scalar_result(time_off_type), _scalar_result(allocation)])
    service = TimeOffRequestService(session)

    data = TimeOffRequestCreate(
        time_off_type_id=time_off_type.id,
        allocation_id=allocation.id,
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 2),
        duration=Decimal("1.00"),
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create(emp_id, data)
    assert exc_info.value.status_code == 422
    assert "not yet approved" in exc_info.value.detail


@pytest.mark.asyncio
async def test_request_create_rejects_someone_elses_allocation():
    emp_id = uuid.uuid4()
    other_id = uuid.uuid4()
    time_off_type = _make_type()
    allocation = _make_allocation(other_id)

    session = FakeSession([_scalar_result(time_off_type), _scalar_result(allocation)])
    service = TimeOffRequestService(session)

    data = TimeOffRequestCreate(
        time_off_type_id=time_off_type.id,
        allocation_id=allocation.id,
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 2),
        duration=Decimal("1.00"),
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create(emp_id, data)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_request_create_requires_allocation_when_type_demands_it():
    emp_id = uuid.uuid4()
    time_off_type = _make_type(requires_allocation=True)

    session = FakeSession([_scalar_result(time_off_type)])
    service = TimeOffRequestService(session)

    data = TimeOffRequestCreate(
        time_off_type_id=time_off_type.id,
        allocation_id=None,
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 2),
        duration=Decimal("1.00"),
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create(emp_id, data)
    assert exc_info.value.status_code == 422
    assert "requires an allocation_id" in exc_info.value.detail


@pytest.mark.asyncio
async def test_request_create_within_balance_succeeds_as_submitted():
    emp_id = uuid.uuid4()
    time_off_type = _make_type()
    allocation = _make_allocation(emp_id, allocated_amount=Decimal("10.00"), taken_amount=Decimal("2.00"))

    session = FakeSession([_scalar_result(time_off_type), _scalar_result(allocation)])
    service = TimeOffRequestService(session)

    data = TimeOffRequestCreate(
        time_off_type_id=time_off_type.id,
        allocation_id=allocation.id,
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 3),
        duration=Decimal("3.00"),
    )

    request = await service.create(emp_id, data)
    assert request.status == "SUBMITTED"
    # taken_amount is only touched on approval, not on submission.
    assert allocation.taken_amount == Decimal("2.00")


@pytest.mark.asyncio
async def test_request_create_auto_approves_when_type_does_not_require_approval():
    emp_id = uuid.uuid4()
    time_off_type = _make_type(requires_approval=False)
    allocation = _make_allocation(emp_id, allocated_amount=Decimal("10.00"), taken_amount=Decimal("0.00"))

    session = FakeSession([_scalar_result(time_off_type), _scalar_result(allocation)])
    service = TimeOffRequestService(session)

    data = TimeOffRequestCreate(
        time_off_type_id=time_off_type.id,
        allocation_id=allocation.id,
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 3),
        duration=Decimal("3.00"),
    )

    request = await service.create(emp_id, data)
    assert request.status == "APPROVED"
    assert allocation.taken_amount == Decimal("3.00")


@pytest.mark.asyncio
async def test_request_approve_deducts_allocation_balance():
    emp_id = uuid.uuid4()
    allocation = _make_allocation(emp_id, allocated_amount=Decimal("10.00"), taken_amount=Decimal("1.00"))
    request = TimeOffRequest(
        id=uuid.uuid4(),
        employee_id=emp_id,
        time_off_type_id=uuid.uuid4(),
        allocation_id=allocation.id,
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 3),
        duration=Decimal("3.00"),
        status="SUBMITTED",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    session = FakeSession([_scalar_result(allocation)])
    service = TimeOffRequestService(session)
    service.get_by_id = AsyncMock(return_value=request)
    service._audit.log = AsyncMock()

    result = await service.approve(request.id, actor_user_id=uuid.uuid4())
    assert result.status == "APPROVED"
    assert allocation.taken_amount == Decimal("4.00")


@pytest.mark.asyncio
async def test_request_approve_rejects_when_already_decided():
    request = TimeOffRequest(
        id=uuid.uuid4(),
        employee_id=uuid.uuid4(),
        time_off_type_id=uuid.uuid4(),
        allocation_id=None,
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 3),
        duration=Decimal("3.00"),
        status="APPROVED",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    session = FakeSession([])
    service = TimeOffRequestService(session)
    service.get_by_id = AsyncMock(return_value=request)

    with pytest.raises(HTTPException) as exc_info:
        await service.approve(request.id, actor_user_id=uuid.uuid4())
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_allocation_approve_rejects_double_approve():
    allocation = _make_allocation(uuid.uuid4(), approval_status="APPROVED")
    session = FakeSession([])
    service = AllocationService(session)
    service.get_by_id = AsyncMock(return_value=allocation)

    with pytest.raises(HTTPException) as exc_info:
        await service.approve(allocation.id)
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_allocation_approve_success():
    allocation = _make_allocation(uuid.uuid4(), approval_status="PENDING")
    session = FakeSession([])
    service = AllocationService(session)
    service.get_by_id = AsyncMock(return_value=allocation)

    result = await service.approve(allocation.id)
    assert result.approval_status == "APPROVED"
