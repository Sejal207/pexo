from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

RuleCategory = Literal["BASIC", "ALLOWANCE", "GROSS", "DEDUCTION", "EMPLOYER_CONTRIBUTION", "NET"]
ComputationType = Literal["FIXED", "PERCENTAGE", "FORMULA"]


class SalaryRuleCreate(BaseModel):
    code: str
    name: str
    category: RuleCategory
    computation_type: ComputationType
    fixed_amount: Optional[Decimal] = None
    percentage_of_rule_code: Optional[str] = None
    percentage_value: Optional[Decimal] = None
    formula_expression: Optional[str] = None
    is_active: bool = True

    @model_validator(mode="after")
    def _check_computation_fields(self) -> "SalaryRuleCreate":
        """Mirrors the DB CHECK constraint client-side for a clean 422
        instead of a raw IntegrityError."""
        if self.computation_type == "FIXED" and self.fixed_amount is None:
            raise ValueError("fixed_amount is required when computation_type is FIXED")
        if self.computation_type == "PERCENTAGE" and (
            self.percentage_of_rule_code is None or self.percentage_value is None
        ):
            raise ValueError(
                "percentage_of_rule_code and percentage_value are required when "
                "computation_type is PERCENTAGE"
            )
        if self.computation_type == "FORMULA" and not self.formula_expression:
            raise ValueError("formula_expression is required when computation_type is FORMULA")
        return self


class SalaryRuleOut(BaseModel):
    id: UUID
    code: str
    name: str
    category: str
    computation_type: str
    fixed_amount: Optional[Decimal] = None
    percentage_of_rule_code: Optional[str] = None
    percentage_value: Optional[Decimal] = None
    formula_expression: Optional[str] = None
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
