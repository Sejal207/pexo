from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.attendance import ATTENDANCE_STATUSES


class AttendanceCreate(BaseModel):
    employee_id: UUID
    work_date: date
    check_in: datetime | None = None
    check_out: datetime | None = None
    status: str = 'PRESENT'
    correction_reason: str | None = None

    @model_validator(mode='after')
    def validate_punches(self):
        if self.status not in ATTENDANCE_STATUSES:
            raise ValueError('Invalid attendance status')
        if self.check_in and self.check_out and self.check_out <= self.check_in:
            raise ValueError('check_out must be later than check_in')
        return self


class AttendanceOut(BaseModel):
    id: UUID
    employee_id: UUID
    work_date: date
    check_in: datetime | None
    check_out: datetime | None
    worked_hours: Decimal | None
    status: str
    is_manual_correction: bool
    corrected_by_user_id: UUID | None
    correction_reason: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
