from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceCreate

class AttendanceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_attendance(self, att_in: AttendanceCreate) -> Attendance:
        record = Attendance(**att_in.model_dump())
        if record.check_in and record.check_out:
            duration = (record.check_out - record.check_in).total_seconds() / 3600.0
            record.worked_hours = max(0.0, round(duration, 2))
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record
