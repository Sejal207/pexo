from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class AttendanceBase(BaseModel):
    employee_id: int
    date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    worked_hours: float = 0.0
    status: str = "PRESENT"

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceOut(AttendanceBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
