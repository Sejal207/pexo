"""
WorkingScheduleService: manages schedules + lines.
The total_weekly_hours on the schedule is kept in sync by app-layer recompute
whenever lines are created or replaced.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.working_schedule import WorkingSchedule, WorkingScheduleLine
from app.schemas.working_schedule import WorkingScheduleCreate, WorkingScheduleUpdate


def _compute_hours(lines: list[WorkingScheduleLine]) -> float:
    """Compute net working hours across all schedule lines."""
    total = 0.0
    for line in lines:
        from datetime import datetime
        start = datetime.combine(datetime.today(), line.start_time)
        end = datetime.combine(datetime.today(), line.end_time)
        duration_minutes = (end - start).seconds / 60 - line.break_minutes
        total += max(duration_minutes, 0) / 60
    return round(total, 2)


class WorkingScheduleService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[WorkingSchedule]:
        result = await self.db.execute(
            select(WorkingSchedule).offset(skip).limit(limit).order_by(WorkingSchedule.name)
        )
        return list(result.scalars().all())

    async def get_by_id(self, schedule_id: UUID) -> Optional[WorkingSchedule]:
        result = await self.db.execute(
            select(WorkingSchedule)
            .options(selectinload(WorkingSchedule.lines))
            .where(WorkingSchedule.id == schedule_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: WorkingScheduleCreate) -> WorkingSchedule:
        schedule = WorkingSchedule(
            name=data.name,
            schedule_type=data.schedule_type,
            total_weekly_hours=0,
        )
        self.db.add(schedule)
        await self.db.flush()  # get schedule.id

        lines = [
            WorkingScheduleLine(
                working_schedule_id=schedule.id,
                day=line.day,
                start_time=line.start_time,
                end_time=line.end_time,
                break_minutes=line.break_minutes,
            )
            for line in data.lines
        ]
        self.db.add_all(lines)
        await self.db.flush()

        schedule.total_weekly_hours = _compute_hours(lines)
        await self.db.commit()
        
        # Reload with lines
        return await self.get_by_id(schedule.id)  # type: ignore[return-value]

    async def update(
        self, schedule: WorkingSchedule, data: WorkingScheduleUpdate
    ) -> WorkingSchedule:
        if data.name is not None:
            schedule.name = data.name
        if data.schedule_type is not None:
            schedule.schedule_type = data.schedule_type

        if data.lines is not None:
            # Replace all existing lines
            await self.db.execute(
                delete(WorkingScheduleLine).where(
                    WorkingScheduleLine.working_schedule_id == schedule.id
                )
            )
            new_lines = [
                WorkingScheduleLine(
                    working_schedule_id=schedule.id,
                    day=line.day,
                    start_time=line.start_time,
                    end_time=line.end_time,
                    break_minutes=line.break_minutes,
                )
                for line in data.lines
            ]
            self.db.add_all(new_lines)
            await self.db.flush()
            schedule.total_weekly_hours = _compute_hours(new_lines)

        await self.db.commit()
        return await self.get_by_id(schedule.id)  # type: ignore[return-value]
