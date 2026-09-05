from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import security
from app.dependencies import require_payroll_user
from app.schemas.payslip import MarkPaidResult, PayslipDetailOut, PayslipOut
from app.services.payslip_service import PayslipService

router = APIRouter(prefix="/payslips", tags=["Payslips"])


def _to_detail(payslip, lines: list[dict]) -> PayslipDetailOut:
    """
    Builds the response via PayslipOut (no `lines` field) first, deliberately
    avoiding `PayslipDetailOut.model_validate(payslip, ...)` directly — that
    would make pydantic read the ORM object's own (lazy, un-loaded) `.lines`
    relationship, which raises MissingGreenlet under the async driver. The
    enriched, rule-name-joined dicts from get_lines_with_rule_info are what
    the API actually returns instead.
    """
    base = PayslipOut.model_validate(payslip, from_attributes=True)
    return PayslipDetailOut(**base.model_dump(), lines=lines)


@router.get("/", response_model=list[PayslipOut])
async def list_payslips(
    payrun_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_payroll_user),
):
    service = PayslipService(db)
    return await service.list_all(payrun_id=payrun_id, skip=skip, limit=limit)


@router.get("/{payslip_id}", response_model=PayslipDetailOut)
async def get_payslip(
    payslip_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_payroll_user),
):
    service = PayslipService(db)
    payslip = await service.get_by_id(payslip_id)
    if payslip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payslip not found")
    lines = await service.get_lines_with_rule_info(payslip_id)
    return _to_detail(payslip, lines)


@router.post("/{payslip_id}/compute", response_model=PayslipDetailOut)
async def compute_payslip(
    payslip_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_payroll_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    service = PayslipService(db)
    payslip = await service.compute_one(payslip_id, bearer_token=credentials.credentials)
    lines = await service.get_lines_with_rule_info(payslip_id)
    return _to_detail(payslip, lines)


@router.post("/{payslip_id}/mark-paid", response_model=MarkPaidResult)
async def mark_paid_payslip(
    payslip_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_payroll_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    service = PayslipService(db)
    _, task_id = await service.mark_paid_one(payslip_id, bearer_token=credentials.credentials)
    return MarkPaidResult(task_ids=[task_id])


@router.get("/{payslip_id}/pdf")
async def get_payslip_pdf(
    payslip_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_payroll_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """"Print Payslip": returns the PDF URL, generating it synchronously now
    if it doesn't exist yet (the user is waiting, unlike Mark Paid's queued
    generation)."""
    service = PayslipService(db)
    pdf_url = await service.get_or_generate_pdf_url(payslip_id, bearer_token=credentials.credentials)
    return {"pdf_url": pdf_url}
