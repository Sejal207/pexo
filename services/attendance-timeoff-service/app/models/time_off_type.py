from datetime import datetime
import uuid
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import TimeoffUnitEnum


class TimeOffType(Base):
    """
    A leave policy (Paid Time Off, Sick Leave, ...). Mirrors schema.sql's
    time_off_type table.

    payroll_work_entry_code is additive beyond schema.sql: it's the field the
    Pipeline 3 spec calls out as the missing link to Pipeline 5's salary rule
    engine (e.g. 'LEAVE_PAID'/'LEAVE_UNPAID'), added now since it's a cheap,
    non-breaking column and expensive to retrofit later.
    """

    __tablename__ = "time_off_type"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    unit: Mapped[str] = mapped_column(TimeoffUnitEnum, nullable=False, server_default="DAYS")
    requires_allocation: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    requires_approval: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    affects_payroll: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    payroll_work_entry_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
