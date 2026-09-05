from datetime import date
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies import require_writer, require_any_role
from app.schemas.contract import ContractCreate, ContractUpdate, ContractOut
from app.services.contract_service import ContractService

router = APIRouter(prefix="/contracts", tags=["Contracts"])


def _extract_user_id(current_user: dict) -> Optional[UUID]:
    raw_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
    if not raw_id:
        return None
    try:
        return UUID(str(raw_id))
    except (ValueError, AttributeError):
        return None


@router.get("/", response_model=list[ContractOut])
async def list_contracts(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by contract status"),
    department_id: Optional[UUID] = Query(None, description="Filter by department ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("HR_MANAGER", "HR_PAYROLL_MANAGER", "HR_PAYROLL_USER")),
):
    service = ContractService(db)
    return await service.list_all(
        status=status_filter,
        department_id=department_id,
        skip=skip,
        limit=limit,
    )


@router.get("/active", response_model=ContractOut)
async def get_active_contract(
    employee_id: UUID = Query(..., description="Employee UUID"),
    as_of: Optional[date] = Query(None, description="Date to check active status (defaults to today)"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("HR_MANAGER", "HR_PAYROLL_MANAGER", "HR_PAYROLL_USER", "EMPLOYEE")),
):
    """
    Canonical endpoint to resolve the active contract for an employee on a given date.
    MUST be declared before /{contract_id} so 'active' is not matched as a UUID.
    """
    target_date = as_of or date.today()
    service = ContractService(db)
    return await service.get_active(employee_id=employee_id, as_of=target_date)


@router.post("/", response_model=ContractOut, status_code=status.HTTP_201_CREATED)
async def create_contract(
    contract_in: ContractCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_writer),
):
    service = ContractService(db)
    actor_id = _extract_user_id(current_user)
    return await service.create(contract_in, actor_user_id=actor_id)


@router.get("/{contract_id}", response_model=ContractOut)
async def get_contract(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("HR_MANAGER", "HR_PAYROLL_MANAGER", "HR_PAYROLL_USER")),
):
    service = ContractService(db)
    contract = await service.get_by_id(contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return contract


@router.patch("/{contract_id}", response_model=ContractOut)
async def update_contract(
    contract_id: UUID,
    contract_in: ContractUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_writer),
):
    service = ContractService(db)
    contract = await service.get_by_id(contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    actor_id = _extract_user_id(current_user)
    return await service.update(contract, contract_in, actor_user_id=actor_id)
