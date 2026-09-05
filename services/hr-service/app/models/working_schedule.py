from datetime import datetime, time
import uuid
from typing import Optional

from sqlalchemy import String, Numeric, DateTime, ForeignKey, Integer, Time, UniqueConstraint, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import ScheduleTypeEnum, DayOfWeekEnum


class WorkingSchedule(Base):
    __tablename__ = "working_schedule"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    schedule_type: Mapped[str] = mapped_column(
        ScheduleTypeEnum, nullable=False, server_default="FULL_TIME"
    )
    # App-layer managed: recomputed whenever lines change
    total_weekly_hours: Mapped[float] = mapped_column(
        Numeric(6, 2), nullable=False, server_default="0"
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

    lines: Mapped[list["WorkingScheduleLine"]] = relationship(
        "WorkingScheduleLine",
        back_populates="working_schedule",
        cascade="all, delete-orphan",
    )
    employees: Mapped[list["Employee"]] = relationship(  # type: ignore[name-defined]
        "Employee",
        foreign_keys="Employee.default_working_schedule_id",
        back_populates="default_working_schedule",
    )
    contracts: Mapped[list["Contract"]] = relationship(  # type: ignore[name-defined]
        "Contract",
        foreign_keys="Contract.working_schedule_id",
        back_populates="working_schedule",
    )


class WorkingScheduleLine(Base):
    __tablename__ = "working_schedule_line"
    __table_args__ = (
        UniqueConstraint("working_schedule_id", "day", "start_time", name="uq_schedule_day_start"),
        CheckConstraint("end_time > start_time", name="ck_end_after_start"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    working_schedule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("working_schedule.id", ondelete="CASCADE"),
        nullable=False,
    )
    day: Mapped[str] = mapped_column(DayOfWeekEnum, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    break_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    working_schedule: Mapped["WorkingSchedule"] = relationship(
        "WorkingSchedule", back_populates="lines"
    )
