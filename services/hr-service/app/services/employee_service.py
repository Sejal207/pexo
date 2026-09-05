"""
EmployeeService: business logic for Employee CRUD.
- All writes produce an audit_log row in the same transaction.
- get_by_id returns EmployeeDetail-compatible data including contracts_count.
- attendance_count and time_off_count are always 0 until those services exist.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.models.contract import Contract
from app.models.employee_bank_account import EmployeeBankAccount
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.services.audit_service import AuditService


class EmployeeService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._audit = AuditService(db)

    async def get_all(
        self,
        *,
        department_id: Optional[UUID] = None,
        employment_status: Optional[str] = None,
        job_position_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Employee]:
        stmt = select(Employee)
        if department_id:
            stmt = stmt.where(Employee.department_id == department_id)
        if employment_status:
            stmt = stmt.where(Employee.employment_status == employment_status)
        if job_position_id:
            stmt = stmt.where(Employee.job_position_id == job_position_id)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, employee_id: UUID) -> Optional[Employee]:
        """Returns Employee ORM object or None."""
        result = await self.db.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        return result.scalar_one_or_none()

    async def get_contracts_count(self, employee_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count()).where(Contract.employee_id == employee_id)
        )
        return result.scalar_one()

    async def list_bank_accounts(self, employee_id: UUID) -> list[EmployeeBankAccount]:
        """
        Consumed by payroll-service (Pipeline 5) to flag "A/C missing" during
        payrun Validate. Also usable directly by HR/the employee themselves.
        """
        result = await self.db.execute(
            select(EmployeeBankAccount)
            .where(EmployeeBankAccount.employee_id == employee_id)
            .order_by(EmployeeBankAccount.is_primary.desc(), EmployeeBankAccount.created_at)
        )
        return list(result.scalars().all())

    async def create(
        self,
        data: EmployeeCreate,
        *,
        actor_user_id: Optional[UUID] = None,
    ) -> Employee:
        employee = Employee(**data.model_dump())
        self.db.add(employee)
        await self.db.flush()  # get generated id before commit
        await self._audit.log(
            user_id=actor_user_id,
            entity_name="employee",
            entity_id=employee.id,
            action="CREATE",
            field_changes=data.model_dump(mode="json"),
        )
        await self.db.commit()
        await self.db.refresh(employee)
        return employee

    async def update(
        self,
        employee: Employee,
        data: EmployeeUpdate,
        *,
        actor_user_id: Optional[UUID] = None,
    ) -> Employee:
        update_dict = data.model_dump(exclude_none=True)
        if not update_dict:
            return employee  # nothing to change

        before = {k: str(getattr(employee, k)) for k in update_dict}
        for key, value in update_dict.items():
            setattr(employee, key, value)

        self.db.add(employee)
        await self.db.flush()
        await self._audit.log(
            user_id=actor_user_id,
            entity_name="employee",
            entity_id=employee.id,
            action="UPDATE",
            field_changes={"before": before, "after": {k: str(v) for k, v in update_dict.items()}},
        )
        await self.db.commit()
        await self.db.refresh(employee)
        return employee
