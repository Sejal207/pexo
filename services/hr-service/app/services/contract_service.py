"""
ContractService: business logic for Contract CRUD.

Key design rules:
- The EXCLUDE USING gist constraint on the DB enforces the overlap rule.
  We catch asyncpg's ExclusionViolationError and surface it as a clean 409.
- get_active(employee_id, date) is the canonical cross-pipeline API that payroll
  and attendance services call — never read a denormalized "current_contract_id".
- Every write produces an audit_log row in the same transaction.
"""
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.contract import Contract
from app.models.working_schedule import WorkingSchedule
from app.schemas.contract import ContractCreate, ContractUpdate
from app.services.audit_service import AuditService

# asyncpg raises this when an exclusion constraint fires
_EXCLUSION_SQLSTATE = "23P01"


class ContractService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._audit = AuditService(db)

    async def list_all(
        self,
        *,
        status: Optional[str] = None,
        department_id: Optional[UUID] = None,
        employee_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Contract]:
        stmt = select(Contract)
        if status:
            stmt = stmt.where(Contract.status == status)
        if department_id:
            stmt = stmt.where(Contract.department_id == department_id)
        if employee_id:
            stmt = stmt.where(Contract.employee_id == employee_id)
        stmt = stmt.offset(skip).limit(limit).order_by(Contract.start_date.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_by_employee(self, employee_id: UUID) -> list[Contract]:
        result = await self.db.execute(
            select(Contract)
            .where(Contract.employee_id == employee_id)
            .order_by(Contract.start_date.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, contract_id: UUID) -> Optional[Contract]:
        result = await self.db.execute(
            select(Contract).where(Contract.id == contract_id)
        )
        return result.scalar_one_or_none()

    async def get_active(self, employee_id: UUID, as_of: date) -> Contract:
        """
        Returns the single ACTIVE contract covering `as_of` date, or raises 404.
        This is the canonical endpoint for cross-service contract resolution.
        """
        stmt = select(Contract).where(
            and_(
                Contract.employee_id == employee_id,
                Contract.status == "ACTIVE",
                Contract.start_date <= as_of,
                or_(
                    Contract.end_date.is_(None),
                    Contract.end_date >= as_of,
                ),
            )
        )
        result = await self.db.execute(stmt)
        contract = result.scalar_one_or_none()
        if contract is None:
            raise HTTPException(
                status_code=404,
                detail=f"No active contract for employee {employee_id} on {as_of}",
            )
        return contract

    async def list_eligible_for_period(
        self,
        *,
        period_start: date,
        period_end: date,
        salary_structure_id: UUID,
        department_id: Optional[UUID] = None,
        contract_type: Optional[str] = None,
    ) -> list[dict]:
        """
        Pipeline 4 (payroll-service) eligibility resolution: every ACTIVE
        contract on `salary_structure_id` whose [start_date, end_date) range
        overlaps [period_start, period_end] — never a single as-of date, since
        a payrun spans a whole period. Working hours resolve the same way
        Pipeline 2 does: the contract's own schedule override, else the
        employee's default schedule.
        """
        stmt = (
            select(Contract)
            .options(selectinload(Contract.employee))
            .where(
                and_(
                    Contract.status == "ACTIVE",
                    Contract.salary_structure_id == salary_structure_id,
                    Contract.start_date <= period_end,
                    or_(Contract.end_date.is_(None), Contract.end_date >= period_start),
                )
            )
        )
        if department_id:
            stmt = stmt.where(Contract.department_id == department_id)
        if contract_type:
            stmt = stmt.where(Contract.contract_type == contract_type)

        result = await self.db.execute(stmt)
        contracts = list(result.scalars().all())

        schedule_ids = {
            c.working_schedule_id or (c.employee.default_working_schedule_id if c.employee else None)
            for c in contracts
        }
        schedule_ids.discard(None)

        hours_by_schedule: dict[UUID, float] = {}
        if schedule_ids:
            ws_result = await self.db.execute(
                select(WorkingSchedule.id, WorkingSchedule.total_weekly_hours).where(
                    WorkingSchedule.id.in_(schedule_ids)
                )
            )
            hours_by_schedule = {row[0]: row[1] for row in ws_result.all()}

        rows = []
        for c in contracts:
            resolved_schedule_id = c.working_schedule_id or (
                c.employee.default_working_schedule_id if c.employee else None
            )
            rows.append(
                {
                    "contract_id": c.id,
                    "employee_id": c.employee_id,
                    "employee_code": c.employee.employee_code if c.employee else None,
                    "employee_first_name": c.employee.first_name if c.employee else None,
                    "employee_last_name": c.employee.last_name if c.employee else None,
                    "contract_type": c.contract_type,
                    "start_date": c.start_date,
                    "end_date": c.end_date,
                    "wage_amount": c.wage_amount,
                    "wage_type": c.wage_type,
                    "salary_structure_id": c.salary_structure_id,
                    "department_id": c.department_id,
                    "job_position_id": c.job_position_id,
                    "working_hours": hours_by_schedule.get(resolved_schedule_id),
                }
            )
        return rows

    async def create(
        self,
        data: ContractCreate,
        *,
        actor_user_id: Optional[UUID] = None,
    ) -> Contract:
        contract = Contract(**data.model_dump())
        self.db.add(contract)
        try:
            await self.db.flush()
        except IntegrityError as exc:
            await self.db.rollback()
            # asyncpg SQLSTATE 23P01 = exclusion_violation
            orig = getattr(exc, "orig", None)
            pg_code = getattr(orig, "sqlstate", None) or getattr(orig, "pgcode", None)
            if pg_code == _EXCLUSION_SQLSTATE:
                raise HTTPException(
                    status_code=409,
                    detail="Contract dates overlap an existing ACTIVE contract for this employee.",
                ) from exc
            raise  # any other integrity error bubbles up as 500

        await self._audit.log(
            user_id=actor_user_id,
            entity_name="contract",
            entity_id=contract.id,
            action="CREATE",
            field_changes=data.model_dump(mode="json"),
        )
        await self.db.commit()
        await self.db.refresh(contract)
        return contract

    async def update(
        self,
        contract: Contract,
        data: ContractUpdate,
        *,
        actor_user_id: Optional[UUID] = None,
    ) -> Contract:
        update_dict = data.model_dump(exclude_none=True)
        if not update_dict:
            return contract

        before = {k: str(getattr(contract, k)) for k in update_dict}
        for key, value in update_dict.items():
            setattr(contract, key, value)

        self.db.add(contract)
        try:
            await self.db.flush()
        except IntegrityError as exc:
            await self.db.rollback()
            orig = getattr(exc, "orig", None)
            pg_code = getattr(orig, "sqlstate", None) or getattr(orig, "pgcode", None)
            if pg_code == _EXCLUSION_SQLSTATE:
                raise HTTPException(
                    status_code=409,
                    detail="Updated contract dates would overlap an existing ACTIVE contract.",
                ) from exc
            raise

        await self._audit.log(
            user_id=actor_user_id,
            entity_name="contract",
            entity_id=contract.id,
            action="UPDATE",
            field_changes={
                "before": before,
                "after": {k: str(v) for k, v in update_dict.items()},
            },
        )
        await self.db.commit()
        await self.db.refresh(contract)
        return contract
