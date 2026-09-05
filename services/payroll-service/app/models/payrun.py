from datetime import date, datetime
import uuid
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, CheckConstraint, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import PayrunStatusEnum


class Payrun(Base):
    __tablename__ = "payrun"
    __table_args__ = (
        CheckConstraint("period_end >= period_start", name="ck_payrun_period_range"),
        Index("idx_payrun_period", "period_start", "period_end"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    salary_structure_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("salary_structure.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(PayrunStatusEnum, nullable=False, server_default="DRAFT")
    # app_user lives in the gateway schema — plain UUID, no FK constraint.
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    computed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    payslips: Mapped[list["Payslip"]] = relationship(  # type: ignore[name-defined]
        "Payslip", back_populates="payrun", cascade="all, delete-orphan"
    )
