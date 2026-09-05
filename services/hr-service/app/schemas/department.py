from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DepartmentCreate(BaseModel):
    name: str
    parent_department_id: Optional[UUID] = None
    manager_employee_id: Optional[UUID] = None


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    parent_department_id: Optional[UUID] = None
    manager_employee_id: Optional[UUID] = None


class DepartmentOut(BaseModel):
    id: UUID
    name: str
    parent_department_id: Optional[UUID] = None
    manager_employee_id: Optional[UUID] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
