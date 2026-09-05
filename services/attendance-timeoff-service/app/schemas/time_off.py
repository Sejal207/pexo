from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------- #
# Time Off Type
# ---------------------------------------------------------------------- #

class TimeOffTypeCreate(BaseModel):
    name: str
    unit: Literal["DAYS", "HOURS"] = "DAYS"
    requires_allocation: bool = True
    requires_approval: bool = True
    affects_payroll: bool = False
    color: Optional[str] = None
    payroll_work_entry_code: Optional[str] = None


class TimeOffTypeOut(BaseModel):
    id: UUID
    name: str
    unit: str
    requires_allocation: bool
    requires_approval: bool
    affects_payroll: bool
    color: Optional[str] = None
    payroll_work_entry_code: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------- #
# Allocation
# ---------------------------------------------------------------------- #

class AllocationCreate(BaseModel):
    employee_id: UUID
    time_off_type_id: UUID
    allocated_amount: Decimal
    valid_from: date
    valid_to: date


class AllocationOut(BaseModel):
    id: UUID
    employee_id: UUID
    time_off_type_id: UUID
    allocated_amount: Decimal
    taken_amount: Decimal
    remaining_amount: Decimal
    valid_from: date
    valid_to: date
    approval_status: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------- #
# Request
# ---------------------------------------------------------------------- #

class TimeOffRequestCreate(BaseModel):
    time_off_type_id: UUID
    allocation_id: Optional[UUID] = None
    start_date: date
    end_date: date
    duration: Decimal
    reason: Optional[str] = None


class TimeOffRequestRefuse(BaseModel):
    reason: str


class TimeOffRequestOut(BaseModel):
    id: UUID
    employee_id: UUID
    time_off_type_id: UUID
    allocation_id: Optional[UUID] = None
    start_date: date
    end_date: date
    duration: Decimal
    status: str
    approved_by_user_id: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------- #
# Internal: consumed by payroll-service (Pipeline 5)
# ---------------------------------------------------------------------- #

class WorkEntrySummary(BaseModel):
    payroll_work_entry_code: str
    total_duration: Decimal
