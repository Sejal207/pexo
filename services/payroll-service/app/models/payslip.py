from datetime import date, datetime
import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Numeric, Text, UniqueConstraint, Index, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import PayslipStatusEnum


class Payslip(Base):
    """
    Associative entity realizing the Payrun <-> Employee M2M relationship.
    employee_id and contract_id are plain UUIDs (no FK): both live in
    hr-service's schema, resolved and snapshotted at payrun-creation time.
    """

    __tablename__ = "payslip"
    __table_args__ = (
        UniqueConstraint("payrun_id", "employee_id", name="uq_payslip_payrun_employee"),
        Index("idx_payslip_employee", "employee_id"),
        Index("idx_payslip_payrun", "payrun_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    payrun_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("payrun.id", ondelete="CASCADE"), nullable=False
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    contract_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    worked_days: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    status: Mapped[str] = mapped_column(PayslipStatusEnum, nullable=False, server_default="DRAFT")
    gross_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    net_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    has_warning: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    warning_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pdf_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    payrun: Mapped["Payrun"] = relationship("Payrun", back_populates="payslips")  # type: ignore[name-defined]
    lines: Mapped[list["PayslipLine"]] = relationship(  # type: ignore[name-defined]
        "PayslipLine",
        back_populates="payslip",
        cascade="all, delete-orphan",
        order_by="PayslipLine.sequence",
    )
