from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.salary_rule import SalaryRule
from app.models.salary_structure import SalaryStructure
from app.models.salary_structure_rule import SalaryStructureRule
from app.schemas.salary_structure import SalaryStructureCreate, StructureRuleAttach


class SalaryStructureService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_all(self) -> list[SalaryStructure]:
        result = await self.db.execute(select(SalaryStructure).order_by(SalaryStructure.name))
        return list(result.scalars().all())

    async def get_by_id(self, structure_id: UUID) -> Optional[SalaryStructure]:
        result = await self.db.execute(
            select(SalaryStructure)
            .options(selectinload(SalaryStructure.structure_rules).selectinload(SalaryStructureRule.salary_rule))
            .where(SalaryStructure.id == structure_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: SalaryStructureCreate) -> SalaryStructure:
        structure = SalaryStructure(**data.model_dump())
        self.db.add(structure)
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise HTTPException(
                status_code=409, detail="A salary structure with this code already exists."
            ) from exc
        await self.db.refresh(structure)
        return structure

    async def attach_rule(self, structure_id: UUID, data: StructureRuleAttach) -> SalaryStructureRule:
        structure = await self.get_by_id(structure_id)
        if structure is None:
            raise HTTPException(status_code=404, detail="Salary structure not found")

        rule_result = await self.db.execute(select(SalaryRule).where(SalaryRule.id == data.salary_rule_id))
        rule = rule_result.scalar_one_or_none()
        if rule is None:
            raise HTTPException(status_code=404, detail="Salary rule not found")

        link = SalaryStructureRule(
            salary_structure_id=structure_id,
            salary_rule_id=data.salary_rule_id,
            sequence=data.sequence,
        )
        self.db.add(link)
        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="This rule is already attached to the structure, or its sequence "
                "position is already taken.",
            ) from exc
        await self.db.refresh(link)
        link.salary_rule = rule
        return link

    async def detach_rule(self, structure_id: UUID, link_id: UUID) -> None:
        result = await self.db.execute(
            select(SalaryStructureRule).where(
                SalaryStructureRule.id == link_id,
                SalaryStructureRule.salary_structure_id == structure_id,
            )
        )
        link = result.scalar_one_or_none()
        if link is None:
            raise HTTPException(status_code=404, detail="Structure/rule link not found")
        await self.db.delete(link)
        await self.db.commit()
