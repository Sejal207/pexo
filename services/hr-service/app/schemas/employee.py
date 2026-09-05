from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict


class EmployeeCreate(BaseModel):
    employee_code: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    date_joined: date
    address_line: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    department_id: Optional[UUID] = None
    job_position_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    default_working_schedule_id: Optional[UUID] = None


class EmployeeUpdate(BaseModel):
    """All fields optional — any subset can be patched."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    address_line: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    date_exit: Optional[date] = None
    profile_image_url: Optional[str] = None
    department_id: Optional[UUID] = None
    job_position_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    default_working_schedule_id: Optional[UUID] = None
    employment_status: Optional[Literal["ACTIVE", "INACTIVE", "TERMINATED", "ON_LEAVE"]] = None


class EmployeeOut(BaseModel):
    """Lightweight response — used for list views."""
    id: UUID
    employee_code: str
    first_name: str
    last_name: str
    email: str
    employment_status: str
    department_id: Optional[UUID] = None
    job_position_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    date_joined: date
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class EmployeeDetail(EmployeeOut):
    """Full response for GET /employees/{id} — includes private fields + smart-button counts."""
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    date_exit: Optional[date] = None
    address_line: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    profile_image_url: Optional[str] = None
    default_working_schedule_id: Optional[UUID] = None
    # Smart-button counts: filled by service layer (0 until sibling services exist)
    contracts_count: int = 0
    attendance_count: int = 0
    time_off_count: int = 0
