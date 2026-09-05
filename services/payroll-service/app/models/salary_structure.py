from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.salary_structure_rule import SalaryStructureRule


class SalaryStructure(Base):
    """A named bundle of salary rules (Pipeline 5 owns the rules themselves).
    Referenced by contract.salary_structure_id (hr-service) as a plain UUID —
    cross-schema, no FK — and by payrun.salary_structure_id here, in-schema.
    """

    __tablename__ = "salary_structure"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    structure_rules: Mapped[list["SalaryStructureRule"]] = relationship(  # type: ignore[name-defined]
        "SalaryStructureRule",
        back_populates="salary_structure",
        cascade="all, delete-orphan",
        order_by="SalaryStructureRule.sequence",
    )
