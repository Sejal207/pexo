from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import require_writer, require_any_role
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentOut

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("/", response_model=list[DepartmentOut])
async def list_departments(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("HR_MANAGER", "HR_PAYROLL_MANAGER", "HR_PAYROLL_USER", "EMPLOYEE")),
):
    result = await db.execute(select(Department).order_by(Department.name))
    return list(result.scalars().all())


@router.post("/", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
async def create_department(
    dept_in: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_writer),
):
    dept = Department(**dept_in.model_dump())
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept


@router.get("/{department_id}", response_model=DepartmentOut)
async def get_department(
    department_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("HR_MANAGER", "HR_PAYROLL_MANAGER", "HR_PAYROLL_USER", "EMPLOYEE")),
):
    result = await db.execute(select(Department).where(Department.id == department_id))
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return dept


@router.patch("/{department_id}", response_model=DepartmentOut)
async def update_department(
    department_id: UUID,
    dept_in: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_writer),
):
    result = await db.execute(select(Department).where(Department.id == department_id))
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    update_data = dept_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dept, field, value)

    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept
