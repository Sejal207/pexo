from datetime import datetime
import uuid
from decimal import Decimal
from typing import Optional, Any

from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PayslipLine(Base):
    """
    One rule's computed contribution to a payslip. salary_rule_code is a
    denormalized text snapshot on purpose (schema.sql): historical payslips
    stay accurate even if a rule is later renamed/deleted.
    """

    __tablename__ = "payslip_line"
    __table_args__ = (
        Index("idx_payslip_line_payslip", "payslip_id", "sequence"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    payslip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("payslip.id", ondelete="CASCADE"), nullable=False
    )
    salary_rule_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("salary_rule.id", ondelete="SET NULL"), nullable=True
    )
    salary_rule_code: Mapped[str] = mapped_column(String(50), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    computation_detail: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    payslip: Mapped["Payslip"] = relationship("Payslip", back_populates="lines")  # type: ignore[name-defined]
