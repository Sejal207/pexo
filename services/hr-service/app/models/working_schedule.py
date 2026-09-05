from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class WorkingSchedule(Base):
    __tablename__ = "working_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    hours_per_week: Mapped[float] = mapped_column(Float, default=40.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    employees = relationship("Employee", back_populates="working_schedule")
