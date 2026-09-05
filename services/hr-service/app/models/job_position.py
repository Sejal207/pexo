from datetime import datetime
import uuid

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.core.database import Base


class JobPosition(Base):
    __tablename__ = "job_position"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("department.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    department: Mapped[Optional["Department"]] = relationship(  # type: ignore[name-defined]
        "Department", back_populates="job_positions"
    )
    employees: Mapped[list["Employee"]] = relationship(  # type: ignore[name-defined]
        "Employee",
        foreign_keys="Employee.job_position_id",
        back_populates="job_position",
    )
