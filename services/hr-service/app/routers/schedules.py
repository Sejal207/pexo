from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.working_schedule import WorkingSchedule
from app.schemas.working_schedule import WorkingScheduleCreate, WorkingScheduleOut

router = APIRouter(prefix="/schedules", tags=["Working Schedules"])

@router.get("/", response_model=list[WorkingScheduleOut])
async def list_schedules(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkingSchedule))
    return result.scalars().all()

@router.post("/", response_model=WorkingScheduleOut)
async def create_schedule(schedule_in: WorkingScheduleCreate, db: AsyncSession = Depends(get_db)):
    sched = WorkingSchedule(**schedule_in.model_dump())
    db.add(sched)
    await db.commit()
    await db.refresh(sched)
    return sched
