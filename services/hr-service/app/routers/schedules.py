from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import require_writer, require_any_role
from app.schemas.working_schedule import (
    WorkingScheduleCreate,
    WorkingScheduleUpdate,
    WorkingScheduleOut,
    WorkingScheduleDetail,
)
from app.services.working_schedule_service import WorkingScheduleService

router = APIRouter(prefix="/schedules", tags=["Working Schedules"])


@router.get("/", response_model=list[WorkingScheduleOut])
async def list_schedules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("HR_MANAGER", "HR_PAYROLL_MANAGER", "HR_PAYROLL_USER", "EMPLOYEE")),
):
    service = WorkingScheduleService(db)
    return await service.get_all(skip=skip, limit=limit)


@router.post("/", response_model=WorkingScheduleDetail, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule_in: WorkingScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_writer),
):
    service = WorkingScheduleService(db)
    return await service.create(schedule_in)


@router.get("/{schedule_id}", response_model=WorkingScheduleDetail)
async def get_schedule(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("HR_MANAGER", "HR_PAYROLL_MANAGER", "HR_PAYROLL_USER", "EMPLOYEE")),
):
    service = WorkingScheduleService(db)
    sched = await service.get_by_id(schedule_id)
    if not sched:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Working schedule not found")
    return sched


@router.patch("/{schedule_id}", response_model=WorkingScheduleDetail)
async def update_schedule(
    schedule_id: UUID,
    schedule_in: WorkingScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_writer),
):
    service = WorkingScheduleService(db)
    sched = await service.get_by_id(schedule_id)
    if not sched:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Working schedule not found")
    return await service.update(sched, schedule_in)
