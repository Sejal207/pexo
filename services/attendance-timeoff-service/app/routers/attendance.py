from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import String, cast, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceCreate, AttendanceOut
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix='/attendance', tags=['Attendance'])


@router.get('/', response_model=list[AttendanceOut])
async def list_attendance(
    employee_id: UUID | None = None,
    date: date | None = None,
    search: str | None = Query(default=None, min_length=1),
    db: AsyncSession = Depends(get_db),
):
    statement = select(Attendance).order_by(Attendance.work_date.desc(), Attendance.check_in.desc())
    if employee_id:
        statement = statement.where(Attendance.employee_id == employee_id)
    if date:
        statement = statement.where(Attendance.work_date == date)
    if search:
        pattern = f'%{search.strip()}%'
        statement = statement.where(or_(cast(Attendance.employee_id, String).ilike(pattern), Attendance.status.ilike(pattern)))
    result = await db.execute(statement)
    return result.scalars().all()


@router.post('/', response_model=AttendanceOut, status_code=201)
async def create_attendance(att_in: AttendanceCreate, db: AsyncSession = Depends(get_db)):
    service = AttendanceService(db)
    return await service.record_attendance(att_in)
