from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.salary_rule import SalaryRule
from app.schemas.salary_rule import SalaryRuleCreate


class SalaryRuleService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_all(self, *, structure_id: Optional[UUID] = None) -> list[SalaryRule]:
        if structure_id is None:
            result = await self.db.execute(select(SalaryRule).order_by(SalaryRule.category, SalaryRule.code))
            return list(result.scalars().all())

        from app.models.salary_structure_rule import SalaryStructureRule

        stmt = (
            select(SalaryRule)
            .join(SalaryStructureRule, SalaryStructureRule.salary_rule_id == SalaryRule.id)
            .where(SalaryStructureRule.salary_structure_id == structure_id)
            .order_by(SalaryStructureRule.sequence)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, rule_id: UUID) -> Optional[SalaryRule]:
        result = await self.db.execute(select(SalaryRule).where(SalaryRule.id == rule_id))
        return result.scalar_one_or_none()

    async def create(self, data: SalaryRuleCreate) -> SalaryRule:
        rule = SalaryRule(**data.model_dump())
        self.db.add(rule)
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            orig = getattr(exc, "orig", None)
            pg_code = getattr(orig, "sqlstate", None) or getattr(orig, "pgcode", None)
            if pg_code == "23505":  # unique_violation
                raise HTTPException(
                    status_code=409, detail="A salary rule with this code already exists."
                ) from exc
            if pg_code == "23503":  # foreign_key_violation
                raise HTTPException(
                    status_code=422,
                    detail=f"percentage_of_rule_code '{data.percentage_of_rule_code}' does not "
                    "reference an existing salary rule.",
                ) from exc
            raise
        await self.db.refresh(rule)
        return rule
