from datetime import date, datetime
from decimal import Decimal
import uuid

from sqlalchemy import Date, DateTime, Numeric, CheckConstraint, Index, Computed, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import ApprovalStatusEnum


class TimeOffAllocation(Base):
    """
    An employee's entitled balance for a Time Off Type over a validity window.
    employee_id is a plain UUID (no FK): the employee record lives in
    hr-service's schema, not this service's — same cross-schema rule as
    Attendance.employee_id.
    """

    __tablename__ = "time_off_allocation"
    __table_args__ = (
        CheckConstraint("valid_to >= valid_from", name="ck_allocation_valid_range"),
        CheckConstraint(
            "taken_amount >= 0 AND taken_amount <= allocated_amount",
            name="ck_allocation_taken_within_bounds",
        ),
        Index("idx_allocation_employee_type", "employee_id", "time_off_type_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    time_off_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("time_off_type.id", ondelete="RESTRICT"),
        nullable=False,
    )
    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    taken_amount: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), nullable=False, server_default="0"
    )
    # Server-computed (Postgres GENERATED ALWAYS); the ORM never writes to this.
    remaining_amount: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), Computed("allocated_amount - taken_amount", persisted=True)
    )
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date] = mapped_column(Date, nullable=False)
    approval_status: Mapped[str] = mapped_column(
        ApprovalStatusEnum, nullable=False, server_default="PENDING"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    time_off_type: Mapped["TimeOffType"] = relationship("TimeOffType")  # type: ignore[name-defined]
