from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ContractBase(BaseModel):
    contract_reference: str
    employee_id: int
    contract_type: str = "FULL_TIME"
    wage: float
    date_start: date
    date_end: Optional[date] = None
    status: str = "ACTIVE"

class ContractCreate(ContractBase):
    pass

class ContractOut(ContractBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
