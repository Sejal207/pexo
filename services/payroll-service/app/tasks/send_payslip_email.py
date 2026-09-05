from datetime import datetime, timezone
from uuid import UUID

from app.clients.hr_client import HRClient
from app.core.async_utils import run_async
from app.core.task_db import TaskSessionLocal
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.celery_app import celery_app
from app.core.security import mint_service_token
from app.models.payslip import Payslip

_TEMPLATE_ENV = Environment(loader=FileSystemLoader("app/mail/templates"))


async def _send_email(payslip_id: str) -> dict:
    # Deferred: mail_config/fastapi_mail and pdf_service (weasyprint) are
    # heavy/optional-native-dep imports — see generate_pdf.py.
    from app.services.pdf_service import render_and_upload_payslip_pdf
    from fastapi_mail import FastMail, MessageSchema, MessageType

    from app.mail.mail_config import mail_config

    async with TaskSessionLocal() as db:
        result = await db.execute(
            select(Payslip)
            .options(selectinload(Payslip.lines))
            .where(Payslip.id == UUID(payslip_id))
        )
        payslip = result.scalar_one_or_none()
        if payslip is None:
            return {"payslip_id": payslip_id, "status": "not_found"}
        if payslip.status != "PAID":
            return {"payslip_id": payslip_id, "status": "skipped", "reason": "not PAID yet"}

        token = mint_service_token(["HR_PAYROLL_MANAGER"])
        if not payslip.pdf_url:
            await render_and_upload_payslip_pdf(db, payslip, bearer_token=token)
            await db.refresh(payslip)

        hr_client = HRClient(token)
        employee = await hr_client.get_employee(payslip.employee_id)

        template = _TEMPLATE_ENV.get_template("payslip_email.html")
        html = template.render(employee_name=employee["first_name"], pdf_url=payslip.pdf_url)

        message = MessageSchema(
            subject="Your Payslip is Ready",
            recipients=[employee["email"]],
            body=html,
            subtype=MessageType.html,
        )
        await FastMail(mail_config).send_message(message)

        payslip.sent_at = datetime.now(timezone.utc)
        db.add(payslip)
        await db.commit()
        return {"payslip_id": payslip_id, "status": "sent", "email": employee["email"]}



@celery_app.task(name="app.tasks.send_payslip_email.send_payslip_email_task")
def send_payslip_email_task(payslip_id: str) -> dict:
    return run_async(_send_email(payslip_id))
