from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.dependencies import (
    READ_ALL_ROLES,
    get_self_employee_id,
    require_any_role,
    require_employee_link,
    require_writer,
)
from app.models.time_off_type import TimeOffType
from app.schemas.time_off import (
    AllocationCreate,
    AllocationOut,
    TimeOffRequestCreate,
    TimeOffRequestOut,
    TimeOffRequestRefuse,
    TimeOffTypeCreate,
    TimeOffTypeOut,
    WorkEntrySummary,
)
from app.services.time_off_service import AllocationService, TimeOffRequestService

router = APIRouter(prefix="/time-off", tags=["Time Off"])


def _extract_user_id(current_user: dict) -> Optional[UUID]:
    raw_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
    if not raw_id:
        return None
    try:
        return UUID(str(raw_id))
    except (ValueError, AttributeError):
        return None


# ------------------------------------------------------------------ #
# Time Off Types
# ------------------------------------------------------------------ #

@router.get("/types", response_model=list[TimeOffTypeOut])
async def list_time_off_types(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(select(TimeOffType).order_by(TimeOffType.name))
    return list(result.scalars().all())


@router.post("/types", response_model=TimeOffTypeOut, status_code=status.HTTP_201_CREATED)
async def create_time_off_type(
    type_in: TimeOffTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_writer),
):
    time_off_type = TimeOffType(**type_in.model_dump())
    db.add(time_off_type)
    await db.commit()
    await db.refresh(time_off_type)
    return time_off_type


# ------------------------------------------------------------------ #
# Allocations
# ------------------------------------------------------------------ #

@router.get("/allocations", response_model=list[AllocationOut])
async def list_allocations(
    employee_id: Optional[UUID] = Query(None, description="Filter by employee (HR_MANAGER+ only)"),
    time_off_type_id: Optional[UUID] = Query(None),
    approval_status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    roles = set(current_user.get("roles", []))
    if not roles & READ_ALL_ROLES:
        self_id = get_self_employee_id(current_user)
        if not self_id:
            raise HTTPException(status_code=403, detail="This account is not linked to an employee record")
        employee_id = self_id

    service = AllocationService(db)
    return await service.list_all(
        employee_id=employee_id,
        time_off_type_id=time_off_type_id,
        approval_status=approval_status,
        skip=skip,
        limit=limit,
    )


@router.post("/allocations", response_model=AllocationOut, status_code=status.HTTP_201_CREATED)
async def create_allocation(
    allocation_in: AllocationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_writer),
):
    service = AllocationService(db)
    return await service.create(allocation_in)


@router.get("/allocations/{allocation_id}", response_model=AllocationOut)
async def get_allocation(
    allocation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = AllocationService(db)
    allocation = await service.get_by_id(allocation_id)
    if allocation is None:
        raise HTTPException(status_code=404, detail="Allocation not found")

    roles = set(current_user.get("roles", []))
    if not roles & READ_ALL_ROLES:
        self_id = get_self_employee_id(current_user)
        if not self_id or allocation.employee_id != self_id:
            raise HTTPException(status_code=403, detail="This allocation does not belong to you")
    return allocation


@router.post("/allocations/{allocation_id}/approve", response_model=AllocationOut)
async def approve_allocation(
    allocation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_writer),
):
    service = AllocationService(db)
    return await service.approve(allocation_id)


# ------------------------------------------------------------------ #
# Requests
# ------------------------------------------------------------------ #

@router.get("/requests", response_model=list[TimeOffRequestOut])
async def list_requests(
    employee_id: Optional[UUID] = Query(None, description="Filter by employee (HR_MANAGER+ only)"),
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    roles = set(current_user.get("roles", []))
    if not roles & READ_ALL_ROLES:
        self_id = get_self_employee_id(current_user)
        if not self_id:
            raise HTTPException(status_code=403, detail="This account is not linked to an employee record")
        employee_id = self_id

    service = TimeOffRequestService(db)
    return await service.list_all(
        employee_id=employee_id, status=status_filter, skip=skip, limit=limit
    )


@router.post("/requests", response_model=TimeOffRequestOut, status_code=status.HTTP_201_CREATED)
async def create_request(
    request_in: TimeOffRequestCreate,
    db: AsyncSession = Depends(get_db),
    employee_id: UUID = Depends(require_employee_link),
):
    service = TimeOffRequestService(db)
    return await service.create(employee_id, request_in)


@router.get("/requests/{request_id}", response_model=TimeOffRequestOut)
async def get_request(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = TimeOffRequestService(db)
    request = await service.get_by_id(request_id)
    if request is None:
        raise HTTPException(status_code=404, detail="Time off request not found")

    roles = set(current_user.get("roles", []))
    if not roles & READ_ALL_ROLES:
        self_id = get_self_employee_id(current_user)
        if not self_id or request.employee_id != self_id:
            raise HTTPException(status_code=403, detail="This request does not belong to you")
    return request


@router.post("/requests/{request_id}/approve", response_model=TimeOffRequestOut)
async def approve_request(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_writer),
):
    service = TimeOffRequestService(db)
    actor_id = _extract_user_id(current_user)
    return await service.approve(request_id, actor_user_id=actor_id)


@router.post("/requests/{request_id}/refuse", response_model=TimeOffRequestOut)
async def refuse_request(
    request_id: UUID,
    refusal_in: TimeOffRequestRefuse,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_writer),
):
    service = TimeOffRequestService(db)
    actor_id = _extract_user_id(current_user)
    return await service.refuse(request_id, reason=refusal_in.reason, actor_user_id=actor_id)


# ------------------------------------------------------------------ #
# Internal: consumed by payroll-service (Pipeline 5)
# ------------------------------------------------------------------ #

@router.get("/work-entries", response_model=list[WorkEntrySummary])
async def get_work_entries(
    employee_id: UUID = Query(...),
    period_start: date = Query(...),
    period_end: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(
        require_any_role("HR_MANAGER", "HR_PAYROLL_USER", "HR_PAYROLL_MANAGER")
    ),
):
    service = TimeOffRequestService(db)
    return await service.get_work_entries(
        employee_id=employee_id, period_start=period_start, period_end=period_end
    )
