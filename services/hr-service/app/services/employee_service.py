from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate

class EmployeeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100):
        result = await self.db.execute(select(Employee).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_id(self, employee_id: int):
        result = await self.db.execute(select(Employee).filter(Employee.id == employee_id))
        return result.scalars().first()

    async def create(self, employee_in: EmployeeCreate) -> Employee:
        emp = Employee(**employee_in.model_dump())
        self.db.add(emp)
        await self.db.commit()
        await self.db.refresh(emp)
        return emp
