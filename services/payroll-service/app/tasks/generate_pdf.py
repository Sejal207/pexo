from uuid import UUID

from app.core.async_utils import run_async
from app.core.task_db import TaskSessionLocal
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.celery_app import celery_app
from app.core.security import mint_service_token
from app.models.payslip import Payslip


async def _generate_pdf(payslip_id: str) -> dict:
    # Deferred: pdf_service imports weasyprint, which needs native libs only
    # guaranteed present in this worker's container (see Dockerfile.worker).
    from app.services.pdf_service import render_and_upload_payslip_pdf

    async with TaskSessionLocal() as db:
        result = await db.execute(
            select(Payslip)
            .options(selectinload(Payslip.lines))
            .where(Payslip.id == UUID(payslip_id))
        )
        payslip = result.scalar_one_or_none()
        if payslip is None:
            return {"payslip_id": payslip_id, "status": "not_found"}

        token = mint_service_token(["HR_PAYROLL_MANAGER"])
        pdf_url = await render_and_upload_payslip_pdf(db, payslip, bearer_token=token)
        return {"payslip_id": payslip_id, "pdf_url": pdf_url, "status": "generated"}



@celery_app.task(name="app.tasks.generate_pdf.generate_pdf_task")
def generate_pdf_task(payslip_id: str) -> dict:
    return run_async(_generate_pdf(payslip_id))
