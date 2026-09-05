from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PayslipLineOut(BaseModel):
    id: UUID
    salary_rule_id: Optional[UUID] = None
    salary_rule_code: str
    # Live-joined against salary_rule at read time (schema.sql doesn't
    # denormalize these onto payslip_line) — null if the rule was since
    # deleted, since salary_rule_id is ON DELETE SET NULL.
    rule_name: Optional[str] = None
    category: Optional[str] = None
    sequence: int
    amount: Decimal
    computation_detail: Optional[dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)


class PayslipOut(BaseModel):
    id: UUID
    payrun_id: UUID
    employee_id: UUID
    contract_id: UUID
    period_start: date
    period_end: date
    worked_days: Optional[Decimal] = None
    status: str
    gross_amount: Optional[Decimal] = None
    net_amount: Optional[Decimal] = None
    has_warning: bool
    warning_notes: Optional[str] = None
    pdf_url: Optional[str] = None
    sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PayslipDetailOut(PayslipOut):
    lines: list[PayslipLineOut] = []


class PayslipComputeResult(BaseModel):
    payslip_id: UUID
    employee_id: UUID
    status: str
    gross_amount: Optional[Decimal] = None
    net_amount: Optional[Decimal] = None
    error: Optional[str] = None


class PayslipWarnings(BaseModel):
    payslip_id: UUID
    employee_id: UUID
    warnings: list[str] = []
    blocking: bool = False


class MarkPaidResult(BaseModel):
    task_ids: list[str]
