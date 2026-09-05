from datetime import date, datetime
import uuid
from typing import Optional

from sqlalchemy import (
    String, Date, DateTime, ForeignKey, CheckConstraint, Index, func, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import EmploymentStatusEnum


class Employee(Base):
    __tablename__ = "employee"
    __table_args__ = (
        CheckConstraint(
            "date_exit IS NULL OR date_exit >= date_joined",
            name="ck_date_exit_after_joined",
        ),
        Index("idx_employee_department", "department_id"),
        Index("idx_employee_manager", "manager_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    employee_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    date_joined: Mapped[date] = mapped_column(Date, nullable=False)
    date_exit: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Address
    address_line: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    pincode: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    profile_image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # FKs
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("department.id", ondelete="SET NULL"),
        nullable=True,
    )
    job_position_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_position.id", ondelete="SET NULL"),
        nullable=True,
    )
    manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employee.id", ondelete="SET NULL"),
        nullable=True,
    )
    default_working_schedule_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("working_schedule.id", ondelete="SET NULL"),
        nullable=True,
    )

    employment_status: Mapped[str] = mapped_column(
        EmploymentStatusEnum, nullable=False, server_default="ACTIVE"
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
    department: Mapped[Optional["Department"]] = relationship(  # type: ignore[name-defined]
        "Department",
        foreign_keys=[department_id],
        back_populates="employees",
    )
    job_position: Mapped[Optional["JobPosition"]] = relationship(  # type: ignore[name-defined]
        "JobPosition",
        foreign_keys=[job_position_id],
        back_populates="employees",
    )
    manager: Mapped[Optional["Employee"]] = relationship(
        "Employee",
        remote_side="Employee.id",
        foreign_keys=[manager_id],
    )
    default_working_schedule: Mapped[Optional["WorkingSchedule"]] = relationship(  # type: ignore[name-defined]
        "WorkingSchedule",
        foreign_keys=[default_working_schedule_id],
        back_populates="employees",
    )
    contracts: Mapped[list["Contract"]] = relationship(  # type: ignore[name-defined]
        "Contract",
        back_populates="employee",
        cascade="all, delete-orphan",
    )
    bank_accounts: Mapped[list["EmployeeBankAccount"]] = relationship(
        "EmployeeBankAccount",
        back_populates="employee",
        cascade="all, delete-orphan",
    )
