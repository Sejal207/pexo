"""
AttendanceService: check-in/check-out session lifecycle + manual correction.

Key design rules (mirrors the discipline set in hr-service's ContractService):
- worked_hours and overtime_hours are ALWAYS server-computed, on check-out and
  again on any manual correction — never accepted from the client.
- The UNIQUE(employee_id, work_date) constraint is the DB-level guarantee of
  "one attendance row per employee per day"; check_in() relies on it and
  surfaces a clean 409 if a race slips past the application-level check.
- Status/overtime derivation calls hr-service (via HRClient) for the employee's
  applicable Working Schedule. That call is best-effort: if hr-service is
  unreachable or the employee has no schedule, we fall back to a worked-hours-
  only PRESENT/ABSENT judgement rather than failing the check-out.
"""
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.hr_client import HRClient
from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceCorrection
from app.services.audit_service import AuditService

_DAY_CODES = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
_LATE_GRACE = timedelta(minutes=10)


class AttendanceService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._audit = AuditService(db)

    # ------------------------------------------------------------------ #
    # Reads
    # ------------------------------------------------------------------ #

    async def get_by_id(self, attendance_id: UUID) -> Optional[Attendance]:
        result = await self.db.execute(
            select(Attendance).where(Attendance.id == attendance_id)
        )
        return result.scalar_one_or_none()

    async def get_open_session(self, employee_id: UUID) -> Optional[Attendance]:
        """The one row (if any) for this employee with an open check-in."""
        stmt = (
            select(Attendance)
            .where(
                Attendance.employee_id == employee_id,
                Attendance.check_in.isnot(None),
                Attendance.check_out.is_(None),
            )
            .order_by(Attendance.work_date.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_all(
        self,
        *,
        employee_id: Optional[UUID] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Attendance]:
        stmt = select(Attendance)
        if employee_id:
            stmt = stmt.where(Attendance.employee_id == employee_id)
        if date_from:
            stmt = stmt.where(Attendance.work_date >= date_from)
        if date_to:
            stmt = stmt.where(Attendance.work_date <= date_to)
        if status:
            stmt = stmt.where(Attendance.status == status)
        stmt = stmt.order_by(Attendance.work_date.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_widget_status(self, employee_id: UUID) -> dict:
        open_session = await self.get_open_session(employee_id)
        if not open_session:
            return {"open": False, "since": None, "elapsed_seconds": None, "attendance_id": None}
        now = datetime.now(timezone.utc)
        elapsed = int((now - open_session.check_in).total_seconds())
        return {
            "open": True,
            "since": open_session.check_in,
            "elapsed_seconds": elapsed,
            "attendance_id": open_session.id,
        }

    # ------------------------------------------------------------------ #
    # Check-in / check-out
    # ------------------------------------------------------------------ #

    async def check_in(self, employee_id: UUID) -> Attendance:
        existing_open = await self.get_open_session(employee_id)
        if existing_open:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Already checked in since {existing_open.check_in.isoformat()} "
                    f"(work_date {existing_open.work_date}); check out first."
                ),
            )

        today = date.today()
        result = await self.db.execute(
            select(Attendance).where(
                Attendance.employee_id == employee_id, Attendance.work_date == today
            )
        )
        record = result.scalar_one_or_none()
        now = datetime.now(timezone.utc)

        if record is not None:
            if record.check_in is not None:
                raise HTTPException(status_code=409, detail="Already checked in for today.")
            record.check_in = now
            record.check_out = None
        else:
            record = Attendance(
                employee_id=employee_id, work_date=today, check_in=now, status="PRESENT"
            )
            self.db.add(record)

        try:
            await self.db.flush()
        except IntegrityError as exc:
            await self.db.rollback()
            raise HTTPException(status_code=409, detail="Already checked in for today.") from exc

        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def check_out(
        self, attendance_id: UUID, employee_id: UUID, *, bearer_token: str
    ) -> Attendance:
        record = await self.get_by_id(attendance_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Attendance record not found")
        if record.employee_id != employee_id:
            raise HTTPException(status_code=403, detail="You may only check yourself out")
        if record.check_in is None:
            raise HTTPException(status_code=409, detail="No open check-in session to close")
        if record.check_out is not None:
            raise HTTPException(status_code=409, detail="This session is already checked out")

        now = datetime.now(timezone.utc)
        record.check_out = now
        record.worked_hours = _hours_between(record.check_in, now)
        record.status, record.overtime_hours = await self._derive_status(
            employee_id=employee_id,
            work_date=record.work_date,
            check_in=record.check_in,
            worked_hours=record.worked_hours,
            bearer_token=bearer_token,
        )

        await self.db.commit()
        await self.db.refresh(record)
        return record

    # ------------------------------------------------------------------ #
    # Manual correction (HR_MANAGER+)
    # ------------------------------------------------------------------ #

    async def correct(
        self,
        attendance_id: UUID,
        data: AttendanceCorrection,
        *,
        actor_user_id: Optional[UUID],
        bearer_token: str,
    ) -> Attendance:
        record = await self.get_by_id(attendance_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Attendance record not found")

        before = {
            "check_in": _iso(record.check_in),
            "check_out": _iso(record.check_out),
            "status": record.status,
        }

        if data.check_in is not None:
            record.check_in = data.check_in
        if data.check_out is not None:
            record.check_out = data.check_out

        if record.check_in and record.check_out and record.check_out <= record.check_in:
            raise HTTPException(status_code=422, detail="check_out must be after check_in")

        if record.check_in and record.check_out:
            record.worked_hours = _hours_between(record.check_in, record.check_out)
            record.status, record.overtime_hours = await self._derive_status(
                employee_id=record.employee_id,
                work_date=record.work_date,
                check_in=record.check_in,
                worked_hours=record.worked_hours,
                bearer_token=bearer_token,
            )
        else:
            record.worked_hours = None
            record.overtime_hours = None

        record.is_manual_correction = True
        record.corrected_by_user_id = actor_user_id
        record.correction_reason = data.reason

        await self._audit.log(
            user_id=actor_user_id,
            entity_name="attendance",
            entity_id=record.id,
            action="UPDATE",
            field_changes={
                "before": before,
                "after": {
                    "check_in": _iso(record.check_in),
                    "check_out": _iso(record.check_out),
                    "status": record.status,
                },
                "reason": data.reason,
            },
        )

        await self.db.commit()
        await self.db.refresh(record)
        return record

    # ------------------------------------------------------------------ #
    # Status / overtime derivation
    # ------------------------------------------------------------------ #

    async def _derive_status(
        self,
        *,
        employee_id: UUID,
        work_date: date,
        check_in: datetime,
        worked_hours: Decimal,
        bearer_token: str,
    ) -> tuple[str, Decimal]:
        line = await self._resolve_schedule_line(employee_id, work_date, bearer_token)
        if line is None:
            status = "PRESENT" if worked_hours > 0 else "ABSENT"
            return status, Decimal("0")

        expected_start = time.fromisoformat(line["start_time"])
        expected_end = time.fromisoformat(line["end_time"])
        break_minutes = line.get("break_minutes", 0) or 0
        expected_minutes = (
            datetime.combine(work_date, expected_end) - datetime.combine(work_date, expected_start)
        ).total_seconds() / 60 - break_minutes
        expected_hours = Decimal(str(round(max(expected_minutes, 0) / 60, 2)))

        overtime = (
            max(worked_hours - expected_hours, Decimal("0")) if expected_hours > 0 else Decimal("0")
        )

        check_in_dt = check_in if check_in.tzinfo else check_in.replace(tzinfo=timezone.utc)
        check_in_time = check_in_dt.astimezone(timezone.utc).time()
        is_late = datetime.combine(work_date, check_in_time) > (
            datetime.combine(work_date, expected_start) + _LATE_GRACE
        )

        if expected_hours > 0 and worked_hours < expected_hours * Decimal("0.5"):
            status = "HALF_DAY"
        elif is_late:
            status = "LATE"
        else:
            status = "PRESENT"

        return status, overtime

    async def _resolve_schedule_line(
        self, employee_id: UUID, work_date: date, bearer_token: str
    ) -> Optional[dict]:
        client = HRClient(bearer_token)
        schedule_id = await client.get_working_schedule_id(employee_id, work_date)
        if schedule_id is None:
            return None
        lines = await client.get_schedule_lines(schedule_id)
        day_code = _DAY_CODES[work_date.weekday()]
        return next((l for l in lines if l.get("day") == day_code), None)


def _hours_between(start: datetime, end: datetime) -> Decimal:
    hours = (end - start).total_seconds() / 3600
    return max(Decimal(str(round(hours, 2))), Decimal("0"))


def _iso(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if value else None
