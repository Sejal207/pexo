from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.payslip import MarkPaidResult, PayslipComputeResult, PayslipOut, PayslipWarnings


class EligibleEmployeesRequest(BaseModel):
    """
    Step 1 of the payrun wizard. Never writes to the DB — see PayrunService.
    `contract_type` stands in for the wireframe's "Employee Type" filter:
    schema.sql has no employee_type column, and contract_type (PERMANENT /
    FIXED_TERM / PROBATION / INTERN) is the closest real segmentation axis.
    """
    salary_structure_id: UUID
    period_start: date
    period_end: date
    department_id: Optional[UUID] = None
    contract_type: Optional[Literal["PERMANENT", "FIXED_TERM", "PROBATION", "INTERN"]] = None

    @field_validator("period_end")
    @classmethod
    def _end_after_start(cls, v: date, info) -> date:
        start = info.data.get("period_start")
        if start and v < start:
            raise ValueError("period_end must be on or after period_start")
        return v


class EligibleEmployeeOut(BaseModel):
    contract_id: UUID
    employee_id: UUID
    employee_code: str
    employee_name: str
    contract_type: str
    working_hours: Optional[Decimal] = None
    start_date: date
    end_date: Optional[date] = None
    wage_amount: Decimal
    wage_type: str


class PayrunCreate(BaseModel):
    """Step 2 -> Create Payrun. Committing requires an explicit employee_ids
    selection — eligibility alone never auto-includes anyone."""
    name: Optional[str] = None
    salary_structure_id: UUID
    period_start: date
    period_end: date
    employee_ids: list[UUID]

    @field_validator("period_end")
    @classmethod
    def _end_after_start(cls, v: date, info) -> date:
        start = info.data.get("period_start")
        if start and v < start:
            raise ValueError("period_end must be on or after period_start")
        return v

    @field_validator("employee_ids")
    @classmethod
    def _at_least_one(cls, v: list[UUID]) -> list[UUID]:
        if not v:
            raise ValueError("Select at least one employee")
        return v


class PayrunOut(BaseModel):
    id: UUID
    name: str
    period_start: date
    period_end: date
    salary_structure_id: UUID
    status: str
    created_by_user_id: Optional[UUID] = None
    computed_at: Optional[datetime] = None
    validated_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PayrunDetailOut(PayrunOut):
    payslips: list[PayslipOut] = []


class PayrunComputeResponse(BaseModel):
    results: list[PayslipComputeResult]


class PayrunValidateResponse(BaseModel):
    results: list[PayslipWarnings]


class PayrunMarkPaidResponse(MarkPaidResult):
    pass
