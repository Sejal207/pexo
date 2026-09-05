from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.dependencies import require_structure_writer
from app.schemas.salary_rule import SalaryRuleCreate, SalaryRuleOut
from app.services.salary_rule_service import SalaryRuleService

router = APIRouter(prefix="/salary-rules", tags=["Salary Rules"])


@router.get("/", response_model=list[SalaryRuleOut])
async def list_rules(
    structure_id: Optional[UUID] = Query(None, description="Filter to one structure's rules, in sequence order"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = SalaryRuleService(db)
    return await service.list_all(structure_id=structure_id)


@router.post("/", response_model=SalaryRuleOut, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule_in: SalaryRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_structure_writer),
):
    service = SalaryRuleService(db)
    return await service.create(rule_in)
