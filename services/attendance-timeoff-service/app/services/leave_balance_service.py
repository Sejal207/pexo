from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.time_off_allocation import TimeOffAllocation
from app.models.time_off_request import TimeOffRequest

class LeaveBalanceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_remaining_leave(self, employee_id: int, time_off_type_id: int, year: int) -> float:
        # Sum allocations
        alloc_q = select(func.sum(TimeOffAllocation.allocated_days)).filter(
            TimeOffAllocation.employee_id == employee_id,
            TimeOffAllocation.time_off_type_id == time_off_type_id,
            TimeOffAllocation.year == year
        )
        total_allocated = (await self.db.execute(alloc_q)).scalar() or 0.0

        # Sum taken leave
        taken_q = select(func.sum(TimeOffRequest.number_of_days)).filter(
            TimeOffRequest.employee_id == employee_id,
            TimeOffRequest.time_off_type_id == time_off_type_id,
            TimeOffRequest.status == "APPROVED"
        )
        total_taken = (await self.db.execute(taken_q)).scalar() or 0.0

        return max(0.0, total_allocated - total_taken)
