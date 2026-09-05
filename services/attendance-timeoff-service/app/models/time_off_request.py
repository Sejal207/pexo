from datetime import date, datetime
from decimal import Decimal
import uuid
from typing import Optional

from sqlalchemy import Date, DateTime, Numeric, Text, CheckConstraint, Index, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import RequestStatusEnum


class TimeOffRequest(Base):
    """
    A request to draw down a specific allocation. employee_id and
    approved_by_user_id are plain UUIDs (no FK): the employee lives in
    hr-service's schema and the reviewer in api-gateway's.
    """

    __tablename__ = "time_off_request"
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="ck_request_date_range"),
        Index("idx_request_employee_status", "employee_id", "status"),
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
    allocation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("time_off_allocation.id", ondelete="SET NULL"),
        nullable=True,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    duration: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        RequestStatusEnum, nullable=False, server_default="DRAFT"
    )
    approved_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
    allocation: Mapped[Optional["TimeOffAllocation"]] = relationship("TimeOffAllocation")  # type: ignore[name-defined]
