from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ContractCreate(BaseModel):
    employee_id: UUID
    contract_type: Literal["PERMANENT", "FIXED_TERM", "PROBATION", "INTERN"]
    start_date: date
    end_date: Optional[date] = None          # None = open-ended
    wage_amount: Decimal
    wage_type: Literal["MONTHLY", "HOURLY"] = "MONTHLY"
    salary_structure_id: UUID
    working_schedule_id: Optional[UUID] = None
    department_id: Optional[UUID] = None     # snapshot at signing time
    job_position_id: Optional[UUID] = None   # snapshot at signing time
    signed_date: Optional[date] = None


class ContractUpdate(BaseModel):
    """Any subset — typical use: expire (set end_date), change status, or correct wage."""
    end_date: Optional[date] = None
    wage_amount: Optional[Decimal] = None
    wage_type: Optional[Literal["MONTHLY", "HOURLY"]] = None
    working_schedule_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    job_position_id: Optional[UUID] = None
    status: Optional[Literal["DRAFT", "ACTIVE", "EXPIRED", "CANCELLED"]] = None
    signed_date: Optional[date] = None


class ContractOut(BaseModel):
    id: UUID
    employee_id: UUID
    contract_type: str
    start_date: date
    end_date: Optional[date] = None
    wage_amount: Decimal
    wage_type: str
    salary_structure_id: UUID
    working_schedule_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    job_position_id: Optional[UUID] = None
    status: str
    signed_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
