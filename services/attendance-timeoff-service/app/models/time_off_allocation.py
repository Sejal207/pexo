from datetime import datetime
from sqlalchemy import Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class TimeOffAllocation(Base):
    __tablename__ = "time_off_allocations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    time_off_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("time_off_types.id"), nullable=False)
    allocated_days: Mapped[float] = mapped_column(Float, default=0.0)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    time_off_type = relationship("TimeOffType", back_populates="allocations")
