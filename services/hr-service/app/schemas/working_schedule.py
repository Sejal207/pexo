from datetime import datetime
from pydantic import BaseModel, ConfigDict

class WorkingScheduleBase(BaseModel):
    name: str
    hours_per_week: float = 40.0

class WorkingScheduleCreate(WorkingScheduleBase):
    pass

class WorkingScheduleOut(WorkingScheduleBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
