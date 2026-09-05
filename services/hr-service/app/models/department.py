from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Department(Base):
    __tablename__ = "department"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    # Self-referencing hierarchy
    parent_department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("department.id", ondelete="SET NULL"),
        nullable=True,
    )
    # FK to employee.id — added after employee table exists.
    # Stored as plain UUID here; relationship declared in Employee model via back_populates.
    manager_employee_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employee.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    parent: Mapped[Optional["Department"]] = relationship(
        "Department", remote_side="Department.id", foreign_keys=[parent_department_id]
    )
    children: Mapped[list["Department"]] = relationship(
        "Department",
        foreign_keys=[parent_department_id],
        back_populates="parent",
    )
    job_positions: Mapped[list["JobPosition"]] = relationship(  # type: ignore[name-defined]
        "JobPosition", back_populates="department"
    )
    employees: Mapped[list["Employee"]] = relationship(  # type: ignore[name-defined]
        "Employee",
        foreign_keys="Employee.department_id",
        back_populates="department",
    )
