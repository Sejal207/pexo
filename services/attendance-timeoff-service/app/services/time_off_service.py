"""
TimeOffService: allocation + request lifecycle for Pipeline 3.

Key design rules:
- An allocation only creates usable balance once its own approval_status is
  APPROVED — request creation checks this upfront.
- Reject-on-insufficient-balance happens at request creation (422), before the
  request ever reaches an approver — never waste a manager's time on a request
  that can't be approved as submitted.
- taken_amount only changes when a request is approved, matching schema.sql's
  design (no "reserved" tracking for pending requests — a known, accepted
  simplification, not a bug).
- If a Time Off Type has requires_approval=False, a request against it is
  auto-approved (and balance deducted) immediately on creation.
- remaining_amount is a DB-generated column; the ORM never writes to it, so
  balance checks compare against allocated_amount - taken_amount directly.
"""
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.time_off_allocation import TimeOffAllocation
from app.models.time_off_request import TimeOffRequest
from app.models.time_off_type import TimeOffType
from app.schemas.time_off import AllocationCreate, TimeOffRequestCreate
from app.services.audit_service import AuditService


class AllocationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, allocation_id: UUID) -> Optional[TimeOffAllocation]:
        result = await self.db.execute(
            select(TimeOffAllocation).where(TimeOffAllocation.id == allocation_id)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        *,
        employee_id: Optional[UUID] = None,
        time_off_type_id: Optional[UUID] = None,
        approval_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TimeOffAllocation]:
        stmt = select(TimeOffAllocation)
        if employee_id:
            stmt = stmt.where(TimeOffAllocation.employee_id == employee_id)
        if time_off_type_id:
            stmt = stmt.where(TimeOffAllocation.time_off_type_id == time_off_type_id)
        if approval_status:
            stmt = stmt.where(TimeOffAllocation.approval_status == approval_status)
        stmt = stmt.order_by(TimeOffAllocation.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, data: AllocationCreate) -> TimeOffAllocation:
        if data.valid_to < data.valid_from:
            raise HTTPException(status_code=422, detail="valid_to must be on or after valid_from")

        allocation = TimeOffAllocation(**data.model_dump())
        self.db.add(allocation)
        await self.db.commit()
        await self.db.refresh(allocation)
        return allocation

    async def approve(self, allocation_id: UUID) -> TimeOffAllocation:
        allocation = await self.get_by_id(allocation_id)
        if allocation is None:
            raise HTTPException(status_code=404, detail="Allocation not found")
        if allocation.approval_status != "PENDING":
            raise HTTPException(
                status_code=409,
                detail=f"Allocation is already {allocation.approval_status}, not PENDING",
            )
        allocation.approval_status = "APPROVED"
        await self.db.commit()
        await self.db.refresh(allocation)
        return allocation


class TimeOffRequestService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._audit = AuditService(db)

    async def get_by_id(self, request_id: UUID) -> Optional[TimeOffRequest]:
        result = await self.db.execute(
            select(TimeOffRequest).where(TimeOffRequest.id == request_id)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        *,
        employee_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TimeOffRequest]:
        stmt = select(TimeOffRequest)
        if employee_id:
            stmt = stmt.where(TimeOffRequest.employee_id == employee_id)
        if status:
            stmt = stmt.where(TimeOffRequest.status == status)
        stmt = stmt.order_by(TimeOffRequest.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, employee_id: UUID, data: TimeOffRequestCreate) -> TimeOffRequest:
        if data.end_date < data.start_date:
            raise HTTPException(status_code=422, detail="end_date must be on or after start_date")

        type_result = await self.db.execute(
            select(TimeOffType).where(TimeOffType.id == data.time_off_type_id)
        )
        time_off_type = type_result.scalar_one_or_none()
        if time_off_type is None:
            raise HTTPException(status_code=404, detail="Time off type not found")

        allocation: Optional[TimeOffAllocation] = None
        if time_off_type.requires_allocation:
            if data.allocation_id is None:
                raise HTTPException(
                    status_code=422,
                    detail="This time off type requires an allocation_id",
                )
            alloc_result = await self.db.execute(
                select(TimeOffAllocation).where(TimeOffAllocation.id == data.allocation_id)
            )
            allocation = alloc_result.scalar_one_or_none()
            if allocation is None:
                raise HTTPException(status_code=404, detail="Allocation not found")
            if allocation.employee_id != employee_id:
                raise HTTPException(
                    status_code=403, detail="This allocation does not belong to you"
                )
            if allocation.approval_status != "APPROVED":
                raise HTTPException(
                    status_code=422,
                    detail="This allocation is not yet approved and has no usable balance",
                )
            remaining = allocation.allocated_amount - allocation.taken_amount
            if data.duration > remaining:
                raise HTTPException(
                    status_code=422,
                    detail=f"Requested duration {data.duration} exceeds remaining balance {remaining}",
                )

        request = TimeOffRequest(
            employee_id=employee_id,
            time_off_type_id=data.time_off_type_id,
            allocation_id=data.allocation_id,
            start_date=data.start_date,
            end_date=data.end_date,
            duration=data.duration,
            reason=data.reason,
            status="SUBMITTED",
        )
        self.db.add(request)

        if not time_off_type.requires_approval:
            # Auto-approve: no human review needed for this policy.
            if allocation is not None:
                allocation.taken_amount = allocation.taken_amount + data.duration
            request.status = "APPROVED"
            request.approved_at = datetime.now(timezone.utc)

        try:
            await self.db.flush()
        except IntegrityError as exc:
            await self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="This request could not be saved (balance constraint violated).",
            ) from exc

        if request.status == "APPROVED":
            await self._audit.log(
                user_id=None,
                entity_name="time_off_request",
                entity_id=request.id,
                action="APPROVE",
                field_changes={"reason": "auto-approved: time off type does not require approval"},
            )

        await self.db.commit()
        await self.db.refresh(request)
        return request

    async def approve(self, request_id: UUID, *, actor_user_id: Optional[UUID]) -> TimeOffRequest:
        request = await self.get_by_id(request_id)
        if request is None:
            raise HTTPException(status_code=404, detail="Time off request not found")
        if request.status not in ("DRAFT", "SUBMITTED"):
            raise HTTPException(
                status_code=409,
                detail=f"Request is already {request.status}, cannot approve",
            )

        if request.allocation_id is not None:
            alloc_result = await self.db.execute(
                select(TimeOffAllocation).where(TimeOffAllocation.id == request.allocation_id)
            )
            allocation = alloc_result.scalar_one_or_none()
            if allocation is not None:
                remaining = allocation.allocated_amount - allocation.taken_amount
                if request.duration > remaining:
                    raise HTTPException(
                        status_code=422,
                        detail=f"Approving would exceed remaining balance {remaining}",
                    )
                allocation.taken_amount = allocation.taken_amount + request.duration

        request.status = "APPROVED"
        request.approved_by_user_id = actor_user_id
        request.approved_at = datetime.now(timezone.utc)

        try:
            await self.db.flush()
        except IntegrityError as exc:
            await self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Approving this request would violate the allocation's balance constraint.",
            ) from exc

        await self._audit.log(
            user_id=actor_user_id,
            entity_name="time_off_request",
            entity_id=request.id,
            action="APPROVE",
        )
        await self.db.commit()
        await self.db.refresh(request)
        return request

    async def refuse(
        self, request_id: UUID, *, reason: str, actor_user_id: Optional[UUID]
    ) -> TimeOffRequest:
        request = await self.get_by_id(request_id)
        if request is None:
            raise HTTPException(status_code=404, detail="Time off request not found")
        if request.status not in ("DRAFT", "SUBMITTED"):
            raise HTTPException(
                status_code=409,
                detail=f"Request is already {request.status}, cannot refuse",
            )

        request.status = "REFUSED"
        request.approved_by_user_id = actor_user_id
        request.approved_at = datetime.now(timezone.utc)
        request.reason = reason

        await self._audit.log(
            user_id=actor_user_id,
            entity_name="time_off_request",
            entity_id=request.id,
            action="REFUSE",
            reason=reason,
        )
        await self.db.commit()
        await self.db.refresh(request)
        return request

    async def get_work_entries(
        self, *, employee_id: UUID, period_start: date, period_end: date
    ) -> list[dict]:
        """
        Internal, consumed by payroll-service: approved leave overlapping a
        payroll period, summed by payroll_work_entry_code.
        """
        stmt = (
            select(TimeOffRequest)
            .options(selectinload(TimeOffRequest.time_off_type))
            .where(
                TimeOffRequest.employee_id == employee_id,
                TimeOffRequest.status == "APPROVED",
                TimeOffRequest.start_date <= period_end,
                TimeOffRequest.end_date >= period_start,
            )
        )
        result = await self.db.execute(stmt)
        requests = result.scalars().all()

        totals: dict[str, Decimal] = {}
        for req in requests:
            code = req.time_off_type.payroll_work_entry_code
            if not code:
                continue
            totals[code] = totals.get(code, Decimal("0")) + req.duration

        return [
            {"payroll_work_entry_code": code, "total_duration": total}
            for code, total in totals.items()
        ]
