from typing import Optional
from uuid import UUID

from app.services.payslip_compute_service import PayslipComputeService
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.payrun import Payrun
from app.models.payslip import Payslip
from app.models.payslip_line import PayslipLine
from app.models.salary_rule import SalaryRule
from app.tasks.generate_pdf import generate_pdf_task


class PayslipService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_all(
        self, *, payrun_id: Optional[UUID] = None, skip: int = 0, limit: int = 100
    ) -> list[Payslip]:
        stmt = select(Payslip)
        if payrun_id:
            stmt = stmt.where(Payslip.payrun_id == payrun_id)
        stmt = stmt.order_by(Payslip.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, payslip_id: UUID) -> Optional[Payslip]:
        result = await self.db.execute(select(Payslip).where(Payslip.id == payslip_id))
        return result.scalar_one_or_none()

    async def get_lines_with_rule_info(self, payslip_id: UUID) -> list[dict]:
        """LEFT JOIN against salary_rule for display-only name/category —
        schema.sql doesn't denormalize those onto payslip_line itself."""
        stmt = (
            select(PayslipLine, SalaryRule.name, SalaryRule.category)
            .outerjoin(SalaryRule, PayslipLine.salary_rule_id == SalaryRule.id)
            .where(PayslipLine.payslip_id == payslip_id)
            .order_by(PayslipLine.sequence)
        )
        result = await self.db.execute(stmt)
        return [
            {
                "id": line.id,
                "salary_rule_id": line.salary_rule_id,
                "salary_rule_code": line.salary_rule_code,
                "rule_name": rule_name,
                "category": category,
                "sequence": line.sequence,
                "amount": line.amount,
                "computation_detail": line.computation_detail,
            }
            for line, rule_name, category in result.all()
        ]

    async def compute_one(self, payslip_id: UUID, *, bearer_token: str) -> Payslip:
        payslip = await self.get_by_id(payslip_id)
        if payslip is None:
            raise HTTPException(status_code=404, detail="Payslip not found")

        payrun_result = await self.db.execute(select(Payrun).where(Payrun.id == payslip.payrun_id))
        payrun = payrun_result.scalar_one()

        compute_service = PayslipComputeService(self.db)
        return await compute_service.compute_payslip(
            payslip, salary_structure_id=payrun.salary_structure_id, bearer_token=bearer_token
        )

    async def mark_paid_one(self, payslip_id: UUID, *, bearer_token: str) -> tuple[Payslip, str]:
        payslip = await self.get_by_id(payslip_id)
        if payslip is None:
            raise HTTPException(status_code=404, detail="Payslip not found")
        if payslip.status != "VALIDATED":
            raise HTTPException(
                status_code=409,
                detail=f"Payslip must be VALIDATED before Mark Paid (currently {payslip.status})",
            )

        compute_service = PayslipComputeService(self.db)
        warnings, blocking = await compute_service.check_warnings(payslip, bearer_token=bearer_token)
        if blocking:
            raise HTTPException(
                status_code=409, detail=f"Mark Paid blocked by outstanding warnings: {warnings}"
            )

        payslip.status = "PAID"
        self.db.add(payslip)
        await self.db.commit()
        await self.db.refresh(payslip)

        task = generate_pdf_task.delay(str(payslip.id))
        return payslip, task.id

    async def get_or_generate_pdf_url(self, payslip_id: UUID, *, bearer_token: str) -> str:
        """Backs GET /payslips/{id}/pdf ("Print Payslip"): synchronous, since
        a user is waiting — generate now if it doesn't exist yet rather than
        queuing (Mark Paid's own queued generation is the fire-and-forget
        path; this one blocks until the artifact is ready)."""
        payslip = await self.get_by_id(payslip_id)
        if payslip is None:
            raise HTTPException(status_code=404, detail="Payslip not found")
        if payslip.pdf_url:
            return payslip.pdf_url

        from app.services.pdf_service import render_and_upload_payslip_pdf

        result = await self.db.execute(
            select(Payslip).options(selectinload(Payslip.lines)).where(Payslip.id == payslip_id)
        )
        payslip_with_lines = result.scalar_one()
        return await render_and_upload_payslip_pdf(
            self.db, payslip_with_lines, bearer_token=bearer_token
        )
