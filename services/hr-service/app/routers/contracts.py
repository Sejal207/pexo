from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.contract import Contract
from app.schemas.contract import ContractCreate, ContractOut
from app.services.contract_service import ContractService

router = APIRouter(prefix="/contracts", tags=["Contracts"])

@router.get("/", response_model=list[ContractOut])
async def list_contracts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contract))
    return result.scalars().all()

@router.post("/", response_model=ContractOut)
async def create_contract(contract_in: ContractCreate, db: AsyncSession = Depends(get_db)):
    service = ContractService(db)
    return await service.create_contract(contract_in)
