from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class TimeOffTypeBase(BaseModel):
    name: str
    code: str
    is_paid: bool = True

class TimeOffTypeCreate(TimeOffTypeBase):
    pass

class TimeOffTypeOut(TimeOffTypeBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TimeOffRequestBase(BaseModel):
    employee_id: int
    time_off_type_id: int
    date_from: date
    date_to: date
    number_of_days: float
    reason: Optional[str] = None
    status: str = "DRAFT"

class TimeOffRequestCreate(TimeOffRequestBase):
    pass

class TimeOffRequestOut(TimeOffRequestBase):
    id: int
    approved_by: Optional[int] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
