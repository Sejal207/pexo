from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceCreate


class AttendanceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_attendance(self, att_in: AttendanceCreate) -> Attendance:
        worked_hours = None
        status = att_in.status
        if att_in.check_in and att_in.check_out:
            seconds = Decimal(str((att_in.check_out - att_in.check_in).total_seconds()))
            worked_hours = (seconds / Decimal('3600')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        elif att_in.check_in and not att_in.check_out:
            status = 'MISSING_CHECKOUT'

        record = Attendance(
            employee_id=att_in.employee_id,
            work_date=att_in.work_date,
            check_in=att_in.check_in,
            check_out=att_in.check_out,
            worked_hours=worked_hours,
            status=status,
            is_manual_correction=True,
            correction_reason=att_in.correction_reason,
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record
