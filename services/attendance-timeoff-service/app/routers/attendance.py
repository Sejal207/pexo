from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, security
from app.dependencies import READ_ALL_ROLES, get_self_employee_id, require_employee_link, require_writer
from app.schemas.attendance import AttendanceCorrection, AttendanceOut, WidgetStatusOut
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Attendance"])


def _extract_user_id(current_user: dict) -> Optional[UUID]:
    raw_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
    if not raw_id:
        return None
    try:
        return UUID(str(raw_id))
    except (ValueError, AttributeError):
        return None


def _assert_owner_or_manager(record_employee_id: UUID, current_user: dict) -> None:
    roles = set(current_user.get("roles", []))
    if roles & READ_ALL_ROLES:
        return
    self_id = get_self_employee_id(current_user)
    if self_id and self_id == record_employee_id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access to other employees' attendance is not allowed",
    )


@router.post("/check-in", response_model=AttendanceOut, status_code=status.HTTP_201_CREATED)
async def check_in(
    db: AsyncSession = Depends(get_db),
    employee_id: UUID = Depends(require_employee_link),
):
    service = AttendanceService(db)
    return await service.check_in(employee_id)


@router.get("/widget-status", response_model=WidgetStatusOut)
async def widget_status(
    db: AsyncSession = Depends(get_db),
    employee_id: UUID = Depends(require_employee_link),
):
    service = AttendanceService(db)
    return await service.get_widget_status(employee_id)


@router.get("/", response_model=list[AttendanceOut])
async def list_attendance(
    employee_id: Optional[UUID] = Query(None, description="Filter by employee (HR_MANAGER+ only)"),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
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

    service = AttendanceService(db)
    return await service.list_all(
        employee_id=employee_id,
        date_from=date_from,
        date_to=date_to,
        status=status_filter,
        skip=skip,
        limit=limit,
    )


@router.get("/{attendance_id}", response_model=AttendanceOut)
async def get_attendance(
    attendance_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = AttendanceService(db)
    record = await service.get_by_id(attendance_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found")
    _assert_owner_or_manager(record.employee_id, current_user)
    return record


@router.post("/{attendance_id}/check-out", response_model=AttendanceOut)
async def check_out(
    attendance_id: UUID,
    db: AsyncSession = Depends(get_db),
    employee_id: UUID = Depends(require_employee_link),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    service = AttendanceService(db)
    return await service.check_out(attendance_id, employee_id, bearer_token=credentials.credentials)


@router.patch("/{attendance_id}", response_model=AttendanceOut)
async def correct_attendance(
    attendance_id: UUID,
    correction_in: AttendanceCorrection,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_writer),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    service = AttendanceService(db)
    actor_id = _extract_user_id(current_user)
    return await service.correct(
        attendance_id, correction_in, actor_user_id=actor_id, bearer_token=credentials.credentials
    )
