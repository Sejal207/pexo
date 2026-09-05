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

from app.models.contract import Contract
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
        skip: int = 0,
        limit: int = 100,
    ) -> list[Contract]:
        stmt = select(Contract)
        if status:
            stmt = stmt.where(Contract.status == status)
        if department_id:
            stmt = stmt.where(Contract.department_id == department_id)
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
