from datetime import date, datetime
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    date_of_joining: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")
    
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"), nullable=True)
    job_position_id: Mapped[int] = mapped_column(Integer, ForeignKey("job_positions.id"), nullable=True)
    working_schedule_id: Mapped[int] = mapped_column(Integer, ForeignKey("working_schedules.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    department = relationship("Department", back_populates="employees")
    job_position = relationship("JobPosition", back_populates="employees")
    working_schedule = relationship("WorkingSchedule", back_populates="employees")
    contracts = relationship("Contract", back_populates="employee")
