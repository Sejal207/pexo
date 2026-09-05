from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceCreate, AttendanceOut
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.get("/", response_model=list[AttendanceOut])
async def list_attendance(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Attendance))
    return result.scalars().all()

@router.post("/", response_model=AttendanceOut)
async def create_attendance(att_in: AttendanceCreate, db: AsyncSession = Depends(get_db)):
    service = AttendanceService(db)
    return await service.record_attendance(att_in)
