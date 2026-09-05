from datetime import date, datetime
from sqlalchemy import String, Integer, Float, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Attendance(Base):
    __tablename__ = "attendance_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    check_in: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    check_out: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    worked_hours: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(50), default="PRESENT")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
