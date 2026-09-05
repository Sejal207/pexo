from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class EmployeeBase(BaseModel):
    employee_code: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    date_of_joining: date
    status: str = "ACTIVE"
    department_id: Optional[int] = None
    job_position_id: Optional[int] = None
    working_schedule_id: Optional[int] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    department_id: Optional[int] = None
    job_position_id: Optional[int] = None
    working_schedule_id: Optional[int] = None

class EmployeeOut(EmployeeBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
