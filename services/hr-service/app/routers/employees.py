from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import require_writer, require_any_role, scope_to_own_employee
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeOut,
    EmployeeDetail,
    EmployeeBankAccountOut,
)
from app.schemas.contract import ContractOut
from app.services.employee_service import EmployeeService
from app.services.contract_service import ContractService

router = APIRouter(prefix="/employees", tags=["Employees"])


def _extract_user_id(current_user: dict) -> Optional[UUID]:
    raw_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
    if not raw_id:
        return None
    try:
        return UUID(str(raw_id))
    except (ValueError, AttributeError):
        return None


@router.get("/", response_model=list[EmployeeOut])
async def list_employees(
    department_id: Optional[UUID] = Query(None, description="Filter by department ID"),
    employment_status: Optional[str] = Query(None, description="Filter by employment status"),
    job_position_id: Optional[UUID] = Query(None, description="Filter by job position ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("HR_MANAGER", "HR_PAYROLL_MANAGER", "HR_PAYROLL_USER", "EMPLOYEE")),
):
    service = EmployeeService(db)
    return await service.get_all(
        department_id=department_id,
        employment_status=employment_status,
        job_position_id=job_position_id,
        skip=skip,
        limit=limit,
    )


@router.post("/", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_in: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_writer),
):
    service = EmployeeService(db)
    actor_id = _extract_user_id(current_user)
    return await service.create(employee_in, actor_user_id=actor_id)


@router.get("/{employee_id}", response_model=EmployeeDetail)
async def get_employee(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(scope_to_own_employee),
):
    service = EmployeeService(db)
    emp = await service.get_by_id(employee_id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    contracts_count = await service.get_contracts_count(employee_id)

    emp_detail = EmployeeDetail.model_validate(emp)
    emp_detail.contracts_count = contracts_count
    emp_detail.attendance_count = 0
    emp_detail.time_off_count = 0
    return emp_detail


@router.patch("/{employee_id}", response_model=EmployeeOut)
async def update_employee(
    employee_id: UUID,
    employee_in: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_writer),
):
    service = EmployeeService(db)
    emp = await service.get_by_id(employee_id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    actor_id = _extract_user_id(current_user)
    return await service.update(emp, employee_in, actor_user_id=actor_id)


@router.get("/{employee_id}/contracts", response_model=list[ContractOut])
async def get_employee_contracts(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("HR_MANAGER", "HR_PAYROLL_MANAGER", "HR_PAYROLL_USER")),
):
    emp_service = EmployeeService(db)
    emp = await emp_service.get_by_id(employee_id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    contract_service = ContractService(db)
    return await contract_service.list_by_employee(employee_id)


@router.get("/{employee_id}/bank-accounts", response_model=list[EmployeeBankAccountOut])
async def get_employee_bank_accounts(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(
        require_any_role("HR_MANAGER", "HR_PAYROLL_MANAGER", "HR_PAYROLL_USER")
    ),
):
    """Internal, consumed by payroll-service (Pipeline 5) to check for a
    missing-bank-account warning during payrun Validate."""
    emp_service = EmployeeService(db)
    emp = await emp_service.get_by_id(employee_id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return await emp_service.list_bank_accounts(employee_id)
