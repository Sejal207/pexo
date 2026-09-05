"""
PayslipComputeService: bridges a payslip's stored data to the RuleEngine
(app/engine/rule_engine.py) and writes the resulting payslip_line rows.

Context-building rules:
- The contract's wage_amount is injected into the evaluation context as
  "WAGE". A rule cannot take a PERCENTAGE of "contract wage" directly
  (percentage_of_rule_code is a strict FK to another salary_rule.code, per
  schema.sql) — instead, seed a FORMULA rule whose formula_expression is
  just "WAGE" so it becomes a normal, percentable context entry. See
  SalaryRule's model docstring.
- Approved-leave durations from attendance-timeoff-service's work-entries
  endpoint are injected by their `payroll_work_entry_code`, so a FORMULA rule
  can read e.g. `WAGE - (WAGE / 30) * LEAVE_UNPAID`.
- worked_days = period length in days minus total leave duration across all
  returned work-entry codes. This assumes a DAYS unit uniformly — the
  work-entries endpoint doesn't currently pass through each time_off_type's
  unit, so mixed DAYS/HOURS leave in one period is a known, accepted
  simplification, not a bug.
- ORM rows are translated into the plain-dict shape RuleEngine already has a
  passing unit test against (calculation_type/amount/percentage/base_variable
  /formula) rather than changing the engine to match the DB's column names.
"""
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.clients.attendance_client import AttendanceClient
from app.clients.hr_client import HRClient
from app.engine.rule_engine import RuleEngine
from app.models.payslip import Payslip
from app.models.payslip_line import PayslipLine
from app.models.salary_structure_rule import SalaryStructureRule
from app.models.salary_rule import SalaryRule


class PayslipComputeService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def check_warnings(
        self, payslip: Payslip, *, bearer_token: str
    ) -> tuple[list[str], bool]:
        """
        Returns (warnings, blocking). Recomputed fresh on every call — never
        trust a stale has_warning flag when deciding whether Mark Paid may
        proceed. Two warning kinds are currently modeled (still-open spec
        decision #4: "which warnings block Mark Paid"):
        - missing bank account -> blocking (payroll can't be disbursed).
        - another payslip for the same employee with an overlapping period,
          in a *different* payrun -> informational only. A hard duplicate
          within the same payrun is already impossible: schema.sql's
          UNIQUE(payrun_id, employee_id) constraint blocks it outright.
        """
        if payslip.status not in ("COMPUTED", "VALIDATED"):
            return (["Payslip has not been computed yet"], True)

        warnings: list[str] = []
        blocking = False

        hr_client = HRClient(bearer_token)
        if not await hr_client.has_primary_bank_account(payslip.employee_id):
            warnings.append("Missing bank account (A/C missing)")
            blocking = True

        dup_stmt = select(Payslip.id).where(
            Payslip.employee_id == payslip.employee_id,
            Payslip.id != payslip.id,
            Payslip.status.in_(["COMPUTED", "VALIDATED", "PAID"]),
            Payslip.period_start <= payslip.period_end,
            Payslip.period_end >= payslip.period_start,
        )
        if (await self.db.execute(dup_stmt)).first() is not None:
            warnings.append("Another payslip exists for an overlapping period")

        return (warnings, blocking)

    async def _load_ordered_rules(self, salary_structure_id: UUID) -> list[tuple[int, SalaryRule]]:
        stmt = (
            select(SalaryStructureRule.sequence, SalaryRule)
            .join(SalaryRule, SalaryStructureRule.salary_rule_id == SalaryRule.id)
            .where(
                SalaryStructureRule.salary_structure_id == salary_structure_id,
                SalaryRule.is_active.is_(True),
            )
            .order_by(SalaryStructureRule.sequence)
        )
        result = await self.db.execute(stmt)
        return list(result.all())

    async def compute_payslip(
        self, payslip: Payslip, *, salary_structure_id: UUID, bearer_token: str
    ) -> Payslip:
        if payslip.status == "PAID":
            raise HTTPException(
                status_code=409, detail="A paid payslip is immutable and cannot be recomputed."
            )

        ordered_rules = await self._load_ordered_rules(salary_structure_id)
        if not ordered_rules:
            raise HTTPException(
                status_code=422,
                detail="This salary structure has no active rules configured.",
            )

        hr_client = HRClient(bearer_token)
        attendance_client = AttendanceClient(bearer_token)

        contract = await hr_client.get_contract(payslip.contract_id)
        work_entries = await attendance_client.get_work_entries(
            employee_id=payslip.employee_id,
            period_start=payslip.period_start,
            period_end=payslip.period_end,
        )

        initial_context: dict[str, float] = {"WAGE": float(contract["wage_amount"])}
        total_leave_duration = Decimal("0")
        for entry in work_entries:
            code = entry["payroll_work_entry_code"]
            duration = Decimal(str(entry["total_duration"]))
            initial_context[code] = float(duration)
            total_leave_duration += duration

        rule_id_by_code: dict[str, Optional[UUID]] = {}
        engine_rules = []
        for sequence, rule in ordered_rules:
            rule_id_by_code[rule.code] = rule.id
            engine_rules.append(
                {
                    "code": rule.code,
                    "name": rule.name,
                    "category": rule.category,
                    "sequence": sequence,
                    "calculation_type": rule.computation_type,
                    "amount": float(rule.fixed_amount) if rule.fixed_amount is not None else 0.0,
                    "percentage": float(rule.percentage_value)
                    if rule.percentage_value is not None
                    else 0.0,
                    "base_variable": rule.percentage_of_rule_code or "",
                    "formula": rule.formula_expression or "0",
                }
            )

        try:
            result = RuleEngine(engine_rules).compute(initial_context=initial_context)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=f"Rule computation failed: {exc}") from exc

        context = result["context"]
        rule_by_code = {rule.code: rule for _, rule in ordered_rules}

        await self.db.execute(delete(PayslipLine).where(PayslipLine.payslip_id == payslip.id))

        gross_amount = Decimal("0")
        net_amount = Decimal("0")
        has_gross = False
        has_net = False
        for line in result["lines"]:
            rule = rule_by_code[line["rule_code"]]
            amount = Decimal(str(line["amount"]))

            if rule.computation_type == "FIXED":
                detail = {"computation_type": "FIXED", "fixed_amount": str(rule.fixed_amount)}
            elif rule.computation_type == "PERCENTAGE":
                detail = {
                    "computation_type": "PERCENTAGE",
                    "base_rule_code": rule.percentage_of_rule_code,
                    "base_amount": context.get(rule.percentage_of_rule_code),
                    "percentage_value": str(rule.percentage_value),
                }
            else:
                detail = {"computation_type": "FORMULA", "formula_expression": rule.formula_expression}

            self.db.add(
                PayslipLine(
                    payslip_id=payslip.id,
                    salary_rule_id=rule_id_by_code.get(rule.code),
                    salary_rule_code=rule.code,
                    sequence=line["sequence"],
                    amount=amount,
                    computation_detail=detail,
                )
            )

            if rule.category == "GROSS":
                gross_amount += amount
                has_gross = True
            elif rule.category == "NET":
                net_amount += amount
                has_net = True

        period_days = (payslip.period_end - payslip.period_start).days + 1
        worked_days = Decimal(period_days) - total_leave_duration
        if worked_days < 0:
            worked_days = Decimal("0")

        payslip.worked_days = worked_days
        payslip.gross_amount = gross_amount if has_gross else None
        payslip.net_amount = net_amount if has_net else None
        payslip.status = "COMPUTED"
        payslip.has_warning = False
        payslip.warning_notes = None

        self.db.add(payslip)
        await self.db.commit()

        result_stmt = (
            select(Payslip)
            .options(selectinload(Payslip.lines))
            .where(Payslip.id == payslip.id)
        )
        refreshed = await self.db.execute(result_stmt)
        return refreshed.scalar_one()
