from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.employee import EmployeeCreate, EmployeeOut
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/", response_model=list[EmployeeOut])
async def list_employees(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    service = EmployeeService(db)
    return await service.get_all(skip=skip, limit=limit)

@router.post("/", response_model=EmployeeOut)
async def create_employee(employee_in: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    service = EmployeeService(db)
    return await service.create(employee_in)

@router.get("/{employee_id}", response_model=EmployeeOut)
async def get_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
    service = EmployeeService(db)
    emp = await service.get_by_id(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp
