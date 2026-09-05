from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import security
from app.dependencies import extract_user_id, require_payroll_user
from app.schemas.payrun import (
    EligibleEmployeeOut,
    EligibleEmployeesRequest,
    PayrunCreate,
    PayrunComputeResponse,
    PayrunDetailOut,
    PayrunMarkPaidResponse,
    PayrunOut,
    PayrunValidateResponse,
)
from app.schemas.payslip import MarkPaidResult
from app.services.payrun_service import PayrunService

router = APIRouter(prefix="/payruns", tags=["Payrun Wizard"])


@router.post("/eligible-employees", response_model=list[EligibleEmployeeOut])
async def get_eligible_employees(
    request_in: EligibleEmployeesRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_payroll_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Step 1 -> Step 2 handoff. Read-only: never writes to the DB, no matter
    what the caller does with the result.
    """
    service = PayrunService(db)
    return await service.get_eligible_employees(request_in, bearer_token=credentials.credentials)


@router.post("/", response_model=PayrunDetailOut, status_code=status.HTTP_201_CREATED)
async def create_payrun(
    payrun_in: PayrunCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_payroll_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """The only endpoint that commits: one payrun + one DRAFT payslip per
    selected employee, atomically."""
    service = PayrunService(db)
    actor_id = extract_user_id(current_user)
    return await service.create_payrun(
        payrun_in, bearer_token=credentials.credentials, actor_user_id=actor_id
    )


@router.get("/", response_model=list[PayrunOut])
async def list_payruns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_payroll_user),
):
    service = PayrunService(db)
    return await service.list_payruns(skip=skip, limit=limit)


@router.get("/{payrun_id}", response_model=PayrunDetailOut)
async def get_payrun(
    payrun_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_payroll_user),
):
    service = PayrunService(db)
    payrun = await service.get_by_id(payrun_id)
    if payrun is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payrun not found")
    return payrun


@router.post("/{payrun_id}/compute", response_model=PayrunComputeResponse)
async def compute_payrun(
    payrun_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_payroll_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Runs the rule engine over every payslip in the payrun. Tolerant of
    partial failure: one bad payslip (status -> ERROR, with the failure
    reason) doesn't stop the rest from computing — see PayrunService."""
    service = PayrunService(db)
    results = await service.compute_payrun(payrun_id, bearer_token=credentials.credentials)
    return PayrunComputeResponse(results=results)


@router.post("/{payrun_id}/validate", response_model=PayrunValidateResponse)
async def validate_payrun(
    payrun_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_payroll_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    service = PayrunService(db)
    results = await service.validate_payrun(payrun_id, bearer_token=credentials.credentials)
    return PayrunValidateResponse(results=results)


@router.post("/{payrun_id}/mark-paid", response_model=PayrunMarkPaidResponse, status_code=status.HTTP_202_ACCEPTED)
async def mark_paid_payrun(
    payrun_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_payroll_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Blocked while any payslip has a blocking warning (see
    PayslipComputeService.check_warnings). Returns immediately — PDF
    generation is queued per payslip, not done inline."""
    service = PayrunService(db)
    task_ids = await service.mark_paid_payrun(payrun_id, bearer_token=credentials.credentials)
    return PayrunMarkPaidResponse(task_ids=task_ids)


@router.post("/{payrun_id}/send-payslips", response_model=MarkPaidResult, status_code=status.HTTP_202_ACCEPTED)
async def send_payslips_payrun(
    payrun_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_payroll_user),
):
    service = PayrunService(db)
    task_ids = await service.send_payslips_payrun(payrun_id)
    return MarkPaidResult(task_ids=task_ids)
