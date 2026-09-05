from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.contract import Contract
from app.schemas.contract import ContractCreate
from fastapi import HTTPException

class ContractService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_contract(self, contract_in: ContractCreate) -> Contract:
        # Validate active contract overlap
        query = select(Contract).filter(
            and_(
                Contract.employee_id == contract_in.employee_id,
                Contract.status == "ACTIVE"
            )
        )
        existing = (await self.db.execute(query)).scalars().first()
        if existing and contract_in.status == "ACTIVE":
            raise HTTPException(
                status_code=400,
                detail=f"Employee already has an active contract: {existing.contract_reference}"
            )
        
        contract = Contract(**contract_in.model_dump())
        self.db.add(contract)
        await self.db.commit()
        await self.db.refresh(contract)
        return contract
