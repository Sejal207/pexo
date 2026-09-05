"""
Renders a payslip to PDF (WeasyPrint) and uploads it to Azure Blob (Azurite
locally). WeasyPrint needs native Pango/cairo/gdk-pixbuf libraries that are
only guaranteed present in the payroll-worker container (see Dockerfile.worker)
— the import is deferred into the function body so importing this module on a
machine without those libs (e.g. a bare Windows dev box) doesn't crash the
whole process, only an actual PDF-render call.
"""
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.hr_client import HRClient
from app.core.config import settings
from app.models.payslip import Payslip

_TEMPLATE_ENV = Environment(loader=FileSystemLoader("app/templates"))


async def render_and_upload_payslip_pdf(
    db: AsyncSession, payslip: Payslip, *, bearer_token: str
) -> str:
    import weasyprint
    from azure.core.exceptions import ResourceExistsError
    from azure.storage.blob.aio import BlobServiceClient

    # Local import: avoids a circular import (payslip_service also imports
    # this module, lazily, for the synchronous "print" path).
    from app.services.payslip_service import PayslipService

    hr_client = HRClient(bearer_token)
    employee = await hr_client.get_employee(payslip.employee_id)
    employee_name = f"{employee['first_name']} {employee['last_name']}"
    lines = await PayslipService(db).get_lines_with_rule_info(payslip.id)

    template = _TEMPLATE_ENV.get_template("payslip_pdf.html")
    html = template.render(payslip=payslip, employee_name=employee_name, lines=lines)
    pdf_bytes = weasyprint.HTML(string=html).write_pdf()

    blob_name = f"payslip-{payslip.id}.pdf"
    async with BlobServiceClient.from_connection_string(
        settings.AZURE_STORAGE_CONNECTION_STRING
    ) as blob_service:
        container = blob_service.get_container_client(settings.AZURE_CONTAINER_NAME)
        try:
            await container.create_container()
        except ResourceExistsError:
            pass
        blob_client = container.get_blob_client(blob_name)
        await blob_client.upload_blob(pdf_bytes, overwrite=True)
        pdf_url = blob_client.url

    payslip.pdf_url = pdf_url
    db.add(payslip)
    await db.commit()
    return pdf_url
