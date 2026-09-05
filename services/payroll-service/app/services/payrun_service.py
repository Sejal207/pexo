"""
PayrunService: Pipeline 4's wizard -> payslip-creation flow.

Key design rules:
- Step 1 (`get_eligible_employees`) NEVER writes to the DB — this is the
  single most-common wizard bug the pipeline spec calls out.
- Only `create_payrun` commits: one payrun row + one payslip row per selected
  employee, in a single transaction. All payslips start DRAFT.
- Eligibility is always recomputed server-side at creation time and the
  client's employee_ids are checked against it — never trust a client-
  supplied contract_id/eligibility list.
- `contract.status = running whose date range overlaps the chosen period` is
  resolved by hr-service's GET /contracts/eligible (see HRClient) — never a
  single as-of date.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.clients.hr_client import HRClient
from app.models.payrun import Payrun
from app.models.payslip import Payslip
from app.models.salary_structure import SalaryStructure
from app.schemas.payrun import EligibleEmployeesRequest, PayrunCreate
from app.services.audit_service import AuditService
from app.services.payslip_compute_service import PayslipComputeService
from app.tasks.generate_pdf import generate_pdf_task
from app.tasks.send_payslip_email import send_payslip_email_task


class PayrunService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._audit = AuditService(db)

    async def _get_active_structure(self, salary_structure_id: UUID) -> SalaryStructure:
        result = await self.db.execute(
            select(SalaryStructure).where(SalaryStructure.id == salary_structure_id)
        )
        structure = result.scalar_one_or_none()
        if structure is None:
            raise HTTPException(status_code=404, detail="Salary structure not found")
        if not structure.is_active:
            raise HTTPException(status_code=422, detail="Salary structure is not active")
        return structure

    async def list_payruns(self, *, skip: int = 0, limit: int = 100) -> list[Payrun]:
        stmt = (
            select(Payrun)
            .order_by(Payrun.period_start.desc(), Payrun.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, payrun_id: UUID) -> Optional[Payrun]:
        result = await self.db.execute(
            select(Payrun)
            .options(selectinload(Payrun.payslips))
            .where(Payrun.id == payrun_id)
        )
        return result.scalar_one_or_none()

    async def get_eligible_employees(
        self, data: EligibleEmployeesRequest, *, bearer_token: str
    ) -> list[dict]:
        await self._get_active_structure(data.salary_structure_id)
        client = HRClient(bearer_token)
        rows = await client.list_eligible_contracts(
            period_start=data.period_start,
            period_end=data.period_end,
            salary_structure_id=data.salary_structure_id,
            department_id=data.department_id,
            contract_type=data.contract_type,
        )
        return [
            {
                "contract_id": row["contract_id"],
                "employee_id": row["employee_id"],
                "employee_code": row["employee_code"],
                "employee_name": f"{row['employee_first_name']} {row['employee_last_name']}",
                "contract_type": row["contract_type"],
                "working_hours": row.get("working_hours"),
                "start_date": row["start_date"],
                "end_date": row.get("end_date"),
                "wage_amount": row["wage_amount"],
                "wage_type": row["wage_type"],
            }
            for row in rows
        ]

    async def create_payrun(
        self, data: PayrunCreate, *, bearer_token: str, actor_user_id: Optional[UUID]
    ) -> Payrun:
        structure = await self._get_active_structure(data.salary_structure_id)

        client = HRClient(bearer_token)
        eligible_rows = await client.list_eligible_contracts(
            period_start=data.period_start,
            period_end=data.period_end,
            salary_structure_id=data.salary_structure_id,
        )
        eligible_by_employee = {UUID(row["employee_id"]): row for row in eligible_rows}

        selected_ids = set(data.employee_ids)
        ineligible = selected_ids - eligible_by_employee.keys()
        if ineligible:
            raise HTTPException(
                status_code=422,
                detail=f"Not eligible for this payrun period/structure: {sorted(str(i) for i in ineligible)}",
            )

        payrun_name = data.name or (
            f"{structure.name} - {data.period_start.isoformat()} to {data.period_end.isoformat()}"
        )
        payrun = Payrun(
            name=payrun_name,
            period_start=data.period_start,
            period_end=data.period_end,
            salary_structure_id=data.salary_structure_id,
            status="DRAFT",
            created_by_user_id=actor_user_id,
        )
        self.db.add(payrun)
        await self.db.flush()  # assign payrun.id for the payslip FKs below

        for employee_id in selected_ids:
            row = eligible_by_employee[employee_id]
            payslip = Payslip(
                payrun_id=payrun.id,
                employee_id=employee_id,
                contract_id=UUID(row["contract_id"]),
                period_start=data.period_start,
                period_end=data.period_end,
                status="DRAFT",
            )
            self.db.add(payslip)

        await self._audit.log(
            user_id=actor_user_id,
            entity_name="payrun",
            entity_id=payrun.id,
            action="CREATE",
            field_changes={
                "salary_structure_id": str(data.salary_structure_id),
                "period_start": data.period_start.isoformat(),
                "period_end": data.period_end.isoformat(),
                "employee_count": len(selected_ids),
            },
        )

        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise HTTPException(
                status_code=409, detail="Could not create payrun (constraint violation)."
            ) from exc

        return await self.get_by_id(payrun.id)  # type: ignore[return-value]

    async def _mark_payslip_error(self, payslip_id: UUID, message: str) -> None:
        # Rollback expires every attribute on every object in the session, so
        # re-fetch the payslip fresh afterward rather than reusing the
        # caller's (now-stale) ORM instance.
        await self.db.rollback()
        result = await self.db.execute(select(Payslip).where(Payslip.id == payslip_id))
        payslip = result.scalar_one()
        payslip.status = "ERROR"
        payslip.has_warning = True
        # No dedicated error-message column on payslip; warning_notes is reused
        # for this when status == ERROR (documented dual-purpose, not a bug).
        payslip.warning_notes = message
        self.db.add(payslip)
        await self.db.commit()

    async def compute_payrun(self, payrun_id: UUID, *, bearer_token: str) -> list[dict]:
        payrun = await self.get_by_id(payrun_id)
        if payrun is None:
            raise HTTPException(status_code=404, detail="Payrun not found")

        compute_service = PayslipComputeService(self.db)
        results: list[dict] = []
        # Snapshot ids/employee_ids up front: a mid-loop rollback (see
        # _mark_payslip_error) expires every attribute on every object still
        # attached to this session, including payslips already processed.
        pending = [(p.id, p.employee_id) for p in payrun.payslips]
        salary_structure_id = payrun.salary_structure_id

        for payslip_id, employee_id in pending:
            payslip_result = await self.db.execute(select(Payslip).where(Payslip.id == payslip_id))
            payslip = payslip_result.scalar_one()
            try:
                computed = await compute_service.compute_payslip(
                    payslip, salary_structure_id=salary_structure_id, bearer_token=bearer_token
                )
                results.append(
                    {
                        "payslip_id": payslip_id,
                        "employee_id": employee_id,
                        "status": computed.status,
                        "gross_amount": computed.gross_amount,
                        "net_amount": computed.net_amount,
                        "error": None,
                    }
                )
            except HTTPException as exc:
                await self._mark_payslip_error(payslip_id, str(exc.detail))
                results.append(
                    {
                        "payslip_id": payslip_id,
                        "employee_id": employee_id,
                        "status": "ERROR",
                        "gross_amount": None,
                        "net_amount": None,
                        "error": str(exc.detail),
                    }
                )

        payrun.status = "COMPUTED"
        payrun.computed_at = datetime.now(timezone.utc)
        self.db.add(payrun)
        await self.db.commit()
        return results

    async def validate_payrun(self, payrun_id: UUID, *, bearer_token: str) -> list[dict]:
        payrun = await self.get_by_id(payrun_id)
        if payrun is None:
            raise HTTPException(status_code=404, detail="Payrun not found")

        compute_service = PayslipComputeService(self.db)
        results: list[dict] = []
        for payslip in payrun.payslips:
            warnings, blocking = await compute_service.check_warnings(
                payslip, bearer_token=bearer_token
            )
            payslip.has_warning = bool(warnings)
            payslip.warning_notes = "; ".join(warnings) if warnings else None
            if payslip.status == "COMPUTED" and not blocking:
                payslip.status = "VALIDATED"
            self.db.add(payslip)
            results.append(
                {
                    "payslip_id": payslip.id,
                    "employee_id": payslip.employee_id,
                    "warnings": warnings,
                    "blocking": blocking,
                }
            )

        payrun.status = "VALIDATED"
        payrun.validated_at = datetime.now(timezone.utc)
        self.db.add(payrun)
        await self.db.commit()
        return results

    async def mark_paid_payrun(self, payrun_id: UUID, *, bearer_token: str) -> list[str]:
        payrun = await self.get_by_id(payrun_id)
        if payrun is None:
            raise HTTPException(status_code=404, detail="Payrun not found")
        if not payrun.payslips:
            raise HTTPException(status_code=422, detail="Payrun has no payslips")

        compute_service = PayslipComputeService(self.db)
        blocked: list[str] = []
        for payslip in payrun.payslips:
            if payslip.status != "VALIDATED":
                blocked.append(f"{payslip.employee_id}: not validated (status={payslip.status})")
                continue
            warnings, blocking = await compute_service.check_warnings(
                payslip, bearer_token=bearer_token
            )
            if blocking:
                blocked.append(f"{payslip.employee_id}: {'; '.join(warnings)}")

        if blocked:
            raise HTTPException(
                status_code=409,
                detail=f"Mark Paid blocked by outstanding warnings: {blocked}",
            )

        task_ids: list[str] = []
        for payslip in payrun.payslips:
            payslip.status = "PAID"
            self.db.add(payslip)
            task = generate_pdf_task.delay(str(payslip.id))
            task_ids.append(task.id)

        payrun.status = "PAID"
        payrun.paid_at = datetime.now(timezone.utc)
        self.db.add(payrun)
        await self.db.commit()
        return task_ids

    async def send_payslips_payrun(self, payrun_id: UUID) -> list[str]:
        payrun = await self.get_by_id(payrun_id)
        if payrun is None:
            raise HTTPException(status_code=404, detail="Payrun not found")

        paid_payslips = [p for p in payrun.payslips if p.status == "PAID"]
        if not paid_payslips:
            raise HTTPException(
                status_code=422, detail="No paid payslips in this payrun to send"
            )

        task_ids = []
        for payslip in paid_payslips:
            task = send_payslip_email_task.delay(str(payslip.id))
            task_ids.append(task.id)
        return task_ids
