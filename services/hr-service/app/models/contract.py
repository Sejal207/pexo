from datetime import date, datetime
import uuid
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, CheckConstraint, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import ContractTypeEnum, WageTypeEnum, ContractStatusEnum


class Contract(Base):
    __tablename__ = "contract"
    __table_args__ = (
        CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name="ck_contract_end_after_start",
        ),
        Index("idx_contract_employee_dates", "employee_id", "start_date", "end_date"),
        # NOTE: The EXCLUDE USING gist constraint for overlapping ACTIVE contracts
        # cannot be expressed in SQLAlchemy's ORM layer — it is created in the
        # Alembic migration via op.execute() raw SQL.
        # Constraint name: excl_no_overlapping_active_contracts
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employee.id", ondelete="CASCADE"),
        nullable=False,
    )
    contract_type: Mapped[str] = mapped_column(
        ContractTypeEnum, nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    wage_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    wage_type: Mapped[str] = mapped_column(
        WageTypeEnum, nullable=False, server_default="MONTHLY"
    )

    # Cross-schema FK (payroll schema owns salary_structure).
    # Stored as plain UUID — no ORM FK declared (Option A from plan).
    salary_structure_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )

    # Contract may override employee's default schedule
    working_schedule_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("working_schedule.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Snapshots at contract-signing time (may differ from employee's current dept/job)
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("department.id", ondelete="SET NULL"),
        nullable=True,
    )
    job_position_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_position.id", ondelete="SET NULL"),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        ContractStatusEnum, nullable=False, server_default="DRAFT"
    )
    signed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    employee: Mapped["Employee"] = relationship(
        "Employee", back_populates="contracts"
    )
    working_schedule: Mapped[Optional["WorkingSchedule"]] = relationship(  # type: ignore[name-defined]
        "WorkingSchedule",
        foreign_keys=[working_schedule_id],
        back_populates="contracts",
    )
