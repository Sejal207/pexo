import uuid

from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SalaryStructureRule(Base):
    """M2M: salary_structure <-> salary_rule, carrying a per-structure sequence."""

    __tablename__ = "salary_structure_rule"
    __table_args__ = (
        UniqueConstraint("salary_structure_id", "salary_rule_id", name="uq_ssr_structure_rule"),
        UniqueConstraint("salary_structure_id", "sequence", name="uq_ssr_structure_sequence"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    salary_structure_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("salary_structure.id", ondelete="CASCADE"), nullable=False
    )
    salary_rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("salary_rule.id", ondelete="RESTRICT"), nullable=False
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)

    salary_structure: Mapped["SalaryStructure"] = relationship(  # type: ignore[name-defined]
        "SalaryStructure", back_populates="structure_rules"
    )
    salary_rule: Mapped["SalaryRule"] = relationship("SalaryRule")  # type: ignore[name-defined]
