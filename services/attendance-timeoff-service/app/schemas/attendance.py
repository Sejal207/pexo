from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AttendanceOut(BaseModel):
    id: UUID
    employee_id: UUID
    work_date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    worked_hours: Optional[Decimal] = None
    overtime_hours: Optional[Decimal] = None
    status: str
    is_manual_correction: bool
    corrected_by_user_id: Optional[UUID] = None
    correction_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AttendanceCorrection(BaseModel):
    """HR_MANAGER+ manual correction.

    worked_hours/overtime_hours/status are never accepted from the client — they
    are always recomputed server-side from the (possibly corrected) timestamps.
    """
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    reason: str


class WidgetStatusOut(BaseModel):
    open: bool
    since: Optional[datetime] = None
    elapsed_seconds: Optional[int] = None
    attendance_id: Optional[UUID] = None
