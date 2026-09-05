from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SalaryStructureCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True


class SalaryStructureOut(BaseModel):
    id: UUID
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class StructureRuleAttach(BaseModel):
    """Attach an existing SalaryRule to a structure at a given sequence
    position. Rules run in ascending sequence order at compute time."""
    salary_rule_id: UUID
    sequence: int


class StructureRuleOut(BaseModel):
    id: UUID
    salary_structure_id: UUID
    salary_rule_id: UUID
    sequence: int
    rule_code: str
    rule_name: str
    rule_category: str
    model_config = ConfigDict(from_attributes=True)


class SalaryStructureDetailOut(SalaryStructureOut):
    rules: list[StructureRuleOut] = []
