from datetime import time, datetime
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkingScheduleLineCreate(BaseModel):
    day: Literal["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    start_time: time
    end_time: time
    break_minutes: int = 0


class WorkingScheduleLineOut(WorkingScheduleLineCreate):
    id: UUID
    working_schedule_id: UUID
    model_config = ConfigDict(from_attributes=True)


class WorkingScheduleCreate(BaseModel):
    name: str
    schedule_type: Literal["FULL_TIME", "PART_TIME", "FLEXIBLE"] = "FULL_TIME"
    lines: list[WorkingScheduleLineCreate] = []


class WorkingScheduleUpdate(BaseModel):
    name: Optional[str] = None
    schedule_type: Optional[Literal["FULL_TIME", "PART_TIME", "FLEXIBLE"]] = None
    lines: Optional[list[WorkingScheduleLineCreate]] = None  # Replace all lines if provided


class WorkingScheduleOut(BaseModel):
    id: UUID
    name: str
    schedule_type: str
    total_weekly_hours: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class WorkingScheduleDetail(WorkingScheduleOut):
    lines: list[WorkingScheduleLineOut] = []
