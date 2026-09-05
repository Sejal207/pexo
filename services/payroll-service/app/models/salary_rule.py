import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import ComputationTypeEnum, RuleCategoryEnum


class SalaryRule(Base):
    """
    A reusable computation step (Basic, HRA, PF, Gross, Net, ...), attached to
    one or more salary structures via salary_structure_rule (with a per-
    structure sequence). `percentage_of_rule_code` is a strict FK to another
    rule's code, per schema.sql — there is no free-standing "contract_wage"/
    "gross" sentinel. To express "% of Wage," seed a FORMULA rule (e.g. code
    "WAGE", formula_expression "WAGE") that captures the contract wage the
    engine injects into its evaluation context; later rules can then take a
    percentage of that rule's code like any other. See
    PayslipComputeService for how the context is built.
    """

    __tablename__ = "salary_rule"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(RuleCategoryEnum, nullable=False)
    computation_type: Mapped[str] = mapped_column(ComputationTypeEnum, nullable=False)
    fixed_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    percentage_of_rule_code: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("salary_rule.code", ondelete="SET NULL"), nullable=True
    )
    percentage_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 3), nullable=True)
    formula_expression: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
