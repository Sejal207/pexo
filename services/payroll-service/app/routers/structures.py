from uuid import UUID

from app.services.salary_structure_service import SalaryStructureService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.dependencies import require_structure_writer
from app.schemas.salary_structure import (
    SalaryStructureCreate,
    SalaryStructureDetailOut,
    SalaryStructureOut,
    StructureRuleAttach,
    StructureRuleOut,
)

router = APIRouter(prefix="/salary-structures", tags=["Salary Structures"])


def _structure_to_detail(structure) -> SalaryStructureDetailOut:
    return SalaryStructureDetailOut(
        id=structure.id,
        name=structure.name,
        code=structure.code,
        description=structure.description,
        is_active=structure.is_active,
        created_at=structure.created_at,
        updated_at=structure.updated_at,
        rules=[
            StructureRuleOut(
                id=link.id,
                salary_structure_id=link.salary_structure_id,
                salary_rule_id=link.salary_rule_id,
                sequence=link.sequence,
                rule_code=link.salary_rule.code,
                rule_name=link.salary_rule.name,
                rule_category=link.salary_rule.category,
            )
            for link in structure.structure_rules
        ],
    )


@router.get("/", response_model=list[SalaryStructureOut])
async def list_structures(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = SalaryStructureService(db)
    return await service.list_all()


@router.post("/", response_model=SalaryStructureOut, status_code=status.HTTP_201_CREATED)
async def create_structure(
    structure_in: SalaryStructureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_structure_writer),
):
    service = SalaryStructureService(db)
    return await service.create(structure_in)


@router.get("/{structure_id}", response_model=SalaryStructureDetailOut)
async def get_structure(
    structure_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = SalaryStructureService(db)
    structure = await service.get_by_id(structure_id)
    if structure is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salary structure not found")
    return _structure_to_detail(structure)


@router.post(
    "/{structure_id}/rules", response_model=StructureRuleOut, status_code=status.HTTP_201_CREATED
)
async def attach_rule(
    structure_id: UUID,
    rule_in: StructureRuleAttach,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_structure_writer),
):
    """Attach an existing salary rule to this structure at a given sequence
    position. Not in the Pipeline 5 spec's endpoint table, but necessary
    plumbing: without it a structure could never actually have any rules."""
    service = SalaryStructureService(db)
    link = await service.attach_rule(structure_id, rule_in)
    return StructureRuleOut(
        id=link.id,
        salary_structure_id=link.salary_structure_id,
        salary_rule_id=link.salary_rule_id,
        sequence=link.sequence,
        rule_code=link.salary_rule.code,
        rule_name=link.salary_rule.name,
        rule_category=link.salary_rule.category,
    )


@router.delete("/{structure_id}/rules/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def detach_rule(
    structure_id: UUID,
    link_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_structure_writer),
):
    service = SalaryStructureService(db)
    await service.detach_rule(structure_id, link_id)
