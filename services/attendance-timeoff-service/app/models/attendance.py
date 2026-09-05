from datetime import date, datetime
from decimal import Decimal
import uuid
from typing import Optional

from sqlalchemy import (
    Date, DateTime, Numeric, Boolean, Text, CheckConstraint, UniqueConstraint, Index, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import AttendanceStatusEnum


class Attendance(Base):
    """
    One row per employee per work_date (mirrors schema.sql's `attendance` table).
    employee_id and corrected_by_user_id are plain UUIDs, not FKs: the employee
    lives in hr-service's schema and the acting user in api-gateway's — services
    never share a foreign key across schema boundaries, only an HTTP contract.

    overtime_hours is an additive column beyond schema.sql (which only has
    worked_hours) — the Pipeline 2 spec's check-out response explicitly returns
    it, so it is persisted rather than recomputed on every read.
    """

    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("employee_id", "work_date", name="uq_attendance_employee_date"),
        CheckConstraint(
            "check_out IS NULL OR check_in IS NULL OR check_out > check_in",
            name="ck_attendance_checkout_after_checkin",
        ),
        Index("idx_attendance_employee_date", "employee_id", "work_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    work_date: Mapped[date] = mapped_column(Date, nullable=False)
    check_in: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    check_out: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    worked_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    overtime_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    status: Mapped[str] = mapped_column(
        AttendanceStatusEnum, nullable=False, server_default="PRESENT"
    )
    is_manual_correction: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    corrected_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    correction_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
